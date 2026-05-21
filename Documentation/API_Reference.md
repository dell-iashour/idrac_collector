# API Reference

## Overview

This document provides detailed reference information for the Dell iDRAC Redfish API endpoints used by the collector, including request/response formats, data structures, and usage examples.

## Redfish API Basics

### Authentication

The collector uses session-based authentication:

1. **Session Creation**: POST to `/redfish/v1/Sessions`
2. **Session Token**: Extracted from `X-Auth-Token` header
3. **Session Usage**: Token included in subsequent requests
4. **Session Cleanup**: DELETE to session endpoint

### Request Format

```http
GET /redfish/v1/Systems/System.Embedded.1?$expand=*($levels=1)
Host: 192.168.1.100:443
X-Auth-Token: <session-token>
Content-Type: application/json
Accept: application/json
```

### Response Format

```json
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.id": "/redfish/v1/Systems/System.Embedded.1",
  "@odata.type": "#ComputerSystem.v1_20_0.ComputerSystem",
  "Id": "System.Embedded.1",
  "Name": "System",
  "Description": "Computer System",
  "Status": {
    "State": "Enabled",
    "Health": "OK"
  }
}
```

## Supported Endpoints

### System Information

**Endpoint**: `/redfish/v1/Systems/System.Embedded.1?$expand=*($levels=1)`

**Description**: Complete system information including hardware details, service tag, and configuration.

**Key Fields**:
- `SystemServiceTag` - Dell service tag (extracted for package naming)
- `Model` - System model
- `Manufacturer` - System manufacturer
- `SerialNumber` - System serial number
- `AssetTag` - Asset tag
- `UUID` - System UUID
- `Status` - System health and state
- `Boot` - Boot configuration
- `ProcessorSummary` - CPU information
- `MemorySummary` - Memory information

**Example Response**:
```json
{
  "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
  "@odata.id": "/redfish/v1/Systems/System.Embedded.1",
  "@odata.type": "#ComputerSystem.v1_20_0.ComputerSystem",
  "Id": "System.Embedded.1",
  "Name": "System",
  "Description": "Computer System",
  "Manufacturer": "Dell Inc.",
  "Model": "PowerEdge R740",
  "SerialNumber": "ABC123",
  "AssetTag": "",
  "UUID": "4c4c4544-0056-3510-8056-c4c04f385432",
  "Status": {
    "State": "Enabled",
    "Health": "OK",
    "HealthRollup": "OK"
  },
  "Boot": {
    "BootOrder": [],
    "BootSourceOverrideMode": "Disabled",
    "UefiTargetBootSourceOverride": null
  },
  "ProcessorSummary": {
    "Count": 2,
    "Model": "Intel(R) Xeon(R) Silver 4210 CPU @ 2.20GHz",
    "Status": {
      "State": "Enabled",
      "Health": "OK"
    }
  },
  "MemorySummary": {
    "TotalSystemMemoryGiB": 64,
    "Status": {
      "State": "Enabled",
      "Health": "OK"
    }
  },
  "Bios": {
    "@odata.id": "/redfish/v1/Systems/System.Embedded.1/Bios"
  },
  "Links": {
    "Chassis": [
      {
        "@odata.id": "/redfish/v1/Chassis/System.Embedded.1"
      }
    ]
  }
}
```

### Memory Information

**Endpoint**: `/redfish/v1/Systems/System.Embedded.1/Memory?$expand=*($levels=1)`

**Description**: Detailed memory module information including capacity, speed, and status.

**Key Fields**:
- `CapacityMiB` - Memory capacity in MiB
- `MemoryDeviceType` - Type of memory (DDR4, etc.)
- `SpeedMHz` - Memory speed
- `Manufacturer` - Memory manufacturer
- `SerialNumber` - Module serial number
- `PartNumber` - Part number
- `Status` - Module health and state

**Example Response**:
```json
{
  "@odata.context": "/redfish/v1/$metadata#MemoryCollection.MemoryCollection",
  "@odata.id": "/redfish/v1/Systems/System.Embedded.1/Memory",
  "@odata.type": "#MemoryCollection.MemoryCollection",
  "Name": "Memory Collection",
  "Description": "Collection of Memory Devices",
  "Members": [
    {
      "@odata.id": "/redfish/v1/Systems/System.Embedded.1/Memory/DIMM.Socket.A1",
      "@odata.type": "#Memory.v1_7_0.Memory",
      "Id": "DIMM.Socket.A1",
      "Name": "DIMM Socket A1",
      "Description": "DIMM Socket A1",
      "CapacityMiB": 16384,
      "MemoryDeviceType": "DDR4",
      "MemoryLocation": {
        "Socket": "A1",
        "MemoryController": "0",
        "Channel": "0",
        "Slot": "0"
      },
      "SpeedMHz": 2666,
      "Manufacturer": "Samsung",
      "SerialNumber": "12345678",
      "PartNumber": "M393A2K40BB1-CRC",
      "Status": {
        "State": "Enabled",
        "Health": "OK"
      },
      "OperatingSpeedMHz": 2666,
      "DataWidthBits": 64,
      "TotalWidthBits": 72,
      "RankCount": 2,
      "VoltageV": 1.2
    }
  ],
  "Members@odata.count": 1
}
```

### Storage Information

**Endpoint**: `/redfish/v1/Systems/System.Embedded.1/Storage?$expand=*($levels=1)`

**Description**: Storage controller and disk information including RAID arrays and physical disks.

**Key Fields**:
- `StorageControllers` - Storage controller information
- `Drives` - Physical disk details
- `Volumes` - Logical volume/RAID information
- `Status` - Storage health and state

**Example Response**:
```json
{
  "@odata.context": "/redfish/v1/$metadata#StorageCollection.StorageCollection",
  "@odata.id": "/redfish/v1/Systems/System.Embedded.1/Storage",
  "@odata.type": "#StorageCollection.StorageCollection",
  "Name": "Storage Collection",
  "Description": "Collection of Storage Subsystems",
  "Members": [
    {
      "@odata.id": "/redfish/v1/Systems/System.Embedded.1/Storage/RAID.Integrated.1-1",
      "@odata.type": "#Storage.v1_7_0.Storage",
      "Id": "RAID.Integrated.1-1",
      "Name": "PERC H730P Mini",
      "Description": "Integrated RAID Controller",
      "StorageControllers": [
        {
          "MemberId": "RAID.Integrated.1-1",
          "Status": {
            "State": "Enabled",
            "Health": "OK"
          },
          "Manufacturer": "Dell Inc.",
          "Model": "PERC H730P Mini",
          "FirmwareVersion": "25.5.5.0005"
        }
      ],
      "Drives": [
        {
          "@odata.id": "/redfish/v1/Systems/System.Embedded.1/Storage/RAID.Integrated.1-1/Drives/Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-1",
          "@odata.type": "#Drive.v1_7_0.Drive",
          "Id": "Disk.Bay.0:Enclosure.Internal.0-1:RAID.Integrated.1-1",
          "Name": "Disk Bay 0",
          "Description": "Physical Disk",
          "CapacityBytes": 1000204885504,
          "Protocol": "SAS",
          "MediaType": "HDD",
          "Manufacturer": "SEAGATE",
          "SerialNumber": "ABC123",
          "Model": "ST1000NM0033",
          "Status": {
            "State": "Enabled",
            "Health": "OK"
          },
          "RotationSpeedRPM": 7200,
          "BlockSizeBytes": 512
        }
      ],
      "Volumes": [
        {
          "@odata.id": "/redfish/v1/Systems/System.Embedded.1/Storage/RAID.Integrated.1-1/Volumes/Volume.0.RAID.Integrated.1-1",
          "@odata.type": "#Volume.v1_2_0.Volume",
          "Id": "Volume.0.RAID.Integrated.1-1",
          "Name": "Volume 0",
          "Description": "RAID Volume",
          "VolumeType": "Mirrored",
          "CapacityBytes": 1000204885504,
          "Status": {
            "State": "Enabled",
            "Health": "OK"
          },
          "RAIDType": "RAID1",
          "NumberOfMediaSpans": 1
        }
      ]
    }
  ],
  "Members@odata.count": 1
}
```

### Network Information

**Endpoint**: `/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces?$expand=*($levels=1)`

**Description**: Network interface card information including MAC addresses, link status, and network configuration.

**Key Fields**:
- `MACAddress` - MAC address
- `SpeedMbps` - Link speed
- `AutoNeg` - Auto-negotiation status
- `LinkStatus` - Link status
- `IPv4Addresses` - IPv4 configuration
- `IPv6Addresses` - IPv6 configuration
- `PermanentMACAddress` - Permanent MAC address

**Example Response**:
```json
{
  "@odata.context": "/redfish/v1/$metadata#EthernetInterfaceCollection.EthernetInterfaceCollection",
  "@odata.id": "/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces",
  "@odata.type": "#EthernetInterfaceCollection.EthernetInterfaceCollection",
  "Name": "Network Interface Collection",
  "Description": "Collection of Network Interfaces",
  "Members": [
    {
      "@odata.id": "/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces/NIC.1",
      "@odata.type": "#EthernetInterface.v1_6_0.EthernetInterface",
      "Id": "NIC.1",
      "Name": "NIC.1",
      "Description": "Network Interface",
      "MACAddress": "A0:B1:C2:D3:E4:F5",
      "PermanentMACAddress": "A0:B1:C2:D3:E4:F5",
      "SpeedMbps": 1000,
      "AutoNeg": true,
      "LinkStatus": "LinkUp",
      "Status": {
        "State": "Enabled",
        "Health": "OK"
      },
      "IPv4Addresses": [
        {
          "Address": "192.168.1.100",
          "SubnetMask": "255.255.255.0",
          "AddressOrigin": "Static",
          "Gateway": "192.168.1.1"
        }
      ],
      "IPv6Addresses": [],
      "InterfaceEnabled": true,
      "FullDuplex": true
    }
  ],
  "Members@odata.count": 1
}
```

### Firmware Information

**Endpoint**: `/redfish/v1/UpdateService/FirmwareInventory?$expand=*($levels=1)`

**Description**: Complete firmware inventory including all device firmware versions and update status.

**Key Fields**:
- `Id` - Firmware identifier
- `Name` - Firmware name
- `Version` - Firmware version
- `Updateable` - Whether firmware can be updated
- `Status` - Firmware health and state
- `Manufacturer` - Firmware manufacturer
- `ReleaseDate` - Firmware release date

**Example Response**:
```json
{
  "@odata.context": "/redfish/v1/$metadata#SoftwareInventoryCollection.SoftwareInventoryCollection",
  "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory",
  "@odata.type": "#SoftwareInventoryCollection.SoftwareInventoryCollection",
  "Name": "Firmware Inventory Collection",
  "Description": "Collection of Firmware Inventory",
  "Members": [
    {
      "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/BIOS.Setup.1-1",
      "@odata.type": "#SoftwareInventory.v1_4_0.SoftwareInventory",
      "Id": "BIOS.Setup.1-1",
      "Name": "BIOS",
      "Description": "BIOS Firmware",
      "Version": "2.15.1",
      "SoftwareType": "BIOS",
      "Oem": {
        "Dell": {
          "PackageType": "BIN",
          "MajorVersion": "2",
          "MinorVersion": "15",
          "PatchVersion": "1",
          "BuildNumber": "0"
        }
      },
      "Updateable": true,
      "Status": {
        "State": "Enabled",
        "Health": "OK"
      },
      "Manufacturer": "Dell Inc.",
      "ReleaseDate": "2022-06-16T00:00:00Z"
    },
    {
      "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/iDRAC.Embedded.1-1",
      "@odata.type": "#SoftwareInventory.v1_4_0.SoftwareInventory",
      "Id": "iDRAC.Embedded.1-1",
      "Name": "iDRAC",
      "Description": "iDRAC Firmware",
      "Version": "5.00.00.00",
      "SoftwareType": "ManagementController",
      "Oem": {
        "Dell": {
          "PackageType": "DEX",
          "MajorVersion": "5",
          "MinorVersion": "00",
          "PatchVersion": "00",
          "BuildNumber": "00"
        }
      },
      "Updateable": true,
      "Status": {
        "State": "Enabled",
        "Health": "OK"
      },
      "Manufacturer": "Dell Inc.",
      "ReleaseDate": "2023-03-15T00:00:00Z"
    }
  ],
  "Members@odata.count": 2
}
```

## Dell OEM Extensions

### Dell System Information

**Endpoint**: `/redfish/v1/Systems/System.Embedded.1/Oem/Dell/DellSystem`

**Description**: Dell-specific system information including detailed hardware and configuration data.

**Key Fields**:
- `NodeID` - Dell node ID
- `ChassisModel` - Chassis model information
- `SystemType` - System type
- `AssetTag` - Asset tag
- `ServiceTag` - Dell service tag
- `PowerState` - Current power state
- `LastUpdateTime` - Last system update

### Dell Rollup Status

**Endpoint**: `/redfish/v1/Systems/System.Embedded.1/Oem/Dell/DellRollupStatus`

**Description**: Aggregated health status for all system components.

**Key Fields**:
- `SystemRollupStatus` - Overall system health
- `StorageRollupStatus` - Storage health
- `MemoryRollupStatus` - Memory health
- `ProcessorRollupStatus` - CPU health
- `PowerSupplyRollupStatus` - Power supply health
- `TempRollupStatus` - Temperature status
- `VoltRollupStatus` - Voltage status

## Query Parameters

### Expansion

The `$expand` parameter allows retrieving related resources in a single request:

```http
GET /redfish/v1/Systems/System.Embedded.1?$expand=*($levels=1)
```

**Levels**:
- `$levels=1` - Expand one level deep
- `$levels=2` - Expand two levels deep
- `*` - Expand all levels

### Filtering

The `$filter` parameter allows filtering results:

```http
GET /redfish/v1/Managers/iDRAC.Embedded.1/LogServices/Lclog/Entries?$filter=Severity eq 'Critical'
```

**Filter Operators**:
- `eq` - Equals
- `ne` - Not equals
- `gt` - Greater than
- `lt` - Less than
- `ge` - Greater than or equal
- `le` - Less than or equal
- `and` - Logical AND
- `or` - Logical OR

### Select

The `$select` parameter allows selecting specific fields:

```http
GET /redfish/v1/Systems/System.Embedded.1?$select=Name,Status,SerialNumber
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 201 | Created | Resource created |
| 400 | Bad Request | Fix request format |
| 401 | Unauthorized | Check credentials |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify endpoint path |
| 409 | Conflict | Resolve conflict |
| 500 | Internal Server Error | Retry or contact support |
| 503 | Service Unavailable | Retry later |

### Error Response Format

```json
{
  "error": {
    "code": "Base.1.8.GeneralError",
    "message": "A general error has occurred. See ExtendedInfo for more information.",
    "@Message.ExtendedInfo": [
      {
        "MessageId": "Base.1.8.PropertyValueNotInList",
        "MessageArgs": ["Property", "Value"],
        "Severity": "Warning",
        "Resolution": "Correct the property value"
      }
    ]
  }
}
```

## Data Types

### Common Data Types

#### Status Object
```json
{
  "State": "Enabled|Disabled|Standby|Offline",
  "Health": "OK|Warning|Critical",
  "HealthRollup": "OK|Warning|Critical"
}
```

#### Resource Reference
```json
{
  "@odata.id": "/redfish/v1/Systems/System.Embedded.1"
}
```

#### Collection Object
```json
{
  "Members": [
    {"@odata.id": "/redfish/v1/Systems/System.Embedded.1/Memory/DIMM1"}
  ],
  "Members@odata.count": 1
}
```

### Dell OEM Data Types

#### Dell System Object
```json
{
  "NodeID": "ABC123",
  "ChassisModel": "PowerEdge R740",
  "SystemType": "Physical",
  "AssetTag": "ASSET123",
  "ServiceTag": "ABC123",
  "PowerState": "On",
  "LastUpdateTime": "2023-11-17T20:07:44+00:00"
}
```

## Rate Limiting

### Recommended Practices

1. **Session Management**: Reuse sessions for multiple requests
2. **Request Spacing**: Add delays between requests to avoid overwhelming iDRAC
3. **Parallel Requests**: Limit concurrent requests to same iDRAC
4. **Timeout Handling**: Implement appropriate timeouts and retry logic

### Collector Implementation

The collector implements these best practices:

- **Connection Reuse**: TCP connections reused for multiple requests
- **Session Management**: Single session per server per collection
- **Parallel Threading**: Configurable parallel processing across servers
- **Retry Logic**: Exponential backoff for failed requests
- **Timeout Configuration**: Per-endpoint timeout settings

## Version Compatibility

### iDRAC Versions

| iDRAC Version | Redfish Version | Supported Features |
|---------------|----------------|-------------------|
| iDRAC 7.x | 1.0.0 | Basic system info |
| iDRAC 8.x | 1.2.0+ | Enhanced endpoints |
| iDRAC 9.x | 1.6.0+ | Full feature support |

### Endpoint Availability

| Endpoint | iDRAC 7 | iDRAC 8 | iDRAC 9 |
|----------|---------|---------|---------|
| System | ✅ | ✅ | ✅ |
| Memory | ✅ | ✅ | ✅ |
| Storage | ✅ | ✅ | ✅ |
| Network | ✅ | ✅ | ✅ |
| Firmware | ✅ | ✅ | ✅ |
| Dell OEM | ⚠️ | ✅ | ✅ |

## Testing Endpoints

### Manual Testing

Use curl to test endpoints manually:

```bash
# Test system endpoint
curl -k -u root:calvin \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  "https://192.168.1.100/redfish/v1/Systems/System.Embedded.1?$expand=*($levels=1)"

# Test with session
SESSION_TOKEN=$(curl -k -u root:calvin \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"UserName":"root","Password":"calvin"}' \
  "https://192.168.1.100/redfish/v1/Sessions" \
  | grep -o '"X-Auth-Token": "[^"]*"' | cut -d'"' -f4)

curl -k \
  -H "X-Auth-Token: $SESSION_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  "https://192.168.1.100/redfish/v1/Systems/System.Embedded.1"
```

### Python Testing

```python
import requests
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Test endpoint
response = requests.get(
    "https://192.168.1.100/redfish/v1/Systems/System.Embedded.1",
    auth=("root", "calvin"),
    verify=False,
    headers={"Accept": "application/json"}
)

if response.status_code == 200:
    data = response.json()
    print(f"System: {data.get('Model')}")
    print(f"Service Tag: {data.get('Oem', {}).get('Dell', {}).get('DellSystem', {}).get('NodeID')}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

## Related Documentation

- [Dell iDRAC Redfish API Documentation](https://www.dell.com/support/home/en-us/drivers/articles/Drivers-Details-About-dell-emc-idrac-redfish-api)
- [Redfish Forum](https://www.dmtf.org/standards/redfish)
- [DMTF Redfish Specification](https://www.dmtf.org/standards/redfish)

## Troubleshooting API Issues

### Common Problems

1. **Authentication Failures**
   - Verify credentials
   - Check account permissions
   - Ensure Redfish is enabled

2. **SSL Certificate Issues**
   - Use `-k` flag with curl for testing
   - Set `verify_ssl: false` in configuration
   - Install proper certificates

3. **Endpoint Not Found**
   - Verify iDRAC version
   - Check endpoint path
   - Use correct system ID

4. **Timeout Issues**
   - Increase timeout values
   - Check network connectivity
   - Reduce request complexity

### Debug Information

Enable verbose logging to see detailed API requests:

```bash
python idrac_collector.py --collect --verbose --log-level DEBUG
```

Check logs for API request details:
```bash
grep "GET request\|POST request" collector.log
```
