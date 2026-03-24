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
    echo "============================================================"\n\
    echo "DATABASE SETUP - Attendance System"\n\
    echo "============================================================"\n\
    echo ""\n\
    echo "[1/5] Initializing database (creating tables)..."\n\
    python init_database.py || echo "[WARN] Database initialization had warnings (tables may already exist)"\n\
    echo ""\n\
    echo "[2/5] Running legacy migrations..."\n\
    python migrate_db.py || echo "[WARN] Legacy migration had warnings..."\n\
    python fix_id_column_type.py || echo "[WARN] ID column fix had warnings..."\n\
    python fix_salary_schema.py || echo "[WARN] Schema fix had warnings..."\n\
    python add_employee_id_column.py || echo "[WARN] employee_id migration failed, continuing..."\n\
    python run_migrations.py || echo "[WARN] Comprehensive migration had warnings..."\n\
    echo ""\n\
    echo "[3/5] Applying payroll enhancements (part-time/contract/OT support)..."\n\
    python migrate_payroll_enhancements.py || echo "[WARN] Payroll enhancements migration had warnings..."\n\
    python migrate_employee_payroll_rules.py || echo "[WARN] Employee payroll rules migration had warnings..."\n\
    echo ""\n\
    echo "[4/5] Adding new allowance columns (Casting, TTB, Plating)..."\n\
    python migrate_add_allowances.py || echo "[WARN] Allowance columns migration had warnings..."\n\
    echo ""\n\
    echo "[4.5/5] Seeding demo data..."\n\
    python reset_and_seed.py || echo "[WARN] Seeding had warnings..."\n\
    echo ""\n\
    echo "[5/5] Running loan/advance migration..."\n\
    python run_loan_migration.py || echo "[WARN] Loan migration had warnings..."\n\
    echo ""\n\
    echo "[6/5] Starting application server..."\n\
    echo "============================================================"\n\
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
    ' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/bin/bash", "/app/start.sh"]
