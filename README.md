# RPI

## Setup

Run this command for development mode:
```bash
docker compose -f compose.dev.yaml up -w --build --remove-orphans
```

Run this command for production mode:
```bash
docker compose -f compose.yaml up -d --build
```