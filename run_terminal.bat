@echo off
cd frontend-terminal
echo Starting Attendance Terminal (Accessible on Network)...
echo Please ensure your mobile is on the same Wi-Fi.
echo Check the IP address below (e.g., http://192.168.x.x:5174)
start cmd /k "npm run dev -- --host"
