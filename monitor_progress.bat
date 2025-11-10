@echo off
title Test Progress Monitor
echo ================================================================================
echo Test Progress Monitor
echo ================================================================================
echo.
echo This will check progress every 30 seconds
echo Press Ctrl+C to stop monitoring
echo.
pause

:loop
cls
echo ================================================================================
echo Test Progress Monitor - %date% %time%
echo ================================================================================
echo.

cd /d "%~dp0host"
python check_progress.py

echo.
echo Refreshing in 30 seconds... (Press Ctrl+C to stop)
timeout /t 30 /nobreak >nul

goto loop
