# 🚂 Railway Deployment Guide (Docker)

Deploy your event monitor webhook server to Railway using Docker.

---

## 🎯 Quick Deploy (3 Steps)

### **Step 1: Push to GitHub**

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Event-based status monitor"

# Push to GitHub
git remote add origin https://github.com/yourusername/openai-monitor.git
git branch -M main
git push -u origin main
```

### **Step 2: Deploy on Railway**

1. Go to: **https://railway.app**
2. Click **"Start a New Project"**
3. Choose **"Deploy from GitHub repo"**
4. Select your repository
5. Railway auto-detects Dockerfile and deploys! ✅

### **Step 3: Get Your URL**

Railway provides a URL like:
```
https://openai-monitor-production.up.railway.app
```

Your webhook endpoint:
```
https://openai-monitor-production.up.railway.app/webhook/statuspage
```

**Done! Your webhook server is live! 🎉**

---

## 📋 Detailed Railway Deployment

### **Option A: Deploy via GitHub (Recommended)**

**1. Connect GitHub:**
```bash
# Make sure code is on GitHub
git push origin main
```

**2. Railway Dashboard:**
- Go to https://railway.app
- Click "New Project"
- Select "Deploy from GitHub repo"
- Authorize GitHub access
- Select your repository
- Select branch: `main`

**3. Railway Auto-Config:**
Railway automatically detects:
- ✅ Dockerfile (uses Docker build)
- ✅ Port exposure (5000)
- ✅ Health check endpoint

**4. Environment Variables (Optional):**
```
No environment variables needed - works out of box!
```

**5. Deploy:**
- Railway builds Docker image
- Deploys container
- Provides public URL

---

### **Option B: Deploy via Railway CLI**

**Install Railway CLI:**
```bash
# macOS
brew install railway

# Or via npm
npm install -g @railway/cli

# Login
railway login
```

**Deploy:**
```bash
# Initialize Railway project
railway init

# Link to project
railway link

# Deploy
railway up

# View logs
railway logs

# Open in browser
railway open
```

---

## 🐳 Docker Configuration Explained

### **Dockerfile**

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY event_monitor.py ./

# Run as non-root user (security)
RUN useradd -m -u 1000 monitor && \
    chown -R monitor:monitor /app
USER monitor

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Start server (Railway sets $PORT)
CMD python event_monitor.py --port ${PORT:-5000} --host 0.0.0.0
```

**Key points:**
- Uses Python 3.11 slim image (smaller size)
- Non-root user for security
- Health check endpoint
- Respects Railway's `$PORT` environment variable

---

## 🧪 Test Locally with Docker

### **Build & Run:**

```bash
# Build Docker image
docker build -t event-monitor .

# Run container
docker run -p 5000:5000 event-monitor

# Or use docker-compose
docker-compose up
```

### **Test Endpoints:**

```bash
# Health check
curl http://localhost:5000/health

# Test webhook
curl -X POST http://localhost:5000/test

# View logs
docker logs -f event-monitor
```

### **Stop:**
```bash
docker-compose down
```

---

## 🌐 Railway Features

### **Automatic Features:**
- ✅ **HTTPS** - Automatic SSL certificates
- ✅ **Custom domains** - Add your own domain
- ✅ **Auto-deploy** - Push to GitHub = auto deploy
- ✅ **Logs** - Real-time log streaming
- ✅ **Metrics** - CPU/Memory monitoring
- ✅ **Scaling** - Vertical scaling available

### **Free Tier:**
- $5 credit per month (covers small apps)
- Automatic sleep after inactivity (wakes on request)
- Perfect for webhooks

---

## 📊 After Deployment

### **Get Your URLs:**

Railway dashboard shows:
- **Public URL**: `https://your-app.up.railway.app`
- **Webhook endpoint**: `https://your-app.up.railway.app/webhook/statuspage`
- **Health check**: `https://your-app.up.railway.app/health`

### **Test Deployed App:**

```bash
# Health check
curl https://your-app.up.railway.app/health

# Expected response:
{
  "status": "running",
  "mode": "event-based (webhooks)",
  "incidents_tracked": 0,
  "timestamp": "2026-02-20T..."
}
```

### **Test Webhook:**

```bash
curl -X POST https://your-app.up.railway.app/webhook/statuspage \
  -H "Content-Type: application/json" \
  -d '{
    "incident": {
      "id": "test123",
      "name": "Chat API Issue",
      "status": "investigating",
      "updated_at": "2025-11-03T14:32:00Z",
      "components": [{"name": "Chat Completions"}],
      "incident_updates": [{
        "body": "Degraded performance due to upstream issue"
      }]
    },
    "page": {"name": "OpenAI API"}
  }'
```

### **View Logs:**

In Railway dashboard:
- Go to your project
- Click "Logs" tab
- See real-time output:
```
[2025-11-03 14:32:00] Product: OpenAI API - Chat Completions
Status: Degraded performance due to upstream issue
```

---

## 🔧 Railway Configuration

### **railway.toml** (Optional Custom Config)

Create `railway.toml` for advanced configuration:

```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "python event_monitor.py --port $PORT --host 0.0.0.0"
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 3

[healthcheck]
path = "/health"
interval = 30
timeout = 5
```

---

## 🚀 Alternative: Render.com (Also Supports Docker)

If you prefer Render:

**1. Push to GitHub**

**2. Render Dashboard:**
- Go to https://render.com
- "New" → "Web Service"
- Connect GitHub repo
- Environment: Docker
- Plan: Free

**3. Settings:**
```
Environment: Docker
Port: 5000
Health Check Path: /health
```

**4. Deploy!**

---

## 📦 Docker vs Buildpack Deployment

| Method | Pros | Cons |
|--------|------|------|
| **Docker** | Full control, reproducible builds, works everywhere | Slightly slower builds |
| **Buildpack** | Faster, automatic detection | Less control |

**Both work on Railway!** Railway auto-detects Dockerfile.

---

## ✅ Deployment Checklist

```bash
# 1. Update Docker files
✅ Dockerfile updated for event_monitor.py
✅ docker-compose.yml updated

# 2. Test locally
✅ docker build -t event-monitor .
✅ docker run -p 5000:5000 event-monitor
✅ curl http://localhost:5000/health

# 3. Push to GitHub
✅ git add .
✅ git commit -m "Production ready"
✅ git push origin main

# 4. Deploy on Railway
✅ Go to railway.app
✅ Deploy from GitHub
✅ Wait for build (~2 minutes)

# 5. Test production
✅ curl https://your-app.up.railway.app/health
✅ Test webhook with Postman
✅ Check logs in Railway dashboard

# 6. Submit
✅ Send webhook URL to assignment email
✅ Include health check URL
```

---

## 🎯 For Submission

**Email Content:**

```
Deployed Webhook Server:

Production URL: https://openai-monitor.up.railway.app
Webhook Endpoint: https://openai-monitor.up.railway.app/webhook/statuspage
Health Check: https://openai-monitor.up.railway.app/health

Technology Stack:
- Python 3.11
- Flask (webhook server)
- Docker (containerization)
- Railway (hosting)

Architecture:
- Event-based webhooks (zero polling)
- Scales to 100+ providers
- Docker containerized for portability

Testing:
See POSTMAN_TESTING.md for test instructions
Health check returns live status

The webhook server is production-ready and awaiting
StatuspageIO webhook configuration.
```

---

## 🔍 Troubleshooting

**Problem: Build fails**
```bash
# Check Dockerfile syntax
docker build -t event-monitor .

# Check logs in Railway dashboard
```

**Problem: App crashes**
```bash
# Check Railway logs
# Ensure Flask is in requirements.txt
# Verify event_monitor.py exists
```

**Problem: Can't access URL**
```bash
# Check Railway dashboard - is service running?
# Verify health check endpoint works
curl https://your-app.up.railway.app/health
```

---

## 🎉 Success!

Your webhook server is now:
- ✅ Containerized with Docker
- ✅ Deployed on Railway
- ✅ Publicly accessible
- ✅ Auto-scales and auto-restarts
- ✅ Production-ready

**Webhook URL for OpenAI:**
```
https://your-app.up.railway.app/webhook/statuspage
```

Share this URL in your assignment submission! 🚀
