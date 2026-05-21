# Configuration Guide

## Overview

This guide provides comprehensive documentation for configuring the iDRAC Redfish Collector. The collector uses YAML-based configuration files for maximum flexibility and maintainability.

## Configuration Files

The collector uses two main configuration files:

- **`config.yaml`** - Collection endpoints, performance settings, and global options
- **`servers.yaml`** - Server definitions, credentials, and connection settings

## Global Configuration (config.yaml)

### Collection Endpoints

```yaml
collection:
  endpoints:
    - name: "system"
      path: "/Systems/System.Embedded.1"
      expand: true
      levels: 1
      enabled: true
      description: "System information including service tag, model, firmware"
      timeout: 30
      retry_attempts: 3
    
    - name: "memory"
      path: "/Systems/System.Embedded.1/Memory"
      expand: true
      levels: 1
      enabled: true
      description: "Memory modules information"
      timeout: 30
      retry_attempts: 3
    
    - name: "storage"
      path: "/Systems/System.Embedded.1/Storage"
      expand: true
      levels: 1
      enabled: true
      description: "Storage controllers and disks"
      timeout: 45
      retry_attempts: 3
    
    - name: "network"
      path: "/Systems/System.Embedded.1/EthernetInterfaces"
      expand: true
      levels: 1
      enabled: true
      description: "Network interface cards and configuration"
      timeout: 30
      retry_attempts: 3
    
    - name: "firmware"
      path: "/UpdateService/FirmwareInventory"
      expand: true
      levels: 1
      enabled: true
      description: "Firmware inventory and versions"
      timeout: 45
      retry_attempts: 3
```

#### Endpoint Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | required | Unique identifier for the endpoint |
| `path` | string | required | Redfish API path |
| `expand` | boolean | false | Enable `$expand` parameter |
| `levels` | integer | 1 | Expansion levels for `$expand` |
| `enabled` | boolean | true | Enable/disable endpoint collection |
| `description` | string | optional | Human-readable description |
| `timeout` | integer | 30 | Request timeout in seconds |
| `retry_attempts` | integer | 3 | Number of retry attempts |
| `filter_query` | string | optional | OData filter query |

### Performance Settings

```yaml
collection:
  parallel_collections: 5        # Number of concurrent collection threads
  collection_timeout: 300        # Overall collection timeout in seconds
  
  # Folder configuration
  temp_folder: "temp"            # Temporary file location
  output_folder: "output"         # Final package location
  compression: true               # Enable ZIP compression
  naming_format: "{service_tag}_{timestamp}.zip"  # Package naming
  
  # Retry configuration
  retry:
    max_attempts: 3              # Maximum retry attempts
    delay: 5                     # Initial retry delay in seconds
    backoff_factor: 2            # Exponential backoff multiplier
```

#### Performance Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `parallel_collections` | integer | 5 | Concurrent collection threads |
| `collection_timeout` | integer | 300 | Overall timeout in seconds |
| `temp_folder` | string | "temp" | Temporary directory |
| `output_folder` | string | "output" | Output directory |
| `compression` | boolean | true | Enable ZIP compression |
| `naming_format` | string | "{service_tag}_{timestamp}.zip" | Package naming pattern |
| `retry.max_attempts` | integer | 3 | Global retry attempts |
| `retry.delay` | integer | 5 | Initial retry delay |
| `retry.backoff_factor` | integer | 2 | Backoff multiplier |

### Logging Configuration

```yaml
logging:
  level: "INFO"                 # Logging level (DEBUG, INFO, WARNING, ERROR)
  file: "collector.log"          # Log file path
  verbose: true                  # Enable verbose logging
```

#### Logging Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | string | "INFO" | Logging level |
| `file` | string | "collector.log" | Log file path |
| `verbose` | boolean | false | Enable detailed logging |

## Server Configuration (servers.yaml)

### Server Groups

Server groups allow you to define shared credentials and settings:

```yaml
server_groups:
  production:
    username: "root"
    password: "calvin"
    verify_ssl: false
    timeout: 30
    base_path: "/redfish/v1"
  
  staging:
    username: "admin"
    password: "staging123"
    verify_ssl: true
    timeout: 45
    base_path: "/redfish/v1"
  
  development:
    username: "devadmin"
    password: "devpass"
    verify_ssl: false
    timeout: 20
    base_path: "/redfish/v1"
```

#### Server Group Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `username` | string | required | iDRAC username |
| `password` | string | required | iDRAC password |
| `verify_ssl` | boolean | true | SSL certificate verification |
| `timeout` | integer | 30 | Request timeout in seconds |
| `base_path` | string | "/redfish/v1" | Redfish base path |

### Individual Servers

```yaml
servers:
  # Server using group credentials
  - host: "100.104.55.247"
    port: 443
    group: "production"
    name: "PROD-SRV-1"
  
  # Server with individual credentials
  - host: "100.104.55.250"
    port: 443
    username: "admin"
    password: "password"
    verify_ssl: false
    timeout: 30
    name: "PROD-SRV-2"
  
  # Server with group override
  - host: "192.168.1.100"
    port: 443
    group: "production"
    timeout: 60              # Override group timeout
    name: "TEST-SRV"
```

#### Server Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | string | required | iDRAC IP address or hostname |
| `port` | integer | 443 | iDRAC port |
| `group` | string | optional | Server group name |
| `username` | string | optional | Override group username |
| `password` | string | optional | Override group password |
| `verify_ssl` | boolean | optional | Override group SSL setting |
| `timeout` | integer | optional | Override group timeout |
| `base_path` | string | optional | Override group base path |
| `name` | string | optional | Friendly server name |

## Configuration Inheritance

The collector uses a hierarchical configuration system:

1. **Default Values** - Built-in defaults
2. **Server Group Settings** - Group-level configuration
3. **Individual Server Settings** - Server-specific overrides

### Inheritance Rules

- Individual server settings override group settings
- Group settings override defaults
- Missing settings are inherited from parent level
- SSL verification from group is always applied if server belongs to group

### Example Inheritance

```yaml
server_groups:
  production:
    username: "root"
    password: "calvin"
    verify_ssl: false
    timeout: 30

servers:
  - host: "192.168.1.100"
    group: "production"
    # Inherits: username=root, password=calvin, verify_ssl=false, timeout=30
  
  - host: "192.168.1.101"
    group: "production"
    timeout: 60
    # Inherits: username=root, password=calvin, verify_ssl=false
    # Overrides: timeout=60
```

## Advanced Configuration

### Custom Endpoints

Add custom Redfish endpoints:

```yaml
collection:
  endpoints:
    - name: "custom_power"
      path: "/Systems/System.Embedded.1/Power"
      expand: true
      levels: 2
      enabled: true
      description: "Power consumption and metrics"
      timeout: 30
      retry_attempts: 3
      filter_query: "PowerMetrics/ConsumedWatts gt 100"
```

### Environment Variables

Use environment variables for sensitive data:

```yaml
# servers.yaml
server_groups:
  production:
    username: "${IDRAC_USER}"
    password: "${IDRAC_PASSWORD}"
    verify_ssl: false
```

Set environment variables:
```bash
export IDRAC_USER="root"
export IDRAC_PASSWORD="calvin"
python idrac_collector.py --collect
```

### Conditional Collection

Enable/disable endpoints based on conditions:

```yaml
collection:
  endpoints:
    - name: "logs"
      path: "/Managers/iDRAC.Embedded.1/LogServices/Lclog/Entries"
      enabled: "${COLLECT_LOGS}"  # Set to "true" to enable
      description: "iDRAC logs"
```

## Configuration Validation

The collector validates configuration before execution:

### Required Fields

- Server `host` is mandatory
- Either `group` or both `username` and `password` must be specified
- Endpoint `name` and `path` are required

### Validation Rules

- Port must be between 1 and 65535
- Timeout must be positive integer
- Log level must be one of: DEBUG, INFO, WARNING, ERROR
- File paths must be accessible

### Validation Errors

Common validation errors and solutions:

```bash
# Error: Server host is required
# Solution: Add host field to server configuration

# Error: Server '192.168.1.100' username is required
# Solution: Add username or specify group

# Error: Endpoint 'system' path is required
# Solution: Add path field to endpoint configuration
```

## Best Practices

### Security

1. **Use Server Groups** - Centralize credential management
2. **Environment Variables** - Store sensitive data in environment variables
3. **File Permissions** - Restrict access to configuration files
4. **SSL Verification** - Enable SSL verification in production

### Performance

1. **Parallel Collections** - Adjust based on network capacity
2. **Timeout Settings** - Set appropriate timeouts for your environment
3. **Endpoint Selection** - Disable unused endpoints to improve speed
4. **Retry Logic** - Configure retry attempts for reliability

### Maintainability

1. **Descriptive Names** - Use meaningful server and endpoint names
2. **Comments** - Add comments to complex configurations
3. **Version Control** - Track configuration changes
4. **Documentation** - Keep configuration documentation updated

## Troubleshooting Configuration

### Common Issues

#### SSL Certificate Errors
```yaml
# Solution: Disable SSL verification for self-signed certificates
server_groups:
  production:
    verify_ssl: false
```

#### Connection Timeouts
```yaml
# Solution: Increase timeout values
server_groups:
  production:
    timeout: 60
```

#### Authentication Failures
```yaml
# Solution: Verify credentials and enable verbose logging
logging:
  verbose: true
  level: "DEBUG"
```

### Debug Configuration

Enable debug logging to troubleshoot configuration issues:

```bash
python idrac_collector.py --test-connections --verbose --log-level DEBUG
```

Check log file for detailed configuration parsing:

```bash
tail -f collector.log | grep "config_manager"
```

## Configuration Templates

### Small Environment Template

```yaml
# config.yaml
collection:
  endpoints:
    - name: "system"
      path: "/Systems/System.Embedded.1"
      expand: true
      enabled: true
    - name: "firmware"
      path: "/UpdateService/FirmwareInventory"
      expand: true
      enabled: true
  parallel_collections: 2
  temp_folder: "temp"
  output_folder: "output"
logging:
  level: "INFO"
  verbose: false
```

### Large Enterprise Template

```yaml
# config.yaml
collection:
  endpoints:
    - name: "system"
      path: "/Systems/System.Embedded.1"
      expand: true
      enabled: true
      timeout: 30
    - name: "memory"
      path: "/Systems/System.Embedded.1/Memory"
      expand: true
      enabled: true
      timeout: 30
    - name: "storage"
      path: "/Systems/System.Embedded.1/Storage"
      expand: true
      enabled: true
      timeout: 45
    - name: "network"
      path: "/Systems/System.Embedded.1/EthernetInterfaces"
      expand: true
      enabled: true
      timeout: 30
    - name: "firmware"
      path: "/UpdateService/FirmwareInventory"
      expand: true
      enabled: true
      timeout: 45
  parallel_collections: 10
  collection_timeout: 600
  retry:
    max_attempts: 5
    delay: 10
    backoff_factor: 2
logging:
  level: "INFO"
  file: "/var/log/idrac_collector.log"
  verbose: true
```

## Next Steps

After configuring the collector:

1. Test connections with `--test-connections`
2. Verify configuration with `--verbose` logging
3. Monitor performance and adjust settings as needed
4. Set up automated collection schedules
5. Review the [Performance Guide](Performance_Guide.md) for optimization tips
