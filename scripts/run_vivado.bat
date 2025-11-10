@echo off
REM Wrapper script to run Vivado with proper environment setup

REM Set up Vivado environment
call "D:\ashwin_shit\2025.1\Vivado\settings64.bat"

REM Run Vivado with provided arguments
"D:\ashwin_shit\2025.1\Vivado\bin\vivado.bat" %*
