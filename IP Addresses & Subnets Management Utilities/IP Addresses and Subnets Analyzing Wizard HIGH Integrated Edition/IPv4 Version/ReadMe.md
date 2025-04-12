# Documentation for IP Address Management Script

## Overview
This Python script provides a comprehensive toolkit for managing and analyzing IP addresses. It allows users to convert IP addresses between different formats, calculate subnet details, and save or display results in various formats. The script supports IPv4 addresses and offers functionalities such as conversion to decimal, hexadecimal, and binary formats, subnet calculations, and saving results in text, CSV, or JSON formats. It also includes a mechanism for batch processing IP addresses from a file.

## Features
- **IP Address Conversion**: Converts IPv4 addresses to decimal, hexadecimal, and binary formats.
- **Subnet Calculations**: Calculates subnet details such as network address, broadcast address, subnet mask, host mask, and the number of usable hosts.
- **IP Address Validation**: Validates IP addresses and CIDR notation.
- **IP Address Range Management**: Computes and saves the range of usable IP addresses within a subnet.
- **Output Formats**: Displays or saves results in plain text, CSV, or JSON formats.
- **Batch Processing**: Processes multiple IP addresses from a file.
- **Interactive Commands**: Provides interactive command options for clearing the screen, terminating the script, or managing IP addresses.

## Dependencies
- **Python 3.x**: The script is compatible with Python 3.x.
- **Python Standard Library**:
  - `ipaddress`: For handling IP address and network operations.
  - `datetime`: For timestamping and date-time operations.
  - `json`: For JSON serialization and deserialization.
  - `os`: For interacting with the operating system, such as clearing the screen.
  - `sys`: For system-specific parameters and functions.
  - `time`: For handling time-related operations.

## Usage
To use the script, execute it from the command line. You can interact with it through a series of prompts and commands.
### Basic Command Flow
1. **Enter IP Address and CIDR**: Input the IP address and CIDR notation in the format `192.168.1.1/24`.
2. **Interactive Commands**:
   - `clear`: Clears the screen.
   - `exit`: Exits the script.
   - `multiple`: Processes IP addresses from a file.
   - `addresses`: Computes and saves the range of usable IP addresses.
3. **Display or Save Results**: Choose between viewing or saving results in various formats (TXT, CSV, JSON).

## Interactive Commands
- **`clear`**: Clears the terminal screen. This command uses `cls` on Windows and `clear` on Unix-based systems.
- **`exit`**: Terminates the script and exits the program.
- **`multiple`**: Allows processing of multiple IP addresses from a user-specified file.
- **`addresses`**: Initiates the IP address range wizard to compute and save usable IP address ranges.

## Special Commands
- **`view`**: After entering the IPv4 address, choose this option to view results in plain text, CSV, or JSON format.
- **`save`**: After entering the IPv4 address, choose this option to save results in a specified format (plain text, CSV, or JSON) to the `./exports/` directory.

## Conclusion
This IP Address Management Script provides a robust and flexible solution for handling IP addresses, performing subnet calculations, and managing IP ranges. Its interactive commands and support for various output formats make it a versatile tool for network administrators and IT professionals. By leveraging the script’s functionalities, users can efficiently manage and analyze IP address data, ensuring accurate and organized network configurations.

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## **Disclaimer:**
Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.