#!/usr/bin/env python3
#
# redfish_client.py - Redfish API Client Module
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
Redfish Client - Standalone Redfish API client for iDRAC
Based on Dell iDRAC Redfish Scripting examples
"""

import json
import ssl
import time
import urllib.request
import urllib.parse
import urllib.error
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RedfishResponse:
    """Redfish API response"""
    success: bool
    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str]
    error: Optional[str] = None
    response_time_ms: float = 0.0


@dataclass
class ServerInfo:
    """Server connection information"""
    host: str
    port: int
    username: str
    password: str
    verify_ssl: bool = True
    timeout: int = 30
    base_path: str = "/redfish/v1"


class RedfishClient:
    """Standalone Redfish API client for iDRAC"""
    
    def __init__(self, server_info: ServerInfo):
        """Initialize Redfish client
        
        Args:
            server_info: Server connection information
        """
        self.server_info = server_info
        self.session_id: Optional[str] = None
        self.session_token: Optional[str] = None
        self.base_url = f"https://{server_info.host}:{server_info.port}{server_info.base_path}"
        self.logger = logging.getLogger('core.redfish_client')
        
        # SSL context
        self.ssl_context = ssl.create_default_context()
        if not server_info.verify_ssl:
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        
        # Connection pooling - reuse opener for multiple requests with SSL context
        https_handler = urllib.request.HTTPSHandler(context=self.ssl_context)
        self.opener = urllib.request.build_opener(https_handler)
        self.opener.addheaders = []
        
        self.logger.debug(f"Initialized Redfish client for {server_info.host}:{server_info.port}")
        self.logger.debug(f"SSL verification: {server_info.verify_ssl}")
        self.logger.debug(f"Base URL: {self.base_url}")
    
    def authenticate(self) -> RedfishResponse:
        """Authenticate with iDRAC and create session
        
        Returns:
            RedfishResponse: Authentication result
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"Authenticating user '{self.server_info.username}' with {self.server_info.host}")
            
            # Prepare authentication request
            auth_url = f"{self.base_url}/Sessions"
            auth_data = {
                "UserName": self.server_info.username,
                "Password": self.server_info.password
            }
            
            # Create request
            request = urllib.request.Request(
                auth_url,
                data=json.dumps(auth_data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json'
                }
            )
            
            # Send request using connection pool
            with self.opener.open(request, timeout=self.server_info.timeout) as response:
                response_data = response.read().decode('utf-8')
                headers = dict(response.headers)
                
                # Extract session information
                self.session_token = headers.get('X-Auth-Token')
                session_url = headers.get('Location')
                
                if session_url:
                    # Extract session ID from URL
                    session_parts = session_url.split('/')
                    self.session_id = session_parts[-1] if session_parts else None
                
                self.logger.debug(f"Authentication successful - Session ID: {self.session_id}")
                self.logger.debug(f"Response time: {(time.time() - start_time) * 1000:.2f}ms")
                
                response_time = (time.time() - start_time) * 1000
                
                return RedfishResponse(
                    success=True,
                    status_code=response.status,
                    data=json.loads(response_data) if response_data else {},
                    headers=headers,
                    response_time_ms=response_time
                )
        
        except urllib.error.HTTPError as e:
            response_time = (time.time() - start_time) * 1000
            error_data = ""
            try:
                error_data = e.read().decode('utf-8')
            except:
                pass
            
            return RedfishResponse(
                success=False,
                status_code=e.code,
                data={},
                headers={},
                error=f"HTTP {e.code}: {error_data}",
                response_time_ms=response_time
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return RedfishResponse(
                success=False,
                status_code=0,
                data={},
                headers={},
                error=f"Authentication failed: {e}",
                response_time_ms=response_time
            )
    
    def logout(self) -> RedfishResponse:
        """Logout and close session
        
        Returns:
            RedfishResponse: Logout result
        """
        if not self.session_id:
            self.logger.debug("No active session to logout")
            return RedfishResponse(
                success=True,
                status_code=200,
                data={},
                headers={},
                error="No active session"
            )
        
        start_time = time.time()
        self.logger.debug(f"Logging out from {self.server_info.host}")
        
        try:
            logout_url = f"{self.base_url}/Sessions/{self.session_id}"
            
            request = urllib.request.Request(
                logout_url,
                method='DELETE',
                headers={
                    'X-Auth-Token': self.session_token,
                    'Content-Type': 'application/json'
                }
            )
            
            with urllib.request.urlopen(request, timeout=self.server_info.timeout, context=self.ssl_context) as response:
                response_time = (time.time() - start_time) * 1000
                
                # Clear session
                self.session_id = None
                self.session_token = None
                
                return RedfishResponse(
                    success=True,
                    status_code=response.status,
                    data={},
                    headers=dict(response.headers),
                    response_time_ms=response_time
                )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return RedfishResponse(
                success=False,
                status_code=0,
                data={},
                headers={},
                error=f"Logout failed: {e}",
                response_time_ms=response_time
            )
    
    def get(self, path: str, expand: bool = False, levels: int = 1, 
            filter_query: Optional[str] = None) -> RedfishResponse:
        """GET request to Redfish endpoint
        
        Args:
            path: API path (relative to base URL)
            expand: Whether to expand relationships
            levels: Number of levels to expand
            filter_query: OData filter query
            
        Returns:
            RedfishResponse: API response
        """
        start_time = time.time()
        
        try:
            # Build URL with query parameters
            url = f"{self.base_url}{path}"
            query_params = []
            
            if expand:
                query_params.append(f"$expand=*($levels={levels})")
            
            if filter_query:
                query_params.append(f"$filter={filter_query}")
            
            if query_params:
                url += "?" + "&".join(query_params)
            
            self.logger.debug(f"GET request to: {url}")
            self.logger.debug(f"Session token: {'Present' if self.session_token else 'Missing'}")
            
            # Create request
            request = urllib.request.Request(
                url,
                headers={
                    'X-Auth-Token': self.session_token,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            # Send request using connection pool
            with self.opener.open(request, timeout=self.server_info.timeout) as response:
                response_data = response.read().decode('utf-8')
                headers = dict(response.headers)
                
                response_time = (time.time() - start_time) * 1000
                
                self.logger.debug(f"GET response: {response.status} in {response_time:.2f}ms")
                
                return RedfishResponse(
                    success=True,
                    status_code=response.status,
                    data=json.loads(response_data) if response_data else {},
                    headers=headers,
                    response_time_ms=response_time
                )
        
        except urllib.error.HTTPError as e:
            response_time = (time.time() - start_time) * 1000
            error_data = ""
            try:
                error_data = e.read().decode('utf-8')
            except:
                pass
            
            return RedfishResponse(
                success=False,
                status_code=e.code,
                data={},
                headers={},
                error=f"HTTP {e.code}: {error_data}",
                response_time_ms=response_time
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return RedfishResponse(
                success=False,
                status_code=0,
                data={},
                headers={},
                error=f"GET request failed: {e}",
                response_time_ms=response_time
            )
    
    def post(self, path: str, data: Dict[str, Any]) -> RedfishResponse:
        """POST request to Redfish endpoint
        
        Args:
            path: API path (relative to base URL)
            data: Request data
            
        Returns:
            RedfishResponse: API response
        """
        start_time = time.time()
        
        try:
            url = f"{self.base_url}{path}"
            
            request = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={
                    'X-Auth-Token': self.session_token,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(request, timeout=self.server_info.timeout, context=self.ssl_context) as response:
                response_data = response.read().decode('utf-8')
                headers = dict(response.headers)
                
                response_time = (time.time() - start_time) * 1000
                
                return RedfishResponse(
                    success=True,
                    status_code=response.status,
                    data=json.loads(response_data) if response_data else {},
                    headers=headers,
                    response_time_ms=response_time
                )
        
        except urllib.error.HTTPError as e:
            response_time = (time.time() - start_time) * 1000
            error_data = ""
            try:
                error_data = e.read().decode('utf-8')
            except:
                pass
            
            return RedfishResponse(
                success=False,
                status_code=e.code,
                data={},
                headers={},
                error=f"HTTP {e.code}: {error_data}",
                response_time_ms=response_time
            )
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return RedfishResponse(
                success=False,
                status_code=0,
                data={},
                headers={},
                error=f"POST request failed: {e}",
                response_time_ms=response_time
            )
    
    def get_system_info(self) -> RedfishResponse:
        """Get basic system information
        
        Returns:
            RedfishResponse: System information
        """
        return self.get("/Systems/System.Embedded.1", expand=True, levels=1)
    
    def get_service_tag(self) -> Optional[str]:
        """Extract service tag from system information
        
        Returns:
            str: Service tag or None if not found
        """
        response = self.get_system_info()
        
        if response.success:
            system_data = response.data
            self.logger.debug(f"System data keys: {list(system_data.keys())}")
            
            # Check for SystemServiceTag in BIOS.Attributes section first
            bios_attributes = system_data.get('Bios', {}).get('Attributes', {})
            system_service_tag = bios_attributes.get('SystemServiceTag')
            self.logger.debug(f"SystemServiceTag found in BIOS.Attributes: {system_service_tag}")
            
            # Try different possible locations for service tag
            service_tag = (
                system_service_tag or
                system_data.get('SystemServiceTag') or
                system_data.get('AssetTag') or
                system_data.get('SerialNumber') or
                system_data.get('PartNumber') or
                system_data.get('Oem', {}).get('Dell', {}).get('ServiceTag')
            )
            
            self.logger.debug(f"Final service tag extracted: {service_tag}")
            return service_tag
        
        self.logger.error(f"Failed to get system info for service tag extraction")
        return None
    
    def test_connection(self) -> RedfishResponse:
        """Test connection to iDRAC
        
        Returns:
            RedfishResponse: Connection test result
        """
        start_time = time.time()
        
        try:
            self.logger.debug(f"Testing connection to {self.server_info.host}")
            
            # First authenticate
            auth_result = self.authenticate()
            if not auth_result.success:
                return auth_result
            
            # Try to get root service
            response = self.get("/")
            
            if response.success:
                response_time = (time.time() - start_time) * 1000
                self.logger.debug(f"Connection test successful for {self.server_info.host}")
                return RedfishResponse(
                    success=True,
                    status_code=200,
                    data={"message": "Connection successful", "service_tag": self.get_service_tag()},
                    headers={},
                    response_time_ms=response_time
                )
            else:
                self.logger.debug(f"Connection test failed for {self.server_info.host}: {response.error}")
                return response
        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.logger.error(f"Connection test exception for {self.server_info.host}: {e}")
            return RedfishResponse(
                success=False,
                status_code=0,
                data={},
                headers={},
                error=f"Connection test failed: {e}",
                response_time_ms=response_time
            )
    
    def __enter__(self):
        """Context manager entry"""
        auth_result = self.authenticate()
        if not auth_result.success:
            raise Exception(f"Authentication failed: {auth_result.error}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session_id:
            self.logout()


class RedfishManager:
    """Manager for multiple Redfish connections"""
    
    def __init__(self):
        self.connections: Dict[str, RedfishClient] = {}
    
    def add_connection(self, name: str, server_info: ServerInfo) -> bool:
        """Add server connection
        
        Args:
            name: Connection name
            server_info: Server connection info
            
        Returns:
            bool: True if added successfully
        """
        try:
            self.connections[name] = RedfishClient(server_info)
            return True
        except Exception:
            return False
    
    def remove_connection(self, name: str) -> bool:
        """Remove server connection
        
        Args:
            name: Connection name
            
        Returns:
            bool: True if removed successfully
        """
        if name in self.connections:
            del self.connections[name]
            return True
        return False
    
    def get_connection(self, name: str) -> Optional[RedfishClient]:
        """Get connection by name
        
        Args:
            name: Connection name
            
        Returns:
            RedfishClient: Connection or None
        """
        return self.connections.get(name)
    
    def test_all_connections(self) -> Dict[str, RedfishResponse]:
        """Test all connections
        
        Returns:
            Dict[str, RedfishResponse]: Test results
        """
        results = {}
        
        for name, client in self.connections.items():
            results[name] = client.test_connection()
        
        return results
    
    def get_all_service_tags(self) -> Dict[str, Optional[str]]:
        """Get service tags for all connections
        
        Returns:
            Dict[str, str]: Service tags by connection name
        """
        service_tags = {}
        
        for name, client in self.connections.items():
            service_tags[name] = client.get_service_tag()
        
        return service_tags
