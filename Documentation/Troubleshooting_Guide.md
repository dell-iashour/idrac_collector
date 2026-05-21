# Troubleshooting Guide

## Overview

This guide provides solutions to common issues encountered when using the iDRAC Redfish Collector. Issues are categorized by type and severity, with step-by-step resolution procedures.

## Quick Diagnosis

### Enable Verbose Logging

For most troubleshooting scenarios, enable verbose logging:

```bash
python idrac_collector.py --test-connections --verbose --log-level DEBUG
```

Check the log file for detailed error information:
```bash
tail -f collector.log
```

### Common Error Patterns

- **Authentication failures** - Check credentials and permissions
- **SSL/TLS errors** - Verify certificate settings
- **Network connectivity** - Test network access to iDRAC
- **Timeout issues** - Adjust timeout values
- **Permission errors** - Verify file system permissions

## Connection Issues

### SSL Certificate Verification Failed

**Error Message:**
```
Authentication failed: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate (_ssl.c:1077)>
```

**Causes:**
- iDRAC using self-signed certificates
- Certificate chain issues
- Outdated certificate authorities

**Solutions:**

#### Option 1: Disable SSL Verification (Quick Fix)
```yaml
# servers.yaml
server_groups:
  production:
    verify_ssl: false
```

#### Option 2: Use Custom Certificate Bundle
```bash
# Set environment variable for custom CA bundle
export SSL_CERT_FILE=/path/to/ca-bundle.crt
python idrac_collector.py --collect
```

#### Option 3: Import iDRAC Certificate
```bash
# Extract iDRAC certificate
openssl s_client -connect 192.168.1.100:443 -showcerts </dev/null > idrac.crt

# Add to system trust store (Linux)
sudo cp idrac.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# Add to system trust store (Windows)
certmgr.msc -> Trusted Root Certification Authorities -> Import
```

### Connection Timeout

**Error Message:**
```
Authentication failed: <urlopen error timed out>
```

**Causes:**
- Network latency
- iDRAC overload
- Firewall blocking
- Incorrect port

**Solutions:**

#### Increase Timeout Values
```yaml
# servers.yaml
server_groups:
  production:
    timeout: 60  # Increase from default 30
```

#### Test Network Connectivity
```bash
# Basic connectivity test
ping 192.168.1.100

# Port connectivity test
telnet 192.168.1.100 443
# or
nc -zv 192.168.1.100 443

# SSL connectivity test
openssl s_client -connect 192.168.1.100:443
```

#### Check Firewall Rules
```bash
# Linux
sudo iptables -L | grep 443
sudo ufw status

# Windows
netsh advfirewall firewall show rule name="iDRAC"
```

### Connection Refused

**Error Message:**
```
Authentication failed: <urlopen error [Errno 111] Connection refused>
```

**Causes:**
- iDRAC service not running
- Wrong port number
- Network blocking
- iDRAC rebooting

**Solutions:**

#### Verify iDRAC Status
- Access iDRAC web interface
- Check if iDRAC is responsive
- Verify port configuration

#### Check Port Configuration
```yaml
# servers.yaml
servers:
  - host: "192.168.1.100"
    port: 443  # Default iDRAC port
```

## Authentication Issues

### Invalid Credentials

**Error Message:**
```
Authentication failed: HTTP Error 401: Unauthorized
```

**Causes:**
- Incorrect username/password
- Account locked out
- Insufficient permissions
- Account disabled

**Solutions:**

#### Verify Credentials Manually
```bash
# Test with curl
curl -k -u root:calvin https://192.168.1.100/redfish/v1/Systems

# Test with web interface
# Access https://192.168.1.100 in browser
```

#### Check Account Status
- Log into iDRAC web interface
- Verify account is not locked
- Check account permissions
- Ensure account has Redfish API access

#### Reset iDRAC Credentials
```bash
# Through iDRAC web interface:
# Users -> Select user -> Reset password
```

### Session Management Issues

**Error Message:**
```
Authentication failed: HTTP Error 403: Forbidden
```

**Causes:**
- Session limit reached
- Concurrent sessions
- Session timeout

**Solutions:**

#### Reduce Parallel Collections
```yaml
# config.yaml
collection:
  parallel_collections: 2  # Reduce from default 5
```

#### Wait for Session Timeout
- Default iDRAC session timeout is 15-30 minutes
- Wait and retry collection

#### Restart iDRAC Service
```bash
# Through iDRAC web interface:
# iDRAC Settings -> Reset iDRAC (last resort)
```

## Data Collection Issues

### Service Tag Extraction Failed

**Symptoms:**
- Package names show "UNKNOWN_HOST" instead of service tag
- Generic package names

**Causes:**
- BIOS data not accessible
- Service tag in unexpected location
- Permission issues

**Solutions:**

#### Enable Debug Logging
```bash
python idrac_collector.py --collect --verbose --log-level DEBUG
```

Check logs for service tag extraction:
```bash
grep "service tag" collector.log
```

#### Manual Service Tag Override
```yaml
# servers.yaml
servers:
  - host: "192.168.1.100"
    name: "SERVER-ABC123"  # Override service tag
```

### Endpoint Collection Failed

**Error Message:**
```
Endpoint 'memory' collection failed: HTTP Error 404: Not Found
```

**Causes:**
- Endpoint not supported on iDRAC version
- Incorrect path
- Insufficient permissions

**Solutions:**

#### Disable Unsupported Endpoints
```yaml
# config.yaml
collection:
  endpoints:
    - name: "memory"
      enabled: false  # Disable problematic endpoint
```

#### Update Endpoint Path
```bash
# Test endpoint manually
curl -k -u root:calvin https://192.168.1.100/redfish/v1/Systems/System.Embedded.1/Memory
```

#### Check iDRAC Version Compatibility
- Verify iDRAC firmware version
- Check Redfish API version support
- Update iDRAC firmware if needed

### Incomplete Data Collection

**Symptoms:**
- Some endpoints succeed, others fail
- Partial data in packages
- Inconsistent collection results

**Causes:**
- Network instability
- iDRAC resource constraints
- Timeout issues

**Solutions:**

#### Increase Retry Attempts
```yaml
# config.yaml
collection:
  endpoints:
    - name: "system"
      retry_attempts: 5  # Increase from default 3
```

#### Adjust Timeout Values
```yaml
# config.yaml
collection:
  endpoints:
    - name: "storage"
      timeout: 60  # Increase for storage endpoints
```

#### Reduce Parallel Collections
```yaml
# config.yaml
collection:
  parallel_collections: 3  # Reduce concurrent load
```

## Performance Issues

### Slow Collection Performance

**Symptoms:**
- Collection taking longer than expected
- High resource usage
- Network bottlenecks

**Solutions:**

#### Optimize Parallel Collections
```yaml
# config.yaml
collection:
  parallel_collections: 10  # Increase for better performance
```

#### Enable Connection Reuse
```bash
# Connection reuse is enabled by default
# Monitor logs for connection reuse messages
grep "connection" collector.log
```

#### Reduce Collected Endpoints
```yaml
# config.yaml
collection:
  endpoints:
    - name: "system"
      enabled: true
    - name: "firmware"
      enabled: true
    # Disable other endpoints for faster collection
```

### Memory Usage High

**Symptoms:**
- Collector using excessive memory
- System slowdown
- Collection failures

**Solutions:**

#### Reduce Parallel Collections
```yaml
# config.yaml
collection:
  parallel_collections: 2  # Reduce memory usage
```

#### Monitor Resource Usage
```bash
# Linux
top -p $(pgrep -f idrac_collector)

# Windows
tasklist /fi "imagename eq python.exe"
```

#### Clean Up Temporary Files
```bash
# Clean up temp directory
rm -rf temp/*
```

## File System Issues

### Permission Denied

**Error Message:**
```
Error: Permission denied when creating output file
```

**Causes:**
- Insufficient file permissions
- Read-only file system
- SELinux/AppArmor restrictions

**Solutions:**

#### Check File Permissions
```bash
# Linux
ls -la output/
chmod 755 output/

# Windows
icacls output /grant Users:(OI)(CI)F
```

#### Change Output Directory
```bash
python idrac_collector.py --output /tmp/idrac_output --collect
```

#### Run with Appropriate User
```bash
# Linux
sudo -u idrac-collector python idrac_collector.py --collect

# Windows
# Run as appropriate user
```

### Disk Space Full

**Error Message:**
```
Error: No space left on device
```

**Solutions:**

#### Check Disk Space
```bash
# Linux
df -h

# Windows
dir /s | find "bytes free"
```

#### Clean Up Old Packages
```bash
# Automatic cleanup
python idrac_collector.py --cleanup --days 7

# Manual cleanup
find output/ -name "*.zip" -mtime +7 -delete
```

#### Change Output Location
```bash
python idrac_collector.py --output /path/to/larger/disk --collect
```

## Configuration Issues

### Invalid Configuration

**Error Message:**
```
Configuration validation errors:
  - Server '192.168.1.100' username is required
```

**Solutions:**

#### Validate Configuration Syntax
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
python -c "import yaml; yaml.safe_load(open('servers.yaml'))"
```

#### Use Configuration Templates
```bash
# Create fresh configuration files
python idrac_collector.py --create-config config_new.yaml
python idrac_collector.py --create-servers servers_new.yaml
```

#### Check Required Fields
```yaml
# servers.yaml - required fields
servers:
  - host: "192.168.1.100"  # Required
    # Either group or username+password required
    group: "production"
    # OR
    username: "root"
    password: "calvin"
```

### Server Group Inheritance Issues

**Symptoms:**
- Credentials not applied from groups
- SSL settings not inherited
- Timeout values not working

**Solutions:**

#### Verify Group Configuration
```yaml
# servers.yaml
server_groups:
  production:
    username: "root"
    password: "calvin"
    verify_ssl: false
    timeout: 30

servers:
  - host: "192.168.1.100"
    group: "production"  # Must match exactly
```

#### Enable Debug Logging
```bash
python idrac_collector.py --test-connections --verbose
```

Check logs for inheritance messages:
```bash
grep "Resolving server config" collector.log
```

## Logging and Debugging

### Enable Comprehensive Logging

```bash
# Full debug logging
python idrac_collector.py --collect --verbose --log-level DEBUG --log-file debug.log
```

### Log File Analysis

#### Common Log Patterns
```bash
# Authentication issues
grep "Authentication" collector.log

# Network issues
grep "timeout\|connection\|ssl" collector.log

# Service tag extraction
grep "service tag" collector.log

# Performance metrics
grep "response time\|collection" collector.log
```

#### Real-time Monitoring
```bash
# Follow log file in real-time
tail -f collector.log | grep -E "(ERROR|WARNING)"

# Filter for specific server
tail -f collector.log | grep "192.168.1.100"
```

### Network Debugging

#### Capture Network Traffic
```bash
# TCPdump (Linux)
sudo tcpdump -i any host 192.168.1.100 and port 443

# Wireshark (Windows/Graphical)
# Capture traffic on iDRAC interface
```

#### DNS Resolution
```bash
# Check DNS resolution
nslookup 192.168.1.100
dig 192.168.1.100

# Test hostname resolution
nslookup idrac-server.example.com
```

## Recovery Procedures

### Complete Reset

If all else fails, perform a complete reset:

1. **Backup Current Configuration**
```bash
cp config.yaml config_backup.yaml
cp servers.yaml servers_backup.yaml
```

2. **Create Fresh Configuration**
```bash
python idrac_collector.py --create-config config_fresh.yaml
python idrac_collector.py --create-servers servers_fresh.yaml
```

3. **Test with Minimal Configuration**
```yaml
# servers_fresh.yaml
servers:
  - host: "192.168.1.100"
    username: "root"
    password: "calvin"
    verify_ssl: false
```

4. **Gradually Add Features**
- Add server groups
- Enable additional endpoints
- Adjust performance settings

### iDRAC Recovery

If iDRAC is unresponsive:

1. **Check iDRAC Status**
   - Access web interface
   - Verify iDRAC is responsive
   - Check system status

2. **Restart iDRAC Service**
   - Through web interface if accessible
   - Physical restart as last resort

3. **Update iDRAC Firmware**
   - Check for firmware updates
   - Apply updates if available

## Prevention and Best Practices

### Regular Maintenance

1. **Monitor Log Files**
   - Check for error patterns
   - Review performance metrics
   - Track collection success rates

2. **Update Configurations**
   - Review server lists regularly
   - Update credentials as needed
   - Adjust performance settings

3. **Clean Up Old Data**
   - Regular cleanup of old packages
   - Monitor disk space usage
   - Archive important data

### Monitoring Setup

1. **Log Monitoring**
```bash
# Set up log rotation
logrotate -f /etc/logrotate.d/idrac_collector

# Monitor for errors
tail -f collector.log | grep -E "(ERROR|CRITICAL)"
```

2. **Performance Monitoring**
```bash
# Monitor collection times
grep "collection completed" collector.log | tail -10

# Monitor success rates
grep "successful" collector.log | tail -10
```

3. **Alert Setup**
```bash
# Create simple alert script
#!/bin/bash
if grep -q "ERROR" collector.log; then
    echo "iDRAC Collector errors detected" | mail -s "Collector Alert" admin@example.com
fi
```

## Contact Support

When to seek help:

- Persistent authentication failures
- Network connectivity issues that can't be resolved
- Performance problems after optimization
- Unexpected error messages in logs

Information to provide:

1. **Collector Version**
   - Python version
   - Operating system
   - Collector version (if applicable)

2. **Configuration Files**
   - Sanitized config.yaml
   - Sanitized servers.yaml
   - Remove sensitive credentials

3. **Log Files**
   - Recent collector.log
   - Debug logs if available
   - Error messages

4. **Environment Details**
   - iDRAC firmware version
   - Network topology
   - Number of servers
   - Collection frequency

## Related Documentation

- [Installation Guide](Installation_Guide.md)
- [Configuration Guide](Configuration_Guide.md)
- [Performance Guide](Performance_Guide.md)
- [API Reference](API_Reference.md)
