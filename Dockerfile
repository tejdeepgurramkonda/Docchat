FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/uploads logs vector_store

# Set permissions
RUN chmod -R 755 data logs vector_store

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default port (Railway will override via $PORT)
ENV PORT=8000

# Expose port
EXPOSE $PORT

# Run the application - Railway will override this CMD with railway.toml startCommand
CMD uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1
