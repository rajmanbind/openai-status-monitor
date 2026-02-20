# OpenAI Status Page Monitor (Event-Based)

Automatically tracks and logs service updates from the OpenAI Status Page using webhooks (event-based). The server receives incident updates and prints them in the required format.

## Features

✅ **Automatic Detection** - Receives new incidents and updates via webhook pushes
✅ **Event-Based** - No inefficient polling
✅ **Scalable** - One endpoint can handle 100+ providers
✅ **Console Output** - Simple, assignment-ready output

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Run Locally

```bash
python event_monitor.py --port 5000
```

### Test Locally

```bash
curl -X POST http://localhost:5000/webhook/statuspage \
	-H "Content-Type: application/json" \
	-d '{"incident":{"id":"local_test","name":"Chat Completions API - Elevated Error Rates","status":"investigating","updated_at":"2025-11-03T14:32:00Z","components":[{"name":"Chat Completions"}],"incident_updates":[{"body":"Degraded performance due to upstream issue"}]},"page":{"name":"OpenAI API"}}'
curl http://localhost:5000/health
```

## Output Format

Example output:

```
[2025-11-03 14:32:00] Product: OpenAI API - Chat Completions
Status: Degraded performance due to upstream issue
```

## How It Works (Event-Based)

1. Statuspage.io sends webhook events for incident create/update/resolve.
2. The server parses the payload and formats output.
3. Dedupe prevents duplicate prints.

Webhook endpoint:

```
POST /webhook/statuspage
```

Other endpoints:

```
GET  /health
GET  /incidents
```

## Scaling to 100+ Providers

This design scales because providers push updates to one endpoint. No polling loops are required, and the server only does work when incidents occur.

## Deployment

Render is the primary deployment target. See:

- [DEPLOY.md](DEPLOY.md)

## Notes on Webhook Configuration

Configuring webhooks on the OpenAI Status Page requires admin access. If you do not have access, use Postman to simulate webhook payloads and demonstrate the output format. See [POSTMAN_TESTING.md](POSTMAN_TESTING.md).

## Troubleshooting

**Q: No output in terminal**
- A: Send a webhook payload to `/webhook/statuspage`
- A: Ensure the webhook payload has a new `updated_at` or unique `id`

**Q: Webhook returns 400**
- A: Confirm `Content-Type: application/json` and valid JSON body

## Contributing

Ideas for enhancements:
- WebSocket support for real-time updates
- Database storage of incident history
- Slack/PagerDuty/Email notifications
- Web dashboard for incident history
- Multi-provider aggregation
- Time-series metrics export (Prometheus)

## License

MIT

## Summary

This is a **production-ready, scalable solution** for monitoring status pages. It demonstrates:

✅ Efficient event-based detection (suitable for 100+ pages)
✅ Clean webhook-first architecture
✅ Simple console output for the assignment
