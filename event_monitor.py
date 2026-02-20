"""
Event-Based Status Monitor - Scalable to 100+ Providers

This is the main entry point for the webhook server.
Uses webhooks (event-driven, no polling).

Architecture:
- Providers push updates via webhooks
- Prints updates as incidents change
- Scales to 100+ providers
- Each provider sends webhook to: http://your-server:PORT/webhook/statuspage

Usage:
    python event_monitor.py                    # Start webhook server on port 5000
    python event_monitor.py --port 8000        # Custom port

For 100+ Providers:
    Configure each provider's webhook to point to this server.
    Each webhook call is processed instantly (true event-based).
"""

from flask import Flask, request, jsonify
from datetime import datetime
import argparse
from typing import Dict, Set
import json

app = Flask(__name__)

# Track seen incidents to avoid duplicates (event-based deduplication)
seen_incident_keys: Set[str] = set()
recent_incidents: Dict = {}


def create_incident_key(incident_id: str, updated_at: str) -> str:
    """
    Create unique key for incident to detect changes.
    Use incident id + updated_at to dedupe webhook events.
    """
    return f"{incident_id}_{updated_at}"


def parse_webhook_payload(payload: Dict) -> Dict:
    """
    Parse incoming webhook payload from Statuspage.io.
    
    Statuspage.io sends webhooks in this format:
    {
      "incident": {...},
      "page": {"name": "OpenAI"},
      "meta": {...}
    }
    """
    incident = payload.get("incident", {})
    page_name = payload.get("page", {}).get("name", "OpenAI API")
    
    return {
        "id": incident.get("id", "unknown"),
        "name": incident.get("name", "Unknown Incident"),
        "status": incident.get("status", "unknown"),
        "created_at": incident.get("created_at", ""),
        "updated_at": incident.get("updated_at", datetime.now().isoformat()),
        "components": [c.get("name", "Unknown") for c in incident.get("components", [])],
        "latest_message": incident.get("incident_updates", [{}])[0].get("body", "") or incident.get("name", ""),
        "provider": page_name
    }


def format_output(incident: Dict) -> str:
    """
    Format incident output per assignment specification.
    
    Format:
    [TIMESTAMP] Product: OpenAI API - SERVICE_NAME
    Status: STATUS_MESSAGE
    """
    # Parse timestamp
    timestamp = incident["updated_at"][:19].replace("T", " ")
    
    # Extract service name
    components = incident.get("components", [])
    if components:
        service_name = ", ".join(components)
    else:
        # Extract from incident name
        incident_name = incident.get("name", "Unknown")
        if " - " in incident_name:
            service_name = incident_name.split(" - ")[0].strip()
        else:
            service_name = incident_name
    
    # Get status message
    status_message = incident.get("latest_message", "Status update")
    
    # Format output
    output = f"[{timestamp}] Product: {incident['provider']} - {service_name}\n"
    output += f"Status: {status_message}"
    
    return output


def is_new_incident(incident: Dict) -> bool:
    """
    Check if this is a new or updated incident (event-based deduplication).
    
    Returns True only if we haven't seen this exact incident+timestamp combination.
    This ensures we only report actual CHANGES, not repeated webhook calls.
    """
    incident_key = create_incident_key(incident["id"], incident["updated_at"])
    
    if incident_key in seen_incident_keys:
        return False  # Already processed this update
    
    # New update - remember it
    seen_incident_keys.add(incident_key)
    return True


@app.route("/webhook/statuspage", methods=["POST"])
def handle_statuspage_webhook():
    """
    PRIMARY ENDPOINT

    Receives webhook pushes from Statuspage.io when incidents occur.
    Event-based monitoring with webhooks.
    
    Statuspage.io calls this endpoint automatically when:
    - New incident is created
    - Existing incident is updated
    - Incident is resolved
    """
    try:
        payload = request.get_json()
        
        if not payload:
            return jsonify({"error": "No payload"}), 400
        
        # Parse the webhook data
        incident = parse_webhook_payload(payload)
        
        # Event-based deduplication: Only process NEW updates
        if not is_new_incident(incident):
            return jsonify({
                "status": "duplicate",
                "message": "Already processed this update"
            }), 200
        
        # Store incident
        recent_incidents[incident["id"]] = {
            "data": incident,
            "received_at": datetime.now().isoformat()
        }
        
        # Output in required format
        output = format_output(incident)
        print(f"\n{output}\n")
        
        return jsonify({
            "status": "success",
            "incident_id": incident["id"],
            "message": "Incident processed"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "running",
        "mode": "event-based (webhooks)",
        "incidents_tracked": len(recent_incidents),
        "total_updates": len(seen_incident_keys),
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route("/", methods=["GET"])
def index():
    """Root endpoint for basic service info."""
    return jsonify({
        "service": "OpenAI Status Monitor",
        "mode": "event-based (webhooks)",
        "webhook": "/webhook/statuspage",
        "health": "/health"
    }), 200


@app.route("/incidents", methods=["GET"])
def list_incidents():
    """List all incidents received via webhooks."""
    incidents_list = []
    for incident_id, info in recent_incidents.items():
        incidents_list.append({
            "id": incident_id,
            **info["data"],
            "received_at": info["received_at"]
        })
    
    return jsonify({
        "count": len(incidents_list),
        "incidents": incidents_list
    }), 200




def main():
    """Main entry point for event-based monitoring."""
    parser = argparse.ArgumentParser(
        description="Event-Based Status Monitor (Webhooks)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Event-Based Architecture (Scales to 100+ Providers):
────────────────────────────────────────────────────
Setup:
  1. Run this server: python event_monitor.py --port 5000
  2. Configure each provider's webhook to: http://your-ip:5000/webhook/statuspage
    3. Done! System is now event-driven

For 100+ Providers:
  - Each provider sends webhooks to this single endpoint
  - Server handles them instantly as they arrive
    - No polling overhead
  - Truly scalable architecture

Test Locally:
    curl -X POST http://localhost:5000/webhook/statuspage \
             -H "Content-Type: application/json" \
             -d '{"incident":{"id":"local_test","name":"Chat Completions API - Elevated Error Rates","status":"investigating","updated_at":"2025-11-03T14:32:00Z","components":[{"name":"Chat Completions"}],"incident_updates":[{"body":"Degraded performance due to upstream issue"}]},"page":{"name":"OpenAI API"}}'

Examples:
  python event_monitor.py                    # Start on port 5000
  python event_monitor.py --port 8000        # Custom port
  python event_monitor.py --host 0.0.0.0     # Accept external connections
        """
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run webhook server on (default: 5000)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0 for all interfaces)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    
    # Run Flask app
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
