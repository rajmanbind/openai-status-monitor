# 🚀 Quick Deployment Guide for event_monitor.py

## Main Entry File
**`event_monitor.py`** - This is your production webhook server

## Local Testing

```bash
# Activate virtual environment
source venv/bin/activate

# Start server
python event_monitor.py --port 5000

# Test it works
curl -X POST http://localhost:5000/test

# Check health
curl http://localhost:5000/health
```

---

## ☁️ Cloud Deployment (Choose One)

### Option 1: Render.com (Recommended - FREE)

**Steps:**
1. Push code to GitHub
2. Go to [render.com](https://render.com) and sign up
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Name:** openai-status-monitor
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python event_monitor.py --port $PORT --host 0.0.0.0`
   - **Plan:** Free

**Your webhook URL will be:** `https://openai-status-monitor.onrender.com/webhook/statuspage`

---

### Option 2: Railway.app (Very Easy - FREE)

**Steps:**
1. Push code to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Railway auto-detects Python and deploys

**Your webhook URL will be:** `https://your-app.railway.app/webhook/statuspage`

---

### Option 3: Heroku (Popular)

**Prerequisites:**
- Install [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- Files already created: `Procfile`, `runtime.txt`, `requirements.txt`

**Deploy:**
```bash
# Login
heroku login

# Create app
heroku create openai-status-monitor

# Deploy
git init
git add .
git commit -m "Deploy event monitor"
git push heroku main

# View logs
heroku logs --tail

# Open app
heroku open
```

**Your webhook URL:** `https://openai-status-monitor.herokuapp.com/webhook/statuspage`

---

### Option 4: AWS EC2 (Full Control)

**Steps:**
1. Launch Ubuntu EC2 instance
2. SSH into server:
```bash
ssh ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv -y

# Clone and setup
git clone your-repo
cd monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/event-monitor.service
```

**Service file:**
```ini
[Unit]
Description=Event-Based Status Monitor
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/monitor
ExecStart=/home/ubuntu/monitor/venv/bin/python event_monitor.py --port 5000 --host 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable:**
```bash
sudo systemctl enable event-monitor
sudo systemctl start event-monitor
sudo systemctl status event-monitor
```

**Your webhook URL:** `http://your-ec2-ip:5000/webhook/statuspage`

---

### Option 5: DigitalOcean App Platform

**Steps:**
1. Push to GitHub
2. Go to DigitalOcean → "Create" → "Apps"
3. Connect GitHub repository
4. Configure:
   - **Run Command:** `python event_monitor.py --port 8080 --host 0.0.0.0`
   - **Port:** 8080

**Your webhook URL:** `https://your-app.ondigitalocean.app/webhook/statuspage`

---

## 🔗 Configure OpenAI Webhook

After deployment, configure OpenAI to send webhooks:

1. Go to: https://manage.statuspage.io/pages/[your-page-id]/webhooks
2. Click "Create Webhook"
3. Enter webhook URL: `https://your-deployed-app.com/webhook/statuspage`
4. Select events:
   - ✅ Incident created
   - ✅ Incident updated
   - ✅ Incident resolved
5. Save

---

## ✅ Verify Deployment

```bash
# Check health
curl https://your-app.com/health

# Expected response:
{
  "status": "running",
  "mode": "event-based (webhooks)",
  "incidents_tracked": 0,
  "timestamp": "2026-02-20T..."
}

# Test webhook
curl -X POST https://your-app.com/test

# Expected output on server logs:
[2026-02-20 14:32:00] Product: OpenAI API - Test Service
Status: This is a test webhook to verify the system is working
```

---

## 📊 Monitor Your Deployment

**View incidents received:**
```bash
curl https://your-app.com/incidents
```

**Check logs:**
- Render: Dashboard → Logs tab
- Railway: Deployment → Logs
- Heroku: `heroku logs --tail`
- AWS: `sudo journalctl -u event-monitor -f`

---

## 🎯 For Submission

**Hosted Version URL:**
```
Webhook Endpoint: https://your-app.com/webhook/statuspage
Health Check: https://your-app.com/health
```

**Include in email to be+submissions@bolna.ai:**
- ZIP file with code
- Link to hosted webhook endpoint
- Link to health check endpoint
