# MegaArtsStore Deployment Guide

Complete guide for deploying MegaArtsStore to production.

---

## 🏠 Local Setup (Development)

### Update `.env` for Blender 5.0.1

Create a `.env` file (copy from `.env.example`):

```ini
# Blender Configuration
BLENDER_ENABLED=true
BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 5.0\blender.exe
```

> **Note**: Adjust the path based on your Blender 5.0.1 installation location.

### Find Your Blender Path

Run in PowerShell:

```powershell
Get-Command blender | Select-Object -ExpandProperty Source
```

Or check common locations:

- `C:\Program Files\Blender Foundation\Blender 5.0\blender.exe`
- `C:\Program Files\Blender Foundation\Blender\blender.exe`

---

## ☁️ Production Deployment Options

For production, you have **3 main options** for handling 3D model processing:

---

## Option 1: Cloud-Based (Recommended) ⭐

**Best for**: Scalability, no server maintenance

### Use a Serverless 3D Processing Service

Instead of running Blender on your server, use cloud services:

#### **A. AWS Lambda + Blender Layer**

- Deploy Blender as a Lambda Layer
- Trigger processing via S3 uploads
- Auto-scales based on demand

**Setup**:

1. Create Lambda layer with Blender binary
2. Upload models to S3
3. Lambda processes and returns results
4. Update your backend to use Lambda API

#### **B. Google Cloud Run + Blender Container**

- Package Blender in Docker container
- Deploy to Cloud Run
- Pay only for processing time

**Dockerfile example**:

```dockerfile
FROM ubuntu:22.04

# Install Blender
RUN apt-get update && apt-get install -y \
    blender \
    python3 \
    python3-pip

# Copy your scripts
COPY app/services/blender_scripts /scripts

# Your FastAPI app
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### **C. Third-Party 3D Processing APIs**

Use existing services (no Blender setup needed):

- **Sketchfab API** - Model optimization and hosting
- **Poly.pizza** - 3D model conversion
- **Clara.io API** - Cloud-based 3D processing

**Update your code**:

```python
# Instead of local Blender, call external API
async def optimize_model_cloud(model_url: str):
    response = await httpx.post(
        "https://api.3dprocessing.com/optimize",
        json={"model_url": model_url}
    )
    return response.json()["optimized_url"]
```

---

## Option 2: VPS with Blender (Medium Complexity)

**Best for**: Full control, moderate traffic

### Recommended Providers

- **DigitalOcean** - $12/month (2GB RAM, 1 vCPU)
- **Linode** - $10/month (2GB RAM, 1 vCPU)
- **AWS EC2** - t3.small ($15/month)

### Setup Steps

#### 1. Choose Ubuntu 22.04 LTS Server

#### 2. Install Blender on Server

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Blender
sudo apt install -y blender

# Verify installation
blender --version
# Should show: Blender 3.6.x or newer
```

#### 3. Update Environment Variables

```bash
# On server, create .env
BLENDER_ENABLED=true
BLENDER_PATH=/usr/bin/blender
```

#### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 5. Run with Systemd (Auto-restart)

Create `/etc/systemd/system/megaartsstore.service`:

```ini
[Unit]
Description=MegaArtsStore Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/megaartsstore
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable megaartsstore
sudo systemctl start megaartsstore
sudo systemctl status megaartsstore
```

---

## Option 3: Disable 3D Processing (Simplest)

**Best for**: MVP, testing, or if you pre-process models offline

### Configuration

```ini
# .env
BLENDER_ENABLED=false
```

### Workflow

1. Process models locally on your Windows machine
2. Upload optimized `.glb` files directly via API
3. Skip the processing pipeline entirely

**Upload pre-processed model**:

```bash
curl -X POST "https://api.megaartsstore.com/render/upload-model" \
  -H "Authorization: Bearer TOKEN" \
  -F "product_id=PRODUCT_ID" \
  -F "file=@optimized_model.glb"
```

---

## 🚀 Recommended Deployment Stack

### For Small to Medium Scale

```
┌─────────────────────────────────────┐
│  Frontend (Vercel/Netlify)          │
│  - React/Next.js                    │
│  - AR viewer (model-viewer)         │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Backend API (Railway/Render)       │
│  - FastAPI                          │
│  - No Blender (use Option 1 or 3)  │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Database (MongoDB Atlas)           │
│  - Free tier: 512MB                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Storage (Cloudinary)               │
│  - Images & 3D models               │
│  - Free tier: 25GB                  │
└─────────────────────────────────────┘
```

### Deployment Platforms (No Blender Needed)

#### **Railway** (Easiest)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

#### **Render**

1. Connect GitHub repo
2. Set environment variables
3. Deploy automatically on push

#### **Heroku**

```bash
# Install Heroku CLI
heroku create megaartsstore-api
git push heroku main
```

---

## 🔧 Environment Variables for Production

Create these in your deployment platform:

```ini
# Required
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
JWT_SECRET_KEY=your-production-secret-key-min-32-chars
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret

# Optional (Payments)
RAZORPAY_KEY_ID=rzp_live_xxxx
RAZORPAY_KEY_SECRET=your-secret

# Optional (Email)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Blender (if using Option 2)
BLENDER_ENABLED=true
BLENDER_PATH=/usr/bin/blender

# Production settings
DEBUG=false
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 📊 Performance Considerations

### If Using Blender in Production

**Resource Requirements**:

- **Minimum**: 2GB RAM, 1 vCPU
- **Recommended**: 4GB RAM, 2 vCPU
- **Heavy processing**: 8GB RAM, 4 vCPU

**Optimization Tips**:

1. **Queue Processing**: Use task queue to prevent blocking
2. **Rate Limiting**: Limit concurrent Blender processes
3. **Caching**: Cache processed models
4. **CDN**: Serve models from Cloudinary CDN

### Without Blender (Recommended)

**Benefits**:

- Lower server costs ($5-10/month vs $15-50/month)
- Faster deployment
- Better scalability
- No processing bottlenecks

**Trade-offs**:

- Manual model optimization
- Or use cloud processing service

---

## 🔐 Security Checklist

- [ ] Change `JWT_SECRET_KEY` to strong random string
- [ ] Set `DEBUG=false` in production
- [ ] Use HTTPS only (SSL certificate)
- [ ] Restrict CORS origins to your domain
- [ ] Enable rate limiting
- [ ] Use environment variables (never commit `.env`)
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

---

## 📈 Monitoring & Logging

### Recommended Tools

**Application Monitoring**:

- **Sentry** - Error tracking (free tier)
- **New Relic** - Performance monitoring
- **Datadog** - Full observability

**Logging**:

```python
# Already configured in app/utils/logger.py
import logging
logger = logging.getLogger(__name__)

logger.info("Processing model")
logger.error("Failed to process", exc_info=True)
```

**Health Checks**:

```bash
# Add to your monitoring
curl https://api.megaartsstore.com/
# Should return: {"status": "ok"}
```

---

## 🎯 My Recommendation

For your use case, I recommend:

### **Phase 1: MVP (Now)**

- Deploy to **Railway** or **Render** (free tier)
- **Disable Blender** (`BLENDER_ENABLED=false`)
- Pre-process models locally
- Upload optimized `.glb` files directly

### **Phase 2: Growth (Later)**

- Move to **DigitalOcean/Linode VPS** ($12/month)
- Install Blender on server
- Enable automated processing

### **Phase 3: Scale (Future)**

- Use **AWS Lambda + Blender Layer**
- Or switch to **Sketchfab API**
- Separate processing service from main API

---

## 🚀 Quick Deploy Commands

### Deploy to Railway (5 minutes)

```bash
# Install CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway add
railway up

# Set environment variables in Railway dashboard
```

### Deploy to Render (via Dashboard)

1. Go to [render.com](https://render.com)
2. Connect GitHub repo
3. Create new Web Service
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy!

---

## 📞 Need Help?

- Check logs: `railway logs` or Render dashboard
- Test locally first: `uvicorn main:app --reload`
- Verify environment variables are set
- Check MongoDB connection string
- Ensure Cloudinary credentials are correct

---

## ✅ Post-Deployment Checklist

- [ ] API is accessible via HTTPS
- [ ] Database connection works
- [ ] File uploads work (Cloudinary)
- [ ] Authentication works (JWT)
- [ ] Payments work (Razorpay test mode)
- [ ] Email notifications work
- [ ] Rate limiting is active
- [ ] CORS is properly configured
- [ ] Health check endpoint responds
- [ ] Logs are being collected
