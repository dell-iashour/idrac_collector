#!/usr/bin/env python3
#
# idrac_collector.py - Main iDRAC Redfish Collector Application
#
# _author_ = Ibrahim Ashour <Ibrahim.Ashour@Dell.com>
# _version_ = 1.0
#
# Copyright (c) 2026, Dell, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#

"""
iDRAC Redfish Collector - Standalone Dell iDRAC data collection tool
Based on Dell iDRAC Redfish Scripting examples
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional

# Add core modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))

from core import IDRACCollector, ConfigManager, FileManager
from core.config_manager import ServerConfig, CollectionEndpoint


def setup_logging(level: str = "INFO", log_file: Optional[str] = None, verbose: bool = False):
    """Setup logging configuration
    
    Args:
        level: Logging level
        log_file: Log file path
        verbose: Verbose logging
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler - simple formatting, normal level
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler - detailed formatting, always includes debug if verbose
    if log_file:
        try:
            # Create directory if it doesn't exist
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use detailed formatter for file logging
            if verbose:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
                )
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG if verbose else log_level)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
            
        except Exception as e:
            print(f"Warning: Failed to create log file {log_file}: {e}")
    
    # Set specific logger for collector modules
    collector_logger = logging.getLogger('idrac_collector')
    collector_logger.setLevel(logging.DEBUG if verbose else log_level)
    
    # Set logging for core modules
    core_logger = logging.getLogger('core')
    core_logger.setLevel(logging.DEBUG if verbose else log_level)
    
    print(f"Logging enabled - Level: {level}")
    if log_file:
        print(f"Log file: {log_file}")
        if verbose:
            print(f"Verbose logging enabled - detailed logs in file")


def create_default_config(config_file: str) -> bool:
    """Create default configuration file
    
    Args:
        config_file: Configuration file path
        
    Returns:
        bool: True if created successfully
    """
    config_manager = ConfigManager()
    
    if config_manager.create_default_config(config_file):
        print(f"Default configuration created: {config_file}")
        return True
    else:
        print(f"Failed to create configuration file: {config_file}")
        return False


def create_default_servers(servers_file: str) -> bool:
    """Create default servers file
    
    Args:
        servers_file: Servers file path
        
    Returns:
        bool: True if created successfully
    """
    try:
        import yaml
        
        default_servers = {
            'servers': [
                {
                    'host': '192.168.1.100',
                    'port': 443,
                    'username': 'root',
                    'password': 'calvin',
                    'verify_ssl': False,
                    'timeout': 30,
                    'name': 'Server-01'
                }
            ]
        }
        
        with open(servers_file, 'w') as f:
            yaml.dump(default_servers, f, default_flow_style=False, indent=2)
        
        print(f"Default servers file created: {servers_file}")
        return True
        
    except Exception as e:
        print(f"Failed to create servers file: {e}")
        return False


def test_connections(config_manager: ConfigManager) -> bool:
    """Test connections to all servers
    
    Args:
        config_manager: Configuration manager
        
    Returns:
        bool: True if all connections successful
    """
    print("Testing server connections...")
    
    # Create collector
    file_manager = FileManager(
        temp_folder=config_manager.global_config.collection.temp_folder,
        output_folder=config_manager.global_config.collection.output_folder
    )
    
    collector = IDRACCollector(file_manager)
    
    # Test connections with resolved server configurations
    resolved_servers = config_manager.get_resolved_servers()
    results = collector.test_all_connections(resolved_servers)
    
    success_count = 0
    for host, result in results.items():
        if result.success:
            print(f"  ✓ {host}: Connected successfully")
            success_count += 1
        else:
            print(f"  ✗ {host}: {result.error}")
    
    print(f"\nConnection test results: {success_count}/{len(results)} successful")
    
    return success_count == len(results)


def collect_data(config_manager: ConfigManager, verbose: bool = False) -> bool:
    """Collect data from all configured servers
    
    Args:
        config_manager: Configuration manager
        verbose: Enable verbose logging
        
    Returns:
        bool: True if collection successful
    """
    print(f"Starting data collection from {len(config_manager.servers)} servers...")
    
    # Validate configuration
    errors = config_manager.validate_config()
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    # Create collector
    file_manager = FileManager(
        temp_folder=config_manager.global_config.collection.temp_folder,
        output_folder=config_manager.global_config.collection.output_folder
    )
    
    collector = IDRACCollector(
        file_manager,
        max_parallel=config_manager.global_config.collection.parallel_collections
    )
    
    # Get enabled endpoints
    endpoints = config_manager.get_enabled_endpoints()
    print(f"Collecting {len(endpoints)} endpoints per server")
    
    # Get resolved server configurations (with group inheritance)
    resolved_servers = config_manager.get_resolved_servers()
    
    if verbose:
        print(f"Resolved {len(resolved_servers)} server configurations:")
        for server in resolved_servers:
            print(f"  - {server.name or server.host} (group: {server.group or 'None'})")
            print(f"    Username: '{server.username}'")
            print(f"    Password: '{server.password}'")
            print(f"    SSL Verify: {server.verify_ssl}")
            print(f"    Timeout: {server.timeout}s")
            print(f"    Base Path: {server.base_path}")
            print()
    
    # Collect data
    results = collector.collect_multiple_servers(resolved_servers, endpoints)
    
    # Display results
    successful_count = 0
    failed_count = 0
    
    print("\nCollection Results:")
    print("-" * 60)
    
    for result in results:
        if result.success:
            print(f"  ✓ {result.server_host} ({result.service_tag})")
            print(f"    Endpoints: {len(result.endpoints_collected)}/{len(endpoints)}")
            print(f"    Package: {os.path.basename(result.package_path) if result.package_path else 'None'}")
            successful_count += 1
        else:
            print(f"  ✗ {result.server_host}")
            if result.errors:
                for error in result.errors[:3]:  # Show first 3 errors
                    print(f"    Error: {error}")
            failed_count += 1
        print()
    
    # Display statistics
    stats = collector.get_stats()
    print(f"Collection Summary:")
    print(f"  Servers: {successful_count} successful, {failed_count} failed")
    print(f"  Endpoints: {stats['successful_endpoints']} successful, {stats['failed_endpoints']} failed")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
    print(f"  Total data size: {stats['total_data_size_mb']:.2f} MB")
    print(f"  Average collection time: {stats['average_collection_time_ms']:.2f} ms")
    
    # Display storage stats
    storage_stats = file_manager.get_storage_stats()
    print(f"\nStorage Statistics:")
    print(f"  Output folder: {storage_stats['output_folder']['size_mb']:.2f} MB")
    print(f"  Packages created: {storage_stats['packages']['total_count']}")
    
    return successful_count > 0


def list_packages(config_manager: ConfigManager):
    """List collected packages
    
    Args:
        config_manager: Configuration manager
    """
    file_manager = FileManager(
        temp_folder=config_manager.global_config.collection.temp_folder,
        output_folder=config_manager.global_config.collection.output_folder
    )
    
    packages = file_manager.list_output_packages()
    
    if not packages:
        print("No packages found")
        return
    
    print(f"Found {len(packages)} packages:")
    print("-" * 80)
    
    for package in packages:
        size_mb = package['size_bytes'] / (1024 * 1024)
        print(f"{package['filename']}")
        print(f"  Service Tag: {package['service_tag']}")
        print(f"  Timestamp: {package['timestamp']}")
        print(f"  Size: {size_mb:.2f} MB")
        print(f"  Created: {package['created_at']}")
        print()


def cleanup_data(config_manager: ConfigParser, days: int = 30):
    """Clean up old data
    
    Args:
        config_manager: Configuration manager
        days: Age in days
    """
    file_manager = FileManager(
        temp_folder=config_manager.global_config.collection.temp_folder,
        output_folder=config_manager.global_config.collection.output_folder
    )
    
    # Clean up temp data
    temp_cleaned = file_manager.cleanup_all_temp_data()
    print(f"Cleaned up {temp_cleaned} temporary folders")
    
    # Clean up old packages
    packages_deleted = file_manager.cleanup_old_packages(days)
    print(f"Deleted {packages_deleted} packages older than {days} days")
    
    # Display storage stats
    storage_stats = file_manager.get_storage_stats()
    print(f"\nCurrent storage usage:")
    print(f"  Temp folder: {storage_stats['temp_folder']['size_mb']:.2f} MB")
    print(f"  Output folder: {storage_stats['output_folder']['size_mb']:.2f} MB")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='iDRAC Redfish Collector - Standalone Dell iDRAC data collection tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config config.yaml --servers servers.yaml
  %(prog)s --host 192.168.1.100 --username root --password calvin
  %(prog)s --test-connections --config config.yaml --servers servers.yaml
  %(prog)s --list-packages --config config.yaml
  %(prog)s --cleanup --days 30 --config config.yaml
        """
    )
    
    # Configuration options
    parser.add_argument('--config', '-c', 
                       help='Configuration file path')
    parser.add_argument('--servers', '-s',
                       help='Servers file path')
    parser.add_argument('--create-config',
                       help='Create default configuration file')
    parser.add_argument('--create-servers',
                       help='Create default servers file')
    
    # Single server options
    parser.add_argument('--host',
                       help='Single server host')
    parser.add_argument('--port', type=int, default=443,
                       help='Server port (default: 443)')
    parser.add_argument('--username',
                       help='Server username')
    parser.add_argument('--password',
                       help='Server password')
    parser.add_argument('--no-ssl-verify', action='store_true',
                       help='Disable SSL certificate verification')
    
    # Action options
    parser.add_argument('--test-connections', action='store_true',
                       help='Test connections to servers')
    parser.add_argument('--collect', action='store_true',
                       help='Collect data from servers')
    parser.add_argument('--list-packages', action='store_true',
                       help='List collected packages')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up old data')
    parser.add_argument('--days', type=int, default=30,
                       help='Days for cleanup (default: 30)')
    
    # Output options
    parser.add_argument('--output', '-o',
                       help='Output folder path')
    parser.add_argument('--temp',
                       help='Temporary folder path')
    
    # Logging options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose logging')
    parser.add_argument('--log-file',
                       help='Log file path')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level (default: INFO)')
    
    args = parser.parse_args()
    
    # Handle configuration creation
    if args.create_config:
        success = create_default_config(args.create_config)
        return 0 if success else 1
    
    if args.create_servers:
        success = create_default_servers(args.create_servers)
        return 0 if success else 1
    
    # Load configuration
    config_manager = ConfigManager(args.config)
    
    # Setup logging using config values, with command line overrides
    log_level = args.log_level or config_manager.global_config.logging_level
    log_file = args.log_file or config_manager.global_config.log_file
    verbose = args.verbose or config_manager.global_config.verbose
    
    setup_logging(log_level, log_file, verbose)
    logger = logging.getLogger('idrac_collector')
    
    # Load servers from file or command line
    if args.host:
        # Single server from command line
        if not args.username or not args.password:
            print("Error: --username and --password required when using --host")
            return 1
        
        server_config = ServerConfig(
            host=args.host,
            port=args.port,
            username=args.username,
            password=args.password,
            verify_ssl=not args.no_ssl_verify
        )
        config_manager.add_server(server_config)
    
    elif args.servers:
        # Load servers from file
        if not config_manager.load_servers(args.servers):
            print(f"Error: Failed to load servers file: {args.servers}")
            return 1
    
    else:
        # No servers specified
        print("Error: No servers specified. Use --host or --servers")
        parser.print_help()
        return 1
    
    # Override output folders if specified
    if args.output:
        config_manager.global_config.collection.output_folder = args.output
    if args.temp:
        config_manager.global_config.collection.temp_folder = args.temp
    
    # Execute actions
    try:
        if args.test_connections:
            success = test_connections(config_manager)
            return 0 if success else 1
        
        elif args.collect or (not args.test_connections and not args.list_packages and not args.cleanup):
            success = collect_data(config_manager, args.verbose)
            return 0 if success else 1
        
        elif args.list_packages:
            list_packages(config_manager)
            return 0
        
        elif args.cleanup:
            cleanup_data(config_manager, args.days)
            return 0
        
        else:
            print("No action specified. Use --collect, --test-connections, --list-packages, or --cleanup")
            parser.print_help()
            return 1
    
    except KeyboardInterrupt:
        print("\nCollection interrupted by user")
        return 1
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
