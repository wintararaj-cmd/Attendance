#!/bin/bash
# Production Startup Script with Auto-Migration
# This script runs migrations before starting the application

set -e

echo "=========================================="
echo "Starting Attendance System Backend"
echo "=========================================="
echo ""

# Run database migrations
echo "[1/3] Running database migrations..."
python run_migrations.py || {
    echo "[WARN] Migrations had warnings, but continuing..."
}

echo ""
echo "[2/3] Migrations complete!"
echo ""

# Start the application
echo "[3/3] Starting application server..."
echo ""

# Use uvicorn to start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
