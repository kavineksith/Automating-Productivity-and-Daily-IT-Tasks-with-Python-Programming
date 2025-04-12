import sys
import ctypes
import win32com.client

# Custom Exception Class
class WMIException(Exception):
    """Custom exception for WMI related errors."""
    def __init__(self, message):
        super().__init__(message)

class WMIClient:
    def __init__(self):
        # Initialize COM
        ctypes.windll.ole32.CoInitialize(None)
        self.locator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        self.wmi = self.locator.ConnectServer(".", "root\\cimv2")
        self.module_list = [
            'Win32_OperatingSystem', 
            'Win32_ComputerSystem', 
            'Win32_Processor', 
            'Win32_PhysicalMemory',
            'Win32_LogicalMemoryConfiguration', 
            'Win32_DiskDrive', 
            'Win32_DiskPartition', 
            'Win32_LogicalDisk', 
            'Win32_NetworkAdapterConfiguration', 
            'Win32_Battery', 
            'Win32_Process', 
            'Win32_Service', 
            'Win32_NTLogEvent', 
            'Win32_Fan', 
            'Win32_TemperatureProbe', 
            'Win32_LogonSession', 
            'Win32_GroupPolicyObject'
        ]

    def get_wmi_data(self, query):
        """Execute the WMI query and return the results."""
        try:
            results = self.wmi.ExecQuery(query)
            return results
        except Exception as e:
            raise WMIException(f"Failed to get WMI data: {e}")

    def display_results(self, results, module_name):
        """Display the results of the WMI query."""
        if results is None:
            print(f"Error: Failed to retrieve data for {module_name}.")
        elif len(results) == 0:
            print(f"No data found for {module_name}.")
        else:
            print(f"\nResults for {module_name}:")
            for result in results:
                print("-" * 40)
                for prop in result.Properties_:
                    print(f"{prop.Name}: {prop.Value}")
                print("-" * 40)

    def run_selected_module(self, module_name):
        """Run WMI query for a specific module and display results."""
        if module_name not in self.module_list:
            raise ValueError(f"Module {module_name} not found in module list.")
        
        query = f"SELECT * FROM {module_name}"
        try:
            results = self.get_wmi_data(query)
            self.display_results(results, module_name)
        except WMIException as e:
            print(e)
        except Exception as e:
            print(f"Unexpected error: {e}")

    def run_all_modules(self):
        """Run WMI queries for all modules and display results."""
        for module_name in self.module_list:
            query = f"SELECT * FROM {module_name}"
            try:
                results = self.get_wmi_data(query)
                self.display_results(results, module_name)
            except WMIException as e:
                print(e)
            except Exception as e:
                print(f"Unexpected error: {e}")

def main():
    client = WMIClient()
    
    # Example usage
    if len(sys.argv) > 1 and sys.argv[1] in client.module_list:
        # Run for a specific module
        client.run_selected_module(sys.argv[1])
    else:
        # Run for all modules
        client.run_all_modules()

    sys.exit(0)

if __name__ == "__main__":
    main()
