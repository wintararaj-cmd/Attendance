FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV and face recognition
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-prod.txt requirements.txt ./

# Install Python dependencies (production-optimized, no heavy ML libs)
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY . .

# Force mock mode for face recognition (no heavy ML dependencies in production)
ENV FORCE_MOCK_MODE=true

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
    echo "🔄 Running database migration..."\n\
    python migrate_db.py || echo "⚠️ Migration failed, continuing anyway..."\n\
    echo "🚀 Starting server..."\n\
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
    ' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/bin/bash", "/app/start.sh"]
