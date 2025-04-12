# Windows Management Interface (WMI) Local Device Analyzer Documentation

## Overview

This script provides comprehensive system information collection and service management capabilities for Windows systems using Windows Management Instrumentation (WMI). It's designed for local system analysis and administration, offering both command-line interface and programmatic access to system data.

## Key Features

- **System Information Collection**: Gather detailed hardware, software, and configuration data
- **Service Management**: Start and stop Windows services
- **Comprehensive Logging**: Detailed logging for troubleshooting and auditing
- **Modular Design**: Easily extensible with new collectors
- **Command-line Interface**: Simple CLI for both interactive and automated use

## Prerequisites

- Windows operating system
- Python 3.7+
- Administrative privileges (for certain operations)
- Required Python packages:
  - `wmi`
  - `pywin32`

## Installation

1. Ensure Python is installed
2. Install required packages:
   ```bash
   pip install wmi pywin32
   ```
3. Download or copy the script to your system

## Usage

### Command-line Interface

```
python wmi_analyzer.py [command] [options]
```

#### Available Commands:

1. **Collect all system information**:
   ```bash
   python wmi_analyzer.py all
   ```

2. **Collect specific information categories**:
   ```bash
   python wmi_analyzer.py specific --collectors system hardware network
   ```
   Available collectors: `system`, `hardware`, `network`, `process`, `service`, `event`, `task`, `disk`, `software`, `user`

3. **Manage services**:
   ```bash
   python wmi_analyzer.py service --services Spooler WinRM --action start
   ```
   Available actions: `start`, `stop`

### Output Format

The script outputs JSON-formatted data with the following structure:

```json
{
  "status": "success|error",
  "operation": "operation_name",
  "data": {
    "collector_name": {
      "collected_data": [...]
    }
  },
  "errors": ["error_messages"]
}
```

## Data Collection Categories

### 1. System Information
- Operating system details
- BIOS information
- Computer system properties

### 2. Hardware Information
- Processors
- Physical memory
- Disk drives
- Network adapters

### 3. Network Configuration
- IP-enabled network adapters
- IP addresses, subnets
- DNS servers

### 4. Process Information
- Running processes
- Process details (PID, command line, memory usage)

### 5. Service Information
- Installed services
- Service status
- Startup modes

### 6. Event Logs
- System event logs (limited to recent entries)

### 7. Scheduled Tasks
- Configured scheduled jobs

### 8. Disk Space
- Logical disks
- Free space, file systems

### 9. Installed Software
- Applications from Win32_Product
- Versions, vendors

### 10. User Accounts
- Local and domain user accounts
- Account status

## Service Management

The script can manage Windows services with the following capabilities:
- Start services
- Stop services

Note: Service management requires administrative privileges.

## Error Handling

The script handles various error conditions:
- WMI connection failures
- Invalid service operations
- Missing or invalid collectors
- Permission issues

Errors are logged and included in the JSON output.

## Logging

The script maintains detailed logs in the `logs` directory:
- Log files are timestamped (e.g., `wmi_info_20230101_120000.log`)
- Logs include:
  - Operation start/stop times
  - Collection results
  - Errors and warnings

## Security Considerations

1. **Run with appropriate privileges**: Some operations require administrative rights
2. **Log files**: Contain sensitive system information - protect accordingly
3. **Service management**: Use caution when stopping system services

## Integration

The `WmiSystemInfo` class can be imported and used in other Python scripts:

```python
from wmi_analyzer import WmiSystemInfo

wmi = WmiSystemInfo()
# Get all information
all_info = wmi.collect_all()
# Get specific information
hw_info = wmi.collect_specific(['hardware', 'network'])
# Manage services
wmi.manage_service('Spooler', 'stop')
```

## Example Use Cases

1. **System Inventory**: Collect complete system information for documentation
   ```bash
   python wmi_analyzer.py all > system_inventory.json
   ```

2. **Troubleshooting**: Check running processes and services
   ```bash
   python wmi_analyzer.py specific --collectors process service
   ```

3. **Service Maintenance**: Stop non-essential services for maintenance
   ```bash
   python wmi_analyzer.py service --services Spooler --action stop
   ```

4. **Disk Monitoring**: Check disk space usage
   ```bash
   python wmi_analyzer.py specific --collectors disk
   ```

## Extending the Script

New collectors can be added by:
1. Creating a new class that inherits from `WmiInfoCollector`
2. Implementing the `_gather_info()` method
3. Adding the collector to the `collectors` dictionary in `WmiSystemInfo.__init__()`

Example:

```python
class NewCollector(WmiInfoCollector):
    def _gather_info(self):
        info = []
        for item in self.c.Win32_ClassName():
            info.append({"Property": item.Property})
        return info
```

## Limitations

1. **Windows-only**: WMI is a Windows-specific technology
2. **Performance**: Some WMI queries can be resource-intensive
3. **Data completeness**: Not all WMI properties are collected by default

## Troubleshooting

1. **Connection errors**:
   - Verify WMI service is running
   - Check administrative privileges
   - Ensure Windows Management Instrumentation is enabled

2. **Missing data**:
   - Some WMI classes require elevated privileges
   - Check log files for specific errors

3. **Service management failures**:
   - Verify service names are correct
   - Check dependency services

## License

This script is provided as-is without warranty. Use at your own risk in production environments.

## Support

For issues or feature requests, please contact the maintainers or open an issue in the repository.