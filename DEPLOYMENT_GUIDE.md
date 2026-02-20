# DEPLOYMENT_GUIDE.md

Complete guide for deploying the OpenAI Status Monitor to production.

## Local Deployment (macOS/Linux)

### Option 1: Direct Python (Simplest)

```bash
# Install dependencies
pip install -r requirements.txt

# Run continuously
python monitor.py --verbose

# Or run in background
nohup python monitor.py > monitor.log 2>&1 &
```

### Option 2: systemd Service (Linux/macOS)

**Create service file:**

```bash
sudo tee /etc/systemd/system/openai-monitor.service > /dev/null <<EOF
[Unit]
Description=OpenAI Status Page Monitor
After=network.target

[Service]
Type=simple
User=monitor
WorkingDirectory=/opt/openai-monitor
ExecStart=/usr/bin/python3 /opt/openai-monitor/monitor.py --verbose
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

**Enable and start:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable openai-monitor
sudo systemctl start openai-monitor

# View logs
sudo journalctl -u openai-monitor -f
```

### Option 3: LaunchAgent (macOS)

**Create plist file:**

```bash
cat > ~/Library/LaunchAgents/com.openai.monitor.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openai.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/opt/openai-monitor/monitor.py</string>
        <string>--verbose</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/var/log/openai-monitor.err.log</string>
    <key>StandardOutPath</key>
    <string>/var/log/openai-monitor.out.log</string>
</dict>
</plist>
EOF
```

**Load it:**

```bash
launchctl load ~/Library/LaunchAgents/com.openai.monitor.plist

# View logs
tail -f /var/log/openai-monitor.out.log
```

## Docker Deployment

### Option 1: Simple Docker Run

```bash
# Build image
docker build -t openai-monitor .

# Run continuously
docker run -d \
  --name openai-monitor \
  --restart always \
  openai-monitor

# View logs
docker logs -f openai-monitor

# Stop
docker stop openai-monitor
docker rm openai-monitor
```

### Option 2: Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f openai-monitor

# Stop all
docker-compose down
```

**Services:**
- `openai-monitor` - Main monitoring service
- `multi-provider-monitor` - Optional: monitors 100+ providers
- `webhook-receiver` - Optional: webhook endpoint on port 5000

### Option 3: Docker Push to Registry

```bash
# Tag image
docker tag openai-monitor myregistry.com/openai-monitor:latest

# Push to registry
docker push myregistry.com/openai-monitor:latest

# Pull and run elsewhere
docker pull myregistry.com/openai-monitor:latest
docker run -d myregistry.com/openai-monitor:latest
```

## Cloud Deployment

### AWS DynamoDB/Lambda (Serverless)

```python
# lambda_handler.py
import json
from openai_status_client import StatusPageClient
from status_tracker import StatusTracker

def lambda_handler(event, context):
    """Lambda function triggered by CloudWatch Events"""
    # Initialize tracker (could use DynamoDB for state)
    tracker = StatusTracker()
    client = StatusPageClient(
        "https://status.openai.com/api/v2",
        "openai"
    )
    
    incidents = client.get_active_incidents()
    new = tracker.detect_new_incidents(incidents)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'new_incidents': len(new),
            'incidents': new
        })
    }
```

**CloudWatch Event Rule:**
- Schedule: `rate(5 minutes)`
- Target: lambda_handler

### AWS ECS (Container Orchestration)

```json
{
  "family": "openai-monitor",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "monitor",
      "image": "openai-monitor:latest",
      "memory": 256,
      "cpu": 128,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/openai-monitor",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Deploy with:
```bash
aws ecs register-task-definition --cli-input-json file://task-def.json
aws ecs create-service \
  --cluster default \
  --service-name openai-monitor \
  --task-definition openai-monitor:1 \
  --desired-count 1
```

### Google Cloud Run (Simplest Cloud Option)

```bash
# Create Dockerfile first
# Then:

gcloud run deploy openai-monitor \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# View logs
gcloud run logs read openai-monitor --limit 50
```

### Kubernetes

```bash
# Create image
docker build -t openai-monitor:v1.0 .

# Create ConfigMap for config
kubectl create configmap monitor-config --from-file=config.py

# Create Deployment
kubectl apply -f k8s-deployment.yaml

# View logs
kubectl logs -f deployment/openai-monitor
```

**k8s-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openai-monitor
spec:
  replicas: 2
  selector:
    matchLabels:
      app: openai-monitor
  template:
    metadata:
      labels:
        app: openai-monitor
    spec:
      containers:
      - name: monitor
        image: openai-monitor:v1.0
        args: ["--verbose", "--interval", "300"]
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python3
            - -c
            - "import requests; requests.get('http://localhost:5000/health')"
          initialDelaySeconds: 30
          periodSeconds: 60
```

## Webhook Deployment (Recommended for 100+ Pages)

### AWS API Gateway + Lambda

```bash
# Create REST API
aws apigateway create-rest-api --name openai-webhook

# Create resource
aws apigateway create-resource --rest-api-id xxx --parent-id yyy --path-part webhook

# Create POST method pointing to Lambda
aws apigateway put-method --rest-api-id xxx --resource-id zzz --http-method POST

# Deploy
aws apigateway create-deployment --rest-api-id xxx --stage-name prod
```

### Webhook URL to configure in Statuspage.io:
```
https://xxx.execute-api.us-east-1.amazonaws.com/prod/webhook
```

## Monitoring the Monitor

### Health Checks

Add endpoint to monitor.py:
```python
@app.route("/health", methods=["GET"])
def health():
    return {"status": "healthy"}, 200
```

Configure monitoring:
```bash
# Uptime monitoring
curl -I https://your-domain.com/health

# Kubernetes liveness probe (see k8s-deployment.yaml)
# Systemd ExecStartPost checks (in service file)
```

### Logging Strategy

**Local development:**
```bash
python monitor.py --verbose
```

**Production:**
```bash
# Docker
docker logs -f openai-monitor

# Kubernetes
kubectl logs -f deployment/openai-monitor

# Systemd
journalctl -u openai-monitor -f

# AWS CloudWatch
aws logs tail /ecs/openai-monitor --follow
```

### Alerting

Set up alerts when monitor fails:

**Datadog:**
```python
from datadog import initialize, api

initialize(api_key="xxx", app_key="yyy")
api.Monitor.create(
    type="monitor",
    query='avg(last_1h):avg:process.uptime{service:openai-monitor} < 300',
    name="OpenAI Monitor Down",
)
```

**PagerDuty:**
```python
import requests

def alert_pagerduty(incident):
    requests.post(
        "https://events.pagerduty.com/v2/enqueue",
        json={
            "routing_key": "YOUR_ROUTING_KEY",
            "event_action": "trigger",
            "payload": {
                "summary": f"OpenAI Status: {incident['name']}",
                "severity": "error",
                "source": "OpenAI Monitor"
            }
        }
    )
```

## Performance Tuning

### For 100+ Providers

```python
# In config.py
POLLING_INTERVAL = 600  # 10 minutes instead of 5
MAX_WORKERS = 10  # Parallel API calls

# Use Redis for distributed state
REDIS_ENABLED = True
REDIS_URL = "redis://localhost:6379/0"
```

### Memory Optimization

```python
# In status_tracker.py - periodic cleanup
def cleanup_old_incidents(days_old=30):
    """Remove resolved incidents older than N days"""
    cutoff = datetime.now() - timedelta(days=days_old)
    for incident_id, data in list(self.known_incidents.items()):
        incident_date = datetime.fromisoformat(data['updated_at'])
        if incident_date < cutoff:
            del self.known_incidents[incident_id]
```

### Network Optimization

```python
# Use connection pooling
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

## Disaster Recovery

### State Backup

If using persistent state:
```bash
# Backup state
cp incidents.db incidents.db.backup

# Restore from backup
cp incidents.db.backup incidents.db
```

### Zero-Downtime Deployment

```bash
# Blue-green deployment with Docker
docker pull openai-monitor:v2.0
docker run -d --name openai-monitor-v2 openai-monitor:v2.0
docker stop openai-monitor
docker rename openai-monitor-v2 openai-monitor
```

## Cost Estimation

### Local (VPS)
- **Compute**: $5-20/month (minimal CPU usage)
- **Storage**: Free (no persistent data needed)
- **Bandwidth**: Free (minimal)
- **Total**: ~$5-20/month

### AWS
- **Lambda**: ~$0.50/month (free tier covers this)
- **API Gateway**: ~$1/month
- **CloudWatch Logs**: ~$0.50/month
- **Total**: ~$2/month

### Kubernetes
- **Cluster**: $15-100+/month (depends on instance size)
- **Storage**: Minimal
- **Total**: $15-100+/month

## Maintenance

### Regular Tasks

- **Daily**: Check logs for errors
- **Weekly**: Verify incident detection working
- **Monthly**: Review and update configuration
- **Quarterly**: Update dependencies

### Dependency Updates

```bash
# Check for updates
pip list --outdated

# Update safely
pip install --upgrade requests python-dateutil pydantic

# Test after update
python test_monitor.py
```

### Log Rotation (Systemd)

Logs are automatically rotated via journalctl.

### Log Rotation (Manual)

```bash
# Create logrotate config
sudo tee /etc/logrotate.d/openai-monitor > /dev/null <<EOF
/var/log/openai-monitor.*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
}
EOF
```

---

Choose the deployment option that best fits your infrastructure!
