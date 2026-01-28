@echo off
cd backend
echo Starting Backend Server...
call venv\Scripts\activate
start cmd /k "python -m uvicorn app.main:app --reload --port 8000"

cd ..
cd frontend-admin
echo Starting Admin Panel...
start cmd /k "npm run dev"

echo System Started! 
echo Backend: http://localhost:8000/docs
echo Frontend: http://localhost:5173
