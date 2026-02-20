# 🧪 Postman Testing Guide for Event Monitor

Your server is running on **http://localhost:5001** (check your terminal for the actual port)

---

## 📋 API Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check server status |
| GET | `/incidents` | List all received incidents |
| POST | `/webhook/statuspage` | Real webhook endpoint (production) |

---

## 🚀 Test 1: Health Check (Easiest)

**Method:** `GET`  
**URL:** `http://localhost:5001/health`  
**Headers:** None needed

**Expected Response:**
```json
{
  "status": "running",
  "mode": "event-based (webhooks)",
  "incidents_tracked": 0,
  "total_updates": 0,
  "timestamp": "2026-02-20T02:18:01.699778"
}
```

**In Postman:**
1. Create new request
2. Set method to **GET**
3. Enter URL: `http://localhost:5001/health`
4. Click **Send**
5. You should see 200 OK with JSON response

---

## 📊 Test 2: List Incidents

**Method:** `GET`  
**URL:** `http://localhost:5001/incidents`  
**Headers:** None needed

**Expected Response:**
```json
{
  "count": 1,
  "incidents": [
    {
      "id": "test_20260220021738",
      "name": "Test Incident - System Check",
      "status": "investigating",
      "components": ["Test Service"],
      "latest_message": "This is a test webhook to verify the system is working",
      "received_at": "2026-02-20T02:17:38.477890"
    }
  ]
}
```

**In Postman:**
1. Create new request
2. Set method to **GET**
3. Enter URL: `http://localhost:5001/incidents`
4. Click **Send**

---

## 🎯 Test 3: Real Webhook (Production Format)

**Method:** `POST`  
**URL:** `http://localhost:5001/webhook/statuspage`  
**Headers:**
```
Content-Type: application/json
```

**Body (Copy this exact JSON):**
```json
{
  "incident": {
    "id": "abc123",
    "name": "Chat Completions API - Elevated Error Rates",
    "status": "investigating",
    "impact": "major",
    "created_at": "2025-11-03T14:30:00Z",
    "updated_at": "2025-11-03T14:32:00Z",
    "components": [
      {
        "name": "Chat Completions"
      }
    ],
    "incident_updates": [
      {
        "body": "Degraded performance due to upstream issue",
        "status": "investigating",
        "created_at": "2025-11-03T14:32:00Z"
      }
    ]
  },
  "page": {
    "name": "OpenAI API"
  }
}
```

**Expected Response:**
```json
{
  "status": "success",
  "incident_id": "abc123",
  "message": "Incident processed"
}
```

**Expected Terminal Output (This is what matters!):**
```
[2025-11-03 14:32:00] Product: OpenAI API - Chat Completions
Status: Degraded performance due to upstream issue
```

**In Postman:**
1. Create new request
2. Set method to **POST**
3. Enter URL: `http://localhost:5001/webhook/statuspage`
4. Go to **Headers** tab:
   - Key: `Content-Type`
   - Value: `application/json`
5. Go to **Body** tab:
   - Select **raw**
   - Select **JSON** from dropdown
   - Paste the JSON above
6. Click **Send**
7. **Check the server logs (local terminal or Render Logs tab) for the formatted output.**

---

## 🔥 Test 4: Multiple Services (Advanced)

**Method:** `POST`  
**URL:** `http://localhost:5001/webhook/statuspage`  
**Headers:** `Content-Type: application/json`

**Body:**
```json
{
  "incident": {
    "id": "xyz789",
    "name": "API Outage",
    "status": "identified",
    "created_at": "2025-11-03T15:00:00Z",
    "updated_at": "2025-11-03T15:05:00Z",
    "components": [
      {
        "name": "Chat Completions"
      },
      {
        "name": "Assistants API"
      },
      {
        "name": "Embeddings"
      }
    ],
    "incident_updates": [
      {
        "body": "We have identified the issue and are working on a fix. Multiple services are affected.",
        "status": "identified"
      }
    ]
  },
  "page": {
    "name": "OpenAI API"
  }
}
```

**Expected Terminal Output:**
```
[2025-11-03 15:05:00] Product: OpenAI API - Chat Completions, Assistants API, Embeddings
Status: We have identified the issue and are working on a fix. Multiple services are affected.
```

---

## 📝 Quick Testing Checklist

1. ✅ **Start Server**
   ```bash
   source venv/bin/activate
   python event_monitor.py --port 5001
   ```

2. ✅ **Test Health** - Verify server is running

3. ✅ **Test Real Webhook** - Send production-format JSON

4. ✅ **Check Terminal** - See formatted output appear

5. ✅ **List Incidents** - Verify incidents were stored

---

## 🎬 Postman Collection (Import This)

Create a new collection in Postman and add these 3 requests:

**Collection Name:** OpenAI Status Monitor

### Request 1: Health Check
- **Name:** Health Check
- **Method:** GET
- **URL:** `http://localhost:5001/health`

### Request 2: Production Webhook
- **Name:** Real Webhook - Chat API Issue
- **Method:** POST
- **URL:** `http://localhost:5001/webhook/statuspage`
- **Headers:** `Content-Type: application/json`
- **Body:** (Use the JSON from Test 3 above)

### Request 3: List Incidents
- **Name:** List All Incidents
- **Method:** GET
- **URL:** `http://localhost:5001/incidents`

---

## 🔍 Troubleshooting

**Problem:** Connection refused  
**Solution:** Make sure server is running (`python event_monitor.py --port 5001`)

**Problem:** 404 Not Found  
**Solution:** Check the URL spelling and port number

**Problem:** No terminal output  
**Solution:** Terminal output only shows for NEW incidents. Send different `id` values each time.

**Problem:** Duplicate response  
**Solution:** This is expected! Change the `updated_at` timestamp to see new output.

---

## ✅ Success Criteria

Your system is working correctly if:

1. ✅ Health check returns status "running"
2. ✅ POST to `/webhook/statuspage` returns `{"status": "success", "incident_id": "...", "message": "Incident processed"}`
3. ✅ **Terminal shows** formatted output like:
   ```
   [TIMESTAMP] Product: OpenAI API - Service
   Status: Message
   ```
4. ✅ GET `/incidents` shows received webhooks

**The terminal output is what matters most - that's what the assignment requires!**
