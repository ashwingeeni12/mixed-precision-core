@echo off
echo ================================================================================
echo Generate Comprehensive Excel Report
echo ================================================================================
echo.
echo This will create a comprehensive Excel report from test results
echo Input:  results\comprehensive_results.csv
echo Output: results\comprehensive_analysis.xlsx
echo.
pause

cd /d "%~dp0host"

if not exist "..\results\comprehensive_results.csv" (
    echo ERROR: No results file found!
    echo Please run tests first: run_all_tests.bat
    pause
    exit /b 1
)

echo.
echo Generating Excel report...
python create_excel_report.py

if errorlevel 1 (
    echo ERROR: Report generation failed!
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo SUCCESS! Excel report created.
echo.
echo Location: results\comprehensive_analysis.xlsx
echo.
echo Opening Excel file...
start "" "..\results\comprehensive_analysis.xlsx"
echo.
echo ================================================================================
pause
