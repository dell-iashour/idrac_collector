# Documentation Index

## Overview

This folder contains comprehensive documentation for the iDRAC Redfish Collector, covering installation, configuration, troubleshooting, and performance optimization.

## Documentation Files

### 📖 [Installation Guide](Installation_Guide.md)
Step-by-step instructions for setting up the collector in your environment.

**Topics Covered:**
- System requirements and prerequisites
- Installation procedures for different platforms
- Configuration file creation
- Initial testing and verification
- Security considerations
- Advanced installation options (Docker, systemd, scheduled tasks)

### ⚙️ [Configuration Guide](Configuration_Guide.md)
Detailed reference for configuring the collector for optimal performance and functionality.

**Topics Covered:**
- Global configuration options (config.yaml)
- Server configuration (servers.yaml)
- Server groups and credential management
- Endpoint configuration and customization
- Performance tuning parameters
- Configuration inheritance and validation
- Best practices and templates

### 🔧 [Troubleshooting Guide](Troubleshooting_Guide.md)
Comprehensive troubleshooting guide for common issues and problems.

**Topics Covered:**
- Connection and authentication issues
- SSL/TLS certificate problems
- Data collection failures
- Performance bottlenecks
- File system and permission issues
- Configuration validation errors
- Debugging techniques and logging
- Recovery procedures

### 📡 [API Reference](API_Reference.md)
Technical reference for Dell iDRAC Redfish API endpoints used by the collector.

**Topics Covered:**
- Supported Redfish endpoints
- Request/response formats
- Dell OEM extensions
- Query parameters and filtering
- Error handling and status codes
- Data types and structures
- Version compatibility
- Manual testing procedures

### ⚡ [Performance Guide](Performance_Guide.md)
Performance optimization recommendations and scaling strategies.

**Topics Covered:**
- Performance factors and bottlenecks
- Configuration optimization
- Connection and SSL optimization
- Endpoint selection and tuning
- System and network optimization
- Monitoring and metrics
- Scaling strategies
- Performance benchmarks

## Quick Reference

### Common Commands

```bash
# Test connections
python idrac_collector.py --test-connections --config config.yaml --servers servers.yaml --verbose

# Collect data
python idrac_collector.py --collect --config config.yaml --servers servers.yaml --verbose

# List packages
python idrac_collector.py --list-packages --config config.yaml

# Cleanup old data
python idrac_collector.py --cleanup --config config.yaml --days 7

# Create default configurations
python idrac_collector.py --create-config config.yaml
python idrac_collector.py --create-servers servers.yaml
```

### Configuration Templates

#### Basic Configuration
```yaml
# servers.yaml
server_groups:
  production:
    username: "root"
    password: "calvin"
    verify_ssl: false

servers:
  - host: "192.168.1.100"
    group: "production"
    name: "SERVER-001"
```

#### Performance Configuration
```yaml
# config.yaml
collection:
  parallel_collections: 10
  endpoints:
    - name: "system"
      path: "/Systems/System.Embedded.1"
      expand: true
      enabled: true
    - name: "firmware"
      path: "/UpdateService/FirmwareInventory"
      expand: true
      enabled: true

logging:
  level: "INFO"
  verbose: true
  file: "collector.log"
```

### Troubleshooting Checklist

1. **Enable verbose logging**: `--verbose --log-level DEBUG`
2. **Check network connectivity**: `telnet <iDRAC_IP> 443`
3. **Verify credentials**: Test via iDRAC web interface
4. **Check SSL certificates**: Use `verify_ssl: false` for testing
5. **Monitor logs**: `tail -f collector.log`
6. **Validate configuration**: Check YAML syntax

## Getting Started

1. **New Users**: Start with [Installation Guide](Installation_Guide.md)
2. **Configuration**: Refer to [Configuration Guide](Configuration_Guide.md)
3. **Issues**: Check [Troubleshooting Guide](Troubleshooting_Guide.md)
4. **Performance**: Optimize with [Performance Guide](Performance_Guide.md)
5. **Technical Details**: See [API Reference](API_Reference.md)

## Support Resources

### Internal Resources
- Main README.md (project root)
- Configuration files: config.yaml, servers.yaml
- Log files: collector.log
- Source code: idrac_collector.py and core/ modules

### External Resources
- [Dell iDRAC Redfish API Documentation](https://www.dell.com/support/home/en-us/drivers/articles/Drivers-Details-About-dell-emc-idrac-redfish-api)
- [DMTF Redfish Specification](https://www.dmtf.org/standards/redfish)
- [Redfish Forum](https://www.dmtf.org/standards/redfish)

### Community Support
- GitHub issues (if applicable)
- Dell support forums
- Redfish community resources

## Documentation Structure

```
Documentation/
├── README.md                    # This index file
├── Installation_Guide.md        # Setup and installation
├── Configuration_Guide.md        # Configuration reference
├── Troubleshooting_Guide.md     # Problem solving
├── API_Reference.md             # Technical API reference
└── Performance_Guide.md         # Performance optimization
```

## Contributing to Documentation

When updating documentation:

1. **Keep it current**: Update with new features and changes
2. **Be comprehensive**: Include examples and use cases
3. **Maintain consistency**: Use standard formatting and terminology
4. **Test instructions**: Verify all commands and examples work
5. **Cross-reference**: Link between related documents

## Version History

### Current Version
- Updated for Python collector with server groups
- Added parallel collection and connection pooling
- Enhanced logging and troubleshooting sections
- Performance optimization guidelines

### Previous Versions
- Basic installation and configuration
- Limited troubleshooting information
- Single-threaded collection only

## Feedback and Contributions

For documentation feedback or contributions:

1. Report issues with documentation accuracy
2. Suggest improvements and additions
3. Contribute examples and best practices
4. Help keep documentation current with features

---

**Last Updated**: 2026-05-20  
**Version**: 2.0 (Python Collector with Enhanced Features)
