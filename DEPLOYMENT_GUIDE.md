# 🚀 EIR Project - Deployment Guide

## Quick Deployment Options

### 1. 🚄 Railway (Recommended - Free Tier)

#### Step 1: Prepare Repository
```bash
# Ensure your changes are committed
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

#### Step 2: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Click "Deploy from GitHub repo"
4. Select your `eir-project` repository
5. Railway will automatically detect and deploy!

#### Step 3: Add Database
1. In Railway dashboard, click "Add Plugin"
2. Select "PostgreSQL"
3. Database will be automatically connected

#### Step 4: Set Environment Variables
```bash
SECRET_KEY=your-secure-secret-key
DEBUG=false
PORT=8000
```

**Your app will be live at**: `https://your-app-name.up.railway.app`

### 2. 🌊 Render

#### Step 1: Setup
1. Go to [render.com](https://render.com)
2. Connect your GitHub account
3. Select "New Web Service"
4. Choose your `eir-project` repository

#### Step 2: Configuration
- **Root Directory**: `./` (repository root)
- **Build Command**: `docker build -f backend/Dockerfile.prod -t eir-app .`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment**: Docker
- **Docker Context**: `.` (root directory)
- **Dockerfile Path**: `backend/Dockerfile.prod`

#### Step 3: Add PostgreSQL
1. Create "New PostgreSQL"
2. Copy the database URL to your web service environment

**Your app will be live at**: `https://your-app-name.onrender.com`

### 3. 🌊 DigitalOcean App Platform

#### Step 1: Create App
```bash
# Install doctl CLI
# Go to DigitalOcean Apps
# Connect GitHub repository
```

#### Step 2: Configuration
```yaml
name: eir-project
services:
- name: web
  source_dir: /
  github:
    repo: Mohamedsalem00/eir-project
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
  environment_slug: docker
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
databases:
- name: eir-db
  engine: PG
  version: "15"
```

**Cost**: ~$5/month

## 🔧 Local Testing Before Deployment

### Test Production Build
```bash
# Build production image
docker build -f backend/Dockerfile.prod -t eir-prod .

# Run production container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e SECRET_KEY="your-secret-key" \
  eir-prod
```

### Test with Production Docker Compose
```bash
# Copy environment template
cp .env.production.template .env.production

# Edit .env.production with your values
nano .env.production

# Run production stack
docker-compose -f docker-compose.prod.yml up
```

## 🌐 Domain Configuration

### Free Domains
- **Railway**: `your-app.up.railway.app`
- **Render**: `your-app.onrender.com`
- **Netlify**: `your-app.netlify.app`

### Custom Domain
1. Purchase domain from Namecheap/GoDaddy
2. Add CNAME record: `www -> your-app.platform.com`
3. Add A record: `@ -> platform-ip`

## 🔒 Security Checklist

### Before Going Live:
- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG=false`
- [ ] Configure proper CORS origins
- [ ] Use strong database passwords
- [ ] Enable HTTPS (automatic on most platforms)
- [ ] Set up monitoring/logging

### Environment Variables for Production:
```bash
# Required
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
DEBUG=false
PORT=8000

# Optional
CORS_ORIGINS=https://yourdomain.com
JWT_SECRET_KEY=your-jwt-secret
LOG_LEVEL=INFO
```

## 📊 Monitoring & Maintenance

### Health Checks
- **Endpoint**: `/verification-etat`
- **Expected**: 200 OK with system status

### API Documentation
- **Swagger UI**: `https://your-domain.com/docs`
- **ReDoc**: `https://your-domain.com/redoc`

### Database Management
```bash
# Access production database (Railway)
railway connect postgres

# Backup database
pg_dump $DATABASE_URL > backup.sql

# Restore database
psql $DATABASE_URL < backup.sql
```

## 🚀 Quick Start Commands

### Deploy to Railway (Fastest)
```bash
npm install -g @railway/cli
railway login
railway link
railway up
```

### Deploy to Render
1. Fork repository
2. Connect to Render
3. Auto-deploy enabled!

**Your EIR API will be publicly accessible and ready for testing!**

## 📱 Testing Your Deployed API

Once deployed, you can test your API at:
- **API Docs**: `https://your-domain.com/docs`
- **Health Check**: `https://your-domain.com/verification-etat`
- **Public Stats**: `https://your-domain.com/public/statistiques`
- **IMEI Check**: `https://your-domain.com/imei/123456789012345`

## 🎯 Next Steps After Deployment

1. **Test all endpoints** using the Swagger UI
2. **Share the API documentation** link
3. **Monitor usage** and performance
4. **Set up custom domain** if needed
5. **Configure backups** for production data

Your EIR project is now ready for public deployment! 🚀

## 🔧 Troubleshooting Common Issues

### Docker Build Context Issues
**Problem**: "COPY failed: no such file or directory"
**Solution**: Ensure Docker Build Context Directory is set to `.` (root)

**Correct Settings for Deployment Platforms:**
```bash
Root Directory: ./
Dockerfile Path: backend/Dockerfile.prod
Docker Build Context: .
Build Command: docker build -f backend/Dockerfile.prod -t eir-app .
```

### Environment Variables Issues
**Problem**: Database connection errors
**Solution**: Set these required environment variables:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-min-32-chars
DEBUG=false
PORT=8000
```

### Port Issues
**Problem**: App not accessible after deployment
**Solution**: Ensure your app binds to `0.0.0.0:$PORT`, not `localhost`

### Build Failures
**Problem**: Docker build fails
**Solution**: 
1. Check Dockerfile path: `backend/Dockerfile.prod`
2. Verify build context is root directory (`.`)
3. Ensure all files are committed to git
