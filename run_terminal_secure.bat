@echo off
cd frontend-terminal
echo Starting Secure HTTPS Terminal...
echo.
echo NOTE: Browser will show "Not Secure" because the certificate is self-signed.
echo Click "Advanced" -> "Proceed" to continue.
echo.
npm run dev -- --host
pause
