@echo off
cd /d %~dp0
echo Running Database Migration...
call venv\Scripts\activate
python migrate_db.py
if %ERRORLEVEL% EQU 0 (
    echo Migration Successful!
) else (
    echo Migration Failed!
)
pause
