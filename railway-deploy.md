# Railway Deployment Guide for ChatDocs AI

## 🚨 CRITICAL: Environment Variables Required

Before deploying to Railway, you **MUST** set the following environment variable:

```
GOOGLE_API_KEY=your_actual_google_api_key_here
```

## 🚀 Step-by-Step Deployment

### 1. Set Environment Variable in Railway
1. Go to your Railway project dashboard
2. Click on **"Variables"** tab
3. Add the following variable:
   - **Name**: `GOOGLE_API_KEY`
   - **Value**: Your actual Google API key (starts with `AIzaSy...`)

### 2. Optional Environment Variables
```
PORT=8000                    # Railway sets this automatically
MODEL_NAME=gemini-2.5-pro   # Default model
TEMPERATURE=0.7             # Response creativity
CHUNK_SIZE=1000             # Text chunk size
CHUNK_OVERLAP=200           # Chunk overlap
DEBUG=false                 # Production mode
```

### 3. Deployment Files
The following files are configured for Railway deployment:

- ✅ `railway.toml` - Railway configuration
- ✅ `Procfile` - Process definition
- ✅ `requirements.txt` - Python dependencies
- ✅ `Dockerfile` - Container configuration (backup)

### 4. Verify Health Check
After deployment, check:
```
https://your-app.up.railway.app/health
```

Should return:
```json
{
  "status": "healthy",
  "environment": {
    "google_api_key": true,
    "port": "8000"
  },
  "database": {
    "status": "healthy"
  }
}
```

## 🔧 Troubleshooting

### Issue: Healthcheck Failure
**Cause**: Missing `GOOGLE_API_KEY` environment variable
**Solution**: Add the API key in Railway Variables tab

### Issue: Build Failure
**Cause**: Dependencies installation timeout
**Solution**: The build timeout is increased to 600 seconds in `railway.toml`

### Issue: App Not Responding
**Cause**: Wrong port binding
**Solution**: Railway automatically sets `$PORT` - our app uses it correctly

### Issue: Database Errors
**Cause**: Missing directories
**Solution**: App automatically creates required directories on startup

## 📊 Monitoring

### Health Check Endpoint
- **URL**: `/health`
- **Method**: GET
- **Response**: System status and statistics

### Logs
View logs in Railway dashboard:
1. Go to your project
2. Click on **"Deployments"**
3. Click on the latest deployment
4. View **"Deploy Logs"** and **"App Logs"**

## 🔄 Redeployment

If you need to redeploy:
1. Make changes to your code
2. Commit and push to GitHub
3. Railway will automatically redeploy
4. Check the health endpoint after deployment

## 🆘 Emergency Reset

If deployment is completely broken:
1. Delete the Railway service
2. Create a new service
3. Connect to GitHub repository
4. Set `GOOGLE_API_KEY` environment variable
5. Deploy

## 📞 Support

If issues persist:
1. Check Railway logs for detailed error messages
2. Verify all environment variables are set
3. Test the health endpoint
4. Contact Railway support if needed

---

**Remember**: The `GOOGLE_API_KEY` is absolutely required for the application to function!
