# Database Migration Guide

## Issue: Missing Columns Error

If you see this error:
```
sqlalchemy.exc.ProgrammingError: column employees.email does not exist
```

This means your database schema is outdated and needs to be migrated.

---

## Quick Fix (Production)

### Option 1: Run Migration Script (Recommended)

1. **SSH into your production server** (or use the platform's console)

2. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

3. **Run the migration script:**
   ```bash
   python migrate_db.py
   ```

4. **Restart your application**

---

### Option 2: Manual SQL Migration

If you have direct database access, run these SQL commands:

```sql
-- Add missing columns to employees table
ALTER TABLE employees ADD COLUMN email VARCHAR;
ALTER TABLE employees ADD COLUMN department VARCHAR;
ALTER TABLE employees ADD COLUMN designation VARCHAR;
ALTER TABLE employees ADD COLUMN employee_type VARCHAR DEFAULT 'full_time';
ALTER TABLE employees ADD COLUMN joining_date DATE;
ALTER TABLE employees ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;

-- Create departments table
CREATE TABLE departments (
    id VARCHAR PRIMARY KEY,
    company_id VARCHAR,
    name VARCHAR NOT NULL,
    description TEXT,
    department_head VARCHAR,
    status VARCHAR DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (company_id) REFERENCES companies(id)
);
```

---

## For Railway/Render Deployment

### Railway:

1. Go to your Railway project
2. Click on your backend service
3. Go to **"Variables"** tab
4. Find your `DATABASE_URL`
5. Use Railway's **"Shell"** or **"Deploy"** to run:
   ```bash
   python backend/migrate_db.py
   ```

### Render:

1. Go to your Render dashboard
2. Click on your backend service
3. Go to **"Shell"** tab
4. Run:
   ```bash
   cd backend
   python migrate_db.py
   ```

---

## Verification

After migration, verify the changes:

```sql
-- Check employees table structure
\d employees

-- Check if departments table exists
\d departments

-- Verify columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'employees';
```

---

## What the Migration Does

The migration script will:

1. ✅ Add `email` column to employees table
2. ✅ Add `department` column to employees table
3. ✅ Add `designation` column to employees table
4. ✅ Add `employee_type` column to employees table
5. ✅ Add `joining_date` column to employees table
6. ✅ Add `updated_at` column to employees table
7. ✅ Create `departments` table if it doesn't exist

---

## Troubleshooting

### Error: "relation 'employees' does not exist"
**Solution**: Your database is completely empty. You need to create all tables first using:
```bash
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Error: "column already exists"
**Solution**: The migration script will skip columns that already exist. This is safe.

### Error: "permission denied"
**Solution**: Ensure your database user has ALTER TABLE permissions.

---

## Prevention: Using Alembic (Future)

For better migration management, consider using Alembic:

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add employee fields"

# Apply migration
alembic upgrade head
```

---

## Need Help?

If you encounter issues:
1. Check the database logs
2. Verify DATABASE_URL is correct
3. Ensure database is accessible
4. Check user permissions

---

**Last Updated**: January 30, 2026
