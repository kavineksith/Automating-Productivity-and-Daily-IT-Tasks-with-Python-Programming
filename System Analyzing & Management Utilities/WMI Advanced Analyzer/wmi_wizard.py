import argparse
import json
import sys
import wmi
import logging
import logging.handlers
import datetime
import os
import re
import secrets
import hashlib
from abc import ABC, abstractmethod
import base64

# Custom exceptions
class WmiError(Exception):
    """Base exception for WMI-related errors"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ConnectionError(WmiError):
    """Exception raised when WMI connection fails"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class QueryError(WmiError):
    """Exception raised when a WMI query fails"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ServiceOperationError(WmiError):
    """Exception raised when a service operation fails"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SecurityViolationError(WmiError):
    """Exception raised when a security violation is detected"""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Encryption utilities for sensitive data
class Encryptor:
    def __init__(self, key_file='encryption.key'):
        self.key_file = key_file
        self.key = self._get_or_create_key()
    
    def _get_or_create_key(self):
        try:
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as f:
                    key = f.read()
            else:
                # Generate a new key with secrets
                key = secrets.token_bytes(32)
                # Save the key to a file with restricted permissions
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                # Restrict file permissions to owner only
                os.chmod(self.key_file, 0o600)
            return key
        except Exception as e:
            raise SecurityViolationError(f"Error handling encryption key: {str(e)}")
    
    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        
        # Simple encryption using XOR with key
        nonce = secrets.token_bytes(16)
        key_hash = hashlib.sha256(self.key + nonce).digest()
        
        encrypted = bytearray(len(data))
        for i in range(len(data)):
            encrypted[i] = data[i] ^ key_hash[i % len(key_hash)]
        
        result = nonce + bytes(encrypted)
        return base64.b64encode(result)
    
    def decrypt(self, encrypted_data):
        data = base64.b64decode(encrypted_data)
        
        # Extract nonce and ciphertext
        nonce = data[:16]
        ciphertext = data[16:]
        
        # Recreate key hash
        key_hash = hashlib.sha256(self.key + nonce).digest()
        
        # Decrypt using XOR
        decrypted = bytearray(len(ciphertext))
        for i in range(len(ciphertext)):
            decrypted[i] = ciphertext[i] ^ key_hash[i % len(key_hash)]
        
        return bytes(decrypted).decode()

# Add a function to generate file checksum
def generate_file_checksum(file_path, algorithm='sha256'):
    """
    Generate checksum for a file using the specified algorithm
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm to use (md5, sha1, sha256, sha512)
    
    Returns:
        str: Hexadecimal checksum of the file
    """
    hash_algorithms = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    if algorithm not in hash_algorithms:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    hash_obj = hash_algorithms[algorithm]()
    
    with open(file_path, 'rb') as f:
        # Read file in chunks to handle large files
        for chunk in iter(lambda: f.read(4096), b''):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()

# Setup logging
def setup_logger():
    """Configure and return logger with security enhancements and checksum generation"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        # Restrict directory permissions
        os.chmod(log_dir, 0o750)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/wmi_info_{timestamp}.log"
    
    logger = logging.getLogger('wmi_system_info')
    logger.setLevel(logging.INFO)
    
    # Create file handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Create sensitive data filter
    class SensitiveDataFilter(logging.Filter):
        def filter(self, record):
            if hasattr(record, 'msg') and isinstance(record.msg, str):
                # Redact passwords, keys, etc.
                record.msg = re.sub(r'password=[^\s,;]*', 'password=*****', record.msg)
                record.msg = re.sub(r'key=[^\s,;]*', 'key=*****', record.msg)
                # Add more patterns as needed
            return True
    
    sensitive_filter = SensitiveDataFilter()
    file_handler.addFilter(sensitive_filter)
    console_handler.addFilter(sensitive_filter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Set file permissions
    os.chmod(log_file, 0o640)
    
    # Add log file info to logger for checksum generation
    logger.log_file = log_file
    
    return logger

# Input validation utilities
def validate_service_name(service_name):
    """Validate service name to prevent command injection"""
    if not service_name or not isinstance(service_name, str):
        return False
    
    # Check for potentially dangerous characters
    dangerous_chars = ['&', '|', ';', '$', '`', '>', '<', '(', ')', '{', '}', '[', ']', '"', "'", '\\']
    if any(char in service_name for char in dangerous_chars):
        return False
    
    # Match against a whitelist pattern for Windows service names
    valid_pattern = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
    if not valid_pattern.match(service_name):
        return False
    
    return True

def validate_query(query):
    """Validate WMI query to prevent injection attacks"""
    if not query or not isinstance(query, str):
        return False
    
    # Check for multiple statements
    if ';' in query:
        return False
    
    # Check for potentially dangerous patterns
    dangerous_patterns = ['--', '/*', '*/', 'xp_', 'exec', 'execute']
    if any(pattern in query.lower() for pattern in dangerous_patterns):
        return False
    
    return True

# Base class for all WMI information gatherers
class WmiInfoCollector(ABC):
    def __init__(self, wmi_connection, logger):
        """
        Initialize with WMI connection and logger
        
        Args:
            wmi_connection: WMI connection object
            logger: Logger instance
        """
        self.c = wmi_connection
        self.logger = logger
        self.section_name = self.__class__.__name__
        self.encryptor = Encryptor()
    
    def collect(self):
        """Template method for collecting WMI information"""
        self.logger.info(f"Starting collection: {self.section_name}")
        try:
            result = self._gather_info()
            self.logger.info(f"Successfully collected {self.section_name}")
            # Check for sensitive data before returning
            result = self._sanitize_sensitive_data(result)
            return result
        except WmiError as e:
            self.logger.error(f"Error collecting {self.section_name}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in {self.section_name}: {str(e)}")
            raise QueryError(f"Failed to query {self.section_name}: Generic error occurred")
    
    @abstractmethod
    def _gather_info(self):
        """Implement in child classes to gather specific information"""
        pass
    
    def _sanitize_sensitive_data(self, data):
        """Remove or encrypt sensitive information before returning"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        sensitive_keys = [
            'password', 'key', 'secret', 'credential', 'token',
            'privatekey', 'passphrase', 'connectionstring'
        ]
        
        for key, value in data.items():
            # Check if this is a sensitive key
            if any(sensitive_word in key.lower() for sensitive_word in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            # Recurse into nested dictionaries
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_sensitive_data(value)
            # Recurse into lists
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_sensitive_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
                
        return sanitized
    
    def _safe_query(self, query):
        """Execute a WMI query with validation"""
        if not validate_query(query):
            raise SecurityViolationError(f"Invalid or potentially dangerous query: {query}")
        
        try:
            return self.c.query(query)
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise QueryError(f"Query execution failed: {str(e)}")

class SystemInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather system information"""
        info = {"operating_systems": [], "bios": [], "computer_systems": []}
        
        # Use safe methods to retrieve information
        try:
            for os_info in self.c.Win32_OperatingSystem():
                os_data = {
                    "Caption": os_info.Caption if hasattr(os_info, 'Caption') else None,
                    "Version": os_info.Version if hasattr(os_info, 'Version') else None,
                    "OSArchitecture": os_info.OSArchitecture if hasattr(os_info, 'OSArchitecture') else None,
                    "InstallDate": os_info.InstallDate if hasattr(os_info, 'InstallDate') else None
                }
                # Remove None values
                os_data = {k: v for k, v in os_data.items() if v is not None}
                info["operating_systems"].append(os_data)
                
            for bios in self.c.Win32_BIOS():
                bios_data = {
                    "SMBIOSBIOSVersion": bios.SMBIOSBIOSVersion if hasattr(bios, 'SMBIOSBIOSVersion') else None,
                    "Manufacturer": bios.Manufacturer if hasattr(bios, 'Manufacturer') else None,
                    "SerialNumber": bios.SerialNumber if hasattr(bios, 'SerialNumber') else None,
                    "ReleaseDate": bios.ReleaseDate if hasattr(bios, 'ReleaseDate') else None
                }
                # Remove None values
                bios_data = {k: v for k, v in bios_data.items() if v is not None}
                info["bios"].append(bios_data)
                
            for system in self.c.Win32_ComputerSystem():
                system_data = {
                    "Name": system.Name if hasattr(system, 'Name') else None,
                    "Manufacturer": system.Manufacturer if hasattr(system, 'Manufacturer') else None,
                    "Model": system.Model if hasattr(system, 'Model') else None,
                    "TotalPhysicalMemory": system.TotalPhysicalMemory if hasattr(system, 'TotalPhysicalMemory') else None
                }
                # Remove None values
                system_data = {k: v for k, v in system_data.items() if v is not None}
                info["computer_systems"].append(system_data)
        except Exception as e:
            self.logger.error(f"Error collecting system info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info

class HardwareInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather hardware information"""
        info = {"processors": [], "physical_memory": [], "video_controllers": [], "sound_devices": []}
        
        try:
            # Collect processor information
            for processor in self.c.Win32_Processor():
                proc_data = {
                    "Name": processor.Name if hasattr(processor, 'Name') else None,
                    "Manufacturer": processor.Manufacturer if hasattr(processor, 'Manufacturer') else None,
                    "Description": processor.Description if hasattr(processor, 'Description') else None,
                    "NumberOfCores": processor.NumberOfCores if hasattr(processor, 'NumberOfCores') else None,
                    "NumberOfLogicalProcessors": processor.NumberOfLogicalProcessors if hasattr(processor, 'NumberOfLogicalProcessors') else None,
                    "CurrentClockSpeed": processor.CurrentClockSpeed if hasattr(processor, 'CurrentClockSpeed') else None,
                    "MaxClockSpeed": processor.MaxClockSpeed if hasattr(processor, 'MaxClockSpeed') else None
                }
                # Remove None values
                proc_data = {k: v for k, v in proc_data.items() if v is not None}
                info["processors"].append(proc_data)
            
            # Collect physical memory information
            for memory in self.c.Win32_PhysicalMemory():
                mem_data = {
                    "Capacity": memory.Capacity if hasattr(memory, 'Capacity') else None,
                    "Manufacturer": memory.Manufacturer if hasattr(memory, 'Manufacturer') else None,
                    "DeviceLocator": memory.DeviceLocator if hasattr(memory, 'DeviceLocator') else None,
                    "Speed": memory.Speed if hasattr(memory, 'Speed') else None,
                    "FormFactor": memory.FormFactor if hasattr(memory, 'FormFactor') else None
                }
                # Remove None values
                mem_data = {k: v for k, v in mem_data.items() if v is not None}
                info["physical_memory"].append(mem_data)
            
            # Collect video controller information
            for video in self.c.Win32_VideoController():
                video_data = {
                    "Name": video.Name if hasattr(video, 'Name') else None,
                    "VideoProcessor": video.VideoProcessor if hasattr(video, 'VideoProcessor') else None,
                    "AdapterRAM": video.AdapterRAM if hasattr(video, 'AdapterRAM') else None,
                    "DriverVersion": video.DriverVersion if hasattr(video, 'DriverVersion') else None,
                    "CurrentHorizontalResolution": video.CurrentHorizontalResolution if hasattr(video, 'CurrentHorizontalResolution') else None,
                    "CurrentVerticalResolution": video.CurrentVerticalResolution if hasattr(video, 'CurrentVerticalResolution') else None
                }
                # Remove None values
                video_data = {k: v for k, v in video_data.items() if v is not None}
                info["video_controllers"].append(video_data)
            
            # Collect sound device information
            for sound in self.c.Win32_SoundDevice():
                sound_data = {
                    "Name": sound.Name if hasattr(sound, 'Name') else None,
                    "Manufacturer": sound.Manufacturer if hasattr(sound, 'Manufacturer') else None,
                    "Status": sound.Status if hasattr(sound, 'Status') else None,
                    "DeviceID": sound.DeviceID if hasattr(sound, 'DeviceID') else None
                }
                # Remove None values
                sound_data = {k: v for k, v in sound_data.items() if v is not None}
                info["sound_devices"].append(sound_data)
                
        except Exception as e:
            self.logger.error(f"Error collecting hardware info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info


class NetworkInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather network adapter information"""
        info = {"network_adapters": [], "ip_configurations": [], "network_shares": []}
        
        try:
            # Collect network adapter information
            for adapter in self.c.Win32_NetworkAdapter():
                adapter_data = {
                    "Name": adapter.Name if hasattr(adapter, 'Name') else None,
                    "Description": adapter.Description if hasattr(adapter, 'Description') else None,
                    "MACAddress": adapter.MACAddress if hasattr(adapter, 'MACAddress') else None,
                    "AdapterType": adapter.AdapterType if hasattr(adapter, 'AdapterType') else None,
                    "NetConnectionID": adapter.NetConnectionID if hasattr(adapter, 'NetConnectionID') else None,
                    "NetEnabled": adapter.NetEnabled if hasattr(adapter, 'NetEnabled') else None,
                    "Speed": adapter.Speed if hasattr(adapter, 'Speed') else None
                }
                # Remove None values
                adapter_data = {k: v for k, v in adapter_data.items() if v is not None}
                info["network_adapters"].append(adapter_data)
            
            # Collect IP configuration information
            for ip_config in self.c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                ip_data = {
                    "Description": ip_config.Description if hasattr(ip_config, 'Description') else None,
                    "IPAddress": ip_config.IPAddress if hasattr(ip_config, 'IPAddress') else None,
                    "IPSubnet": ip_config.IPSubnet if hasattr(ip_config, 'IPSubnet') else None,
                    "DefaultIPGateway": ip_config.DefaultIPGateway if hasattr(ip_config, 'DefaultIPGateway') else None,
                    "DHCPEnabled": ip_config.DHCPEnabled if hasattr(ip_config, 'DHCPEnabled') else None,
                    "DHCPServer": ip_config.DHCPServer if hasattr(ip_config, 'DHCPServer') else None,
                    "DNSServerSearchOrder": ip_config.DNSServerSearchOrder if hasattr(ip_config, 'DNSServerSearchOrder') else None
                }
                # Remove None values
                ip_data = {k: v for k, v in ip_data.items() if v is not None}
                info["ip_configurations"].append(ip_data)
            
            # Collect network share information
            for share in self.c.Win32_Share():
                share_data = {
                    "Name": share.Name if hasattr(share, 'Name') else None,
                    "Path": share.Path if hasattr(share, 'Path') else None,
                    "Description": share.Description if hasattr(share, 'Description') else None,
                    "Type": share.Type if hasattr(share, 'Type') else None
                }
                # Remove None values
                share_data = {k: v for k, v in share_data.items() if v is not None}
                info["network_shares"].append(share_data)
                
        except Exception as e:
            self.logger.error(f"Error collecting network info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info


class ProcessInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather process information"""
        info = {"processes": []}
        
        try:
            # Collect process information
            query = "SELECT * FROM Win32_Process"
            processes = self._safe_query(query)
            
            for process in processes:
                # Get owner information safely
                owner = None
                try:
                    owner_method = process.GetOwner()
                    if owner_method and owner_method[0] == 0:
                        owner = f"{owner_method[2]}\\{owner_method[1]}" if owner_method[2] else owner_method[1]
                except:
                    pass
                
                process_data = {
                    "Name": process.Name if hasattr(process, 'Name') else None,
                    "ProcessId": process.ProcessId if hasattr(process, 'ProcessId') else None,
                    "ExecutablePath": process.ExecutablePath if hasattr(process, 'ExecutablePath') else None,
                    "CommandLine": process.CommandLine if hasattr(process, 'CommandLine') else None,
                    "CreationDate": process.CreationDate if hasattr(process, 'CreationDate') else None,
                    "Priority": process.Priority if hasattr(process, 'Priority') else None,
                    "WorkingSetSize": process.WorkingSetSize if hasattr(process, 'WorkingSetSize') else None,
                    "Owner": owner
                }
                # Remove None values
                process_data = {k: v for k, v in process_data.items() if v is not None}
                info["processes"].append(process_data)
                
        except Exception as e:
            self.logger.error(f"Error collecting process info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info


class ServiceInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather service information"""
        info = {"services": []}
        
        try:
            # Collect service information
            for service in self.c.Win32_Service():
                service_data = {
                    "Name": service.Name if hasattr(service, 'Name') else None,
                    "DisplayName": service.DisplayName if hasattr(service, 'DisplayName') else None,
                    "State": service.State if hasattr(service, 'State') else None,
                    "StartMode": service.StartMode if hasattr(service, 'StartMode') else None,
                    "PathName": service.PathName if hasattr(service, 'PathName') else None,
                    "StartName": service.StartName if hasattr(service, 'StartName') else None,
                    "Description": service.Description if hasattr(service, 'Description') else None
                }
                # Remove None values
                service_data = {k: v for k, v in service_data.items() if v is not None}
                info["services"].append(service_data)
                
        except Exception as e:
            self.logger.error(f"Error collecting service info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info


class EventLogCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather event log information with safe limits"""
        info = {"event_logs": [], "recent_events": []}
        max_events = 100  # Limit to prevent huge result sets
        
        try:
            # Collect event log information
            for event_log in self.c.Win32_NTEventLogFile():
                log_data = {
                    "LogFileName": event_log.LogFileName if hasattr(event_log, 'LogFileName') else None,
                    "Name": event_log.Name if hasattr(event_log, 'Name') else None,
                    "FileSize": event_log.FileSize if hasattr(event_log, 'FileSize') else None,
                    "NumberOfRecords": event_log.NumberOfRecords if hasattr(event_log, 'NumberOfRecords') else None,
                    "MaxFileSize": event_log.MaxFileSize if hasattr(event_log, 'MaxFileSize') else None
                }
                # Remove None values
                log_data = {k: v for k, v in log_data.items() if v is not None}
                info["event_logs"].append(log_data)
            
            # Collect recent events from System and Application logs
            for log_type in ["System", "Application"]:
                try:
                    # Safely construct query with event limit
                    query = f"SELECT * FROM Win32_NTLogEvent WHERE Logfile = '{log_type}' AND TimeGenerated > '20220101000000.000000-000'"
                    events = self._safe_query(query)
                    
                    count = 0
                    for event in events:
                        if count >= max_events // 2:  # Split limit between logs
                            break
                            
                        event_data = {
                            "LogFile": event.Logfile if hasattr(event, 'Logfile') else None,
                            "EventCode": event.EventCode if hasattr(event, 'EventCode') else None,
                            "Type": event.Type if hasattr(event, 'Type') else None,
                            "TimeGenerated": event.TimeGenerated if hasattr(event, 'TimeGenerated') else None,
                            "SourceName": event.SourceName if hasattr(event, 'SourceName') else None,
                            "Message": event.Message if hasattr(event, 'Message') else None
                        }
                        # Remove None values
                        event_data = {k: v for k, v in event_data.items() if v is not None}
                        info["recent_events"].append(event_data)
                        count += 1
                except Exception as e:
                    self.logger.error(f"Error collecting events from {log_type} log: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Error collecting event log info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info


class ScheduledTaskCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather scheduled task information"""
        info = {"scheduled_tasks": []}
        
        try:
            # We'll use the appropriate class for scheduled tasks
            # This uses COM object query because WMI doesn't directly expose scheduled tasks
            import win32com.client
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            folders = [scheduler.GetFolder('\\')]
            
            while folders:
                current_folder = folders.pop(0)
                
                # Add subfolders to the list
                for subfolder in current_folder.GetFolders(0):
                    folders.append(subfolder)
                
                # Get tasks from the current folder
                for task in current_folder.GetTasks(0):
                    task_def = task.Definition
                    actions = []
                    
                    # Collect information about task actions
                    for action_index in range(1, task_def.Actions.Count + 1):
                        action = task_def.Actions.Item(action_index)
                        action_type = {0: "Execute", 5: "Com Handler", 6: "Send Email", 7: "Show Message"}.get(action.Type, "Unknown")
                        
                        if action.Type == 0:  # Execute action
                            actions.append({
                                "Type": action_type,
                                "Path": action.Path if hasattr(action, 'Path') else None,
                                "Arguments": action.Arguments if hasattr(action, 'Arguments') else None,
                                "WorkingDirectory": action.WorkingDirectory if hasattr(action, 'WorkingDirectory') else None
                            })
                        else:
                            actions.append({"Type": action_type})
                    
                    # Collect task information
                    task_data = {
                        "Name": task.Name,
                        "Path": task.Path,
                        "Enabled": task.Enabled,
                        "LastRunTime": str(task.LastRunTime) if hasattr(task, 'LastRunTime') else None,
                        "NextRunTime": str(task.NextRunTime) if hasattr(task, 'NextRunTime') else None,
                        "Actions": actions,
                        "State": {1: "Disabled", 2: "Queued", 3: "Ready", 4: "Running"}.get(task.State, "Unknown")
                    }
                    
                    # Remove None values
                    task_data = {k: v for k, v in task_data.items() if v is not None}
                    info["scheduled_tasks"].append(task_data)
                
        except ImportError:
            self.logger.error("win32com module not available, cannot collect scheduled task information")
            info["error"] = "win32com module not available - cannot collect scheduled task information"
        except Exception as e:
            self.logger.error(f"Error collecting scheduled task info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info


class DiskSpaceCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather disk space information"""
        info = {"logical_disks": [], "physical_disks": []}
        
        try:
            # Collect logical disk information
            for disk in self.c.Win32_LogicalDisk(DriveType=3):  # Type 3 = Local Disk
                disk_data = {
                    "DeviceID": disk.DeviceID if hasattr(disk, 'DeviceID') else None,
                    "VolumeName": disk.VolumeName if hasattr(disk, 'VolumeName') else None,
                    "FileSystem": disk.FileSystem if hasattr(disk, 'FileSystem') else None,
                    "Size": disk.Size if hasattr(disk, 'Size') else None,
                    "FreeSpace": disk.FreeSpace if hasattr(disk, 'FreeSpace') else None
                }
                
                # Calculate used space and percentage
                if disk.Size and disk.FreeSpace:
                    disk_data["UsedSpace"] = int(disk.Size) - int(disk.FreeSpace)
                    disk_data["UsedPercentage"] = round((disk_data["UsedSpace"] / int(disk.Size)) * 100, 2)
                
                # Remove None values
                disk_data = {k: v for k, v in disk_data.items() if v is not None}
                info["logical_disks"].append(disk_data)
            
            # Collect physical disk information
            for disk in self.c.Win32_DiskDrive():
                disk_data = {
                    "Model": disk.Model if hasattr(disk, 'Model') else None,
                    "SerialNumber": disk.SerialNumber if hasattr(disk, 'SerialNumber') else None,
                    "Size": disk.Size if hasattr(disk, 'Size') else None,
                    "InterfaceType": disk.InterfaceType if hasattr(disk, 'InterfaceType') else None,
                    "Partitions": disk.Partitions if hasattr(disk, 'Partitions') else None,
                    "Status": disk.Status if hasattr(disk, 'Status') else None
                }
                # Remove None values
                disk_data = {k: v for k, v in disk_data.items() if v is not None}
                info["physical_disks"].append(disk_data)
                
        except Exception as e:
            self.logger.error(f"Error collecting disk space info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info


class InstalledSoftwareCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather installed software information"""
        info = {"installed_software": []}
        
        try:
            # Query for installed software using WMI
            for product in self.c.Win32_Product():
                product_data = {
                    "Name": product.Name if hasattr(product, 'Name') else None,
                    "Vendor": product.Vendor if hasattr(product, 'Vendor') else None,
                    "Version": product.Version if hasattr(product, 'Version') else None,
                    "InstallDate": product.InstallDate if hasattr(product, 'InstallDate') else None,
                    "InstallLocation": product.InstallLocation if hasattr(product, 'InstallLocation') else None
                }
                # Remove None values
                product_data = {k: v for k, v in product_data.items() if v is not None}
                info["installed_software"].append(product_data)
            
            # Also try registry method as fallback, since Win32_Product can be incomplete
            try:
                import winreg
                registry_keys = [
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
                    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
                ]
                
                for reg_root, reg_path in registry_keys:
                    try:
                        registry_key = winreg.OpenKey(reg_root, reg_path)
                        
                        for i in range(0, winreg.QueryInfoKey(registry_key)[0]):
                            try:
                                subkey_name = winreg.EnumKey(registry_key, i)
                                subkey = winreg.OpenKey(registry_key, subkey_name)
                                
                                try:
                                    product_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                    # Skip entries that don't have a display name
                                    if not product_name:
                                        continue
                                        
                                    # Check if this software is already in our list
                                    if any(p.get("Name") == product_name for p in info["installed_software"]):
                                        continue
                                    
                                    product_data = {"Name": product_name}
                                    
                                    # Try to get additional values
                                    registry_values = [
                                        ("Publisher", "Publisher", "Vendor"),
                                        ("DisplayVersion", "DisplayVersion", "Version"),
                                        ("InstallDate", "InstallDate", "InstallDate"),
                                        ("InstallLocation", "InstallLocation", "InstallLocation")
                                    ]
                                    
                                    for reg_name, reg_key, dict_key in registry_values:
                                        try:
                                            value = winreg.QueryValueEx(subkey, reg_key)[0]
                                            if value:
                                                product_data[dict_key] = value
                                        except:
                                            pass
                                    
                                    # Only add if we have more than just the name
                                    if len(product_data) > 1:
                                        info["installed_software"].append(product_data)
                                except:
                                    pass
                                finally:
                                    winreg.CloseKey(subkey)
                            except:
                                pass
                    except:
                        pass
            except ImportError:
                self.logger.warning("winreg module not available, registry data not collected")
                
        except Exception as e:
            self.logger.error(f"Error collecting installed software info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info


class UserAccountCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather user account information"""
        info = {"user_accounts": [], "user_groups": []}
        
        try:
            # Collect user account information
            for user in self.c.Win32_UserAccount():
                user_data = {
                    "Name": user.Name if hasattr(user, 'Name') else None,
                    "FullName": user.FullName if hasattr(user, 'FullName') else None,
                    "Domain": user.Domain if hasattr(user, 'Domain') else None,
                    "SID": user.SID if hasattr(user, 'SID') else None,
                    "AccountType": user.AccountType if hasattr(user, 'AccountType') else None,
                    "Disabled": user.Disabled if hasattr(user, 'Disabled') else None,
                    "LocalAccount": user.LocalAccount if hasattr(user, 'LocalAccount') else None,
                    "Description": user.Description if hasattr(user, 'Description') else None
                }
                # Remove None values and sensitive information
                user_data = {k: v for k, v in user_data.items() if v is not None}
                info["user_accounts"].append(user_data)
            
            # Collect user group information
            for group in self.c.Win32_Group():
                group_data = {
                    "Name": group.Name if hasattr(group, 'Name') else None,
                    "Caption": group.Caption if hasattr(group, 'Caption') else None,
                    "Domain": group.Domain if hasattr(group, 'Domain') else None,
                    "SID": group.SID if hasattr(group, 'SID') else None,
                    "LocalAccount": group.LocalAccount if hasattr(group, 'LocalAccount') else None,
                    "Description": group.Description if hasattr(group, 'Description') else None
                }
                
                # Get group members
                try:
                    group_members = []
                    for association in self.c.Win32_GroupUser(GroupComponent=f'Win32_Group.Domain="{group.Domain}",Name="{group.Name}"'):
                        if hasattr(association, 'PartComponent'):
                            # The PartComponent property contains the reference to the user account
                            # Format is like: 'Win32_UserAccount.Domain="domain",Name="username"'
                            part_comp = association.PartComponent
                            if isinstance(part_comp, str):
                                # Extract member name from the string
                                import re
                                match = re.search(r'Name="([^"]+)"', part_comp)
                                if match:
                                    group_members.append(match.group(1))
                    
                    if group_members:
                        group_data["Members"] = group_members
                except Exception as e:
                    self.logger.warning(f"Error getting members for group {group.Name}: {str(e)}")
                
                # Remove None values
                group_data = {k: v for k, v in group_data.items() if v is not None}
                info["user_groups"].append(group_data)
                
        except Exception as e:
            self.logger.error(f"Error collecting user account info details: {str(e)}")
            # Return partial data instead of failing completely
            info["error"] = "Partial data collection - some information may be missing"
            
        return info

# Service management with enhanced security
class ServiceManager:
    def __init__(self, wmi_connection, logger):
        """
        Initialize service manager with enhanced security
        
        Args:
            wmi_connection: WMI connection object
            logger: Logger instance
        """
        self.c = wmi_connection
        self.logger = logger
        # Track operation attempts for rate limiting
        self.operation_timestamps = []
        # Maximum operations per minute
        self.rate_limit = 10
    
    def _check_rate_limit(self):
        """Implement rate limiting for service operations"""
        current_time = datetime.datetime.now()
        # Keep only timestamps from the last minute
        self.operation_timestamps = [
            ts for ts in self.operation_timestamps 
            if (current_time - ts).total_seconds() < 60
        ]
        
        # Check if we're over the limit
        if len(self.operation_timestamps) >= self.rate_limit:
            self.logger.warning(f"Rate limit exceeded: {len(self.operation_timestamps)} operations in last minute")
            return False
        
        # Add the current operation
        self.operation_timestamps.append(current_time)
        return True
    
    def start_service(self, service_name):
        """
        Start a Windows service with enhanced security
        
        Args:
            service_name: Name of the service to start
        
        Returns:
            bool: Success status
        """
        # Validate input
        if not validate_service_name(service_name):
            self.logger.error(f"Invalid service name: {service_name}")
            raise ServiceOperationError(f"Invalid service name")
        
        # Check rate limiting
        if not self._check_rate_limit():
            raise ServiceOperationError("Operation rate limit exceeded. Try again later.")
        
        self.logger.info(f"Attempting to start service: {service_name}")
        try:
            services = self.c.Win32_Service(Name=service_name)
            if not services:
                raise ServiceOperationError(f"Service {service_name} not found")
                
            service = services[0]
            if service.State == "Running":
                self.logger.info(f"Service {service_name} is already running")
                return True
                
            # Check security - example: prevent starting critical system services
            critical_services = ["WinDefend", "BITS", "CryptSvc", "Dhcp", "DNS", "lanmanserver"]
            if service_name in critical_services:
                self.logger.warning(f"Attempt to modify critical service: {service_name}")
                raise SecurityViolationError(f"Cannot modify critical system service: {service_name}")
            
            result = service.StartService()
            if result[0] == 0:
                self.logger.info(f"Successfully started service {service_name}")
                return True
            else:
                raise ServiceOperationError(f"Failed to start service {service_name}, return code: {result[0]}")
        except WmiError as e:
            self.logger.error(f"Service operation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error when starting service: {str(e)}")
            raise ServiceOperationError(f"Failed to start service: Generic error occurred")

    def stop_service(self, service_name):
        """
        Stop a Windows service with enhanced security
        
        Args:
            service_name: Name of the service to stop
        
        Returns:
            bool: Success status
        """
        # Validate input
        if not validate_service_name(service_name):
            self.logger.error(f"Invalid service name: {service_name}")
            raise ServiceOperationError(f"Invalid service name")
        
        # Check rate limiting
        if not self._check_rate_limit():
            raise ServiceOperationError("Operation rate limit exceeded. Try again later.")
        
        self.logger.info(f"Attempting to stop service: {service_name}")
        try:
            services = self.c.Win32_Service(Name=service_name)
            if not services:
                raise ServiceOperationError(f"Service {service_name} not found")
                
            service = services[0]
            if service.State == "Stopped":
                self.logger.info(f"Service {service_name} is already stopped")
                return True
            
            # Check security - example: prevent stopping critical system services
            critical_services = ["WinDefend", "BITS", "CryptSvc", "Dhcp", "DNS", "lanmanserver"]
            if service_name in critical_services:
                self.logger.warning(f"Attempt to modify critical service: {service_name}")
                raise SecurityViolationError(f"Cannot modify critical system service: {service_name}")
                
            result = service.StopService()
            if result[0] == 0:
                self.logger.info(f"Successfully stopped service {service_name}")
                return True
            else:
                raise ServiceOperationError(f"Failed to stop service {service_name}, return code: {result[0]}")
        except WmiError as e:
            self.logger.error(f"Service operation error: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error when stopping service: {str(e)}")
            raise ServiceOperationError(f"Failed to stop service: Generic error occurred")

class WmiSystemInfo:
    def __init__(self, use_credentials=False, username=None, password=None, domain=None):
        """Initialize WMI System Information class with secure connection options"""
        self.logger = setup_logger()
        self.logger.info("Initializing WMI System Information")
        
        # Record script execution for auditing
        self._log_execution()
        
        try:
            # Connect with appropriate credentials
            if use_credentials and username and password:
                if domain:
                    connection_str = f"{domain}\\{username}"
                else:
                    connection_str = username
                
                self.logger.info(f"Establishing WMI connection as {connection_str}")
                self.c = wmi.WMI(user=connection_str, password=password)
            else:
                self.logger.info("Establishing WMI connection with current credentials")
                self.c = wmi.WMI()
                
            self.logger.info("WMI connection established")
        except Exception as e:
            self.logger.critical(f"Failed to connect to WMI: {str(e)}")
            raise ConnectionError(f"Could not establish WMI connection: {str(e)}")
            
        # Initialize service manager with rate limiting
        self.service_manager = ServiceManager(self.c, self.logger)
        
        # Initialize collectors
        self.collectors = {
            "system": SystemInfoCollector(self.c, self.logger),
            "hardware": HardwareInfoCollector(self.c, self.logger),
            "network": NetworkInfoCollector(self.c, self.logger),
            "process": ProcessInfoCollector(self.c, self.logger),
            "service": ServiceInfoCollector(self.c, self.logger),
            "event": EventLogCollector(self.c, self.logger),
            "task": ScheduledTaskCollector(self.c, self.logger),
            "disk": DiskSpaceCollector(self.c, self.logger),
            "software": InstalledSoftwareCollector(self.c, self.logger),
            "user": UserAccountCollector(self.c, self.logger)
        }
    
    def _log_execution(self):
        """Log script execution for audit purposes"""
        try:
            audit_dir = 'audit'
            if not os.path.exists(audit_dir):
                os.makedirs(audit_dir)
                os.chmod(audit_dir, 0o750)
            
            audit_file = os.path.join(audit_dir, 'execution_log.txt')
            timestamp = datetime.datetime.now().isoformat()
            username = os.getenv('USERNAME') or os.getenv('USER') or 'unknown'
            
            with open(audit_file, 'a') as f:
                f.write(f"{timestamp} - Script executed by {username}\n")
            
            os.chmod(audit_file, 0o640)
        except Exception as e:
            self.logger.error(f"Error logging execution: {str(e)}")
    
    def collect_all(self):
        """Collect all WMI information with enhanced security"""
        self.logger.info("Starting collection of all WMI information")
        results = {}
        
        for name, collector in self.collectors.items():
            try:
                self.logger.info(f"Collecting {name} information")
                results[name] = collector.collect()
            except WmiError as e:
                self.logger.error(f"Error collecting {name} information: {str(e)}")
                results[name] = {"error": "Collection failed"}
            except Exception as e:
                self.logger.error(f"Unexpected error in {name} collection: {str(e)}")
                results[name] = {"error": "Unexpected error occurred"}
                
        self.logger.info("Completed collection of all WMI information")
        return results
    
    def collect_specific(self, collector_names):
        """Collect specific WMI information"""
        self.logger.info(f"Starting collection of specific WMI information: {collector_names}")
        results = {}
        
        for name in collector_names:
            if name in self.collectors:
                try:
                    self.logger.info(f"Collecting {name} information")
                    results[name] = self.collectors[name].collect()
                except WmiError as e:
                    self.logger.error(f"Error collecting {name} information: {str(e)}")
                    results[name] = {"error": "Collection failed"}
                except Exception as e:
                    self.logger.error(f"Unexpected error in {name} collection: {str(e)}")
                    results[name] = {"error": "Unexpected error occurred"}
            else:
                self.logger.warning(f"Unknown collector: {name}")
                results[name] = {"error": f"Unknown collector: {name}"}
                
        self.logger.info("Completed collection of specific WMI information")
        return results
    
    def manage_service(self, service_name, action):
        """
        Manage a service with enhanced security
        
        Args:
            service_name: Name of the service
            action: Action to perform (start/stop)
        
        Returns:
            bool: Success status
        """
        # Validate inputs to prevent command injection
        if not validate_service_name(service_name):
            raise ServiceOperationError(f"Invalid service name: {service_name}")
        
        valid_actions = ["start", "stop"]
        if not action or not isinstance(action, str) or action.lower() not in valid_actions:
            self.logger.error(f"Invalid service action: {action}")
            raise ServiceOperationError(f"Invalid service action: {action}")
        
        if action.lower() == "start":
            return self.service_manager.start_service(service_name)
        elif action.lower() == "stop":
            return self.service_manager.stop_service(service_name)

def main():
    """
    Main function with enhanced security for argument handling
    """
    # Set up secure argument parsing
    parser = argparse.ArgumentParser(description='Windows Management Interface (WMI) Information Collection Tool')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Parser for collecting all information
    all_parser = subparsers.add_parser('all', help='Collect all system information')
    
    # Parser for collecting specific information
    specific_parser = subparsers.add_parser('specific', help='Collect specific system information')
    specific_parser.add_argument('--collectors', nargs='+', required=True, 
                               help='List of collectors to run (system, hardware, network, process, service, event, task, disk, software, user)')
    
    # Parser for managing services
    service_parser = subparsers.add_parser('service', help='Manage system services')
    service_parser.add_argument('--services', nargs='+', required=True, help='List of services to manage')
    service_parser.add_argument('--action', choices=['start', 'stop'], required=True, help='Action to perform on services')
    
    # Add authentication options to all parsers
    for subparser in [all_parser, specific_parser, service_parser]:
        auth_group = subparser.add_argument_group('authentication')
        auth_group.add_argument('--use-credentials', action='store_true', help='Use specific credentials for WMI connection')
        auth_group.add_argument('--username', help='Username for WMI connection')
        auth_group.add_argument('--password', help='Password for WMI connection')
        auth_group.add_argument('--domain', help='Domain for WMI connection')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logger for main function
    logger = setup_logger()
    
    try:
        # Validate arguments for security
        if args.command == 'specific':
            valid_collectors = ['system', 'hardware', 'network', 'process', 'service', 'event', 'task', 'disk', 'software', 'user']
            for collector in args.collectors:
                if collector not in valid_collectors:
                    logger.error(f"Invalid collector: {collector}")
                    raise ValueError(f"Invalid collector: {collector}")
        
        if args.command == 'service':
            for service in args.services:
                if not validate_service_name(service):
                    logger.error(f"Invalid service name: {service}")
                    raise ValueError(f"Invalid service name: {service}")
        
        # Check authentication parameters
        if getattr(args, 'use_credentials', False):
            if not getattr(args, 'username', None) or not getattr(args, 'password', None):
                logger.error("Username and password required when use-credentials is specified")
                raise ValueError("Username and password required when use-credentials is specified")
        
        # Create WmiSystemInfo instance with proper credentials
        if getattr(args, 'use_credentials', False):
            wmi_info = WmiSystemInfo(
                use_credentials=True,
                username=args.username,
                password=args.password,
                domain=args.domain
            )
        else:
            wmi_info = WmiSystemInfo()
        
        # Initialize results dictionary
        results = {"status": "success", "data": {}, "errors": []}
        
        # Execute requested command
        if args.command == 'all':
            # Collect all information
            results["data"] = wmi_info.collect_all()
            results["operation"] = "collect_all"
        
        elif args.command == 'specific':
            # Collect specific information
            results["data"] = wmi_info.collect_specific(args.collectors)
            results["operation"] = "collect_specific"
            results["collectors"] = args.collectors
        
        elif args.command == 'service':
            # Manage services
            services = args.services
            action = args.action
            service_results = {}
            
            for service_name in services:
                try:
                    success = wmi_info.manage_service(service_name, action)
                    service_results[service_name] = {
                        "status": "success" if success else "failed",
                        "action": action
                    }
                except ServiceOperationError as e:
                    service_results[service_name] = {
                        "status": "error",
                        "action": action,
                        "error": str(e)
                    }
                    results["errors"].append(f"Error with service {service_name}: {str(e)}")
                except SecurityViolationError as e:
                    service_results[service_name] = {
                        "status": "security_violation",
                        "action": action,
                        "error": str(e)
                    }
                    results["errors"].append(f"Security violation with service {service_name}: {str(e)}")
            
            results["data"]["services"] = service_results
            results["operation"] = "service_management"
            results["action"] = action
        
        else:
            # No command provided, show help
            parser.print_help()
            return 1
        
        # Output results as JSON
        json_output = json.dumps(results, indent=4)
        print(json_output)
        
        # Also save results to a secure file
        result_dir = 'results'
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
            os.chmod(result_dir, 0o750)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"{result_dir}/wmi_results_{timestamp}.json"
        
        with open(result_file, 'w') as f:
            f.write(json_output)
        
        # Secure the results file
        os.chmod(result_file, 0o640)

        logger.info(f"Results saved to {result_file}")

        # Generate checksums for log file and results file
        log_checksum = generate_file_checksum(logger.log_file)
        result_checksum = generate_file_checksum(result_file)
        
        # Save checksums
        checksum_file = f"{result_dir}/checksums_{timestamp}.txt"
        with open(checksum_file, 'w') as f:
            f.write(f"Log file ({logger.log_file}): {log_checksum}\n")
            f.write(f"Result file ({result_file}): {result_checksum}\n")
        
        # Secure the checksum file
        os.chmod(checksum_file, 0o640)

        logger.info(f"Checksums saved to {checksum_file}")
        
        # Print checksums to console
        print(f"\nFile Checksums (SHA-256):")
        print(f"Log file: {log_checksum}")
        print(f"Result file: {result_checksum}")

        return 0
        
    except ValueError as e:
        logger.error(f"Argument validation error: {str(e)}")
        results = {
            "status": "error",
            "error": str(e),
            "operation": getattr(args, 'command', 'unknown')
        }
        print(json.dumps(results, indent=4))
        return 1
    except ConnectionError as e:
        logger.error(f"WMI connection error: {str(e)}")
        results = {
            "status": "error",
            "error": str(e),
            "operation": getattr(args, 'command', 'unknown')
        }
        print(json.dumps(results, indent=4))
        return 1
    except QueryError as e:
        logger.error(f"WMI query error: {str(e)}")
        results = {
            "status": "error",
            "error": str(e),
            "operation": getattr(args, 'command', 'unknown')
        }
        print(json.dumps(results, indent=4))
        return 1
    except ServiceOperationError as e:
        logger.error(f"Service operation error: {str(e)}")
        results = {
            "status": "error",
            "error": str(e),
            "operation": getattr(args, 'command', 'unknown')
        }
        print(json.dumps(results, indent=4))
        return 1
    except SecurityViolationError as e:
        logger.error(f"Security violation: {str(e)}")
        results = {
            "status": "security_violation",
            "error": str(e),
            "operation": getattr(args, 'command', 'unknown')
        }
        print(json.dumps(results, indent=4))
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        results = {
            "status": "error",
            "error": f"Unexpected error occurred: {str(e)}",
            "operation": getattr(args, 'command', 'unknown')
        }
        print(json.dumps(results, indent=4))
        return 1

if __name__ == "__main__":
    sys.exit(main())
