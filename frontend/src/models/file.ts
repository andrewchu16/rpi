// File-related types
export interface FileInfo {
  id: string;
  title: string;
  file_type: 'markdown' | 'image' | 'pdf';
  file_size: number;
  upload_date: string;
  content?: string;
  metadata?: Record<string, unknown>;
}

export interface FileListResponse {
  files: FileInfo[];
  pagination: {
    page: number;
    page_size: number;
    total_pages: number;
    total_items: number;
    has_next: boolean;
    has_previous: boolean;
  };
}

export interface UploadResponse {
  message: string;
  file_info: FileInfo;
}

export interface BulkUploadResponse {
  message: string;
  successful_uploads: FileInfo[];
  failed_uploads: Array<{
    filename: string;
    error: string;
  }>;
  total_files: number;
  successful_count: number;
  failed_count: number;
}
