# WMI System Information Collection Tool - Documentation

## Overview

This Python script provides a comprehensive tool for collecting system information and managing services through Windows Management Instrumentation (WMI), both locally and on remote Windows systems. The tool is designed for system administrators and IT professionals who need to gather detailed system information or manage services across multiple Windows machines.

## Features

- Collects detailed system information across multiple categories
- Supports both local and remote Windows systems
- Provides service management capabilities (start/stop services)
- Comprehensive error handling and logging
- JSON output for easy parsing and integration with other tools
- Modular design with separate collectors for different information types

## Requirements

- Python 3.6 or higher
- `wmi` package (install with `pip install wmi`)
- Windows operating system (local or remote target)
- Appropriate permissions for WMI access (admin rights recommended)

## Installation

1. Ensure Python 3.6+ is installed
2. Install the required package:
   ```
   pip install wmi
   ```
3. Download the script file (e.g., `wmi_system_info.py`)

## Usage

### General Syntax

```
python wmi_system_info.py [command] [options]
```

### Commands

#### 1. Collect All System Information

Collects all available system information.

```
python wmi_system_info.py all [--remote COMPUTER] [--username USER] [--password PASS]
```

**Options:**
- `--remote`: Remote computer name (optional, for local system if omitted)
- `--username`: Username for remote connection (required if --remote is specified)
- `--password`: Password for remote connection (required if --remote is specified)

**Example (local):**
```
python wmi_system_info.py all
```

**Example (remote):**
```
python wmi_system_info.py all --remote COMPUTER01 --username admin --password P@ssw0rd
```

#### 2. Collect Specific Information

Collects only specified categories of information.

```
python wmi_system_info.py specific --collectors COLLECTOR1 COLLECTOR2... [--remote COMPUTER] [--username USER] [--password PASS]
```

**Available Collectors:**
- `system`: Operating system, BIOS, and computer system information
- `hardware`: Processor, memory, disks, and network adapters
- `network`: Network configuration
- `process`: Running processes
- `service`: Installed services
- `event`: System event logs
- `task`: Scheduled tasks
- `disk`: Disk space information
- `software`: Installed software
- `user`: User accounts

**Example (local):**
```
python wmi_system_info.py specific --collectors system hardware network
```

**Example (remote):**
```
python wmi_system_info.py specific --collectors service process --remote COMPUTER02 --username admin --password P@ssw0rd
```

#### 3. Manage Services

Start or stop Windows services.

```
python wmi_system_info.py service --services SERVICE1 SERVICE2... --action [start|stop] [--remote COMPUTER] [--username USER] [--password PASS]
```

**Example (local):**
```
python wmi_system_info.py service --services Spooler --action stop
```

**Example (remote):**
```
python wmi_system_info.py service --services WinRM BITS --action start --remote COMPUTER03 --username admin --password P@ssw0rd
```

## Output Format

The script outputs JSON data to stdout with the following structure:

```json
{
    "status": "success|error",
    "operation": "operation_name",
    "connection": "local|remote",
    "data": {
        // Collected data or service operation results
    },
    "errors": [
        // Any error messages encountered
    ]
}
```

### Example Output (collect all)

```json
{
    "status": "success",
    "operation": "collect_all",
    "connection": "remote",
    "remote_machine": "COMPUTER01",
    "data": {
        "system": {
            "operating_systems": [
                {
                    "Caption": "Microsoft Windows 10 Enterprise",
                    "Version": "10.0.19042",
                    "OSArchitecture": "64-bit",
                    "InstallDate": "20210101000000.000000-000"
                }
            ],
            "bios": [
                {
                    "SMBIOSBIOSVersion": "1.2.3",
                    "Manufacturer": "Dell Inc.",
                    "SerialNumber": "ABC123",
                    "ReleaseDate": "20200101000000.000000-000"
                }
            ],
            "computer_systems": [
                {
                    "Name": "COMPUTER01",
                    "Manufacturer": "Dell Inc.",
                    "Model": "OptiPlex 7070",
                    "TotalPhysicalMemory": "17179869184"
                }
            ]
        },
        // Additional sections...
    }
}
```

### Example Output (service management)

```json
{
    "status": "success",
    "operation": "service_management",
    "connection": "local",
    "action": "start",
    "data": {
        "services": {
            "Spooler": {
                "status": "success",
                "action": "start"
            }
        }
    }
}
```

## Error Handling

The script provides detailed error information in the JSON output when something goes wrong:

```json
{
    "status": "error",
    "operation": "collect_all",
    "error": "Authentication error: Invalid credentials"
}
```

Common error scenarios:
- Authentication failures for remote connections
- Connection issues (firewall, WMI not enabled)
- Permission issues
- Invalid service names for service operations

## Logging

The script creates detailed log files in a `logs` directory with timestamps in the filename (e.g., `logs/wmi_info_20240101_123456.log`). Logs include:
- Connection attempts and status
- Collection operations
- Service management operations
- Detailed error information

## Security Considerations

1. **Credentials**: When running remote commands, credentials are passed as command-line arguments which may be visible in process lists. Consider:
   - Using environment variables for credentials
   - Prompting for password input
   - Clearing command history after use

2. **Permissions**: The script requires administrative privileges for most operations.

3. **Firewall**: For remote connections, ensure Windows Firewall allows WMI connections (typically port 135 and dynamic RPC ports).

## Customization

The script can be extended by adding new collector classes. To create a new collector:

1. Create a new class inheriting from `WmiInfoCollector`
2. Implement the `_gather_info()` method
3. Add the collector to the `collectors` dictionary in `WmiSystemInfo.__init__()`

Example new collector:

```python
class NewCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather new information"""
        info = {}
        # Implementation here
        return info
```

## Troubleshooting

1. **Connection Issues**:
   - Verify the remote computer is accessible
   - Check WMI is enabled on the remote computer
   - Verify firewall settings allow WMI traffic

2. **Authentication Issues**:
   - Verify username and password are correct
   - Ensure the account has administrative privileges
   - Check UAC restrictions on the remote computer

3. **Permission Issues**:
   - Run the script as Administrator
   - Verify WMI permissions on the remote computer

4. **Service Issues**:
   - Verify service names are correct
   - Check service dependencies

## License

This script is provided as-is without warranty. Users are free to modify and distribute it according to their needs.

## Support

For issues or feature requests, please contact the script author/maintainer.

---

This documentation provides comprehensive information about the WMI System Information Collection Tool. The script's modular design and detailed error handling make it suitable for both ad-hoc use and integration into larger system management solutions.