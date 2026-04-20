#!/bin/bash
# AI-Powered Agentic Test Automation System - Linux/Mac Startup Script
# This script starts the web application on Linux or Mac

echo "========================================"
echo "AI-Powered Test Automation System"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
echo ""

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3"
    exit 1
fi

# Check if requirements are installed
python3 -c "import flask" &> /dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
    echo "Dependencies installed successfully"
    echo ""
fi

# Create necessary directories
mkdir -p generated_tests logs reports output

echo "Starting web application..."
echo ""
echo "The application will be available at: http://localhost:5001"
echo "Press Ctrl+C to stop the server"
echo ""

# Start the application
python3 app.py
