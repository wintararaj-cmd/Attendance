@echo off
REM Deployment Migration Script for Windows
REM This script runs database migrations automatically during deployment

echo ============================================================
echo DEPLOYMENT MIGRATION SCRIPT
echo ============================================================
echo.

REM Check if we're in the right directory
if not exist "add_employee_id_column.py" (
    echo [ERROR] Migration script not found!
    echo Please run this script from the backend directory
    exit /b 1
)

echo [INFO] Starting database migrations...
echo.

REM Run the employee_id column migration
echo [STEP 1] Adding employee_id column to salary_structures...
python add_employee_id_column.py

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] employee_id column migration completed!
) else (
    echo [FAILED] employee_id column migration failed!
    exit /b 1
)

echo.

REM Run the comprehensive salary structure migration
echo [STEP 2] Adding comprehensive salary components...
python migrate_salary_structure.py

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Salary structure migration completed!
) else (
    echo [WARN] Salary structure migration had warnings ^(this may be expected^)
)

echo.
echo ============================================================
echo [COMPLETE] All migrations finished!
echo ============================================================
echo.
echo Next steps:
echo 1. Restart your application server
echo 2. Test the salary configuration feature
echo.

pause
