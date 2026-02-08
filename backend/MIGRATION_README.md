# Database Migration Scripts

This directory contains scripts to manage database schema migrations for the Attendance & Payroll System.

## Quick Start

### Run All Migrations (Recommended)

```bash
python run_migrations.py
```

This will automatically run all migrations in the correct order.

## Available Scripts

### 1. `run_migrations.py` ⭐ **Recommended**
**Purpose:** Automated migration runner that executes all migrations in sequence  
**Platform:** Cross-platform (Windows, Linux, macOS)  
**Usage:**
```bash
python run_migrations.py
```

**Features:**
- Runs all migrations in correct order
- Colored output for easy monitoring
- Proper error handling
- Timeout protection
- Works on all platforms

---

### 2. `add_employee_id_column.py`
**Purpose:** Adds the missing `employee_id` column to `salary_structures` table  
**Critical:** Yes - Required for salary configuration to work  
**Usage:**
```bash
python add_employee_id_column.py
```

**What it does:**
- Adds `employee_id VARCHAR` column
- Creates foreign key to `employees(id)`
- Adds unique constraint
- Fixes: "column salary_structures.employee_id does not exist" error

---

### 3. `migrate_salary_structure.py`
**Purpose:** Adds comprehensive salary components (allowances, benefits, deductions)  
**Critical:** No - Adds optional columns  
**Usage:**
```bash
python migrate_salary_structure.py
```

**What it does:**
- Adds allowance columns (HRA, Conveyance, Medical, Education, Other)
- Adds deduction columns (PF, ESI, TDS)
- Adds benefit columns (Bonus, Incentive)
- Adds calculation settings (is_pf_applicable, is_esi_applicable)
- Adds timestamps (created_at, updated_at)

---

### 4. `deploy_migrate.sh` (Linux/macOS)
**Purpose:** Bash script to run all migrations  
**Platform:** Linux, macOS  
**Usage:**
```bash
chmod +x deploy_migrate.sh
./deploy_migrate.sh
```

---

### 5. `deploy_migrate.bat` (Windows)
**Purpose:** Batch script to run all migrations  
**Platform:** Windows  
**Usage:**
```cmd
deploy_migrate.bat
```

---

### 6. `start_production.sh`
**Purpose:** Production startup script with auto-migration  
**Platform:** Linux, macOS  
**Usage:**
```bash
chmod +x start_production.sh
./start_production.sh
```

**Features:**
- Runs migrations automatically on startup
- Starts the FastAPI application with uvicorn
- Ensures database is always up-to-date

---

## Migration Order

Migrations should be run in this order:

1. **add_employee_id_column.py** (Critical)
2. **migrate_salary_structure.py** (Optional)

The `run_migrations.py` script handles this automatically.

## For Production Deployment

See [DEPLOYMENT_MIGRATION_GUIDE.md](./DEPLOYMENT_MIGRATION_GUIDE.md) for detailed deployment instructions.

### Quick Production Steps

1. **SSH into production server**
2. **Navigate to backend directory**
   ```bash
   cd /path/to/backend
   ```
3. **Run migrations**
   ```bash
   python run_migrations.py
   ```
4. **Restart application**
   ```bash
   # Systemd
   sudo systemctl restart attendance-api
   
   # Docker
   docker-compose restart backend
   
   # PM2
   pm2 restart attendance-api
   ```

## Troubleshooting

### "Migration script not found"
**Solution:** Run the script from the `backend` directory

### "Connection refused" or "Authentication failed"
**Solution:** Check your `.env` file for correct DATABASE_URL

### "Column already exists"
**Solution:** This is fine! The migration will skip existing columns

### "Permission denied"
**Solution:** Ensure database user has ALTER TABLE permissions

## Verification

After running migrations, verify success:

```sql
-- Check if employee_id column exists
\d salary_structures

-- Should show employee_id column with foreign key constraint
```

Or test in the application:
1. Go to Payroll Management
2. Click "Configure" for any employee
3. Enter salary details
4. Click "Save" - should work without errors

## Rollback

If you need to rollback (use with caution):

```sql
ALTER TABLE salary_structures DROP COLUMN IF EXISTS employee_id;
ALTER TABLE salary_structures DROP CONSTRAINT IF EXISTS fk_salary_employee;
ALTER TABLE salary_structures DROP CONSTRAINT IF EXISTS unique_employee_salary;
```

## Support

For issues or questions:
1. Check [DEPLOYMENT_MIGRATION_GUIDE.md](./DEPLOYMENT_MIGRATION_GUIDE.md)
2. Review migration logs
3. Verify database connectivity
4. Check application logs

---

**Last Updated:** February 8, 2026  
**Maintained by:** Development Team
