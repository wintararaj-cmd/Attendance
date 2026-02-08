# Deployment Migration Guide

## Overview
This guide explains how to run database migrations to fix the "Failed to save salary" error.

## The Problem
The `salary_structures` table is missing the `employee_id` column, which causes the error:
```
column salary_structures.employee_id does not exist
```

## Solution: Run Migrations

### Method 1: Automated Migration Runner (Recommended)

Use the Python-based migration runner that works on all platforms:

```bash
# Navigate to backend directory
cd backend

# Run all migrations
python run_migrations.py
```

This will:
1. Add the `employee_id` column to `salary_structures`
2. Add all other missing salary components
3. Set up proper foreign keys and constraints

### Method 2: Individual Migration Scripts

Run migrations manually in order:

```bash
# Step 1: Add employee_id column
python add_employee_id_column.py

# Step 2: Add other salary components
python migrate_salary_structure.py
```

### Method 3: Platform-Specific Scripts

**Linux/macOS:**
```bash
chmod +x deploy_migrate.sh
./deploy_migrate.sh
```

**Windows:**
```cmd
deploy_migrate.bat
```

## For Production Deployment

### Option A: SSH into Production Server

1. SSH into your production server:
   ```bash
   ssh user@your-server.com
   ```

2. Navigate to the backend directory:
   ```bash
   cd /path/to/backend
   ```

3. Run migrations:
   ```bash
   python run_migrations.py
   ```

4. Restart the application:
   ```bash
   # For systemd
   sudo systemctl restart attendance-api
   
   # For Docker
   docker-compose restart backend
   
   # For PM2
   pm2 restart attendance-api
   ```

### Option B: Using Coolify

1. Open Coolify dashboard
2. Navigate to your application
3. Open the terminal/console
4. Run:
   ```bash
   cd /app
   python run_migrations.py
   ```
5. Restart the application from Coolify dashboard

### Option C: Direct Database Access

If you have direct database access, run this SQL:

```sql
-- Add employee_id column
ALTER TABLE salary_structures 
ADD COLUMN employee_id VARCHAR;

-- Add foreign key constraint
ALTER TABLE salary_structures 
ADD CONSTRAINT fk_salary_employee 
FOREIGN KEY (employee_id) REFERENCES employees(id);

-- Add unique constraint
ALTER TABLE salary_structures 
ADD CONSTRAINT unique_employee_salary 
UNIQUE (employee_id);
```

### Option D: Use the Fix Endpoint

Access the built-in fix endpoint:
```
https://api.t3sol.in/api/v1/fix-salary-schema
```

## Integrating into Deployment Process

### For Docker Deployments

Add to your `Dockerfile` or `docker-compose.yml`:

```dockerfile
# In Dockerfile, after copying files
RUN python run_migrations.py || true
```

Or create a startup script:

```bash
#!/bin/bash
# startup.sh

# Run migrations
python run_migrations.py

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### For Coolify

Add a pre-deployment script in Coolify settings:

```bash
cd /app
python run_migrations.py
```

### For Manual Deployments

Add to your deployment checklist:
1. Pull latest code
2. **Run migrations: `python run_migrations.py`**
3. Restart application
4. Test functionality

## Verification

After running migrations, verify the fix:

1. **Check database schema:**
   ```sql
   \d salary_structures
   ```
   
   You should see `employee_id` column listed.

2. **Test in the application:**
   - Open the Payroll Management page
   - Click "Configure" for any employee
   - Enter salary details
   - Click "Save Salary Configuration"
   - Should save successfully without errors

3. **Check logs:**
   ```bash
   tail -f backend_debug_forced.log
   ```
   
   Look for:
   ```
   [INFO] Salary structure saved successfully
   ```

## Troubleshooting

### Migration Fails with Connection Error

**Problem:** Cannot connect to database

**Solution:**
- Check DATABASE_URL in `.env` file
- Verify database credentials
- Ensure database server is running
- Check firewall rules

### Column Already Exists Error

**Problem:** `column "employee_id" already exists`

**Solution:** This is fine! The migration will skip existing columns.

### Permission Denied

**Problem:** Cannot alter table

**Solution:**
- Ensure database user has ALTER TABLE permissions
- Run as database superuser if needed

### Migration Timeout

**Problem:** Migration takes too long

**Solution:**
- Check database connection speed
- Run during low-traffic period
- Increase timeout in `run_migrations.py`

## Rollback (If Needed)

If something goes wrong, you can rollback:

```sql
-- Remove employee_id column (only if needed)
ALTER TABLE salary_structures 
DROP COLUMN IF EXISTS employee_id;

-- Remove constraints
ALTER TABLE salary_structures 
DROP CONSTRAINT IF EXISTS fk_salary_employee;

ALTER TABLE salary_structures 
DROP CONSTRAINT IF EXISTS unique_employee_salary;
```

## Support

If you encounter issues:
1. Check the migration logs
2. Verify database connectivity
3. Ensure you have proper permissions
4. Contact your database administrator if needed

---

**Last Updated:** February 8, 2026  
**Version:** 1.0
