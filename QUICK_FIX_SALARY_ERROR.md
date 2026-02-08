# Quick Fix Guide: "Failed to Save Salary" Error

## Problem
When trying to save salary configuration in the Payroll Management page, you get an error:
```
Failed to save salary
```

Backend errors:
1. **Missing Column:** `column salary_structures.employee_id does not exist`
2. **Schema Mismatch:** Extra columns (`name`, `hra_percentage`) in database that don't exist in the model

## Root Cause
1. The database table `salary_structures` is missing the `employee_id` column
2. The database has extra columns that cause SQLAlchemy to fail when trying to save

## Solution

### For Production Server (t3sol.in)

#### Option 1: SSH and Run Migration (Recommended)

1. **SSH into your server:**
   ```bash
   ssh user@your-server.com
   ```

2. **Navigate to backend:**
   ```bash
   cd /path/to/backend
   ```

3. **Run migration:**
   ```bash
   python run_migrations.py
   ```

4. **Restart application:**
   ```bash
   # If using systemd
   sudo systemctl restart attendance-api
   
   # If using Docker
   docker-compose restart backend
   
   # If using PM2
   pm2 restart all
   ```

#### Option 2: Using Coolify

1. Open Coolify dashboard
2. Go to your application
3. Open Terminal/Console
4. Run:
   ```bash
   cd /app
   python run_migrations.py
   ```
5. Restart from Coolify dashboard

#### Option 3: Direct SQL (If you have database access)

Connect to your PostgreSQL database and run:

```sql
ALTER TABLE salary_structures ADD COLUMN employee_id VARCHAR;
ALTER TABLE salary_structures ADD CONSTRAINT fk_salary_employee FOREIGN KEY (employee_id) REFERENCES employees(id);
ALTER TABLE salary_structures ADD CONSTRAINT unique_employee_salary UNIQUE (employee_id);
```

Then restart your application.

## Verification

After running the migration:

1. **Go to:** https://t3sol.in/payroll
2. **Click:** "Configure" button for any employee
3. **Enter:** Some salary values (e.g., Basic: 15000, HRA: 7500)
4. **Click:** "Save Salary Configuration"
5. **Expected:** Success message "Salary structure saved successfully!"

## Files Created

All migration scripts have been pushed to GitHub:

- ✅ `backend/run_migrations.py` - Main migration runner
- ✅ `backend/add_employee_id_column.py` - Fixes the employee_id issue
- ✅ `backend/deploy_migrate.sh` - Linux/macOS deployment script
- ✅ `backend/deploy_migrate.bat` - Windows deployment script
- ✅ `backend/start_production.sh` - Auto-migration startup script
- ✅ `backend/DEPLOYMENT_MIGRATION_GUIDE.md` - Detailed guide
- ✅ `backend/MIGRATION_README.md` - Migration scripts documentation

## Next Steps

1. **Pull latest code** on your production server:
   ```bash
   git pull origin main
   ```

2. **Run migrations:**
   ```bash
   python run_migrations.py
   ```

3. **Restart application**

4. **Test** the salary configuration feature

## Need Help?

See the detailed guides:
- [DEPLOYMENT_MIGRATION_GUIDE.md](./DEPLOYMENT_MIGRATION_GUIDE.md) - Complete deployment instructions
- [MIGRATION_README.md](./MIGRATION_README.md) - Migration scripts documentation

---

**Created:** February 8, 2026  
**Status:** Ready to deploy
