@echo off
cd frontend-terminal
if not exist node_modules (
    echo Installing dependencies... (This may take a minute)
    call npm install
)
echo Starting Terminal...
npm run dev -- --host
pause
