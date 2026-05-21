# iDRAC Redfish Collector

A high-performance, standalone collector for Dell iDRAC Redfish API data collection with advanced features for enterprise environments.

## Overview

This collector connects to Dell iDRAC interfaces via Redfish API to collect configurable system information and package it for secure transmission. Designed for large-scale deployments with support for server groups, parallel processing, and comprehensive logging.

## Key Features

- **🚀 High Performance**: Parallel collection with configurable threading and connection pooling
- **🔧 Server Groups**: Flexible credential management with inheritance and overrides
- **📝 Comprehensive Logging**: Detailed verbose logging with file output for troubleshooting
- **🛡️ SSL Management**: Flexible SSL certificate verification with per-server configuration
- **📦 Smart Packaging**: Automatic service tag extraction and intelligent package naming
- **🔄 Connection Reuse**: Optimized TCP connection reuse for multiple requests
- **⚡ Enterprise Ready**: Built for large-scale deployments with thousands of servers
- **🔍 Debug Support**: Extensive logging and troubleshooting capabilities

## Collection Endpoints

The collector can gather data from the following Redfish endpoints:

- **System**: `/redfish/v1/Systems/System.Embedded.1?$expand=*($levels=1)`
- **Memory**: `/redfish/v1/Systems/System.Embedded.1/Memory?$expand=*($levels=1)`
- **Storage**: `/redfish/v1/Systems/System.Embedded.1/Storage?$expand=*($levels=1)`
- **Network**: `/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces?$expand=*($levels=1)`
- **Firmware**: `/redfish/v1/UpdateService/FirmwareInventory?$expand=*($levels=1)`

## Quick Start

### Prerequisites
- Python 3.7+ (uses only standard library)
- Network access to Dell iDRAC interfaces
- Appropriate credentials for iDRAC access

### Basic Usage

```bash
# Test connections
python idrac_collector.py --test-connections --config config.yaml --servers servers.yaml --verbose

# Collect data
python idrac_collector.py --collect --config config.yaml --servers servers.yaml --verbose

# List packages
python idrac_collector.py --list-packages --config config.yaml

# Cleanup old data
python idrac_collector.py --cleanup --config config.yaml --days 7
```

## Configuration

### Server Groups (servers.yaml)

```yaml
# Server groups for shared credentials
server_groups:
  production:
    username: "root"
    password: "password"
    verify_ssl: false
    timeout: 30
    base_path: "/redfish/v1"

  staging:
    username: "admin"
    password: "staging123"
    verify_ssl: true
    timeout: 45

# Server definitions
servers:
  - host: "192.168.1.247"
    port: 443
    group: "production"
    name: "PROD-SRV-1"

  - host: "192.168.1.250"
    port: 443
    group: "production"
    name: "PROD-SRV-2"

  - host: "192.168.1.100"
    port: 443
    username: "admin"
    password: "password"
    verify_ssl: false
    timeout: 30
    name: "TEST-SRV"
```

### Collection Configuration (config.yaml)

```yaml
# Collection endpoints
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

# Performance settings
  parallel_collections: 5
  collection_timeout: 300

# Folder configuration
  temp_folder: "temp"
  output_folder: "output"
  compression: true
  naming_format: "{service_tag}_{timestamp}.zip"

# Logging Configuration
logging:
  level: "INFO"
  file: "collector.log"
  verbose: true
```

## Performance Features

### Parallel Collection
- Configurable parallel processing (default: 5 threads)
- Connection pooling for optimal resource usage
- Thread-safe logging and statistics

### Connection Optimization
- TCP connection reuse for multiple requests
- SSL context optimization for self-signed certificates
- Configurable timeouts and retry logic

### Service Tag Detection
- Automatic extraction from BIOS.Attributes.SystemServiceTag
- Fallback to multiple service tag sources
- Unique package naming per server

## Command Line Options

```bash
python idrac_collector.py [OPTIONS]

Options:
  --config FILE           Configuration file (default: config.yaml)
  --servers FILE          Servers file (default: servers.yaml)
  --collect               Collect data from all servers
  --test-connections      Test connectivity to all servers
  --list-packages         List collected packages
  --cleanup DAYS          Remove packages older than DAYS
  --verbose, -v           Enable verbose logging
  --log-level LEVEL       Logging level (DEBUG, INFO, WARNING, ERROR)
  --log-file FILE         Log file path
  --output DIR            Output directory
  --temp DIR              Temporary directory
  --host HOST             Single server host
  --port PORT             Single server port (default: 443)
  --username USER         Single server username
  --password PASS         Single server password
  --no-ssl-verify         Disable SSL verification
  --create-config FILE    Create default configuration file
  --create-servers FILE   Create default servers file
```

## Output Structure

```
output/
├── DV5V8T2_20260520_202645.zip    # Server 1 package
├── 8JLW8T2_20260520_202647.zip    # Server 2 package
└── ...

temp/                              # Temporary collection files
└── collector.log                   # Detailed logging
```

Each package contains:
- `system.json` - System information
- `memory.json` - Memory configuration
- `storage.json` - Storage controllers
- `network.json` - Network interfaces
- `firmware.json` - Firmware inventory
- `collection_metadata.json` - Collection statistics

## Documentation

For detailed documentation, see the `Documentation/` folder:

- **Installation Guide** - Step-by-step setup instructions
- **Configuration Guide** - Detailed configuration options
- **Troubleshooting Guide** - Common issues and solutions
- **API Reference** - Redfish endpoint details
- **Performance Guide** - Optimization recommendations

## Requirements

- Python 3.7+
- Network access to Dell iDRAC interfaces
- Valid iDRAC credentials
- Sufficient disk space for collected data

## License

Enterprise iDRAC collection tool for authorized system administration use only.
