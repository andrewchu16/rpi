import asyncio
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
from llama_cpp import Llama
from src.chat.config import chat_config
from src.chat.schema import ChatMessage

logger = logging.getLogger(__name__)
print(logger)

class LLM:
    """LLaMA.cpp-based LLM service for chat generation using GGUF models."""

    def __init__(self) -> None:
        """Initialize the LLaMA.cpp-based LLM model."""
        model_path: str = chat_config.model_name

        # Load the model using llama-cpp-python
        logger.info(f"Loading GGUF model from {model_path}...")
        print(f"Loading GGUF model from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=chat_config.max_context_length,  # Context window size
            n_threads=None,  # Use all available CPU threads
            verbose=False,  # Set to True for debugging
        )
        logger.info("GGUF model loaded successfully!")

        # Set generation parameters
        self.max_new_tokens: int = chat_config.max_response_tokens
        self.temperature: float = 0.7
        self.top_p: float = 0.9
        self.top_k: int = 40

    def _format_conversation(self, conversation_history: List[ChatMessage]) -> str:
        """Format conversation history into a prompt string for the model.

        Args:
            conversation_history: List of chat messages

        Returns:
            Formatted prompt string
        """
        # Convert to the format expected by the model
        messages: List[Dict[str, str]] = [
            {"role": message.sender.value, "content": message.content}
            for message in conversation_history
        ]

        # Use the model's built-in chat template
        try:
            # LLaMA.cpp handles chat formatting automatically
            return messages
        except Exception as e:
            logger.warning(f"Error formatting conversation: {e}")
            # Fallback to manual formatting
            return self._manual_format(messages)

    def _manual_format(self, messages: List[Dict[str, str]]) -> str:
        """Manual formatting for conversations when chat template is not available.

        Args:
            messages: List of message dictionaries

        Returns:
            Formatted prompt string
        """
        formatted: str = ""
        for message in messages:
            role: str = message["role"]
            content: str = message["content"]
            if role == "user":
                formatted += f"<|user|>\n{content}<|end|>\n"
            elif role == "assistant":
                formatted += f"<|assistant|>\n{content}<|end|>\n"

        formatted += "<|assistant|>\n"
        return formatted

    async def generate_response(self, conversation_history: List[ChatMessage]) -> str:
        """Generate a complete response for the given conversation history.

        Args:
            conversation_history: List of chat messages

        Returns:
            Generated response text
        """
        # Format the conversation
        messages = self._format_conversation(conversation_history)

        # Generate response using LLaMA.cpp
        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                stop=["<|end|>", "<|user|>"],
            )

            # Extract the response content
            if response and "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"].strip()
            else:
                logger.error("No response generated from model")
                return "I'm sorry, I couldn't generate a response."

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, there was an error generating a response."

    async def stream_response(
        self, conversation_history: List[ChatMessage]
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens as they are generated.

        Args:
            conversation_history: List of chat messages

        Yields:
            Accumulated response text as it's generated
        """
        # Format the conversation
        messages = self._format_conversation(conversation_history)

        try:
            # Create streaming completion
            stream = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                stop=["<|end|>", "<|user|>"],
                stream=True,
            )

            accumulated_text: str = ""

            # Stream the response
            for chunk in stream:
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        content = delta["content"]
                        accumulated_text += content
                        yield accumulated_text

                        # Small delay to simulate streaming
                        await asyncio.sleep(0.05)

        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            yield "I'm sorry, there was an error generating a response."
