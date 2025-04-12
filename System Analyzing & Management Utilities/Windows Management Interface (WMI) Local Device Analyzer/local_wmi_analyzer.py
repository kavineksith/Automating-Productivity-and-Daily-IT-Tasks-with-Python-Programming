"""

For Locally Located Device Analyzing Script of Windows Management Interface (WMI)

"""

import argparse
import json
import sys
import wmi
import logging
import datetime
import os
from abc import ABC, abstractmethod

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

# Setup logging
def setup_logger():
    """Configure and return logger"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/wmi_info_{timestamp}.log"
    
    logger = logging.getLogger('wmi_system_info')
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    # console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)
    
    return logger

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
    
    def collect(self):
        """Template method for collecting WMI information"""
        self.logger.info(f"Starting collection: {self.section_name}")
        try:
            result = self._gather_info()
            self.logger.info(f"Successfully collected {self.section_name}")
            return result
        except WmiError as e:
            self.logger.error(f"Error collecting {self.section_name}: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in {self.section_name}: {str(e)}")
            raise QueryError(f"Failed to query {self.section_name}: {str(e)}")
    
    @abstractmethod
    def _gather_info(self):
        """Implement in child classes to gather specific information"""
        pass

class SystemInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather system information"""
        info = {"operating_systems": [], "bios": [], "computer_systems": []}
        
        for os_info in self.c.Win32_OperatingSystem():
            os_data = {
                "Caption": os_info.Caption,
                "Version": os_info.Version,
                "OSArchitecture": os_info.OSArchitecture,
                "InstallDate": os_info.InstallDate
            }
            info["operating_systems"].append(os_data)
            
        for bios in self.c.Win32_BIOS():
            bios_data = {
                "SMBIOSBIOSVersion": bios.SMBIOSBIOSVersion,
                "Manufacturer": bios.Manufacturer,
                "SerialNumber": bios.SerialNumber,
                "ReleaseDate": bios.ReleaseDate
            }
            info["bios"].append(bios_data)
            
        for system in self.c.Win32_ComputerSystem():
            system_data = {
                "Name": system.Name,
                "Manufacturer": system.Manufacturer,
                "Model": system.Model,
                "TotalPhysicalMemory": system.TotalPhysicalMemory
            }
            info["computer_systems"].append(system_data)
            
        return info

class HardwareInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather hardware information"""
        info = {"processors": [], "memory": [], "disks": [], "network_adapters": []}
        
        for processor in self.c.Win32_Processor():
            proc_data = {
                "Name": processor.Name,
                "NumberOfCores": processor.NumberOfCores,
                "MaxClockSpeed": processor.MaxClockSpeed,
                "L2CacheSize": processor.L2CacheSize,
                "L3CacheSize": processor.L3CacheSize,
                "DeviceID": processor.DeviceID
            }
            info["processors"].append(proc_data)
            
        for memory in self.c.Win32_PhysicalMemory():
            mem_data = {
                "Capacity": memory.Capacity,
                "Speed": memory.Speed,
                "Manufacturer": memory.Manufacturer,
                "DeviceLocator": memory.DeviceLocator,
                "PartNumber": memory.PartNumber
            }
            info["memory"].append(mem_data)
            
        for disk in self.c.Win32_DiskDrive():
            disk_data = {
                "Model": disk.Model,
                "Size": disk.Size,
                "InterfaceType": disk.InterfaceType,
                "MediaType": disk.MediaType,
                "SerialNumber": disk.SerialNumber
            }
            info["disks"].append(disk_data)
            
        for adapter in self.c.Win32_NetworkAdapter():
            if adapter.MACAddress:
                adapter_data = {
                    "Name": adapter.Name,
                    "MACAddress": adapter.MACAddress,
                    "AdapterType": adapter.AdapterType,
                    "Speed": adapter.Speed,
                    "DeviceID": adapter.DeviceID
                }
                info["network_adapters"].append(adapter_data)
                
        return info

class NetworkInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather network configuration information"""
        info = {"network_configs": []}
        
        try:
            for adapter in self.c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                adapter_data = {
                    "Description": adapter.Description,
                    "MACAddress": adapter.MACAddress,
                    "IPAddress": adapter.IPAddress,
                    "IPSubnet": adapter.IPSubnet,
                    "DefaultIPGateway": adapter.DefaultIPGateway,
                    "DNSServerSearchOrder": adapter.DNSServerSearchOrder
                }
                info["network_configs"].append(adapter_data)
        except Exception as e:
            self.logger.warning(f"Some network adapters might not have complete information: {str(e)}")
            
        return info

class ProcessInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather process information"""
        info = {"processes": []}
        
        for process in self.c.Win32_Process():
            try:
                process_data = {
                    "Name": process.Name,
                    "ProcessId": process.ProcessId,
                    "CommandLine": process.CommandLine,
                    "ExecutablePath": process.ExecutablePath,
                    "WorkingSetSize": process.WorkingSetSize,
                    "Priority": process.Priority
                }
                info["processes"].append(process_data)
            except Exception as e:
                self.logger.debug(f"Could not get complete info for process {process.Name}: {str(e)}")
                
        return info

class ServiceInfoCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather service information"""
        info = {"services": []}
        
        for service in self.c.Win32_Service():
            service_data = {
                "Name": service.Name,
                "DisplayName": service.DisplayName,
                "State": service.State,
                "StartMode": service.StartMode,
                "PathName": service.PathName,
                "StartName": service.StartName
            }
            info["services"].append(service_data)
            
        return info

class EventLogCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather system event logs (limited to recent entries)"""
        info = {"events": []}
        
        # Limit to last 100 events to avoid excessive logging
        try:
            query = "SELECT * FROM Win32_NTLogEvent WHERE Logfile='System' AND TimeGenerated > '20220101000000.000000-000'"
            for event in self.c.query(query)[:100]:
                event_data = {
                    "EventCode": event.EventCode,
                    "SourceName": event.SourceName,
                    "TimeGenerated": event.TimeGenerated,
                    "Type": event.Type,
                    "Message": event.Message
                }
                info["events"].append(event_data)
        except Exception as e:
            self.logger.warning(f"Limited event log collection: {str(e)}")
            
        return info

class ScheduledTaskCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather scheduled task information"""
        info = {"scheduled_tasks": []}
        
        try:
            for task in self.c.Win32_ScheduledJob():
                task_data = {
                    "JobId": task.JobId,
                    "Command": task.Command,
                    "RunTimes": task.RunTimes,
                    "Status": task.Status
                }
                info["scheduled_tasks"].append(task_data)
        except Exception as e:
            self.logger.warning(f"Scheduled task collection issue: {str(e)}")
            
        return info

class DiskSpaceCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather disk space information"""
        info = {"logical_disks": []}
        
        for disk in self.c.Win32_LogicalDisk(DriveType=3):
            disk_data = {
                "DeviceID": disk.DeviceID,
                "VolumeName": disk.VolumeName,
                "Size": disk.Size,
                "FreeSpace": disk.FreeSpace,
                "FileSystem": disk.FileSystem
            }
            info["logical_disks"].append(disk_data)
            
        return info

class InstalledSoftwareCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather installed software information"""
        info = {"installed_software": []}
        
        try:
            for app in self.c.Win32_Product():
                app_data = {
                    "Name": app.Name,
                    "Version": app.Version,
                    "Vendor": app.Vendor,
                    "InstallDate": app.InstallDate,
                    "InstallLocation": app.InstallLocation
                }
                info["installed_software"].append(app_data)
        except Exception as e:
            self.logger.warning(f"Software collection issue: {str(e)}")
            
        return info

class UserAccountCollector(WmiInfoCollector):
    def _gather_info(self):
        """Gather user account information"""
        info = {"user_accounts": []}
        
        for user in self.c.Win32_UserAccount():
            user_data = {
                "Name": user.Name,
                "Caption": user.Caption,
                "Domain": user.Domain,
                "SID": user.SID,
                "AccountType": user.AccountType,
                "Disabled": user.Disabled,
                "Status": user.Status
            }
            info["user_accounts"].append(user_data)
            
        return info

class ServiceManager:
    def __init__(self, wmi_connection, logger):
        """
        Initialize service manager
        
        Args:
            wmi_connection: WMI connection object
            logger: Logger instance
        """
        self.c = wmi_connection
        self.logger = logger
    
    def start_service(self, service_name):
        """
        Start a Windows service
        
        Args:
            service_name: Name of the service to start
        
        Returns:
            bool: Success status
        """
        self.logger.info(f"Attempting to start service: {service_name}")
        try:
            services = self.c.Win32_Service(Name=service_name)
            if not services:
                raise ServiceOperationError(f"Service {service_name} not found")
                
            service = services[0]
            if service.State == "Running":
                self.logger.info(f"Service {service_name} is already running")
                return True
                
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
            raise ServiceOperationError(f"Failed to start service: {str(e)}")
    
    def stop_service(self, service_name):
        """
        Stop a Windows service
        
        Args:
            service_name: Name of the service to stop
        
        Returns:
            bool: Success status
        """
        self.logger.info(f"Attempting to stop service: {service_name}")
        try:
            services = self.c.Win32_Service(Name=service_name)
            if not services:
                raise ServiceOperationError(f"Service {service_name} not found")
                
            service = services[0]
            if service.State == "Stopped":
                self.logger.info(f"Service {service_name} is already stopped")
                return True
                
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
            raise ServiceOperationError(f"Failed to stop service: {str(e)}")

class WmiSystemInfo:
    def __init__(self):
        """Initialize WMI System Information class"""
        self.logger = setup_logger()
        self.logger.info("Initializing WMI System Information")
        try:
            self.c = wmi.WMI()
            self.logger.info("WMI connection established")
        except Exception as e:
            self.logger.critical(f"Failed to connect to WMI: {str(e)}")
            raise ConnectionError(f"Could not establish WMI connection: {str(e)}")
            
        # Initialize service manager
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
    
    def collect_all(self):
        """Collect all WMI information"""
        self.logger.info("Starting collection of all WMI information")
        results = {}
        
        for name, collector in self.collectors.items():
            try:
                self.logger.info(f"Collecting {name} information")
                results[name] = collector.collect()
            except WmiError as e:
                self.logger.error(f"Error collecting {name} information: {str(e)}")
                results[name] = {"error": str(e)}
            except Exception as e:
                self.logger.error(f"Unexpected error in {name} collection: {str(e)}")
                results[name] = {"error": f"Unexpected error: {str(e)}"}
                
        self.logger.info("Completed collection of all WMI information")
        return results
        
    def collect_specific(self, collector_names):
        """
        Collect specific WMI information
        
        Args:
            collector_names: List of collector names to run
        
        Returns:
            dict: Collection results
        """
        self.logger.info(f"Starting collection of specific WMI information: {collector_names}")
        results = {}
        
        for name in collector_names:
            if name in self.collectors:
                try:
                    self.logger.info(f"Collecting {name} information")
                    results[name] = self.collectors[name].collect()
                except WmiError as e:
                    self.logger.error(f"Error collecting {name} information: {str(e)}")
                    results[name] = {"error": str(e)}
                except Exception as e:
                    self.logger.error(f"Unexpected error in {name} collection: {str(e)}")
                    results[name] = {"error": f"Unexpected error: {str(e)}"}
            else:
                self.logger.warning(f"Unknown collector: {name}")
                results[name] = {"error": f"Unknown collector: {name}"}
                
        self.logger.info("Completed collection of specific WMI information")
        return results
    
    def manage_service(self, service_name, action):
        """
        Manage a service
        
        Args:
            service_name: Name of the service
            action: Action to perform (start/stop)
        
        Returns:
            bool: Success status
        """
        if action.lower() == "start":
            return self.service_manager.start_service(service_name)
        elif action.lower() == "stop":
            return self.service_manager.stop_service(service_name)
        else:
            self.logger.error(f"Unknown service action: {action}")
            raise ServiceOperationError(f"Unknown service action: {action}")

def main():
    """
    Main function that handles command line arguments and executes requested operations
    """
    # Set up logger
    logger = setup_logger()
    logger.info("Starting WMI Information Collection Tool")
    
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
   
    # Parse arguments
    args = parser.parse_args()
    logger.debug(f"Parsed arguments: {args}")
   
    try:
        # Create WmiSystemInfo instance
        logger.info("Initializing WMI connection")
        wmi_info = WmiSystemInfo()
        logger.info("WMI connection initialized successfully")
       
        # Initialize results dictionary
        results = {"status": "success", "data": {}, "errors": []}
       
        # Execute requested command
        if args.command == 'all':
            # Collect all information
            logger.info("Collecting all system information")
            results["data"] = wmi_info.collect_all()
            logger.info("Successfully collected all system information")
            results["operation"] = "collect_all"
       
        elif args.command == 'specific':
            # Collect specific information
            collectors = args.collectors
            logger.info(f"Collecting specific information: {', '.join(collectors)}")
            results["data"] = wmi_info.collect_specific(collectors)
            logger.info(f"Successfully collected specific information: {', '.join(collectors)}")
            results["operation"] = "collect_specific"
            results["collectors"] = collectors
       
        elif args.command == 'service':
            # Manage services
            services = args.services
            action = args.action
            logger.info(f"Managing services: {', '.join(services)} - Action: {action}")
            service_results = {}
           
            for service_name in services:
                try:
                    logger.info(f"Attempting to {action} service: {service_name}")
                    success = wmi_info.manage_service(service_name, action)
                    service_results[service_name] = {
                        "status": "success" if success else "failed",
                        "action": action
                    }
                    if success:
                        logger.info(f"Successfully performed {action} on service: {service_name}")
                    else:
                        logger.warning(f"Failed to {action} service: {service_name}")
                except ServiceOperationError as e:
                    error_msg = f"Error with service {service_name}: {str(e)}"
                    logger.error(error_msg)
                    service_results[service_name] = {
                        "status": "error",
                        "action": action,
                        "error": str(e)
                    }
                    results["errors"].append(error_msg)
           
            results["data"]["services"] = service_results
            results["operation"] = "service_management"
            results["action"] = action
       
        else:
            # No command provided, show help
            logger.warning("No command specified, showing help")
            parser.print_help()
            return 1
       
        # Output results as JSON
        logger.info("Operation completed successfully")
        print(json.dumps(results, indent=4))
        logger.debug(f"Results: {json.dumps(results)}")
       
    except ConnectionError as e:
        error_msg = f"Connection error: {str(e)}"
        logger.error(error_msg)
        error_result = {
            "status": "error",
            "operation": args.command if hasattr(args, 'command') else "unknown",
            "error": error_msg
        }
        print(json.dumps(error_result, indent=4))
        return 1
   
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.exception(error_msg)  # This logs the full stack trace
        error_result = {
            "status": "error",
            "operation": args.command if hasattr(args, 'command') else "unknown",
            "error": error_msg
        }
        print(json.dumps(error_result, indent=4))
        return 1
   
    logger.info("Script execution completed")
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
