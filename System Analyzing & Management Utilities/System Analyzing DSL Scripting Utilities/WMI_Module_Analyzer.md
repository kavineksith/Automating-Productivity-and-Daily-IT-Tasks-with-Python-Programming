# WMI_Module_Explorer.ps1 Documentation

## Overview

`WMI_Module_Explorer.ps1` is a PowerShell script designed to facilitate the exploration and retrieval of information from various Windows Management Instrumentation (WMI) classes. This script provides an interactive interface for users to select WMI classes and fetch relevant system data, making it a valuable tool for system administrators and IT professionals. 

## Features

- **List WMI Modules**: Displays a comprehensive list of WMI classes available on the system, with an indication of their availability.
- **Interactive Module Selection**: Allows users to choose a WMI class by entering its corresponding index number.
- **Data Retrieval**: Fetches and displays information from the selected WMI class using the `Get-CimInstance` cmdlet.
- **Error Handling**: Includes robust error handling to manage invalid inputs and issues with data retrieval.
- **Availability Status**: Indicates which WMI classes are not available on the current Windows OS version.

## Dependencies

- **PowerShell**: The script is designed to run on Windows PowerShell. It is compatible with PowerShell versions available on Windows systems.
- **WMI/CIM**: The script utilizes the WMI (Windows Management Instrumentation) classes to gather system information.

## Usage

1. **Save the Script**: Save the script to a file named `WMI_Module_Explorer.ps1` on your Windows system.
2. **Open PowerShell**: Launch PowerShell with administrative privileges to ensure access to WMI classes and system data.
3. **Navigate to the Script Directory**: Use the `cd` command to navigate to the directory where the script is saved.
4. **Execute the Script**: Run the script by typing `.\WMI_Module_Explorer.ps1` and pressing Enter.

## Interactive Commands

1. **List Modules**: When executed, the script displays a list of available WMI classes with their indices. Each class is followed by an availability status indicating whether it is supported on the current OS.
2. **Select Module**: After listing the modules, the script prompts the user to enter the index number corresponding to the desired WMI class. This interactive command allows the user to select the class from which they want to retrieve information.

## Special Commands

- **Error Handling**: The script includes error handling for:
  - **Invalid Index**: If the user enters an index outside the valid range, the script provides a message indicating that the selection is invalid.
  - **Data Retrieval Issues**: If there is an issue with retrieving data from the selected WMI class (e.g., class not available), the script catches and displays an appropriate error message.

## Conclusion

`WMI_Module_Explorer.ps1` is a powerful and user-friendly tool for exploring WMI classes and retrieving system information on Windows platforms. Its interactive nature and robust error handling make it an essential utility for system administrators and IT professionals who need to query and manage system data efficiently. The script’s design ensures that users can easily navigate WMI classes, select relevant modules, and handle potential errors gracefully.

For further customization or enhancement, users may modify the script to include additional WMI classes or adapt the error handling logic based on specific requirements.

---

This documentation provides a structured overview of the script, making it easier for users to understand its purpose, features, and usage.