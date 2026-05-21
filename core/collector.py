#!/usr/bin/env python3
#
# collector.py - Main Data Collection Module
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
iDRAC Collector - Main collection logic for iDRAC Redfish data collection
"""

import time
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from .redfish_client import RedfishClient, ServerInfo, RedfishResponse
from .config_manager import CollectionEndpoint, ServerConfig
from .file_manager import FileManager


@dataclass
class CollectionResult:
    """Result of collection operation"""
    success: bool
    server_host: str
    service_tag: Optional[str]
    endpoints_collected: List[str]
    endpoints_failed: List[str]
    total_files: int
    package_path: Optional[str]
    collection_time_ms: float
    errors: List[str]
    warnings: List[str]
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class EndpointResult:
    """Result of single endpoint collection"""
    endpoint_name: str
    success: bool
    response: Optional[RedfishResponse]
    file_path: Optional[str]
    error: Optional[str]
    collection_time_ms: float


class IDRACCollector:
    """Main iDRAC data collector"""
    
    def __init__(self, file_manager: FileManager, max_parallel: int = 5):
        """Initialize collector
        
        Args:
            file_manager: File manager instance
            max_parallel: Maximum parallel collections
        """
        self.file_manager = file_manager
        self.max_parallel = max_parallel
        self.logger = logging.getLogger('core.collector')
        
        # Collection statistics
        self.stats = {
            'total_servers': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'total_endpoints': 0,
            'successful_endpoints': 0,
            'failed_endpoints': 0,
            'total_collection_time_ms': 0,
            'total_data_size_bytes': 0
        }
        
        # Thread lock for stats updates
        self.stats_lock = threading.Lock()
        
        self.logger.debug(f"Initialized collector with max_parallel={max_parallel}")
    
    def collect_server(self, server_config: ServerConfig, 
                      endpoints: List[CollectionEndpoint]) -> CollectionResult:
        """Collect data from single server
        
        Args:
            server_config: Server configuration
            endpoints: List of endpoints to collect
            
        Returns:
            CollectionResult: Collection result
        """
        start_time = time.time()
        
        result = CollectionResult(
            success=False,
            server_host=server_config.host,
            service_tag=None,
            endpoints_collected=[],
            endpoints_failed=[],
            total_files=0,
            package_path=None,
            collection_time_ms=0,
            errors=[],
            warnings=[]
        )
        
        # Create server info
        server_info = ServerInfo(
            host=server_config.host,
            port=server_config.port,
            username=server_config.username,
            password=server_config.password,
            verify_ssl=server_config.verify_ssl,
            timeout=server_config.timeout,
            base_path=server_config.base_path
        )
        
        # Create Redfish client
        client = RedfishClient(server_info)
        
        try:
            # Authenticate
            auth_result = client.authenticate()
            if not auth_result.success:
                result.errors.append(f"Authentication failed: {auth_result.error}")
                return result
            
            # Get service tag
            service_tag = client.get_service_tag()
            result.service_tag = service_tag or f"UNKNOWN_{server_config.host}"
            
            # Create temporary folder
            server_folder = self.file_manager.create_server_temp_folder(result.service_tag)
            
            # Collect endpoints
            endpoint_results = []
            
            for endpoint in endpoints:
                if not endpoint.enabled:
                    continue
                
                endpoint_result = self._collect_endpoint(client, endpoint, server_folder)
                endpoint_results.append(endpoint_result)
                
                if endpoint_result.success:
                    result.endpoints_collected.append(endpoint.name)
                else:
                    result.endpoints_failed.append(endpoint.name)
                    if endpoint_result.error:
                        result.errors.append(f"Endpoint '{endpoint.name}': {endpoint_result.error}")
            
            # Save collection metadata
            self._save_collection_metadata(server_folder, server_config, endpoint_results)
            
            # Create package
            package_path = self.file_manager.create_server_package(
                server_folder, result.service_tag, compression=True
            )
            result.package_path = str(package_path)
            result.total_files = len([f for f in server_folder.rglob('*') if f.is_file()])
            
            # Clean up temp folder
            self.file_manager.cleanup_temp_data(server_folder)
            
            # Determine success
            result.success = len(result.endpoints_collected) > 0
            
            if result.success:
                result.message = f"Successfully collected {len(result.endpoints_collected)} endpoints"
            else:
                result.message = "Failed to collect any endpoints"
        
        except Exception as e:
            result.errors.append(f"Collection failed: {e}")
        
        finally:
            # Logout
            try:
                client.logout()
            except:
                pass
            
            # Update timing
            result.collection_time_ms = (time.time() - start_time) * 1000
            
            # Update statistics
            self._update_stats(result, endpoint_results)
        
        return result
    
    def _collect_endpoint(self, client: RedfishClient, endpoint: CollectionEndpoint, 
                         server_folder) -> EndpointResult:
        """Collect data from single endpoint
        
        Args:
            client: Redfish client
            endpoint: Endpoint configuration
            server_folder: Server temporary folder
            
        Returns:
            EndpointResult: Collection result
        """
        start_time = time.time()
        
        result = EndpointResult(
            endpoint_name=endpoint.name,
            success=False,
            response=None,
            file_path=None,
            error=None,
            collection_time_ms=0
        )
        
        # Retry logic
        last_error = None
        
        for attempt in range(endpoint.retry_attempts + 1):
            try:
                # Make request
                response = client.get(
                    endpoint.path,
                    expand=endpoint.expand,
                    levels=endpoint.levels,
                    filter_query=endpoint.filter_query
                )
                
                if response.success:
                    # Save response
                    metadata = {
                        'endpoint': endpoint.name,
                        'path': endpoint.path,
                        'expand': endpoint.expand,
                        'levels': endpoint.levels,
                        'filter_query': endpoint.filter_query,
                        'attempt': attempt + 1,
                        'response_time_ms': response.response_time_ms
                    }
                    
                    file_path = self.file_manager.save_raw_response(
                        server_folder, endpoint.name, response.data, metadata
                    )
                    
                    result.success = True
                    result.response = response
                    result.file_path = str(file_path)
                    break
                
                else:
                    last_error = response.error
                    if attempt < endpoint.retry_attempts:
                        # Wait before retry
                        wait_time = 2 ** attempt  # Exponential backoff
                        time.sleep(wait_time)
            
            except Exception as e:
                last_error = str(e)
                if attempt < endpoint.retry_attempts:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
        
        # Set error if failed
        if not result.success:
            result.error = last_error
        
        result.collection_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def _save_collection_metadata(self, server_folder, server_config: ServerConfig, 
                                 endpoint_results: List[EndpointResult]):
        """Save collection metadata
        
        Args:
            server_folder: Server temporary folder
            server_config: Server configuration
            endpoint_results: Endpoint collection results
        """
        metadata = {
            'collection_info': {
                'server_host': server_config.host,
                'server_port': server_config.port,
                'collected_at': datetime.now().isoformat(),
                'collector_version': '1.0.0'
            },
            'endpoints': [],
            'summary': {
                'total_endpoints': len(endpoint_results),
                'successful_endpoints': len([r for r in endpoint_results if r.success]),
                'failed_endpoints': len([r for r in endpoint_results if not r.success]),
                'total_collection_time_ms': sum(r.collection_time_ms for r in endpoint_results)
            }
        }
        
        # Add endpoint metadata
        for endpoint_result in endpoint_results:
            endpoint_metadata = {
                'name': endpoint_result.endpoint_name,
                'success': endpoint_result.success,
                'collection_time_ms': endpoint_result.collection_time_ms,
                'file_saved': endpoint_result.file_path is not None
            }
            
            if endpoint_result.error:
                endpoint_metadata['error'] = endpoint_result.error
            
            if endpoint_result.response:
                endpoint_metadata['response_status'] = endpoint_result.response.status_code
                endpoint_metadata['response_time_ms'] = endpoint_result.response.response_time_ms
            
            metadata['endpoints'].append(endpoint_metadata)
        
        # Save metadata file
        self.file_manager.save_json_data(server_folder, 'collection_metadata', metadata)
    
    def collect_multiple_servers(self, servers: List[ServerConfig], 
                               endpoints: List[CollectionEndpoint]) -> List[CollectionResult]:
        """Collect data from multiple servers with parallel processing
        
        Args:
            servers: List of server configurations
            endpoints: List of endpoints to collect
            
        Returns:
            List[CollectionResult]: Collection results
        """
        results = []
        
        if self.max_parallel <= 1 or len(servers) == 1:
            # Sequential collection
            self.logger.debug("Using sequential collection")
            for server_config in servers:
                result = self.collect_server(server_config, endpoints)
                results.append(result)
        else:
            # Parallel collection
            self.logger.debug(f"Using parallel collection with {self.max_parallel} threads")
            with ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
                # Submit all collection tasks
                future_to_server = {
                    executor.submit(self.collect_server, server_config, endpoints): server_config
                    for server_config in servers
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_server):
                    server_config = future_to_server[future]
                    try:
                        result = future.result()
                        results.append(result)
                        self.logger.debug(f"Completed collection for {server_config.host}")
                    except Exception as e:
                        self.logger.error(f"Collection failed for {server_config.host}: {e}")
                        # Create failed result
                        failed_result = CollectionResult(
                            success=False,
                            server_host=server_config.host,
                            service_tag=None,
                            endpoints_collected=[],
                            endpoints_failed=[],
                            total_files=0,
                            package_path=None,
                            collection_time_ms=0,
                            errors=[f"Collection failed: {e}"],
                            warnings=[]
                        )
                        results.append(failed_result)
        
        return results
    
    def test_server_connection(self, server_config: ServerConfig) -> RedfishResponse:
        """Test connection to server
        
        Args:
            server_config: Server configuration
            
        Returns:
            RedfishResponse: Connection test result
        """
        server_info = ServerInfo(
            host=server_config.host,
            port=server_config.port,
            username=server_config.username,
            password=server_config.password,
            verify_ssl=server_config.verify_ssl,
            timeout=server_config.timeout,
            base_path=server_config.base_path
        )
        
        client = RedfishClient(server_info)
        
        try:
            return client.test_connection()
        finally:
            try:
                client.logout()
            except:
                pass
    
    def test_all_connections(self, server_configs: List[ServerConfig]) -> Dict[str, RedfishResponse]:
        """Test connections to all servers
        
        Args:
            server_configs: List of server configurations
            
        Returns:
            Dict[str, RedfishResponse]: Test results by host
        """
        results = {}
        
        for server_config in server_configs:
            results[server_config.host] = self.test_server_connection(server_config)
        
        return results
    
    def _update_stats(self, result: CollectionResult, endpoint_results: List[EndpointResult]):
        """Update collection statistics
        
        Args:
            result: Collection result
            endpoint_results: Endpoint results
        """
        self.stats['total_servers'] += 1
        
        if result.success:
            self.stats['successful_collections'] += 1
        else:
            self.stats['failed_collections'] += 1
        
        self.stats['total_endpoints'] += len(endpoint_results)
        self.stats['successful_endpoints'] += len([r for r in endpoint_results if r.success])
        self.stats['failed_endpoints'] += len([r for r in endpoint_results if not r.success])
        self.stats['total_collection_time_ms'] += result.collection_time_ms
        
        if result.package_path:
            try:
                package_size = 0
                for file_path in Path(result.package_path).parent.rglob('*'):
                    if file_path.is_file():
                        package_size += file_path.stat().st_size
                self.stats['total_data_size_bytes'] += package_size
            except:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics
        
        Returns:
            Dict[str, Any]: Statistics
        """
        stats = self.stats.copy()
        
        # Calculate derived statistics
        if stats['total_servers'] > 0:
            stats['success_rate'] = (stats['successful_collections'] / stats['total_servers']) * 100
            stats['failure_rate'] = (stats['failed_collections'] / stats['total_servers']) * 100
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
        
        if stats['total_endpoints'] > 0:
            stats['endpoint_success_rate'] = (stats['successful_endpoints'] / stats['total_endpoints']) * 100
        else:
            stats['endpoint_success_rate'] = 0.0
        
        # Add timing statistics
        if stats['successful_collections'] > 0:
            stats['average_collection_time_ms'] = stats['total_collection_time_ms'] / stats['successful_collections']
        else:
            stats['average_collection_time_ms'] = 0.0
        
        # Add size statistics
        stats['total_data_size_mb'] = round(stats['total_data_size_bytes'] / (1024 * 1024), 2)
        
        return stats
    
    def reset_stats(self):
        """Reset collection statistics"""
        self.stats = {
            'total_servers': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'total_endpoints': 0,
            'successful_endpoints': 0,
            'failed_endpoints': 0,
            'total_collection_time_ms': 0,
            'total_data_size_bytes': 0
        }
