# Enhanced WMI System Information Collection Tool - Comprehensive Documentation

## Overview

This enhanced Python script provides a secure and comprehensive tool for collecting system information and managing services through Windows Management Instrumentation (WMI), both locally and on remote Windows systems. The tool includes significant security enhancements, input validation, and audit capabilities for enterprise use.

## Key Security Enhancements

1. **Credential Protection**:
   - Redaction of sensitive data in logs
   - Secure credential handling
   - Domain authentication support

2. **Input Validation**:
   - Service name validation to prevent command injection
   - WMI query validation to prevent injection attacks
   - Argument validation for all commands

3. **Audit & Integrity**:
   - Execution logging with timestamps
   - File checksum generation (SHA-256)
   - Secure file permissions (640 for files, 750 for directories)

4. **Operation Security**:
   - Critical service protection
   - Operation rate limiting
   - Sensitive data redaction in outputs

5. **Data Protection**:
   - Encryption utilities for sensitive data
   - Sanitization of output data
   - Secure storage of results

## Features

- Collects detailed system information across 10 categories:
  - System information
  - Hardware details
  - Network configuration
  - Running processes
  - Service status
  - Event logs
  - Scheduled tasks
  - Disk space
  - Installed software
  - User accounts

- Secure service management capabilities:
  - Start services
  - Stop services
  - Protection for critical system services

- Enhanced logging and auditing:
  - Execution tracking
  - Checksum verification
  - Secure log storage

## Requirements

- Python 3.6 or higher
- Required packages:
  - `wmi` (install with `pip install wmi`)
  - `pywin32` (for scheduled tasks, install with `pip install pywin32`)
- Windows operating system (local or remote target)
- Appropriate permissions for WMI access (admin rights recommended)

## Installation

1. Ensure Python 3.6+ is installed
2. Install required packages:
   ```
   pip install wmi pywin32
   ```
3. Download the script file (e.g., `wmi_system_info_secure.py`)

## Usage

### General Syntax

```
python wmi_system_info_secure.py [command] [options]
```

### Commands

#### 1. Collect All System Information

Collects all available system information (10 categories).

```
python wmi_system_info_secure.py all [--use-credentials] [--username USER] [--password PASS] [--domain DOMAIN]
```

**Authentication Options**:
- `--use-credentials`: Flag to use specific credentials
- `--username`: Username for authentication
- `--password`: Password for authentication
- `--domain`: Domain for authentication (optional)

**Examples**:
- Local system:
  ```
  python wmi_system_info_secure.py all
  ```
- Remote with credentials:
  ```
  python wmi_system_info_secure.py all --use-credentials --username admin --password P@ssw0rd --domain CORP
  ```

#### 2. Collect Specific Information

Collects only specified categories of information.

```
python wmi_system_info_secure.py specific --collectors COLLECTOR1 COLLECTOR2... [authentication options]
```

**Available Collectors**:
- `system`: OS, BIOS, and computer system info
- `hardware`: Processors, memory, video, sound
- `network`: Adapters, IP config, shares
- `process`: Running processes
- `service`: Installed services
- `event`: Event logs
- `task`: Scheduled tasks
- `disk`: Disk space and physical disks
- `software`: Installed applications
- `user`: User accounts and groups

**Example**:
```
python wmi_system_info_secure.py specific --collectors system network service --use-credentials --username admin --password P@ssw0rd
```

#### 3. Manage Services

Start or stop Windows services with security checks.

```
python wmi_system_info_secure.py service --services SERVICE1 SERVICE2... --action [start|stop] [authentication options]
```

**Security Notes**:
- Validates service names to prevent injection
- Protects critical system services
- Implements rate limiting (10 operations/minute)

**Example**:
```
python wmi_system_info_secure.py service --services Spooler --action stop --use-credentials --username admin --password P@ssw0rd
```

## Output Format

The script outputs JSON data to stdout with the following structure:

```json
{
    "status": "success|error|security_violation",
    "operation": "operation_name",
    "data": {
        // Collected data or service operation results
    },
    "errors": [
        // Any error messages encountered
    ]
}
```

### Output Files

1. **Results File**:
   - Location: `results/wmi_results_TIMESTAMP.json`
   - Contains full output data
   - Permissions: 640 (owner read/write, group read)

2. **Log File**:
   - Location: `logs/wmi_info_TIMESTAMP.log`
   - Contains detailed execution log
   - Permissions: 640

3. **Checksum File**:
   - Location: `results/checksums_TIMESTAMP.txt`
   - Contains SHA-256 checksums of log and result files
   - Permissions: 640

## Security Best Practices

1. **Credential Handling**:
   - Avoid passing passwords on command line where possible
   - Consider using environment variables for sensitive data
   - Use service accounts with minimum required privileges

2. **File Security**:
   - Script creates secure directories (750 permissions)
   - Output files have restricted permissions (640)
   - Checksums verify file integrity

3. **Operation Safety**:
   - Critical services cannot be modified
   - Rate limiting prevents accidental flooding
   - All operations are logged

4. **Audit Trail**:
   - Execution logs track all script runs
   - Timestamps on all files
   - Checksums for verification

## Error Handling

The script provides detailed error information in the JSON output:

1. **Connection Errors**:
   - Authentication failures
   - WMI access issues

2. **Security Violations**:
   - Attempts to modify protected services
   - Invalid service names
   - Rate limit exceeded

3. **Collection Errors**:
   - Partial data collection
   - Permission issues
   - WMI query failures

Example error output:
```json
{
    "status": "error",
    "operation": "service_management",
    "error": "Cannot modify critical system service: WinDefend"
}
```

## Customization

### Adding New Collectors

1. Create a new class inheriting from `WmiInfoCollector`
2. Implement the `_gather_info()` method
3. Add the collector to the `collectors` dictionary in `WmiSystemInfo.__init__()`

Example template:
```python
class NewCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather new information"""
        info = {}
        # Implementation here
        return info
```

### Modifying Security Settings

1. **Critical Services**:
   - Modify `critical_services` list in `ServiceManager` class

2. **Rate Limiting**:
   - Adjust `rate_limit` in `ServiceManager.__init__()`

3. **Sensitive Data**:
   - Update `sensitive_keys` in `WmiInfoCollector._sanitize_sensitive_data()`

## Troubleshooting

1. **Connection Issues**:
   - Verify WMI is enabled on target
   - Check firewall settings (port 135 + RPC)
   - Ensure credentials have proper permissions

2. **Permission Errors**:
   - Run as Administrator
   - Check WMI permissions
   - Verify DCOM settings

3. **Missing Data**:
   - Some information requires elevated privileges
   - Certain WMI classes may not be available on all systems

4. **Script Errors**:
   - Check log files for details
   - Verify Python version and dependencies
   - Validate input parameters

## License

This script is provided as-is without warranty. Users are free to modify and distribute it according to their organizational policies.

---

This enhanced version provides enterprise-grade security features while maintaining all the functionality of the original tool. The added security measures make it suitable for use in regulated environments where data protection and auditability are critical requirements.