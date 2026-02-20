#!/bin/bash
# Setup script for OpenAI Status Monitor
# Run this once to set up the virtual environment and install dependencies

echo "🚀 Setting up OpenAI Status Monitor..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip --quiet

# Install requirements
echo "📥 Installing dependencies (this may take a minute)..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo ""
echo "1. Activate the environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the server:"
echo "   python event_monitor.py --port 5000"
echo ""
echo "3. Send a webhook payload:"
echo "   curl -X POST http://localhost:5000/webhook/statuspage -H \"Content-Type: application/json\" -d '{\"incident\":{\"id\":\"local_test\",\"name\":\"Chat Completions API - Elevated Error Rates\",\"status\":\"investigating\",\"updated_at\":\"2025-11-03T14:32:00Z\",\"components\":[{\"name\":\"Chat Completions\"}],\"incident_updates\":[{\"body\":\"Degraded performance due to upstream issue\"}]},\"page\":{\"name\":\"OpenAI API\"}}'"
echo ""
echo "4. Check health:"
echo "   curl http://localhost:5000/health"
echo ""
echo "💡 To deactivate the environment later, run: deactivate"
