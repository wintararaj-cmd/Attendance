# Coolify Deployment Guide - Enhanced Payroll System

## Overview

This guide covers deploying the Attendance System with enhanced payroll features (part-time/contract workers and OT support) to Coolify.

## Prerequisites

- Coolify instance running
- PostgreSQL database configured
- GitHub repository connected to Coolify

## Deployment Steps

### 1. Environment Variables

Set these environment variables in Coolify:

```env
# Database
DATABASE_URL=postgresql://username:password@postgres-host:5432/attendance_db

# JWT Secret (generate a secure random string)
SECRET_KEY=your-super-secret-jwt-key-here

# Optional: Face Recognition Mode
FORCE_MOCK_MODE=true  # Set to false for real face recognition
```

### 2. Database Configuration

The Dockerfile now includes automatic database setup with 4 stages:

**Stage 1: Database Initialization**
- Creates all tables from SQLAlchemy models
- Runs `init_database.py`

**Stage 2: Legacy Migrations**
- Runs existing migration scripts for backward compatibility
- Includes: `migrate_db.py`, `fix_id_column_type.py`, etc.

**Stage 3: Payroll Enhancements** ⭐ NEW
- Adds part-time/contract worker support
- Adds OT tracking fields
- Runs `migrate_payroll_enhancements.py`

**Stage 4: Start Application**
- Launches the FastAPI server on port 8000

### 3. Dockerfile Changes

The updated Dockerfile now includes:

```dockerfile
# Startup sequence:
1. python init_database.py           # Create all tables
2. python migrate_db.py              # Legacy migrations
3. python migrate_payroll_enhancements.py  # NEW: Payroll features
4. uvicorn app.main:app              # Start server
```

### 4. Deploy to Coolify

#### Option A: Via Coolify UI

1. **Go to your Coolify project**
2. **Select the backend service**
3. **Trigger a new deployment**:
   - Click "Deploy" or "Redeploy"
   - Coolify will pull latest code and rebuild

#### Option B: Via Git Push

```bash
# Commit the changes
git add backend/Dockerfile
git add backend/init_database.py
git add backend/migrate_payroll_enhancements.py
git commit -m "Add payroll enhancements migration to deployment"

# Push to trigger auto-deployment
git push origin main
```

### 5. Verify Deployment

After deployment, check the logs in Coolify:

**Expected Output:**
```
============================================================
DATABASE SETUP - Attendance System
============================================================

[1/4] Initializing database (creating tables)...
[OK] Using app database configuration
============================================================
DATABASE INITIALIZATION
============================================================
Database: your-db-host:5432/attendance_db
[1/3] Dropping existing tables (if any)...
   [OK] Existing tables dropped
[2/3] Creating all tables from models...
   [OK] All tables created successfully
[3/3] Verifying table creation...
   [OK] admin_users: 5 columns
   [OK] companies: 4 columns
   [OK] departments: 8 columns
   [OK] employees: 16 columns
   [OK] attendance_logs: 11 columns
   [OK] salary_structures: 27 columns

[2/4] Running legacy migrations...
[WARN] Legacy migration had warnings...

[3/4] Applying payroll enhancements (part-time/contract/OT support)...
Starting migration: Add Part-time/Contract Worker & OT Support...
Database: your-db-host:5432/attendance_db

Step 1: Adding columns to salary_structures table...
   [OK] Added column: is_hourly_based
   [OK] Added column: hourly_rate
   [OK] Added column: contract_rate_per_day
   [OK] Added column: ot_rate_multiplier
   [OK] Added column: ot_weekend_multiplier
   [OK] Added column: ot_holiday_multiplier

Step 2: Adding OT tracking columns to attendance_logs table...
   [OK] Added column: ot_hours
   [OK] Added column: ot_weekend_hours
   [OK] Added column: ot_holiday_hours
   [OK] Added column: total_hours_worked

[SUCCESS] Migration completed successfully!

[4/4] Starting application server...
============================================================
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. Post-Deployment Verification

**Test the API endpoints:**

```bash
# Check health
curl https://your-app.coolify.app/health

# Get employee payroll (should include new fields)
curl https://your-app.coolify.app/api/v1/payroll/employee/{emp_id}

# Configure salary with new fields
curl -X POST https://your-app.coolify.app/api/v1/employees/{emp_id}/salary \
  -H "Content-Type: application/json" \
  -d '{
    "is_hourly_based": true,
    "hourly_rate": 200,
    "ot_rate_multiplier": 1.5,
    "ot_weekend_multiplier": 2.0,
    "ot_holiday_multiplier": 2.5
  }'
```

## Troubleshooting

### Issue: "Table already exists" errors

**Solution:** This is normal on redeployments. The migrations are idempotent and will skip existing tables/columns.

### Issue: "Connection refused" to database

**Solution:** 
1. Check DATABASE_URL in Coolify environment variables
2. Ensure PostgreSQL service is running
3. Verify network connectivity between services

### Issue: Migration warnings appear

**Solution:** Warnings are expected if:
- Tables already exist (init_database.py)
- Columns already exist (migrate_payroll_enhancements.py)
- Legacy migrations run on already-migrated database

The application will start successfully despite warnings.

### Issue: "No module named 'psycopg2'"

**Solution:** This shouldn't happen as `psycopg2-binary` is in requirements.txt. If it does:
1. Check requirements.txt is being copied correctly
2. Verify Docker build logs
3. Rebuild the container

## Rollback Plan

If deployment fails:

1. **Revert to previous deployment** in Coolify UI
2. **Or restore database** from backup:
   ```bash
   # Restore from backup
   pg_restore -d attendance_db backup.sql
   ```

## Database Backup Recommendation

Before deploying to production:

```bash
# Backup your database
pg_dump -h localhost -U postgres attendance_db > backup_before_payroll_enhancements.sql
```

## Features After Deployment

✅ **Part-time Workers**
- Hourly-based salary calculation
- Configurable hourly rates

✅ **Contract Workers**
- Daily rate salary calculation
- Configurable daily rates

✅ **Overtime Tracking**
- Weekday OT (1.5x multiplier)
- Weekend OT (2.0x multiplier)
- Holiday OT (2.5x multiplier)

✅ **Flexible Payroll**
- Employee type-based calculations
- PF/ESI rules adjusted per type
- Comprehensive payslip breakdown

## Monitoring

**Check application logs:**
```bash
# In Coolify, view logs for:
- Database initialization success
- Migration completion
- Server startup
- API request handling
```

**Monitor database:**
```sql
-- Check new columns exist
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'salary_structures' 
  AND column_name IN ('is_hourly_based', 'hourly_rate', 'contract_rate_per_day');

-- Check attendance OT columns
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'attendance_logs' 
  AND column_name IN ('ot_hours', 'ot_weekend_hours', 'ot_holiday_hours');
```

## Support

For issues during deployment:
- Check Coolify logs
- Review `PAYROLL_ENHANCEMENTS.md` for feature documentation
- Review `DATABASE_SETUP_GUIDE.md` for local setup
- Check `backend/migrate_payroll_enhancements.py` for migration details

---

**Deployment Checklist:**
- [ ] Environment variables set in Coolify
- [ ] Database backup created
- [ ] Code pushed to repository
- [ ] Deployment triggered
- [ ] Logs reviewed for success
- [ ] API endpoints tested
- [ ] New features verified

**Ready to deploy!** 🚀
