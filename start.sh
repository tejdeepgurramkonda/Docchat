#!/bin/bash
# Railway startup script for ChatDocs AI

# Get the port from environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting ChatDocs AI on port $PORT"

# Start the application
exec python -m uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1
