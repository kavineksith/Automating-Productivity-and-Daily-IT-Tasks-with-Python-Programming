# Documentation for IPv6 Address Processing Script

## Overview
This Python script provides a comprehensive suite of functionalities for processing IPv6 addresses. It allows users to input an IPv6 address with CIDR notation, convert and format the address into various representations, and perform subnet calculations. The script offers interactive commands to view or save results in multiple formats, including plain text, CSV, and JSON. Additionally, it provides error handling and screen management features to enhance usability and robustness.

## Features
- **IP Address Conversion**: Converts IPv6 addresses into hexadecimal, binary, and decimal formats.
- **Subnet Calculations**: Computes various subnet-related details including network address, broadcast address, subnet mask, and the number of hosts.
- **Address Formatting**: Formats IPv6 addresses and subnet details into human-readable formats and structured data.
- **Result Saving and Displaying**: Provides options to view or save results in plain text, CSV, or JSON formats.
- **Interactive Commands**: Allows users to clear the screen, exit the script, and interactively choose how to display or save results.

## Dependencies
- **Python 3.x**: The script is compatible with Python 3.x.
The script relies on the following Python standard libraries:
- `datetime`: For generating timestamps for file exports.
- `ipaddress`: For IPv6 address manipulations and subnet calculations.
- `json`: For handling JSON serialization and deserialization.
- `os`: For operating system functionalities such as screen clearing.
- `sys`: For system-specific parameters and functions.
- `time`: For implementing delays.

## Usage
To run the script, execute it in a Python environment. The script continuously prompts for an IPv6 address and CIDR notation until the user decides to exit. 

### Running the Script
1. Open a terminal or command prompt.
2. Execute the script with `python script_name.py` where `script_name.py` is the name of the file containing the script.
3. Enter an IPv6 address and CIDR notation in the format `2001:0db8:85a3:0000:0000:8a2e:0370:7334/64` when prompted.
4. Follow the interactive prompts to view or save the results.

## Interactive Commands
- **`clear`**: Clears the terminal screen using appropriate system commands.
- **`exit`**: Terminates the script and exits the program.

## Special Commands
- **`view`**: After entering the IPv6 address, choose this option to view results in plain text, CSV, or JSON format.
- **`save`**: After entering the IPv6 address, choose this option to save results in a specified format (plain text, CSV, or JSON) to the `./exports/` directory.

## Conclusion
This script is a powerful tool for IPv6 address analysis and subnet calculation. By offering a variety of conversion and formatting options, it caters to both educational and practical needs related to IP address management. The interactive nature of the script, combined with its ability to handle errors gracefully, ensures a user-friendly experience for anyone needing to work with IPv6 addresses and their related subnet information.

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## **Disclaimer:**
Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.