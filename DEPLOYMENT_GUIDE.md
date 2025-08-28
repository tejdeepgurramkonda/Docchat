# 🚀 ChatDocs AI - Deployment Guide

Complete guide to deploy your ChatDocs AI application using various methods.

## 📋 Pre-Deployment Checklist

### 1. Prepare Environment Variables
Create a production `.env` file:
```env
# Google Gemini API Configuration
GOOGLE_API_KEY=your_actual_api_key_here

# Application Configuration
APP_NAME=DOCChat
APP_VERSION=1.0.0
DEBUG=False

# Vector Store Configuration
VECTOR_STORE_TYPE=faiss
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# LLM Configuration
MODEL_NAME=gemini-2.5-pro
TEMPERATURE=0.7
MAX_TOKENS=100000

# File Upload Configuration
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=pdf,docx,txt

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/usage.log

# Database Configuration
DATABASE_URL=sqlite:///data/docchat.db

# Production Settings
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### 2. Update Requirements for Production
Add production dependencies to `requirements.txt`:
```txt
# Core dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
jinja2>=3.1.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
gunicorn>=21.2.0

# AI/ML dependencies
google-generativeai>=0.3.0
langchain>=0.1.0
langchain-google-genai>=0.0.5
langchain-community>=0.0.10

# Vector store
faiss-cpu>=1.7.4

# Document processing
PyMuPDF>=1.23.0
python-docx>=0.8.11
tiktoken>=0.5.0

# Production
redis>=5.0.0
celery>=5.3.0
nginx
```

## 🌐 Deployment Options

## 1. 🐳 Docker Deployment (Recommended)

### Create Dockerfile
```dockerfile
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

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Create docker-compose.yml
```yaml
version: '3.8'

services:
  docchat:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - docchat
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

### Deploy with Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## 2. ☁️ Cloud Platform Deployments

### A. Heroku Deployment

1. **Create Procfile:**
```txt
web: uvicorn app:app --host 0.0.0.0 --port $PORT --workers 4
```

2. **Create runtime.txt:**
```txt
python-3.11.9
```

3. **Deploy:**
```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-docchat-app

# Set environment variables
heroku config:set GOOGLE_API_KEY=your_key_here
heroku config:set DEBUG=False

# Deploy
git add .
git commit -m "Initial deployment"
git push heroku main
```

### B. Railway Deployment

1. **Connect GitHub repository to Railway**
2. **Set environment variables in Railway dashboard**
3. **Deploy automatically on push**

Railway config (`railway.toml`):
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app:app --host 0.0.0.0 --port $PORT"

[env]
PORT = "8000"
```

### C. Vercel Deployment

1. **Create vercel.json:**
```json
{
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

2. **Deploy:**
```bash
npm i -g vercel
vercel --prod
```

### D. DigitalOcean App Platform

1. **Create .do/app.yaml:**
```yaml
name: docchat-ai
services:
- name: web
  source_dir: /
  github:
    repo: your-username/docchat
    branch: main
  run_command: uvicorn app:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: GOOGLE_API_KEY
    value: your_key_here
    type: SECRET
  - key: DEBUG
    value: "False"
  http_port: 8080
```

## 3. 🖥️ VPS/Server Deployment

### A. Ubuntu Server Setup

1. **Update system:**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install Python and dependencies:**
```bash
sudo apt install python3 python3-pip python3-venv nginx -y
```

3. **Create application user:**
```bash
sudo useradd -m -s /bin/bash docchat
sudo su - docchat
```

4. **Setup application:**
```bash
# Clone your repository
git clone https://github.com/your-username/docchat.git
cd docchat

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
nano .env  # Edit with your settings
```

5. **Create systemd service:**
```bash
sudo nano /etc/systemd/system/docchat.service
```

```ini
[Unit]
Description=ChatDocs AI FastAPI application
After=network.target

[Service]
User=docchat
Group=docchat
WorkingDirectory=/home/docchat/docchat
Environment="PATH=/home/docchat/docchat/venv/bin"
ExecStart=/home/docchat/docchat/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

6. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/docchat
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    # Handle file uploads
    client_max_body_size 100M;
}
```

7. **Enable and start services:**
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/docchat /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Enable and start application
sudo systemctl enable docchat
sudo systemctl start docchat
sudo systemctl status docchat
```

### B. SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

## 4. 🏢 Enterprise Deployment

### A. Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: docchat-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: docchat
  template:
    metadata:
      labels:
        app: docchat
    spec:
      containers:
      - name: docchat
        image: your-registry/docchat:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: docchat-secrets
              key: google-api-key
---
apiVersion: v1
kind: Service
metadata:
  name: docchat-service
spec:
  selector:
    app: docchat
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### B. AWS ECS Deployment

**task-definition.json:**
```json
{
  "family": "docchat-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "docchat",
      "image": "your-account.dkr.ecr.region.amazonaws.com/docchat:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "GOOGLE_API_KEY",
          "value": "your-key-here"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/docchat",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

## 🔧 Production Optimizations

### 1. Performance Settings
```python
# In app.py - Add production configurations
import os
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not os.getenv("DEBUG", "True").lower() == "true":
        # Production optimizations
        import logging
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
    yield
    # Shutdown
    pass

app = FastAPI(
    title="DOCChat",
    description="Chat with your documents",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "False").lower() == "true" else None,
)
```

### 2. Database Configuration
```python
# Use PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/docchat.db")

if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration
    import asyncpg
    # Async database setup
```

### 3. Caching with Redis
```python
import redis
import json

# Redis client
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Cache responses
def cache_response(key: str, data: dict, ttl: int = 3600):
    redis_client.setex(key, ttl, json.dumps(data))

def get_cached_response(key: str):
    cached = redis_client.get(key)
    return json.loads(cached) if cached else None
```

## 🔒 Security Considerations

### 1. Environment Security
- Use environment variables for all secrets
- Never commit `.env` files
- Use secret management services (AWS Secrets Manager, etc.)

### 2. API Security
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)
```

### 3. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("10/minute")
async def chat_with_document(request: Request, chat_request: ChatRequest):
    # Your chat logic
    pass
```

## 📊 Monitoring and Logging

### 1. Application Monitoring
```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 2. Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": os.getenv("APP_VERSION", "1.0.0")
    }
```

## 🚀 Quick Deployment Commands

### Local Testing
```bash
# Production-like testing
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Quick Deploy
```bash
# Build and run
docker build -t docchat .
docker run -p 8000:8000 --env-file .env docchat
```

### Git-based Deployment
```bash
# Set up automatic deployment
git add .
git commit -m "Deploy to production"
git push origin main
```

## 📞 Support

- **Documentation**: Check README_COMPLETE.md
- **Issues**: Create GitHub issues
- **Production Support**: Set up monitoring and alerting

---

**Choose the deployment method that best fits your needs and infrastructure requirements!** 🎯

**Recommended for beginners**: Docker + DigitalOcean App Platform
**Recommended for production**: VPS with Nginx + SSL
**Recommended for enterprise**: Kubernetes or AWS ECS
