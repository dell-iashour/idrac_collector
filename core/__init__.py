#!/usr/bin/env python3
#
# __init__.py - Core Module Package Initialization
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
iDRAC Redfish Collector - Core Modules
Standalone core functionality for iDRAC data collection
"""

from .redfish_client import RedfishClient
from .collector import IDRACCollector
from .config_manager import ConfigManager
from .file_manager import FileManager

__all__ = [
    'RedfishClient',
    'IDRACCollector', 
    'ConfigManager',
    'FileManager'
]
