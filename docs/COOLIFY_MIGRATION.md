# Coolify Database Migration Guide

## 🚀 Quick Fix for Coolify Deployment

Since you're using **Coolify**, the migration process is slightly different. Here's how to run it:

---

## ✅ **Method 1: Using Coolify Console (Recommended)**

### Step 1: Access Coolify Console
1. Open your **Coolify Dashboard**
2. Navigate to your **Backend Application**
3. Click on **"Terminal"** or **"Console"** tab

### Step 2: Run Migration
In the console, run:

```bash
python backend/migrate_db.py
```

**OR** if that doesn't work, try:

```bash
cd /app
python backend/migrate_db.py
```

### Step 3: Restart Application
After successful migration:
1. Go back to Coolify dashboard
2. Click **"Restart"** on your backend application
3. Wait for it to come back online

---

## ✅ **Method 2: Direct Database Access**

If you have access to your PostgreSQL database in Coolify:

### Step 1: Access Database Console
1. In Coolify, go to your **Database** resource
2. Click on **"Terminal"** or **"psql"**

### Step 2: Run SQL Commands
```sql
-- Connect to your database
\c attendance_db

-- Add missing columns to employees table
ALTER TABLE employees ADD COLUMN IF NOT EXISTS email VARCHAR;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS department VARCHAR;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS designation VARCHAR;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_type VARCHAR DEFAULT 'full_time';
ALTER TABLE employees ADD COLUMN IF NOT EXISTS joining_date DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;

-- Create departments table
CREATE TABLE IF NOT EXISTS departments (
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

-- Verify changes
\d employees
\d departments
```

---

## ✅ **Method 3: One-Time Deployment Command**

You can also add the migration to your deployment process:

### Update your Coolify Build Command:
```bash
# In Coolify Build Command or Post-Deployment Script
python backend/migrate_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

This will run migration automatically on every deployment.

---

## 🔍 **Troubleshooting Coolify Issues**

### Issue: "python: command not found"
**Solution**: Use `python3` instead:
```bash
python3 backend/migrate_db.py
```

### Issue: "No module named 'sqlalchemy'"
**Solution**: Install dependencies first:
```bash
pip install -r backend/requirements.txt
python backend/migrate_db.py
```

### Issue: "DATABASE_URL not set"
**Solution**: 
1. Go to Coolify dashboard
2. Navigate to your backend app
3. Check **Environment Variables**
4. Ensure `DATABASE_URL` is set correctly
5. Format: `postgresql://user:password@host:port/database`

### Issue: "Permission denied"
**Solution**: The migration script is safe and read-only for checking. For actual migration, ensure your database user has ALTER TABLE permissions.

---

## 📋 **What Gets Migrated**

The script will:

✅ Add `email` column to employees  
✅ Add `department` column to employees  
✅ Add `designation` column to employees  
✅ Add `employee_type` column to employees  
✅ Add `joining_date` column to employees  
✅ Add `updated_at` column to employees  
✅ Create `departments` table  

**Note**: The script is **idempotent** - it won't break if columns already exist.

---

## 🎯 **Coolify-Specific Commands**

```bash
# Check current directory
pwd

# List files
ls -la

# Check if backend directory exists
ls backend/

# Run migration from root
python backend/migrate_db.py

# Check Python version
python --version

# Install dependencies if needed
pip install sqlalchemy psycopg2-binary

# Verify database connection
python -c "import os; print(os.getenv('DATABASE_URL', 'Not set'))"
```

---

## 🔐 **Environment Variables to Check**

Make sure these are set in Coolify:

| Variable | Example | Required |
|----------|---------|----------|
| `DATABASE_URL` | `postgresql://user:pass@db:5432/attendance` | ✅ Yes |
| `SECRET_KEY` | `your-secret-key` | ✅ Yes |
| `ALGORITHM` | `HS256` | ✅ Yes |

---

## 📊 **Verify Migration Success**

After running the migration, verify it worked:

```bash
# In Coolify console
python -c "
from sqlalchemy import create_engine, inspect
import os
engine = create_engine(os.getenv('DATABASE_URL'))
inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('employees')]
print('Employees columns:', columns)
print('Has email:', 'email' in columns)
print('Has department:', 'department' in columns)
"
```

Expected output:
```
Employees columns: ['id', 'company_id', 'emp_code', 'first_name', 'last_name', 'mobile_no', 'email', 'department', 'designation', 'employee_type', 'joining_date', 'status', 'face_encoding_ref', 'is_face_registered', 'created_at', 'updated_at']
Has email: True
Has department: True
```

---

## 🚨 **If All Else Fails**

### Manual SQL via Coolify Database Console:

1. **Access Database**:
   - Coolify Dashboard → Your Database → Terminal

2. **Run this complete script**:
```sql
-- Add columns one by one
DO $$ 
BEGIN
    -- Add email
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='employees' AND column_name='email') THEN
        ALTER TABLE employees ADD COLUMN email VARCHAR;
    END IF;
    
    -- Add department
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='employees' AND column_name='department') THEN
        ALTER TABLE employees ADD COLUMN department VARCHAR;
    END IF;
    
    -- Add designation
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='employees' AND column_name='designation') THEN
        ALTER TABLE employees ADD COLUMN designation VARCHAR;
    END IF;
    
    -- Add employee_type
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='employees' AND column_name='employee_type') THEN
        ALTER TABLE employees ADD COLUMN employee_type VARCHAR DEFAULT 'full_time';
    END IF;
    
    -- Add joining_date
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='employees' AND column_name='joining_date') THEN
        ALTER TABLE employees ADD COLUMN joining_date DATE;
    END IF;
    
    -- Add updated_at
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='employees' AND column_name='updated_at') THEN
        ALTER TABLE employees ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- Create departments table
CREATE TABLE IF NOT EXISTS departments (
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

3. **Verify**:
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'employees'
ORDER BY ordinal_position;
```

---

## ✨ **After Successful Migration**

Once migration is complete:

1. ✅ **Restart** your backend application in Coolify
2. ✅ **Test** the Department Management page
3. ✅ **Verify** employee registration works with all fields
4. ✅ **Check** that no more "column does not exist" errors appear

---

## 📞 **Still Having Issues?**

If you're still stuck:

1. **Check Coolify Logs**:
   - Go to your backend app
   - Click "Logs" tab
   - Look for any database connection errors

2. **Verify Database Connection**:
   ```bash
   python -c "import os; from sqlalchemy import create_engine; engine = create_engine(os.getenv('DATABASE_URL')); print('Connected!' if engine else 'Failed')"
   ```

3. **Check Database Permissions**:
   - Ensure your database user has `ALTER TABLE` permissions
   - Coolify usually sets this up correctly by default

---

**Last Updated**: January 30, 2026  
**Platform**: Coolify  
**Database**: PostgreSQL
