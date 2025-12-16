# Railway Deployment Guide

Complete guide to deploying your GIS Satellite Analysis application on Railway.

## Prerequisites

1. GitHub account with this repository pushed
2. Railway account (sign up at https://railway.app)
3. Anthropic API key (get from https://console.anthropic.com/)

## Deployment Steps

### Step 1: Set Up Railway Project

1. **Create Railway Account**
   - Go to https://railway.app
   - Click "Login" and sign in with GitHub
   - Authorize Railway to access your repositories

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `newGitTest` repository
   - Railway will detect your project

### Step 2: Deploy Backend Service

1. **Add Backend Service**
   - In your Railway project, click "New Service"
   - Select "GitHub Repo" → Choose your repository
   - Railway will detect the Dockerfile in `backend/`

2. **Configure Backend Service**
   - Click on the backend service
   - Go to "Settings" → "General"
   - Set **Root Directory**: `backend`
   - Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   - Go to "Variables" tab
   - Add the following variables:
     ```
     ANTHROPIC_API_KEY=your_anthropic_api_key_here
     ```
   - Railway will automatically add `PORT` and `DATABASE_URL`

4. **Add PostgreSQL Database**
   - Click "+ New" in your project
   - Select "Database" → "Add PostgreSQL"
   - Railway will automatically:
     - Create a PostgreSQL instance
     - Set the `DATABASE_URL` variable in your backend service

5. **Deploy**
   - Backend will automatically build and deploy
   - Wait for deployment to complete (5-10 minutes first time)
   - Copy the backend URL (e.g., `https://your-app.railway.app`)

### Step 3: Deploy Frontend Service

1. **Add Frontend Service**
   - Click "+ New" → "GitHub Repo"
   - Select your repository again
   - This creates a second service

2. **Configure Frontend Service**
   - Click on the frontend service
   - Go to "Settings" → "General"
   - Set **Root Directory**: `frontend`
   - Set **Build Command**: `npm install && npm run build`
   - Set **Start Command**: `npx serve -s build -l $PORT`

3. **Set Environment Variables**
   - Go to "Variables" tab
   - Add:
     ```
     REACT_APP_API_URL=https://your-backend-url.railway.app
     ```
   - Replace with your actual backend URL from Step 2

4. **Install Serve Package**
   - We need to add `serve` to frontend dependencies
   - This is already handled if you use the updated `package.json`

5. **Generate Domain**
   - Go to "Settings" → "Networking"
   - Click "Generate Domain"
   - Your frontend will be accessible at `https://your-frontend.railway.app`

### Step 4: Configure CORS

The backend needs to allow requests from your frontend domain.

1. **Update Backend CORS**
   - The app is already configured to allow all origins for demo
   - For production, you should restrict this:
   - Go to backend service → "Variables"
   - Add: `ALLOWED_ORIGINS=https://your-frontend.railway.app`
   - Update `backend/app/main.py` to use this variable

### Step 5: Test Your Deployment

1. **Visit Your Frontend**
   - Go to `https://your-frontend.railway.app`
   - You should see the GIS Analysis interface

2. **Test Upload**
   - Try uploading a sample GeoTIFF image
   - Check backend logs if there are issues

3. **Test Query**
   - Select an image
   - Enter query: "number of cars"
   - Verify AI response

## Project Structure in Railway

Your Railway project should have 3 services:

```
┌─────────────────────────────────────┐
│ Railway Project: GIS Analysis      │
├─────────────────────────────────────┤
│                                     │
│  🐳 Backend (FastAPI)              │
│     URL: backend-xxx.railway.app   │
│     Env: ANTHROPIC_API_KEY         │
│          DATABASE_URL (auto)       │
│                                     │
│  📦 PostgreSQL Database            │
│     Auto-linked to backend         │
│                                     │
│  ⚛️  Frontend (React)              │
│     URL: frontend-xxx.railway.app  │
│     Env: REACT_APP_API_URL         │
│                                     │
└─────────────────────────────────────┘
```

## Environment Variables Reference

### Backend Service
| Variable | Value | Notes |
|----------|-------|-------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Get from Anthropic console |
| `DATABASE_URL` | Auto-set | Railway provides this |
| `PORT` | Auto-set | Railway provides this |

### Frontend Service
| Variable | Value | Notes |
|----------|-------|-------|
| `REACT_APP_API_URL` | `https://backend-xxx.railway.app` | Your backend URL |
| `PORT` | Auto-set | Railway provides this |

## Monitoring & Logs

### View Logs
1. Click on any service
2. Go to "Deployments" tab
3. Click "View Logs"
4. Monitor real-time application logs

### View Metrics
1. Click on service
2. Go to "Metrics" tab
3. View CPU, memory, network usage

## Cost Estimation

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month includes:
  - $5 usage credit
  - Shared CPU
  - 512MB RAM per service
  - 1GB disk per service

**Estimated costs for this app**:
- Backend: ~$2-3/month (with low traffic)
- Frontend: ~$1-2/month
- PostgreSQL: ~$1-2/month
- **Total**: ~$4-7/month (within $5 credit for low usage)

## Troubleshooting

### Build Failures

**Problem**: Backend build fails with GDAL errors
**Solution**: The Dockerfile uses official GDAL image, should work automatically

**Problem**: Frontend build fails
**Solution**: Check `package.json` has all dependencies

### Runtime Issues

**Problem**: Backend crashes with database errors
**Solution**:
- Verify `DATABASE_URL` is set
- Check PostgreSQL service is running
- View logs for specific error

**Problem**: Frontend can't reach backend
**Solution**:
- Verify `REACT_APP_API_URL` is correct
- Check backend is deployed and running
- Test backend URL directly: `https://backend-url.railway.app/`

**Problem**: CORS errors
**Solution**:
- Update CORS origins in `backend/app/main.py`
- Add frontend URL to allowed origins

### Database Issues

**Problem**: Tables not created
**Solution**: Database tables are auto-created on first backend startup via `init_db()`

**Problem**: Need to reset database
**Solution**:
- In Railway, delete PostgreSQL service
- Create new PostgreSQL service
- Backend will auto-create tables on restart

## Updating Your Deployment

Railway auto-deploys when you push to GitHub:

1. **Make changes locally**
   ```bash
   git add .
   git commit -m "Update feature"
   git push
   ```

2. **Railway automatically**:
   - Detects the push
   - Rebuilds affected services
   - Deploys new version
   - Zero-downtime rollout

## Storage Considerations

### Uploaded Images

**Current**: Stored in `backend/uploads/` (ephemeral on Railway)

**Problem**: Railway restarts lose uploaded files

**Solutions**:

1. **Railway Volumes** (Simplest):
   ```bash
   # In Railway dashboard:
   # Settings → Volumes → Add Volume
   # Mount path: /app/uploads
   ```

2. **Cloud Storage** (Production):
   - Use AWS S3, Google Cloud Storage, or Cloudinary
   - Update `backend/app/main.py` upload handler
   - Store file references in database, files in cloud

### YOLO Models

Models auto-download on first run (~6MB). They persist in the container.

## Security Recommendations

For production deployment:

1. **Restrict CORS**:
   ```python
   # backend/app/main.py
   origins = [
       "https://your-frontend.railway.app",
   ]
   ```

2. **Add Rate Limiting**:
   ```bash
   pip install slowapi
   ```

3. **Add Authentication**:
   - Implement user auth
   - Protect API endpoints
   - Add API keys for programmatic access

4. **Environment Variables**:
   - Never commit `.env` files
   - Use Railway's variable management

## Scaling Considerations

When you need to scale:

1. **Upgrade Railway Plan**:
   - Pro plan: More resources, better performance
   - Custom domains, teams, etc.

2. **Optimize Docker Image**:
   - Use multi-stage builds
   - Reduce image size
   - Cache dependencies

3. **Add Caching**:
   - Redis for query results
   - CDN for static assets

4. **Database Optimization**:
   - Add indexes
   - Connection pooling
   - Read replicas

## Next Steps

After successful deployment:

1. ✅ Set up custom domain (Railway Settings → Domains)
2. ✅ Add monitoring (Railway Metrics or external like Sentry)
3. ✅ Implement cloud storage for images
4. ✅ Add user authentication
5. ✅ Set up CI/CD testing
6. ✅ Configure backups for PostgreSQL

## Support Resources

- **Railway Docs**: https://docs.railway.app/
- **Railway Discord**: https://discord.gg/railway
- **Railway Status**: https://status.railway.app/

## Cost-Free Alternative: Render

If you exceed Railway's free tier:

1. Deploy to Render.com (similar process)
2. Free tier includes:
   - 750 hours/month web services
   - Free PostgreSQL
   - Auto-deploys from GitHub

See `RENDER_DEPLOYMENT.md` for instructions.

---

**Questions?** Check the main README.md or open an issue on GitHub.
