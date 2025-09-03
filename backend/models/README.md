# MLX Models Directory

This directory is dedicated to storing machine learning models used by the RPI backend.

## Current Setup

The backend now uses **MLX** (Apple's machine learning framework) instead of PyTorch/Transformers for better performance on Apple Silicon.

## Dependencies

- `mlx>=0.3.0` - Core MLX framework
- `mlx-lm>=0.2.0` - MLX language model utilities
- `transformers>=4.40.0` - For tokenizer compatibility

## Model Configuration

The LLM service is configured to use:
- **Model**: `mlx-community/llama-3.2-3B-instruct`
- **Framework**: MLX (optimized for Apple Silicon)
- **Generation Parameters**:
  - Temperature: 0.7
  - Top-p: 0.9
  - Max tokens: Configurable via `chat_config.max_response_tokens`

## Benefits of MLX

1. **Apple Silicon Optimization**: Native performance on M1/M2/M3 chips
2. **Memory Efficiency**: Better memory management than PyTorch
3. **Fast Inference**: Optimized for local inference
4. **No CUDA Dependencies**: Pure Apple ecosystem solution

## Installation

Install dependencies using uv:

```bash
cd backend
uv sync
```

## Usage

The LLM service automatically handles:
- Model loading and initialization
- Conversation formatting
- Token generation and streaming
- Response processing

## Model Files

When models are downloaded, they will be cached in the standard MLX cache location:
- **macOS**: `~/Library/Application Support/mlx`
- **Linux**: `~/.cache/mlx`
