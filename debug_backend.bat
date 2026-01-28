@echo off
cd backend
echo Starting backend... > ..\backend_debug.log
call venv\Scripts\activate >> ..\backend_debug.log 2>&1
echo Venv activated. >> ..\backend_debug.log
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 >> ..\backend_debug.log 2>&1
