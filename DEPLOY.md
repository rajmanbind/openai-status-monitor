# Deployment Guide (Render Focus)

This guide covers how to run and deploy the webhook server in [event_monitor.py](event_monitor.py).

## Local Run

```bash
pip install -r requirements.txt
python event_monitor.py --port 5000
```

Test locally:

```bash
curl -X POST http://localhost:5000/webhook/statuspage \
   -H "Content-Type: application/json" \
   -d '{"incident":{"id":"local_test","name":"Chat Completions API - Elevated Error Rates","status":"investigating","updated_at":"2025-11-03T14:32:00Z","components":[{"name":"Chat Completions"}],"incident_updates":[{"body":"Degraded performance due to upstream issue"}]},"page":{"name":"OpenAI API"}}'
curl http://localhost:5000/health
```

## Docker (Optional)

Build and run the container:

```bash
docker build -t event-monitor .
docker run -p 5000:5000 event-monitor
```

## Render Deployment (Recommended)

1. Push the repo to GitHub.
2. Go to https://render.com and create a new Web Service.
3. Connect your GitHub repository.
4. Set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python event_monitor.py --port $PORT --host 0.0.0.0`
   - Plan: Free

Your webhook endpoint:

```
https://openai-status-monitor.onrender.com/webhook/statuspage
```

Health check:

```
https://openai-status-monitor.onrender.com/health
```

## Webhook Configuration

If you have admin access to the Statuspage.io dashboard, configure a webhook to:

```
https://openai-status-monitor.onrender.com/webhook/statuspage
```

If you do not have access, use Postman to simulate webhook payloads. See [POSTMAN_TESTING.md](POSTMAN_TESTING.md).

## Verify Deployment

```bash
curl https://openai-status-monitor.onrender.com/health
curl -X POST https://openai-status-monitor.onrender.com/webhook/statuspage \
   -H "Content-Type: application/json" \
   -d '{"incident":{"id":"live_test","name":"Chat Completions API - Elevated Error Rates","status":"investigating","updated_at":"2025-11-03T14:32:00Z","components":[{"name":"Chat Completions"}],"incident_updates":[{"body":"Degraded performance due to upstream issue"}]},"page":{"name":"OpenAI API"}}'
```

Expected server log output:

```
[2025-11-03 14:32:00] Product: OpenAI API - Chat Completions
Status: Degraded performance due to upstream issue
```

## Submission

Include in your email to be+submissions@bolna.ai:

```
Webhook Endpoint: https://openai-status-monitor.onrender.com/webhook/statuspage
Health Check: https://openai-status-monitor.onrender.com/health
```
