# Database Setup Guide - Part-time/Contract Worker & OT Support

## Issue: Tables Don't Exist

The migration failed because the base database tables haven't been created yet. Follow these steps to set up your database properly.

## Step-by-Step Setup

### Step 1: Initialize the Database (Create All Tables)

Run this command to create all base tables:

```bash
cd backend
python init_database.py
```

This will:
- Drop any existing tables (if any)
- Create all tables from the SQLAlchemy models:
  - `admin_users`
  - `companies`
  - `departments`
  - `employees`
  - `attendance_logs`
  - `salary_structures` (with basic structure)

### Step 2: Run Payroll Enhancements Migration

After the base tables are created, run the payroll enhancements migration:

```bash
python migrate_payroll_enhancements.py
```

This will add:
- **To `salary_structures`**: hourly_rate, contract_rate_per_day, OT multipliers
- **To `attendance_logs`**: OT tracking fields

### Step 3: Verify the Setup

Check that all tables and columns exist:

```bash
python -c "from app.core.database import engine; from sqlalchemy import inspect; inspector = inspect(engine); print('Tables:', inspector.get_table_names()); print('Salary columns:', [c['name'] for c in inspector.get_columns('salary_structures')])"
```

## Alternative: If You Have Existing Data

If you already have data in your database and don't want to drop tables, use this approach:

### Option A: Manual Table Creation (PostgreSQL)

Connect to your PostgreSQL database and run:

```sql
-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    id VARCHAR PRIMARY KEY,
    company_id VARCHAR,
    emp_code VARCHAR NOT NULL,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR,
    mobile_no VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE,
    department VARCHAR,
    designation VARCHAR,
    employee_type VARCHAR DEFAULT 'full_time',
    joining_date DATE,
    status VARCHAR DEFAULT 'active',
    face_encoding_ref VARCHAR,
    is_face_registered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create other tables...
-- (See app/models/models.py for complete schema)
```

### Option B: Use migrate_db.py (If Tables Partially Exist)

If some tables exist but are missing columns:

```bash
python migrate_db.py
```

This will:
- Add missing columns to existing tables
- Create missing tables
- Migrate old salary structure schema

## Troubleshooting

### Error: "No module named 'psycopg2'"

Install PostgreSQL driver:
```bash
python -m pip install psycopg2-binary
```

### Error: "Connection refused" or "Authentication failed"

Check your `.env` file has correct database credentials:
```
DATABASE_URL=postgresql://username:password@localhost:5432/attendance_db
```

### Error: "Permission denied"

Make sure your PostgreSQL user has CREATE TABLE permissions:
```sql
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO your_username;
```

## What Gets Created

### Base Tables (init_database.py)
1. **admin_users** - Admin login credentials
2. **companies** - Company information
3. **departments** - Department management
4. **employees** - Employee records with employee_type field
5. **attendance_logs** - Attendance tracking
6. **salary_structures** - Salary configuration (basic)

### Enhanced Fields (migrate_payroll_enhancements.py)
1. **salary_structures additions**:
   - `is_hourly_based` - Flag for hourly workers
   - `hourly_rate` - Hourly rate
   - `contract_rate_per_day` - Daily rate
   - `ot_rate_multiplier` - Weekday OT (1.5x)
   - `ot_weekend_multiplier` - Weekend OT (2.0x)
   - `ot_holiday_multiplier` - Holiday OT (2.5x)

2. **attendance_logs additions**:
   - `ot_hours` - Regular OT hours
   - `ot_weekend_hours` - Weekend OT hours
   - `ot_holiday_hours` - Holiday OT hours
   - `total_hours_worked` - Total hours (for hourly workers)

## Quick Start (Fresh Database)

For a completely fresh setup:

```bash
cd backend

# Step 1: Install dependencies
python -m pip install psycopg2-binary

# Step 2: Initialize database
python init_database.py

# Step 3: Add payroll enhancements
python migrate_payroll_enhancements.py

# Step 4: Start the application
python -m uvicorn app.main:app --reload
```

## Next Steps After Setup

1. **Create an admin user** (if needed)
2. **Register employees** with different employee types
3. **Configure salary structures** with new fields
4. **Test payroll calculation** for different worker types

---

**Need Help?**
- Check `PAYROLL_ENHANCEMENTS.md` for detailed documentation
- Review `backend/app/models/models.py` for complete schema
- Check logs for specific error messages
