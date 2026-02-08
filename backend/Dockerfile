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
COPY requirements.txt .

# Install Python dependencies (includes DeepFace for real face recognition)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Enable real face recognition (comment out to use mock mode)
# ENV FORCE_MOCK_MODE=true

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
    echo "🔄 Running database migrations..."\n\
    python migrate_db.py || echo "⚠️ Old migration had warnings..."\n\
    echo "🔧 Fixing salary schema..."\n\
    python fix_salary_schema.py || echo "⚠️ Schema fix had warnings..."\n\
    echo "🔧 Adding employee_id column..."\n\
    python add_employee_id_column.py || echo "⚠️ employee_id migration failed, continuing..."\n\
    echo "🔧 Running comprehensive migrations..."\n\
    python run_migrations.py || echo "⚠️ Comprehensive migration had warnings..."\n\
    echo "🚀 Starting server..."\n\
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
    ' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/bin/bash", "/app/start.sh"]

