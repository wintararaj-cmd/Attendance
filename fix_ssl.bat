@echo off
cd frontend-terminal
echo Force installing SSL plugin...
call npm install @vitejs/plugin-basic-ssl --save-dev --force
if errorlevel 1 (
    echo Installation failed!
    pause
    exit /b
)
echo Installation complete. Verifying...
if exist node_modules\@vitejs\plugin-basic-ssl (
    echo Plugin found!
    echo Starting server...
    npm run dev -- --host
) else (
    echo Plugin STILL missing. Check your permissions or internet.
    pause
)
