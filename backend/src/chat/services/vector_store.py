# pip install hnswlib
from collections import defaultdict, OrderedDict
from typing import Union
import hnswlib
import numpy as np
import threading
import json
from pathlib import Path


class VectorStore:
    """
    Hot in-RAM HNSW index with LFU eviction (LRU tie-break within same freq).
    - O(1) get/put/evict using:
        * key_info:  id -> {"label": int, "freq": int}
        * freq_map:  freq -> OrderedDict[id -> None]   (left=LRU, right=MRU)
        * min_freq:  smallest freq currently present
    - Labels are recycled via a free-label stack so we never exceed max_elements.
    """

    def __init__(
        self,
        dim: int,
        capacity: int,
        space: str = "cosine",
        M: int = 32,
        ef_construction: int = 200,
        ef_search: int = 256,
        allow_updates: bool = True,
    ) -> None:
        """
        Initialize the LFU Hot Index with HNSW vector search capabilities.

        Args:
            dim: Dimension of the vector embeddings to be stored
            capacity: Maximum number of vectors that can be stored in the index
            space: Distance metric for HNSW ("cosine", "l2", or "ip")
            M: Maximum number of bi-directional links for each element in HNSW
            ef_construction: Size of the dynamic candidate list during construction
            ef_search: Size of the dynamic candidate list during search
            allow_updates: Whether to allow updates to existing vectors (unused in current implementation)
        """
        # Store configuration parameters
        self.dim: int = dim
        self.capacity: int = int(capacity)
        self.lock: threading.RLock = threading.RLock()

        # Initialize HNSW index for vector similarity search
        self.index: hnswlib.Index = hnswlib.Index(space=space, dim=dim)
        # Important: enable replace_deleted so we can reuse slots on eviction
        self.index.init_index(
            max_elements=self.capacity,
            M=M,
            ef_construction=ef_construction,
            allow_replace_deleted=True,
        )
        self.index.set_ef(ef_search)

        # LFU (Least Frequently Used) eviction data structures
        self.key_info: dict[
            str, dict[str, int]
        ] = {}  # id -> {"label": int, "freq": int}
        self.freq_map: dict[int, OrderedDict[str, None]] = defaultdict(
            OrderedDict
        )  # freq -> OrderedDict of ids
        self.min_freq: int = 0  # Tracks the smallest frequency currently present

        # ID/label mapping for hnswlib (maps HNSW internal labels to our string IDs)
        self.label_to_id: dict[int, str] = {}

        # Pre-allocate a pool of labels [capacity-1 ... 0] for O(1) .pop()
        # This ensures we never exceed max_elements and can reuse deleted slots
        self.free_labels: list[int] = list(range(self.capacity - 1, -1, -1))

    # ---------- internal LFU helpers ----------
    def _insert_freq_bucket_tail(self, id_str: str, freq: int) -> None:
        """
        Insert an item at the tail (most recently used) of a frequency bucket.

        Args:
            id_str: The string identifier of the item
            freq: The frequency bucket to insert into
        """
        self.freq_map[freq][id_str] = None  # append to tail (MRU in this freq)

    def _remove_from_freq_bucket(self, id_str: str, freq: int) -> None:
        """
        Remove an item from a frequency bucket and clean up empty buckets.

        Args:
            id_str: The string identifier of the item to remove
            freq: The frequency bucket to remove from
        """
        bucket = self.freq_map[freq]
        bucket.pop(id_str, None)
        if not bucket:
            del self.freq_map[freq]
            if self.min_freq == freq:
                # min_freq will be adjusted by caller if needed
                pass

    def _bump_freq(self, id_str: str) -> None:
        """
        Increment the access frequency of an item and move it to the appropriate bucket.

        Args:
            id_str: The string identifier of the item to bump
        """
        info = self.key_info[id_str]
        f = info["freq"]
        self._remove_from_freq_bucket(id_str, f)
        new_f = f + 1
        info["freq"] = new_f
        self._insert_freq_bucket_tail(id_str, new_f)
        if self.min_freq == f and f not in self.freq_map:
            self.min_freq = new_f

    def _evict_one(self) -> None:
        """
        Evict the least frequently used item (with LRU tie-breaker).

        This method removes the least recently used item from the smallest frequency bucket,
        marks it as deleted in the HNSW index, and returns its label to the free pool.
        """
        # Evict LRU from the smallest frequency bucket
        f = self.min_freq
        victim_id, _ = self.freq_map[f].popitem(last=False)  # pop LRU within min_freq
        if not self.freq_map[f]:
            del self.freq_map[f]
        info = self.key_info.pop(victim_id)
        lbl = info["label"]
        self.label_to_id.pop(lbl, None)
        # mark_deleted so search ignores it; keep label for reuse
        self.index.mark_deleted(lbl)
        self.free_labels.append(lbl)

    # ---------- public API ----------
    def add(self, id_str: str, vec: Union[list[float], np.ndarray]) -> None:
        """
        Add a vector to the index with the given string identifier.

        If the ID already exists, the old vector is replaced. If the index is at capacity,
        the least frequently used item is evicted first.

        Args:
            id_str: Unique string identifier for the vector (e.g., query hash)
            vec: Vector embedding to store (list or numpy array)

        Raises:
            RuntimeError: If no free labels are available (should not happen in normal operation)
        """
        # Ensure vector is in the correct format for HNSW
        vec = np.asarray(vec, dtype=np.float32).reshape(1, -1)
        with self.lock:
            # Update = delete old first (simple & safe approach)
            if id_str in self.key_info:
                self.delete(id_str)

            # Evict least frequently used item if at capacity
            if len(self.key_info) >= self.capacity:
                self._evict_one()

            # Allocate a reusable label from the free pool
            if not self.free_labels:
                raise RuntimeError("No free labels available (logic error)")
            lbl = self.free_labels.pop()

            # Insert vector into HNSW index; replace_deleted=True lets us reuse deleted slots
            self.index.add_items(
                vec, ids=np.array([lbl], dtype=np.int64), replace_deleted=True
            )
            self.label_to_id[lbl] = id_str

            # Insert into LFU tracking structures with initial frequency of 1
            self.key_info[id_str] = {"label": lbl, "freq": 1}
            self._insert_freq_bucket_tail(id_str, 1)
            self.min_freq = 1

    def delete(self, id_str: str) -> None:
        """
        Remove a vector from the index by its string identifier.

        Args:
            id_str: The string identifier of the vector to remove
        """
        with self.lock:
            info = self.key_info.pop(id_str, None)
            if info is None:
                return
            lbl = info["label"]
            f = info["freq"]
            self._remove_from_freq_bucket(id_str, f)
            self.label_to_id.pop(lbl, None)
            self.index.mark_deleted(lbl)
            self.free_labels.append(lbl)
            # Repair min_freq if needed
            if self.min_freq == f and f not in self.freq_map:
                # next higher freq present? else 0 if cache empty
                self.min_freq = min(self.freq_map.keys(), default=0)

    def search(
        self, query_vec: Union[list[float], np.ndarray], k: int = 5
    ) -> list[tuple[str, float]]:
        """
        Search for the k most similar vectors to the query vector.

        This method performs a k-nearest neighbor search and automatically updates
        the access frequency of found items (bumping their frequency for LFU tracking).

        Args:
            query_vec: The query vector to search for (list or numpy array)
            k: Number of nearest neighbors to return

        Returns:
            List of tuples containing (id_string, distance) for the k nearest neighbors.
            Only returns items that are currently in the index (skips deleted items).
            Returns empty list if index is empty.
        """
        q = np.asarray(query_vec, dtype=np.float32).reshape(1, -1)
        with self.lock:
            # Check if index is empty or has fewer elements than requested
            current_count = len(self.key_info)
            if current_count == 0:
                return []
            
            # Adjust k to not exceed available elements
            actual_k = min(k, current_count)
            
            try:
                labels, dists = self.index.knn_query(q, k=actual_k)
                lbls = labels[0].tolist()
                ds = dists[0].tolist()

                # Map labels -> ids; deleted labels might appear as unknown -> skip
                ids = [self.label_to_id.get(int(label)) for label in lbls]

                # Bump freq for hits we actually own
                for i in ids:
                    if i is not None and i in self.key_info:
                        self._bump_freq(i)

                return [(i, float(d)) for i, d in zip(ids, ds) if i is not None]
            except Exception as e:
                # Log the error and return empty list as fallback
                print(f"Warning: Vector search failed: {e}")
                return []

    def save(self, dirpath: Union[str, Path]) -> None:
        """
        Save the index and metadata to disk for persistence.

        This method saves both the HNSW index binary file and a JSON metadata file
        containing all the LFU tracking information needed to restore the index.

        Args:
            dirpath: Directory path where to save the index files
        """
        Path(dirpath).mkdir(parents=True, exist_ok=True)
        self.index.save_index(str(Path(dirpath, "hot_hnsw.bin")))
        meta = {
            "dim": self.dim,
            "capacity": self.capacity,
            "id_to_label": {k: v["label"] for k, v in self.key_info.items()},
            "freqs": {k: v["freq"] for k, v in self.key_info.items()},
            "label_to_id": self.label_to_id,
            "free_labels": self.free_labels,
            "min_freq": self.min_freq,
        }
        Path(dirpath, "meta.json").write_text(json.dumps(meta))

    def load(
        self, dirpath: Union[str, Path], space: str = "cosine", ef_search: int = 256
    ) -> None:
        """
        Load a previously saved index and metadata from disk.

        This method restores both the HNSW index and all LFU tracking information
        from the saved files, allowing the index to continue operating with the
        same state as when it was saved.

        Args:
            dirpath: Directory path where the index files are located
            space: Distance metric for HNSW (must match the saved index)
            ef_search: Search parameter for the loaded index
        """
        # Recreate index object and load
        self.index = hnswlib.Index(space=space, dim=self.dim)
        self.index.load_index(
            str(Path(dirpath, "hot_hnsw.bin")), allow_replace_deleted=True
        )
        self.index.set_ef(ef_search)

        # Load and restore metadata
        meta = json.loads(Path(dirpath, "meta.json").read_text())
        self.capacity = meta["capacity"]
        self.label_to_id = {int(k): v for k, v in meta["label_to_id"].items()}
        self.free_labels = list(meta["free_labels"])
        self.min_freq = int(meta["min_freq"])

        # Clear existing data structures
        self.key_info.clear()
        self.freq_map.clear()

        # Restore LFU tracking information
        for id_str, lbl in meta["id_to_label"].items():
            f = int(meta["freqs"].get(id_str, 1))
            self.key_info[id_str] = {"label": int(lbl), "freq": f}
            self._insert_freq_bucket_tail(id_str, f)

        # Ensure min_freq is correctly set
        if self.freq_map:
            self.min_freq = min(self.freq_map.keys())
        else:
            self.min_freq = 0
