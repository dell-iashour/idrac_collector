# Installation Guide

## Overview

This guide provides step-by-step instructions for setting up the iDRAC Redfish Collector in your environment.

## Prerequisites

### System Requirements

- **Operating System**: Windows 10+, Linux, or macOS
- **Python**: Version 3.7 or higher
- **Network**: TCP/443 access to Dell iDRAC interfaces
- **Storage**: Sufficient disk space for collected data (typically 1-10 MB per server)

### Network Requirements

- Firewall rules allowing outbound HTTPS (port 443) to iDRAC IPs
- DNS resolution for iDRAC hostnames (if using hostnames)
- Network latency under 500ms recommended for optimal performance

### iDRAC Requirements

- Dell servers with iDRAC 7/8/9 firmware
- Redfish API enabled (default on modern iDRAC versions)
- Valid iDRAC user account with appropriate permissions
- For self-signed certificates: SSL verification can be disabled

## Installation Steps

### 1. Download the Collector

```bash
# Extract the collector package to your desired location
# Example: C:\tools\idrac_collector or /opt/idrac_collector
```

### 2. Verify Python Installation

```bash
# Check Python version
python --version
# Should show Python 3.7.x or higher

# If Python is not installed, install from:
# - Windows: https://python.org/downloads/
# - Linux: sudo apt install python3 python3-pip
# - macOS: brew install python3
```

### 3. Verify Collector Functionality

```bash
# Navigate to collector directory
cd idrac_collector

# Test basic functionality
python idrac_collector.py --help

# Should display command line options
```

### 4. Create Initial Configuration

```bash
# Create default configuration files
python idrac_collector.py --create-config config.yaml
python idrac_collector.py --create-servers servers.yaml
```

### 5. Configure Server Access

Edit `servers.yaml` with your iDRAC server information:

```yaml
server_groups:
  production:
    username: "root"
    password: "calvin"
    verify_ssl: false
    timeout: 30

servers:
  - host: "192.168.1.100"
    port: 443
    group: "production"
    name: "SERVER-001"
```

### 6. Test Connections

```bash
# Test connectivity to your servers
python idrac_collector.py --test-connections --config config.yaml --servers servers.yaml --verbose
```

### 7. Run First Collection

```bash
# Collect data from all configured servers
python idrac_collector.py --collect --config config.yaml --servers servers.yaml --verbose
```

## Configuration Options

### File Locations

- **Main Script**: `idrac_collector.py`
- **Configuration**: `config.yaml`
- **Server List**: `servers.yaml`
- **Log File**: `collector.log` (in current directory)
- **Output**: `output/` folder (configurable)

### Directory Structure

```
idrac_collector/
├── idrac_collector.py          # Main collector script
├── config.yaml                 # Collection configuration
├── servers.yaml                # Server definitions
├── collector.log               # Detailed logs (created automatically)
├── output/                     # Collected data packages
└── Documentation/              # This guide and other documentation
```

## Security Considerations

### Credential Management

- Store configuration files in secure location
- Use service accounts with minimal required permissions
- Consider using environment variables for sensitive data
- Rotate credentials regularly

### SSL/TLS Configuration

- **Production**: Use valid certificates and enable SSL verification
- **Development**: Can disable SSL verification for self-signed certificates
- **Network**: Ensure iDRAC interfaces are accessible on required ports

### File Permissions

- Restrict access to configuration files containing credentials
- Set appropriate permissions on output directories
- Consider encrypting collected data packages

## Troubleshooting Installation

### Common Issues

#### Python Version Issues
```bash
# Error: Python version too old
# Solution: Install Python 3.7+ or use python3 command instead of python
python3 idrac_collector.py --help
```

#### Permission Errors
```bash
# Error: Permission denied when creating files
# Solution: Run with appropriate permissions or change output directory
python idrac_collector.py --output /tmp/idrac_output --collect
```

#### Network Connectivity
```bash
# Error: Connection timeout
# Solution: Check network connectivity and firewall rules
telnet 192.168.1.100 443
```

#### SSL Certificate Errors
```bash
# Error: SSL certificate verification failed
# Solution: Disable SSL verification for testing (not recommended for production)
# Add verify_ssl: false to server configuration
```

### Verification Steps

1. **Python Installation**: `python --version`
2. **Collector Help**: `python idrac_collector.py --help`
3. **Configuration Files**: Verify `config.yaml` and `servers.yaml` exist
4. **Network Access**: Test connectivity to iDRAC interfaces
5. **Authentication**: Verify iDRAC credentials work manually

## Advanced Installation

### Systemd Service (Linux)

Create `/etc/systemd/system/idrac-collector.service`:

```ini
[Unit]
Description=iDRAC Redfish Collector
After=network.target

[Service]
Type=oneshot
User=idrac-collector
WorkingDirectory=/opt/idrac_collector
ExecStart=/usr/bin/python3 /opt/idrac_collector/idrac_collector.py --collect
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable idrac-collector.service
sudo systemctl start idrac-collector.service
```

### Windows Scheduled Task

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., daily at 2 AM)
4. Action: Start program
   - Program: `python`
   - Arguments: `idrac_collector.py --collect --config config.yaml --servers servers.yaml`
   - Start in: Path to collector directory

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .
RUN pip install --no-deps -r requirements.txt 2>/dev/null || true

CMD ["python", "idrac_collector.py", "--collect"]
```

Build and run:
```bash
docker build -t idrac-collector .
docker run -v $(pwd)/config.yaml:/app/config.yaml -v $(pwd)/servers.yaml:/app/servers.yaml -v $(pwd)/output:/app/output idrac-collector
```

## Next Steps

After successful installation:

1. Review the [Configuration Guide](Configuration_Guide.md) for detailed configuration options
2. Check the [Troubleshooting Guide](Troubleshooting_Guide.md) for common issues
3. Review the [Performance Guide](Performance_Guide.md) for optimization tips
4. Set up automated collection using scheduled tasks or cron jobs
