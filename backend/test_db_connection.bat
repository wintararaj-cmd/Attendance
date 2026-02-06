@echo off
cd /d %~dp0
echo Testing PostgreSQL Connection...
call venv\Scripts\activate
python check_postgres.py
pause
