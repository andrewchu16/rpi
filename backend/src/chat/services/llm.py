import asyncio
import logging
from typing import AsyncGenerator, List, Dict
from llama_cpp import Llama
from src.chat.config import chat_config
from src.chat.schema import ChatMessage

logger = logging.getLogger(__name__)


class LLM:
    """LLaMA.cpp-based LLM service for chat generation using GGUF models."""

    # System prompts
    RESPONSE_SYSTEM_PROMPT = (
        "You are a helpful, knowledgeable, and friendly AI assistant. "
        "Provide accurate, concise, and helpful responses to user questions. "
        "Be conversational and engaging while staying focused on being useful."
    )

    SUMMARIZE_SYSTEM_PROMPT = (
        "You are an expert at summarizing conversations. "
        "Your task is to read the entire conversation and output a single, clear, rephrased question "
        "that captures the main intent and context of what the user is asking about. "
        "The output should be only one line, no explanation, no additional text - just the rephrased question."
    )

    def __init__(self) -> None:
        """Initialize the LLaMA.cpp-based LLM model."""
        model_path: str = chat_config.llm_model_path

        # Load the model using llama-cpp-python
        logger.info(f"Loading GGUF model from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=chat_config.max_context_token_count,  # Context window size
            n_threads=None,  # Use all available CPU threads
            verbose=False,  # Set to True for debugging
        )
        logger.info("GGUF model loaded successfully!")

        # Set generation parameters
        self.max_new_tokens: int = chat_config.max_response_token_count
        self.temperature: float = 0.7
        self.top_p: float = 0.9
        self.top_k: int = 20

    def _format_conversation(
        self, conversation_history: List[ChatMessage], system_prompt: str = None
    ) -> List[Dict[str, str]]:
        """Format conversation history into a prompt string for the model.

        Args:
            conversation_history: List of chat messages
            system_prompt: Optional system prompt to prepend

        Returns:
            List of message dictionaries for the model
        """
        # Convert to the format expected by the model
        messages: List[Dict[str, str]] = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation messages
        for message in conversation_history:
            # Map AI role to assistant for the model
            role = "assistant" if message.sender.value == "AI" else message.sender.value
            messages.append({"role": role, "content": message.content})

        return messages

    async def generate_response(self, conversation_history: List[ChatMessage]) -> str:
        """Generate a complete response for the given conversation history.

        Args:
            conversation_history: List of chat messages

        Returns:
            Generated response text
        """
        # Format the conversation with system prompt for responses
        messages = self._format_conversation(
            conversation_history, self.RESPONSE_SYSTEM_PROMPT
        )

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

    async def summarize_conversation(
        self, conversation_history: List[ChatMessage]
    ) -> str:
        """Summarize the given conversation history into a single rephrased question.

        Args:
            conversation_history: List of chat messages

        Returns:
            A single line rephrased question summarizing the conversation
        """
        # Format the conversation with system prompt for summarization
        messages = self._format_conversation(
            conversation_history, self.SUMMARIZE_SYSTEM_PROMPT
        )

        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=50,  # Keep summary short
                temperature=0.3,  # Lower temperature for more focused summary
                top_p=0.8,
                top_k=20,
                stop=[
                    "<|end|>",
                    "<|user|>",
                    "\n",
                ],  # Stop at newline to ensure single line
            )

            # Extract the response content
            if response and "choices" in response and len(response["choices"]) > 0:
                summary = response["choices"][0]["message"]["content"].strip()
                # Ensure it's a single line
                summary = summary.split("\n")[0].strip()
                return summary if summary else "What is your question?"
            else:
                logger.error("No summary generated from model")
                return "What is your question?"

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "What is your question?"

    async def stream_response(
        self, conversation_history: List[ChatMessage]
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens as they are generated.

        Args:
            conversation_history: List of chat messages

        Yields:
            Individual tokens as they are generated
        """
        # Format the conversation with system prompt for responses
        messages = self._format_conversation(
            conversation_history, self.RESPONSE_SYSTEM_PROMPT
        )

        try:
            # Create streaming completion
            stream = self.llm.create_chat_completion(
                messages=messages,
                max_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                top_k=self.top_k,
                stream=True,
            )

            # Stream the response
            for chunk in stream:
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta:
                        content = delta["content"]
                        yield content

        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            yield "I'm sorry, there was an error generating a response."
