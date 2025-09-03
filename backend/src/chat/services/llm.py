import asyncio
from typing import AsyncGenerator, List, Dict, Any, Optional
from mlx_lm import load, generate
import mlx.core as mx
import mlx.nn as nn

from src.chat.config import chat_config
from src.chat.schema import ChatMessage


class LLM:
    """MLX-based LLM service for chat generation."""
    
    def __init__(self) -> None:
        """Initialize the MLX-based LLM model and tokenizer."""
        model_name: str = chat_config.model_name
        
        # Load the model and tokenizer using MLX
        self.model, self.tokenizer = load(model_name)
        
        # Set generation parameters
        self.max_new_tokens: int = chat_config.max_response_tokens
        self.temperature: float = 0.7
        self.top_p: float = 0.9
        
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
        
        # Apply chat template if available, otherwise format manually
        try:
            text: str = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        except AttributeError:
            # Fallback to manual formatting if chat template not available
            text = self._manual_format(messages)
            
        return text
    
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
        prompt: str = self._format_conversation(conversation_history)
        
        # Tokenize the input
        tokens: mx.array = self.tokenizer.encode(prompt)
        
        # Generate response
        response_tokens: mx.array = generate(
            self.model,
            self.tokenizer,
            prompt,
            max_tokens=self.max_new_tokens,
            temp=self.temperature,
            top_p=self.top_p,
        )
        
        # Decode the response
        response: str = self.tokenizer.decode(response_tokens)
        
        # Remove the original prompt from the response
        if response.startswith(prompt):
            response = response[len(prompt):].strip()
            
        return response

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
        prompt: str = self._format_conversation(conversation_history)
        
        # Tokenize the input
        tokens: mx.array = self.tokenizer.encode(prompt)
        
        # Initialize generation state
        logits: mx.array = self.model(tokens)
        next_token: mx.array = mx.argmax(logits[-1:], axis=-1)
        tokens = mx.concatenate([tokens, next_token])
        
        accumulated_text: str = ""
        
        # Stream generation
        for _ in range(self.max_new_tokens):
            # Generate next token
            logits = self.model(tokens)
            next_token = mx.argmax(logits[-1:], axis=-1)
            tokens = mx.concatenate([tokens, next_token])
            
            # Decode the new token
            new_text: str = self.tokenizer.decode(next_token)
            
            # Skip special tokens
            if new_text.strip() and not new_text.startswith("<|"):
                accumulated_text += new_text
                yield accumulated_text
                
                # Small delay to simulate streaming
                await asyncio.sleep(0.2)
            
            # Check for end of response
            if next_token.item() == self.tokenizer.eos_token_id:
                break
