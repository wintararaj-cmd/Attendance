@echo off
echo Cleaning up huge Git history...

REM Removing the old git repo completely to flush big files from history
rd /s /q .git

echo Re-initializing Git...
git init

echo Adding files (excluding ignored ones)...
git add .

echo Committing...
git commit -m "Fresh commit: Complete Attendance System"

echo Renaming branch...
git branch -M main

echo Adding remote...
git remote add origin https://github.com/wintararaj-cmd/Attendance.git

echo Uploading (Force Push) to GitHub...
git push -u origin main --force

echo Done!
pause
