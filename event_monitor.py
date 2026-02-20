"""Event-based webhook server for OpenAI status incidents."""

from flask import Flask, request, jsonify
from datetime import datetime
import argparse
from typing import Dict, Set
import json
import logging

app = Flask(__name__)

# Track seen incidents to avoid duplicates (event-based deduplication)
seen_incident_keys: Set[str] = set()
recent_incidents: Dict = {}


def create_incident_key(incident_id: str, updated_at: str) -> str:
    """Create a unique incident key for dedupe."""
    return f"{incident_id}_{updated_at}"


def parse_webhook_payload(payload: Dict) -> Dict:
    """Parse incoming Statuspage webhook payload."""
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
    """Format incident output per assignment specification."""
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
    """Return True only for new or updated incidents."""
    incident_key = create_incident_key(incident["id"], incident["updated_at"])
    
    if incident_key in seen_incident_keys:
        return False  # Already processed this update
    
    # New update - remember it
    seen_incident_keys.add(incident_key)
    return True


@app.route("/webhook/statuspage", methods=["POST"])
def handle_statuspage_webhook():
    """Handle Statuspage incident webhooks."""
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
        print(output, flush=True)
        
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

def main():
    """Run the webhook server."""
    parser = argparse.ArgumentParser(
        description="Event-Based Status Monitor (Webhooks)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Event-Based Architecture (Scales to 100+ Providers):
────────────────────────────────────────────────────

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
    
    
    # Suppress request access logs so only formatted output is printed
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    # Run Flask app
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
