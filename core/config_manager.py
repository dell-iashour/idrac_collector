#!/usr/bin/env python3
#
# config_manager.py - Configuration Management Module
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
Configuration Manager - Standalone configuration management for iDRAC collector
"""

import json
import yaml
import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CollectionEndpoint:
    """Collection endpoint configuration"""
    name: str
    path: str
    expand: bool = True
    levels: int = 1
    enabled: bool = True
    filter_query: Optional[str] = None
    description: str = ""
    timeout: int = 30
    retry_attempts: int = 3


@dataclass
class ServerGroup:
    """Server group configuration for shared credentials"""
    username: str
    password: str
    verify_ssl: bool = True
    timeout: int = 30
    base_path: str = "/redfish/v1"


@dataclass
class ServerConfig:
    """Server configuration"""
    host: str
    port: int = 443
    username: str = ""
    password: str = ""
    verify_ssl: bool = True
    timeout: int = 30
    base_path: str = "/redfish/v1"
    name: Optional[str] = None
    group: Optional[str] = None


@dataclass
class CollectionConfig:
    """Collection configuration"""
    endpoints: List[CollectionEndpoint] = field(default_factory=list)
    temp_folder: str = "temp"
    output_folder: str = "output"
    compression: bool = True
    naming_format: str = "{service_tag}_{timestamp}.zip"
    parallel_collections: int = 5
    collection_timeout: int = 300
    
    # Retry configuration
    max_attempts: int = 3
    delay: int = 5
    backoff_factor: float = 2.0
    
    # Output configuration
    include_metadata: bool = True
    include_timestamps: bool = True
    pretty_print_json: bool = True


@dataclass
class GlobalConfig:
    """Global collector configuration"""
    collection: CollectionConfig = field(default_factory=CollectionConfig)
    logging_level: str = "INFO"
    log_file: Optional[str] = None
    verbose: bool = False


class ConfigManager:
    """Configuration manager for iDRAC collector"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.global_config = GlobalConfig()
        self.servers: List[ServerConfig] = []
        self.server_groups: Dict[str, ServerGroup] = {}
        
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> bool:
        """Load configuration from file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Parse global configuration
            if 'collection' in data:
                collection_data = data['collection']
                
                # Parse endpoints
                endpoints = []
                for endpoint_data in collection_data.get('endpoints', []):
                    endpoint = CollectionEndpoint(
                        name=endpoint_data['name'],
                        path=endpoint_data['path'],
                        expand=endpoint_data.get('expand', True),
                        levels=endpoint_data.get('levels', 1),
                        enabled=endpoint_data.get('enabled', True),
                        filter_query=endpoint_data.get('filter_query'),
                        description=endpoint_data.get('description', ''),
                        timeout=endpoint_data.get('timeout', 30),
                        retry_attempts=endpoint_data.get('retry_attempts', 3)
                    )
                    endpoints.append(endpoint)
                
                self.global_config.collection = CollectionConfig(
                    endpoints=endpoints,
                    temp_folder=collection_data.get('temp_folder', 'temp'),
                    output_folder=collection_data.get('output_folder', 'output'),
                    compression=collection_data.get('compression', True),
                    naming_format=collection_data.get('naming_format', '{service_tag}_{timestamp}.zip'),
                    parallel_collections=collection_data.get('parallel_collections', 5),
                    collection_timeout=collection_data.get('collection_timeout', 300),
                    max_attempts=collection_data.get('retry', {}).get('max_attempts', 3),
                    delay=collection_data.get('retry', {}).get('delay', 5),
                    backoff_factor=collection_data.get('retry', {}).get('backoff_factor', 2.0),
                    include_metadata=collection_data.get('output', {}).get('include_metadata', True),
                    include_timestamps=collection_data.get('output', {}).get('include_timestamps', True),
                    pretty_print_json=collection_data.get('output', {}).get('pretty_print_json', True)
                )
            
            # Parse logging configuration
            self.global_config.logging_level = data.get('logging', {}).get('level', 'INFO')
            self.global_config.log_file = data.get('logging', {}).get('file')
            self.global_config.verbose = data.get('logging', {}).get('verbose', False)
            
            # Parse server groups if included
            if 'server_groups' in data:
                self.server_groups = {}
                for group_name, group_data in data['server_groups'].items():
                    group = ServerGroup(
                        username=group_data['username'],
                        password=group_data['password'],
                        verify_ssl=group_data.get('verify_ssl', True),
                        timeout=group_data.get('timeout', 30),
                        base_path=group_data.get('base_path', '/redfish/v1')
                    )
                    self.server_groups[group_name] = group
            
            # Parse servers if included
            if 'servers' in data:
                self.servers = []
                for server_data in data['servers']:
                    server = ServerConfig(
                        host=server_data['host'],
                        port=server_data.get('port', 443),
                        username=server_data.get('username', ''),
                        password=server_data.get('password', ''),
                        verify_ssl=server_data.get('verify_ssl', True),
                        timeout=server_data.get('timeout', 30),
                        base_path=server_data.get('base_path', '/redfish/v1'),
                        name=server_data.get('name'),
                        group=server_data.get('group')
                    )
                    self.servers.append(server)
            
            self.config_file = config_file
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def load_servers(self, servers_file: str) -> bool:
        """Load server configuration from file
        
        Args:
            servers_file: Path to servers file
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            with open(servers_file, 'r', encoding='utf-8') as f:
                if servers_file.endswith('.yaml') or servers_file.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            self.servers = []
            
            # Parse server groups if included
            if 'server_groups' in data:
                self.server_groups = {}
                for group_name, group_data in data['server_groups'].items():
                    group = ServerGroup(
                        username=group_data['username'],
                        password=group_data['password'],
                        verify_ssl=group_data.get('verify_ssl', True),
                        timeout=group_data.get('timeout', 30),
                        base_path=group_data.get('base_path', '/redfish/v1')
                    )
                    self.server_groups[group_name] = group
            
            for server_data in data.get('servers', []):
                server = ServerConfig(
                    host=server_data['host'],
                    port=server_data.get('port', 443),
                    username=server_data.get('username', ''),
                    password=server_data.get('password', ''),
                    verify_ssl=server_data.get('verify_ssl', True),
                    timeout=server_data.get('timeout', 30),
                    base_path=server_data.get('base_path', '/redfish/v1'),
                    name=server_data.get('name'),
                    group=server_data.get('group')
                )
                self.servers.append(server)
            
            return True
            
        except Exception as e:
            print(f"Error loading servers: {e}")
            return False
    
    def add_server(self, server: ServerConfig) -> None:
        """Add server configuration
        
        Args:
            server: Server configuration
        """
        self.servers.append(server)
    
    def remove_server(self, host: str) -> bool:
        """Remove server by host
        
        Args:
            host: Server host
            
        Returns:
            bool: True if removed
        """
        for i, server in enumerate(self.servers):
            if server.host == host:
                del self.servers[i]
                return True
        return False
    
    def get_server(self, host: str) -> Optional[ServerConfig]:
        """Get server configuration by host
        
        Args:
            host: Server host
            
        Returns:
            ServerConfig: Server configuration or None
        """
        for server in self.servers:
            if server.host == host:
                return server
        return None
    
    def get_resolved_server_config(self, server: ServerConfig) -> ServerConfig:
        """Get server configuration with group inheritance resolved
        
        Args:
            server: Server configuration
            
        Returns:
            ServerConfig: Resolved server configuration
        """
        logger = logging.getLogger('core.config_manager')
        logger.debug(f"Resolving server config for {server.host}, group: {server.group}")
        
        resolved = ServerConfig(
            host=server.host,
            port=server.port,
            username=server.username,
            password=server.password,
            verify_ssl=server.verify_ssl,
            timeout=server.timeout,
            base_path=server.base_path,
            name=server.name,
            group=server.group
        )
        
        logger.debug(f"Initial config - Username: '{resolved.username}', SSL: {resolved.verify_ssl}")
        
        # Apply group settings if group is specified and credentials are not explicitly set
        if server.group and server.group in self.server_groups:
            group = self.server_groups[server.group]
            logger.debug(f"Found group '{server.group}' - Username: '{group.username}', SSL: {group.verify_ssl}")
            
            # Always apply group settings if they're not explicitly set in server
            if not resolved.username:
                resolved.username = group.username
                logger.debug(f"Applied group username: '{resolved.username}'")
            if not resolved.password:
                resolved.password = group.password
                logger.debug(f"Applied group password")
            # For SSL, always use group setting if server has group specified
            # This ensures group settings override defaults
            resolved.verify_ssl = group.verify_ssl
            logger.debug(f"Applied group SSL setting: {resolved.verify_ssl}")
            if server.timeout == 30 and group.timeout != 30:  # Only use group default if not explicitly changed
                resolved.timeout = group.timeout
            if resolved.base_path == "/redfish/v1" and group.base_path != "/redfish/v1":  # Only use group default if not explicitly changed
                resolved.base_path = group.base_path
        else:
            logger.debug(f"No group found or group not specified for {server.group}")
        
        logger.debug(f"Final config - Username: '{resolved.username}', SSL: {resolved.verify_ssl}")
        
        return resolved
    
    def get_resolved_servers(self) -> List[ServerConfig]:
        """Get all server configurations with group inheritance resolved
        
        Returns:
            List[ServerConfig]: Resolved server configurations
        """
        return [self.get_resolved_server_config(server) for server in self.servers]
    
    def add_endpoint(self, endpoint: CollectionEndpoint) -> None:
        """Add collection endpoint
        
        Args:
            endpoint: Collection endpoint
        """
        self.global_config.collection.endpoints.append(endpoint)
    
    def remove_endpoint(self, name: str) -> bool:
        """Remove collection endpoint by name
        
        Args:
            name: Endpoint name
            
        Returns:
            bool: True if removed
        """
        for i, endpoint in enumerate(self.global_config.collection.endpoints):
            if endpoint.name == name:
                del self.global_config.collection.endpoints[i]
                return True
        return False
    
    def get_endpoint(self, name: str) -> Optional[CollectionEndpoint]:
        """Get collection endpoint by name
        
        Args:
            name: Endpoint name
            
        Returns:
            CollectionEndpoint: Endpoint or None
        """
        for endpoint in self.global_config.collection.endpoints:
            if endpoint.name == name:
                return endpoint
        return None
    
    def get_enabled_endpoints(self) -> List[CollectionEndpoint]:
        """Get list of enabled endpoints
        
        Returns:
            List[CollectionEndpoint]: Enabled endpoints
        """
        return [ep for ep in self.global_config.collection.endpoints if ep.enabled]
    
    def save_config(self, config_file: Optional[str] = None) -> bool:
        """Save configuration to file
        
        Args:
            config_file: Path to save file (uses loaded file if None)
            
        Returns:
            bool: True if saved successfully
        """
        try:
            file_path = config_file or self.config_file
            if not file_path:
                raise ValueError("No configuration file specified")
            
            # Build configuration data
            data = {
                'collection': {
                    'endpoints': [
                        {
                            'name': ep.name,
                            'path': ep.path,
                            'expand': ep.expand,
                            'levels': ep.levels,
                            'enabled': ep.enabled,
                            'filter_query': ep.filter_query,
                            'description': ep.description,
                            'timeout': ep.timeout,
                            'retry_attempts': ep.retry_attempts
                        }
                        for ep in self.global_config.collection.endpoints
                    ],
                    'temp_folder': self.global_config.collection.temp_folder,
                    'output_folder': self.global_config.collection.output_folder,
                    'compression': self.global_config.collection.compression,
                    'naming_format': self.global_config.collection.naming_format,
                    'parallel_collections': self.global_config.collection.parallel_collections,
                    'collection_timeout': self.global_config.collection.collection_timeout,
                    'retry': {
                        'max_attempts': self.global_config.collection.max_attempts,
                        'delay': self.global_config.collection.delay,
                        'backoff_factor': self.global_config.collection.backoff_factor
                    },
                    'output': {
                        'include_metadata': self.global_config.collection.include_metadata,
                        'include_timestamps': self.global_config.collection.include_timestamps,
                        'pretty_print_json': self.global_config.collection.pretty_print_json
                    }
                },
                'logging': {
                    'level': self.global_config.logging_level,
                    'file': self.global_config.log_file,
                    'verbose': self.global_config.verbose
                },
                'servers': [
                    {
                        'host': server.host,
                        'port': server.port,
                        'username': server.username,
                        'password': server.password,
                        'verify_ssl': server.verify_ssl,
                        'timeout': server.timeout,
                        'base_path': server.base_path,
                        'name': server.name
                    }
                    for server in self.servers
                ]
            }
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def create_default_config(self, config_file: str) -> bool:
        """Create default configuration file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            bool: True if created successfully
        """
        try:
            # Default endpoints based on requirements
            default_endpoints = [
                CollectionEndpoint(
                    name="system",
                    path="/redfish/v1/Systems/System.Embedded.1",
                    expand=True,
                    levels=1,
                    enabled=True,
                    description="System information"
                ),
                CollectionEndpoint(
                    name="memory",
                    path="/redfish/v1/Systems/System.Embedded.1/Memory",
                    expand=True,
                    levels=1,
                    enabled=True,
                    description="Memory information"
                ),
                CollectionEndpoint(
                    name="storage",
                    path="/redfish/v1/Systems/System.Embedded.1/Storage",
                    expand=True,
                    levels=1,
                    enabled=True,
                    description="Storage information"
                ),
                CollectionEndpoint(
                    name="network",
                    path="/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces",
                    expand=True,
                    levels=1,
                    enabled=True,
                    description="Network interfaces"
                ),
                CollectionEndpoint(
                    name="health",
                    path="/redfish/v1/Systems/System.Embedded.1/Oem/Dell/DellRollupStatus",
                    expand=True,
                    levels=1,
                    enabled=True,
                    description="System health status"
                ),
                CollectionEndpoint(
                    name="logs",
                    path="/redfish/v1/Managers/iDRAC.Embedded.1/LogServices/Lclog/Entries",
                    expand=True,
                    levels=1,
                    enabled=True,
                    filter_query="Severity eq 'Critical'",
                    description="Critical logs"
                ),
                CollectionEndpoint(
                    name="assembly",
                    path="/redfish/v1/Chassis/System.Embedded.1/Assembly",
                    expand=True,
                    levels=1,
                    enabled=True,
                    description="Assembly information"
                ),
                CollectionEndpoint(
                    name="firmware",
                    path="/redfish/v1/UpdateService/FirmwareInventory",
                    expand=True,
                    levels=1,
                    enabled=True,
                    description="Firmware inventory"
                )
            ]
            
            self.global_config.collection.endpoints = default_endpoints
            
            # Save configuration
            return self.save_config(config_file)
            
        except Exception as e:
            print(f"Error creating default configuration: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """Validate configuration
        
        Returns:
            List[str]: Validation errors
        """
        errors = []
        
        # Validate collection configuration
        collection = self.global_config.collection
        
        if not collection.endpoints:
            errors.append("No collection endpoints configured")
        
        if not collection.temp_folder:
            errors.append("Temp folder not specified")
        
        if not collection.output_folder:
            errors.append("Output folder not specified")
        
        # Validate endpoints
        for endpoint in collection.endpoints:
            if not endpoint.name:
                errors.append("Endpoint name is required")
            
            if not endpoint.path:
                errors.append(f"Endpoint '{endpoint.name}' path is required")
            
            if not endpoint.path.startswith('/'):
                errors.append(f"Endpoint '{endpoint.name}' path must start with '/'")
        
        # Validate servers using resolved configurations
        resolved_servers = self.get_resolved_servers()
        
        if not resolved_servers:
            errors.append("No servers configured")
        
        for server in resolved_servers:
            if not server.host:
                errors.append("Server host is required")
            
            if not server.username:
                errors.append(f"Server '{server.host}' username is required")
            
            if not server.password:
                errors.append(f"Server '{server.host}' password is required")
            
            if server.port < 1 or server.port > 65535:
                errors.append(f"Server '{server.host}' port must be between 1 and 65535")
        
        return errors
    
    def get_summary(self) -> Dict[str, Any]:
        """Get configuration summary
        
        Returns:
            Dict[str, Any]: Configuration summary
        """
        return {
            'servers_count': len(self.servers),
            'endpoints_count': len(self.global_config.collection.endpoints),
            'enabled_endpoints': len(self.get_enabled_endpoints()),
            'temp_folder': self.global_config.collection.temp_folder,
            'output_folder': self.global_config.collection.output_folder,
            'compression': self.global_config.collection.compression,
            'parallel_collections': self.global_config.collection.parallel_collections,
            'logging_level': self.global_config.logging_level,
            'servers': [
                {
                    'host': server.host,
                    'port': server.port,
                    'name': server.name or server.host
                }
                for server in self.servers
            ],
            'endpoints': [
                {
                    'name': ep.name,
                    'path': ep.path,
                    'enabled': ep.enabled,
                    'expand': ep.expand
                }
                for ep in self.global_config.collection.endpoints
            ]
        }
