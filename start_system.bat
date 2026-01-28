@echo off
echo Starting Backend...
start "Attendance Backend" cmd /k "cd backend && call venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Admin Frontend...
start "Attendance Admin" cmd /k "cd frontend-admin && npm run dev"

echo Starting Terminal Frontend...
start "Attendance Terminal" cmd /k "cd frontend-terminal && npm run dev -- --host"

echo System launching...
echo ---------------------------------------------------
echo Admin Panel:    http://localhost:5173
echo Terminal App:   http://localhost:5174  (Use Network IP for Mobile)
echo Backend API:    http://localhost:8000/docs
echo ---------------------------------------------------
pause
