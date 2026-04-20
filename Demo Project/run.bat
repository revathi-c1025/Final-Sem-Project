@echo off
REM AI-Powered Agentic Test Automation System - Windows Startup Script
REM This script starts the web application on Windows

echo ========================================
echo AI-Powered Test Automation System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%
echo.

REM Check if requirements are installed
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully
    echo.
)

REM Create necessary directories
if not exist "generated_tests" mkdir generated_tests
if not exist "logs" mkdir logs
if not exist "reports" mkdir reports
if not exist "output" mkdir output

echo Starting web application...
echo.
echo The application will be available at: http://localhost:5001
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python app.py

pause
