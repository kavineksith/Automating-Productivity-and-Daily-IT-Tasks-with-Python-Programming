# WMIClient Python Script Documentation

## Overview

The `WMIClient` Python script is designed to interact with Windows Management Instrumentation (WMI) to gather and display various system information through WMI queries. By leveraging the `win32com.client` library, the script enables users to retrieve and visualize data from different WMI classes. This tool is useful for system administrators and IT professionals seeking to monitor and analyze system metrics, hardware configurations, and other system details on Windows platforms.

## Features

- **WMI Query Execution**: Execute WMI queries to retrieve information from various WMI classes.
- **Display Results**: Present the results in a readable format, including detailed information about properties and values.
- **Selective Module Query**: Run WMI queries for a specific module selected by the user.
- **All Modules Query**: Execute WMI queries for all predefined WMI modules and display the collected data.
- **Custom Exception Handling**: Use a custom exception class to manage and report WMI-related errors effectively.

## Dependencies

- **Python 3.x**: Requires Python 3.x for execution.
- **pywin32**: A Python library for interacting with Windows COM objects. Install using `pip install pywin32`.
- **ctypes**: A built-in Python library used for COM initialization.
- **win32com.client**: Part of the `pywin32` package used for WMI interactions.

## Usage

1. **Install Dependencies**: Ensure that `pywin32` is installed by running `pip install pywin32`.
2. **Save the Script**: Save the provided script as `wmi_client.py`.
3. **Run the Script**:
   - **To Query a Specific Module**: Provide the module name as a command-line argument.
     ```bash
     python wmi_client.py Win32_Processor
     ```
   - **To Query All Modules**: Run the script without any command-line arguments.
     ```bash
     python wmi_client.py
     ```

## Interactive Commands

- **Run Selected Module**: Queries a specific WMI module provided as a command-line argument. Displays detailed information about the selected module.
  - **Example**: `python wmi_client.py Win32_DiskDrive`
  - **Output**: Displays results for the `Win32_DiskDrive` module, showing all properties and their values.

- **Run All Modules**: Executes WMI queries for all predefined modules and displays their results.
  - **Command**: `python wmi_client.py`
  - **Output**: Sequentially displays results for each module in the list.

## Special Commands

- **Error Handling**: The script uses a custom exception class `WMIException` to handle and report errors during WMI query execution. This improves error management and provides clear feedback on issues.
  - **Example**: If a query fails, an error message like `Failed to get WMI data: [error details]` will be printed.

- **Module List**: The script includes a predefined list of WMI modules. The following modules are supported:
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

## Conclusion

The `WMIClient` script provides a powerful and flexible tool for querying and displaying system information using Windows Management Instrumentation. By encapsulating functionality within a class and incorporating robust error handling, it ensures a reliable and user-friendly experience. Whether you need detailed information from a specific WMI module or a comprehensive report on all supported modules, this script offers an efficient solution for system monitoring and analysis.

For further customization, users can extend the script to include additional WMI modules or modify the output format to suit their specific needs.
