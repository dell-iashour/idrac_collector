@echo off
REM iDRAC Redfish Collector - Windows Batch Script
REM This script provides an easy way to run the collector on Windows

echo iDRAC Redfish Collector
echo ========================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if config file exists
if not exist "config.yaml" (
    echo Creating default configuration file...
    python idrac_collector.py --create-config config.yaml
    if errorlevel 1 (
        echo Error: Failed to create configuration file
        pause
        exit /b 1
    )
)

REM Check if servers file exists
if not exist "servers.yaml" (
    echo Creating default servers file...
    python idrac_collector.py --create-servers servers.yaml
    if errorlevel 1 (
        echo Error: Failed to create servers file
        pause
        exit /b 1
    )
    echo.
    echo Please edit servers.yaml with your server information
    echo Then run this script again
    pause
    exit /b 0
)

REM Run the collector
echo Starting data collection...
python idrac_collector.py --config config.yaml --servers servers.yaml --collect

if errorlevel 1 (
    echo.
    echo Collection completed with errors
) else (
    echo.
    echo Collection completed successfully
)

echo.
echo Check the 'output' folder for collected data packages
pause
