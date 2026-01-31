@echo off
echo Creating default super admin user...
curl -X POST "http://localhost:8000/api/v1/auth/create-super-admin" -H "Content-Type: application/json" -d "{\"username\": \"admin\", \"password\": \"admin123\", \"secret\": \"setup-secret-123\"}"
echo.
pause
