#!/usr/bin/env python3
#
# file_manager.py - File Operations and Compression Module
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
File Manager - Standalone file operations and compression for iDRAC collector
"""

import os
import json
import zipfile
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class FileManager:
    """File manager for iDRAC collector operations"""
    
    def __init__(self, temp_folder: str = "temp", output_folder: str = "output"):
        """Initialize file manager
        
        Args:
            temp_folder: Temporary folder path
            output_folder: Output folder path
        """
        self.temp_folder = Path(temp_folder)
        self.output_folder = Path(output_folder)
        
        # Create folders if they don't exist
        self.temp_folder.mkdir(parents=True, exist_ok=True)
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def create_server_temp_folder(self, service_tag: str) -> Path:
        """Create temporary folder for server data
        
        Args:
            service_tag: Server service tag
            
        Returns:
            Path: Temporary folder path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{service_tag}_{timestamp}"
        server_folder = self.temp_folder / folder_name
        server_folder.mkdir(exist_ok=True)
        
        return server_folder
    
    def save_json_data(self, folder: Path, filename: str, data: Dict[str, Any], 
                      pretty_print: bool = True) -> Path:
        """Save data as JSON file
        
        Args:
            folder: Target folder
            filename: Filename
            data: Data to save
            pretty_print: Whether to pretty print JSON
            
        Returns:
            Path: Saved file path
        """
        file_path = folder / f"{filename}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if pretty_print:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        
        return file_path
    
    def save_raw_response(self, folder: Path, endpoint_name: str, 
                         response_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Path:
        """Save raw Redfish response
        
        Args:
            folder: Target folder
            endpoint_name: Name of endpoint
            response_data: Response data
            metadata: Optional metadata to include
            
        Returns:
            Path: Saved file path
        """
        # Prepare data with metadata
        save_data = {
            "endpoint": endpoint_name,
            "collected_at": datetime.now().isoformat(),
            "data": response_data
        }
        
        if metadata:
            save_data["metadata"] = metadata
        
        return self.save_json_data(folder, endpoint_name, save_data)
    
    def create_server_package(self, server_folder: Path, service_tag: str, 
                             compression: bool = True) -> Path:
        """Create package for server data
        
        Args:
            server_folder: Server data folder
            service_tag: Server service tag
            compression: Whether to compress
            
        Returns:
            Path: Package file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if compression:
            # Create ZIP file
            zip_filename = f"{service_tag}_{timestamp}.zip"
            zip_path = self.output_folder / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in server_folder.rglob('*'):
                    if file_path.is_file():
                        # Calculate relative path for ZIP
                        arcname = file_path.relative_to(server_folder.parent)
                        zip_file.write(file_path, arcname)
            
            return zip_path
        else:
            # Copy folder to output
            output_folder_name = f"{service_tag}_{timestamp}"
            output_path = self.output_folder / output_folder_name
            
            shutil.copytree(server_folder, output_path, dirs_exist_ok=True)
            
            return output_path
    
    def cleanup_temp_data(self, server_folder: Path) -> bool:
        """Clean up temporary data for server
        
        Args:
            server_folder: Server temp folder
            
        Returns:
            bool: True if cleaned up successfully
        """
        try:
            if server_folder.exists():
                shutil.rmtree(server_folder)
            return True
        except Exception:
            return False
    
    def cleanup_all_temp_data(self) -> int:
        """Clean up all temporary data
        
        Returns:
            int: Number of folders cleaned up
        """
        cleaned_count = 0
        
        try:
            for folder in self.temp_folder.iterdir():
                if folder.is_dir():
                    shutil.rmtree(folder)
                    cleaned_count += 1
        except Exception:
            pass
        
        return cleaned_count
    
    def get_temp_folder_size(self) -> int:
        """Get size of temporary folder in bytes
        
        Returns:
            int: Size in bytes
        """
        total_size = 0
        
        try:
            for file_path in self.temp_folder.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        
        return total_size
    
    def get_output_folder_size(self) -> int:
        """Get size of output folder in bytes
        
        Returns:
            int: Size in bytes
        """
        total_size = 0
        
        try:
            for file_path in self.output_folder.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception:
            pass
        
        return total_size
    
    def list_output_packages(self) -> List[Dict[str, Any]]:
        """List all output packages
        
        Returns:
            List[Dict[str, Any]]: Package information
        """
        packages = []
        
        try:
            for item in self.output_folder.iterdir():
                if item.is_file() and item.suffix == '.zip':
                    stat = item.stat()
                    
                    # Extract service tag and timestamp from filename
                    name_without_ext = item.stem
                    parts = name_without_ext.split('_')
                    
                    service_tag = parts[0] if parts else 'unknown'
                    timestamp = '_'.join(parts[1:]) if len(parts) > 1 else 'unknown'
                    
                    packages.append({
                        'filename': item.name,
                        'path': str(item),
                        'service_tag': service_tag,
                        'timestamp': timestamp,
                        'size_bytes': stat.st_size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'type': 'zip'
                    })
                
                elif item.is_dir():
                    stat = item.stat()
                    
                    # Extract service tag and timestamp from folder name
                    name_parts = item.name.split('_')
                    
                    service_tag = name_parts[0] if name_parts else 'unknown'
                    timestamp = '_'.join(name_parts[1:]) if len(name_parts) > 1 else 'unknown'
                    
                    # Calculate folder size
                    folder_size = 0
                    for file_path in item.rglob('*'):
                        if file_path.is_file():
                            folder_size += file_path.stat().st_size
                    
                    packages.append({
                        'filename': item.name,
                        'path': str(item),
                        'service_tag': service_tag,
                        'timestamp': timestamp,
                        'size_bytes': folder_size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'type': 'folder'
                    })
        
        except Exception:
            pass
        
        # Sort by creation time (newest first)
        packages.sort(key=lambda x: x['created_at'], reverse=True)
        
        return packages
    
    def find_packages_by_service_tag(self, service_tag: str) -> List[Dict[str, Any]]:
        """Find packages by service tag
        
        Args:
            service_tag: Service tag to search for
            
        Returns:
            List[Dict[str, Any]]: Matching packages
        """
        all_packages = self.list_output_packages()
        
        matching_packages = [
            pkg for pkg in all_packages 
            if pkg['service_tag'].lower() == service_tag.lower()
        ]
        
        return matching_packages
    
    def delete_package(self, package_path: str) -> bool:
        """Delete package
        
        Args:
            package_path: Path to package
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            path = Path(package_path)
            
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            
            return True
        except Exception:
            return False
    
    def cleanup_old_packages(self, days: int = 30) -> int:
        """Clean up packages older than specified days
        
        Args:
            days: Age in days
            
        Returns:
            int: Number of packages deleted
        """
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        deleted_count = 0
        
        try:
            for item in self.output_folder.iterdir():
                stat = item.stat()
                
                if stat.st_ctime < cutoff_time:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                    
                    deleted_count += 1
        
        except Exception:
            pass
        
        return deleted_count
    
    def get_package_contents(self, package_path: str) -> List[Dict[str, Any]]:
        """Get contents of package
        
        Args:
            package_path: Path to package
            
        Returns:
            List[Dict[str, Any]]: Package contents
        """
        contents = []
        path = Path(package_path)
        
        try:
            if path.is_file() and path.suffix == '.zip':
                # List ZIP contents
                with zipfile.ZipFile(path, 'r') as zip_file:
                    for file_info in zip_file.infolist():
                        contents.append({
                            'filename': file_info.filename,
                            'size_bytes': file_info.file_size,
                            'compressed_size_bytes': file_info.compress_size,
                            'is_dir': file_info.is_dir(),
                            'date_time': f"{file_info.date_time[0]}-{file_info.date_time[1]:02d}-{file_info.date_time[2]:02d} {file_info.date_time[3]:02d}:{file_info.date_time[4]:02d}:{file_info.date_time[5]:02d}"
                        })
            
            elif path.is_dir():
                # List folder contents
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        stat = file_path.stat()
                        relative_path = file_path.relative_to(path)
                        
                        contents.append({
                            'filename': str(relative_path),
                            'size_bytes': stat.st_size,
                            'compressed_size_bytes': stat.st_size,
                            'is_dir': False,
                            'date_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
        
        except Exception:
            pass
        
        return contents
    
    def extract_package(self, package_path: str, extract_to: Optional[str] = None) -> bool:
        """Extract package to folder
        
        Args:
            package_path: Path to package
            extract_to: Extract destination (defaults to temp folder)
            
        Returns:
            bool: True if extracted successfully
        """
        try:
            path = Path(package_path)
            
            if extract_to:
                extract_folder = Path(extract_to)
            else:
                extract_folder = self.temp_folder / f"extract_{path.stem}"
            
            extract_folder.mkdir(parents=True, exist_ok=True)
            
            if path.is_file() and path.suffix == '.zip':
                # Extract ZIP
                with zipfile.ZipFile(path, 'r') as zip_file:
                    zip_file.extractall(extract_folder)
                
                return True
            
            elif path.is_dir():
                # Copy folder
                shutil.copytree(path, extract_folder / path.name, dirs_exist_ok=True)
                return True
        
        except Exception:
            pass
        
        return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics
        
        Returns:
            Dict[str, Any]: Storage statistics
        """
        temp_size = self.get_temp_folder_size()
        output_size = self.get_output_folder_size()
        packages = self.list_output_packages()
        
        return {
            'temp_folder': {
                'path': str(self.temp_folder),
                'size_bytes': temp_size,
                'size_mb': round(temp_size / (1024 * 1024), 2)
            },
            'output_folder': {
                'path': str(self.output_folder),
                'size_bytes': output_size,
                'size_mb': round(output_size / (1024 * 1024), 2)
            },
            'packages': {
                'total_count': len(packages),
                'zip_count': len([p for p in packages if p['type'] == 'zip']),
                'folder_count': len([p for p in packages if p['type'] == 'folder']),
                'total_size_bytes': sum(p['size_bytes'] for p in packages),
                'total_size_mb': round(sum(p['size_bytes'] for p in packages) / (1024 * 1024), 2)
            }
        }
