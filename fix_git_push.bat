@echo off
echo Syncing with remote repository...
git pull origin main --allow-unrelated-histories

echo Pushing changes...
git push -u origin main
if %errorlevel% neq 0 (
    echo.
    echo Push failed. You might have merge conflicts.
    echo Please resolve them manually or force push if you are sure.
    echo To force push (DANGEROUS: overwrites remote): git push -u origin main --force
)
pause
