@echo off
echo ================================================================================
echo Mixed-Precision Matrix Multiplication - Comprehensive Test Suite
echo ================================================================================
echo.
echo This will run 126 simulations (42 test cases x 3 precisions)
echo Estimated time: 4-10 hours
echo.

echo Setting up Vivado environment...
call "D:\ashwin_shit\2025.1\Vivado\settings64.bat" >nul 2>&1

echo.
echo Starting tests...
echo.

cd /d "%~dp0host"
python run_comprehensive_test.py

echo.
echo ================================================================================
echo Tests complete!
echo Results saved to: results\comprehensive_results.csv
echo.
echo Generate Excel report with:
echo   python host\create_excel_report.py
echo ================================================================================
echo.
pause
