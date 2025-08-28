# 🚄 Railway Deployment Guide for ChatDocs AI

Railway is a modern deployment platform that makes it easy to deploy applications directly from GitHub.

## 🚀 Quick Railway Deployment

### Step 1: Prepare Your Repository

1. **Push your code to GitHub:**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/your-username/docchat-ai.git
git push -u origin main
```

### Step 2: Deploy on Railway

1. **Visit Railway:** https://railway.app
2. **Sign up/Login** with GitHub
3. **Click "New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose your ChatDocs AI repository**

### Step 3: Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

```env
GOOGLE_API_KEY=your_actual_api_key_here
MODEL_NAME=gemini-2.5-pro
TEMPERATURE=0.7
MAX_TOKENS=100000
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEBUG=False
```

### Step 4: Configure Build Settings

Railway will auto-detect your Python app, but you can create a `railway.toml` for custom settings:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 60
restartPolicyType = "ON_FAILURE"

[env]
PORT = "8000"
PYTHONPATH = "/app"
```

### Step 5: Deploy!

Railway will automatically:
- ✅ Install dependencies from `requirements.txt`
- ✅ Build your application
- ✅ Deploy to a public URL
- ✅ Provide HTTPS automatically

**Your app will be live at:** `https://your-app-name.railway.app`

---

# 🎨 Render Deployment Guide for ChatDocs AI

Render is another excellent platform for deploying web applications with great developer experience.

## 🚀 Quick Render Deployment

### Step 1: Prepare Your Repository

Same as Railway - push your code to GitHub.

### Step 2: Deploy on Render

1. **Visit Render:** https://render.com
2. **Sign up/Login** with GitHub
3. **Click "New +"** → **"Web Service"**
4. **Connect your GitHub repository**
5. **Choose your ChatDocs AI repository**

### Step 3: Configure Service Settings

**Basic Settings:**
- **Name:** `docchat-ai`
- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`

**Advanced Settings:**
- **Auto-Deploy:** `Yes` (deploys on git push)
- **Health Check Path:** `/health`

### Step 4: Configure Environment Variables

In Render dashboard, add these environment variables:

```env
GOOGLE_API_KEY=your_actual_api_key_here
MODEL_NAME=gemini-2.5-pro
TEMPERATURE=0.7
MAX_TOKENS=100000
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEBUG=False
PYTHON_VERSION=3.11.9
```

### Step 5: Deploy!

Render will automatically:
- ✅ Install Python 3.11
- ✅ Install dependencies
- ✅ Deploy your application
- ✅ Provide HTTPS and custom domain support

**Your app will be live at:** `https://your-app-name.onrender.com`

---

## 📁 Required Files for Both Platforms

Make sure these files are in your repository:

### `requirements.txt` (Updated for Cloud Deployment)
```txt
# Core dependencies
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
jinja2>=3.1.0
python-multipart>=0.0.6
python-dotenv>=1.0.0

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

# Additional for cloud deployment
gunicorn>=21.2.0
```

### `render.yaml` (Optional - for Render)
```yaml
services:
  - type: web
    name: docchat-ai
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.9
      - key: GOOGLE_API_KEY
        sync: false
      - key: DEBUG
        value: False
```

### `railway.toml` (Optional - for Railway)
```toml
[build]
builder = "nixpacks"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1"
healthcheckPath = "/health"
healthcheckTimeout = 60
restartPolicyType = "ON_FAILURE"

[env]
PYTHONPATH = "/app"
PYTHON_VERSION = "3.11"
```

---

## 🔧 Production Optimizations for Cloud

### Update `app.py` for Production

Add this at the top of your `app.py`:

```python
import os

# Production settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", 8000))

# Update FastAPI app
app = FastAPI(
    title="DOCChat",
    description="Chat with your documents",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# Add startup event for cloud deployment
@app.on_event("startup")
async def startup_event():
    # Ensure directories exist
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("vector_store", exist_ok=True)
```

### Add Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    """Health check for cloud platforms"""
    try:
        # Test database connection
        db_stats = db.get_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "total_chats": db_stats.get("total_chats", 0),
            "version": os.getenv("APP_VERSION", "1.0.0")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

---

## 🚀 Deployment Commands

### For Railway:
```bash
# Push to GitHub (auto-deploys)
git add .
git commit -m "Deploy to Railway"
git push origin main

# Railway CLI (optional)
npm install -g @railway/cli
railway login
railway link
railway deploy
```

### For Render:
```bash
# Push to GitHub (auto-deploys)
git add .
git commit -m "Deploy to Render" 
git push origin main

# Render CLI (optional)
npm install -g @render/cli
render auth login
render services deploy
```

---

## 🔍 Platform Comparison

| Feature | Railway | Render |
|---------|---------|---------|
| **Free Tier** | $5 credit/month | 750 hours/month |
| **Auto-deploy** | ✅ GitHub integration | ✅ GitHub integration |
| **Custom Domains** | ✅ Free | ✅ Free |
| **SSL/HTTPS** | ✅ Automatic | ✅ Automatic |
| **Scaling** | Automatic | Manual/Automatic |
| **Database** | PostgreSQL add-on | PostgreSQL service |
| **Logs** | Real-time | Real-time |
| **Build Time** | Fast | Fast |

---

## 🎯 Recommended Setup

### For **Railway** (Recommended for beginners):
1. Simple setup with `railway.toml`
2. GitHub auto-deploy
3. Built-in metrics and logs
4. Easy environment variable management

### For **Render** (Recommended for production):
1. More detailed configuration options
2. Better performance monitoring
3. Multiple environment support
4. Advanced networking features

---

## 📞 Troubleshooting

### Common Issues:

1. **Build Fails:**
   - Check `requirements.txt` format
   - Ensure Python version compatibility
   - Check build logs in platform dashboard

2. **App Crashes:**
   - Check environment variables are set
   - Review application logs
   - Verify Google API key is valid

3. **File Upload Issues:**
   - Cloud platforms may have file size limits
   - Consider using cloud storage (AWS S3, etc.)

4. **Database Issues:**
   - SQLite works for testing
   - Use PostgreSQL for production
   - Check database connection in logs

### Quick Fixes:
```bash
# Test locally first
uvicorn app:app --host 0.0.0.0 --port 8000

# Check logs
railway logs  # for Railway
# or check Render dashboard for logs

# Redeploy
git commit --allow-empty -m "Redeploy"
git push origin main
```

---

## 🎉 Next Steps After Deployment

1. ✅ **Test your deployment** - Upload a document and chat
2. ✅ **Set up custom domain** (optional)
3. ✅ **Monitor performance** using platform dashboards  
4. ✅ **Set up database backups**
5. ✅ **Configure alerts** for downtime

**Your ChatDocs AI will be live and accessible worldwide! 🌍**

---

**Need help with specific deployment issues? Let me know!**
