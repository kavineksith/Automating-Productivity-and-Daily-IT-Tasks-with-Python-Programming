## WMI Query Tools - PowerShell & Python Script Documentation

### Overview
This documentation covers two powerful tools designed for interacting with Windows Management Instrumentation (WMI):  
1. **WMI_Module_Explorer.ps1** - A PowerShell script for exploring and querying WMI classes.  
2. **WMIClient Python Script** - A Python script for querying WMI classes and displaying system information.

Both tools allow system administrators and IT professionals to retrieve valuable system data from Windows environments through an easy-to-use interface, supporting error handling and detailed reporting.

### Features
- **WMI Query Execution**: Retrieve system data from various WMI classes using either PowerShell or Python.
- **Interactive Interface**:
  - **PowerShell**: Users can select WMI classes interactively by entering an index number to retrieve class-specific data.
  - **Python**: Query specific WMI modules via command-line arguments or run all predefined queries at once.
- **Error Handling**: Both scripts include robust error management to handle invalid inputs and WMI query failures, ensuring smooth operation.
- **Availability Status**: Both scripts indicate which WMI classes are available on the system and which are not supported by the current OS version.

### Dependencies
- **PowerShell** (for `WMI_Module_Explorer.ps1`): Compatible with all versions of PowerShell on Windows.
- **Python 3.x** (for `WMIClient`): Requires Python 3.x and the `pywin32` library (`pip install pywin32`).
- **WMI/CIM**: Both tools leverage WMI (Windows Management Instrumentation) for gathering system data.

### Usage Instructions

#### **WMI_Module_Explorer.ps1 (PowerShell)**
1. Save the script as `WMI_Module_Explorer.ps1` on your system.
2. Open PowerShell as Administrator.
3. Navigate to the directory containing the script and run it using:
   ```powershell
   .\WMI_Module_Explorer.ps1
   ```
4. Select a WMI class by entering its index when prompted, and the script will fetch and display relevant data.

#### **WMIClient Python Script**
1. Install the necessary dependencies with:
   ```bash
   pip install pywin32
   ```
2. Save the script as `wmi_client.py`.
3. To query a specific WMI class, run the script with the class name as an argument:
   ```bash
   python wmi_client.py Win32_Processor
   ```
4. To query all available modules, run the script without arguments:
   ```bash
   python wmi_client.py
   ```

### Interactive Commands

#### **PowerShell Script**  
- **List Modules**: The script will display a list of all available WMI classes along with their availability status.
- **Select Module**: After displaying the list, the user can enter the index number to select a WMI class for querying.
- **Error Handling**: Handles invalid input and data retrieval issues, providing clear error messages.

#### **Python Script**  
- **Run Selected Module**: Provide a module name as an argument to query a specific WMI class:
  - Example:
    ```bash
    python wmi_client.py Win32_OperatingSystem
    ```
- **Run All Modules**: Execute the script without arguments to query all predefined WMI classes:
  ```bash
  python wmi_client.py
  ```
- **Error Handling**: The script uses custom exception handling to manage and report errors during the WMI query process.

### Supported WMI Classes (Both Scripts)
- `Win32_OperatingSystem`
- `Win32_ComputerSystem`
- `Win32_Processor`
- `Win32_PhysicalMemory`
- `Win32_LogicalMemoryConfiguration`
- `Win32_DiskDrive`
- `Win32_DiskPartition`
- `Win32_LogicalDisk`
- `Win32_NetworkAdapterConfiguration`
- `Win32_Battery`
- `Win32_Process`
- `Win32_Service`
- `Win32_NTLogEvent`
- `Win32_Fan`
- `Win32_TemperatureProbe`
- `Win32_LogonSession`
- `Win32_GroupPolicyObject`

### Conclusion
Both `WMI_Module_Explorer.ps1` (PowerShell) and `WMIClient.py` (Python) offer a flexible and user-friendly way to explore and query WMI data on Windows systems. These tools are ideal for system administrators and IT professionals who need to monitor system configurations, hardware, processes, and other metrics. With robust error handling and easy-to-understand interfaces, these scripts provide an efficient method for gathering system information via WMI. 

*For further customization, users can modify the scripts to include additional WMI classes or adapt the error handling logic to suit specific needs.*

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### **Disclaimer:**
Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.
