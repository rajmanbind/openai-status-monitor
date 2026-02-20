# Event-Based Status Monitor - Docker Image

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY event_monitor.py ./

# Create non-root user for security
RUN useradd -m -u 1000 monitor && \
    chown -R monitor:monitor /app
USER monitor

# Expose webhook port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run webhook server
# Railway/Render will set PORT env variable, use it if available
CMD python event_monitor.py --port ${PORT:-5000} --host 0.0.0.0
