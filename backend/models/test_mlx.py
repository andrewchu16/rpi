#!/usr/bin/env python3
"""
Test script for MLX LLM integration.
Run this to verify that the MLX setup is working correctly.
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chat.services.llm import LLM
from chat.schema import ChatMessage, ChatSender


async def test_llm():
    """Test the MLX LLM service."""
    print("🚀 Testing MLX LLM Integration...")
    
    try:
        # Initialize the LLM service
        print("📥 Loading MLX model...")
        llm = LLM()
        print("✅ Model loaded successfully!")
        
        # Test conversation formatting
        print("\n💬 Testing conversation formatting...")
        messages = [
            ChatMessage(
                id=1,
                sender=ChatSender.USER,
                content="Hello, how are you today?",
                timestamp=None
            )
        ]
        
        # Test response generation
        print("🤖 Generating response...")
        response = await llm.generate_response(messages)
        print(f"✅ Response generated: {response[:100]}...")
        
        # Test streaming
        print("\n🌊 Testing streaming response...")
        stream_count = 0
        async for token in llm.stream_response(messages):
            stream_count += 1
            if stream_count <= 3:  # Just show first few tokens
                print(f"   Token {stream_count}: {token[:50]}...")
            elif stream_count == 4:
                print("   ... (continuing)")
                break
        
        print(f"✅ Streaming test completed. Generated {stream_count} tokens.")
        
        print("\n🎉 All tests passed! MLX integration is working correctly.")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("MLX LLM Integration Test")
    print("=" * 60)
    
    success = asyncio.run(test_llm())
    
    if success:
        print("\n✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
