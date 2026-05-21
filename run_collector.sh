#!/bin/bash
# iDRAC Redfish Collector - Linux/Unix Shell Script
# This script provides an easy way to run the collector on Linux/Unix systems

echo "iDRAC Redfish Collector"
echo "========================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi

# Check if config file exists
if [ ! -f "config.yaml" ]; then
    echo "Creating default configuration file..."
    python3 idrac_collector.py --create-config config.yaml
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create configuration file"
        exit 1
    fi
fi

# Check if servers file exists
if [ ! -f "servers.yaml" ]; then
    echo "Creating default servers file..."
    python3 idrac_collector.py --create-servers servers.yaml
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create servers file"
        exit 1
    fi
    echo
    echo "Please edit servers.yaml with your server information"
    echo "Then run this script again"
    exit 0
fi

# Run the collector
echo "Starting data collection..."
python3 idrac_collector.py --config config.yaml --servers servers.yaml --collect

if [ $? -ne 0 ]; then
    echo
    echo "Collection completed with errors"
else
    echo
    echo "Collection completed successfully"
fi

echo
echo "Check the 'output' folder for collected data packages"
