# Backend API

A FastAPI-based chat API with PostgreSQL database support.

## Features

- Chat message handling with `/response` and `/stream` endpoints
- PostgreSQL database storage for messages, cache info, and processing info
- Automatic database table creation on startup
- Docker support with PostgreSQL service

## Database Schema

### Messages Table
- `id`: Primary key
- `sender`: Message sender ("user" or "AI")
- `content`: Message content
- `timestamp`: Message timestamp

### Cache Info Table
- `id`: Primary key
- `message_id`: Foreign key to messages table
- `hit`: Whether message was found in cache
- `cache_timestamp`: When message was cached
- `num_hits`: Number of cache hits

### Processing Info Table
- `id`: Primary key
- `message_id`: Foreign key to messages table
- `start_timestamp`: Processing start time
- `end_timestamp`: Processing end time

## API Endpoints

- `POST /chat/response` - Get a chat response (saves to database)
- `POST /chat/stream` - Stream a chat response (saves to database)
- `GET /chat/messages` - Get stored messages from database
- `GET /chat/messages/{id}/cache` - Get cache info for a message
- `GET /chat/messages/{id}/processing` - Get processing info for a message
- `GET /chat/info` - Get API statistics

## Development Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Start the development environment:
   ```bash
   docker-compose -f compose.dev.yaml up -d
   ```

3. The API will be available at `http://localhost:8000`
   - Database tables are automatically created on startup

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Enable/disable debug mode
- `ALLOWED_ORIGINS`: CORS allowed origins

## Docker

The application includes Docker support with:
- PostgreSQL 16 database
- FastAPI backend with hot reload
- Nginx reverse proxy (production)
- SSL certificate management (production)