## Documentation : Contact Manager

## Overview

The Contact Manager is a robust command-line application designed to manage a contact list through a JSON file. This Python-based tool allows users to perform essential contact management tasks including adding, updating, deleting, searching, and displaying contacts. With built-in error handling and support for regex-based searches, it offers a user-friendly and efficient way to maintain contact information.

## Features

- **Add Contacts**: Create and store new contacts with details such as name, phone number, and email address.
- **Delete Contacts**: Remove contacts from the list by specifying their index.
- **Update Contacts**: Modify existing contact details, including name, phone number, and email.
- **Search Contacts**: Search for contacts using regular expressions to match name, phone number, or email.
- **Display Contacts**: List all contacts in the system with their details.
- **Error Handling**: Gracefully manage errors related to file operations and user inputs.

## Dependencies

- **Python 3.x**: The script is compatible with Python 3.x. Ensure Python is installed on your system.
- **Standard Libraries**: Utilizes Python's built-in libraries:
  - `json` for handling JSON file operations.
  - `re` for regular expression operations.
  - `sys` for system-specific parameters and functions.

No external libraries or packages are required beyond the standard Python installation.

## Usage

To utilize the Contact Manager, follow these steps:

1. **Obtain the Script**: Download or clone the script file from the repository.
2. **Execute the Script**: Run the script using Python from your command line or terminal:

   ```bash
   python contact_manager.py
   ```

3. **Follow On-Screen Prompts**: Interact with the command-line interface to manage contacts.

## Interactive Commands

The Contact Manager provides the following interactive commands:

1. **Add Contact**:
   - **Command**: `1`
   - **Description**: Add a new contact with specified name, phone number, and email address.
   - **Prompts**: Name, Phone Number, Email Address.

2. **Delete Contact**:
   - **Command**: `2`
   - **Description**: Delete an existing contact based on its index in the contact list.
   - **Prompt**: Index of the contact to delete.

3. **Update Contact**:
   - **Command**: `3`
   - **Description**: Update details of an existing contact by specifying its index and new values for name, phone number, or email.
   - **Prompts**: Index of the contact to update, New Name (optional), New Phone Number (optional), New Email Address (optional).

4. **Search Contacts**:
   - **Command**: `4`
   - **Description**: Search for contacts using a regular expression pattern. Matches can be found in name, phone number, or email.
   - **Prompt**: Search pattern (regex).

5. **Display Contacts**:
   - **Command**: `5`
   - **Description**: Display all contacts in the list with their details.
   - **Output**: List of all contacts.

6. **Exit**:
   - **Command**: `6`
   - **Description**: Exit the Contact Manager application.

## Special Commands

- **Error Handling**: The application includes robust error handling for file operations (e.g., file not found, invalid JSON format) and user inputs (e.g., invalid index).
- **Keyboard Interrupt**: The script handles keyboard interruptions (Ctrl+C) gracefully, allowing users to exit the application without abrupt termination.

## Conclusion

The Contact Manager is a comprehensive tool for managing contact information through a command-line interface. It provides essential functionalities for adding, updating, deleting, and searching contacts while ensuring data integrity and user-friendly interactions. With its built-in error handling and flexible search capabilities, this script is well-suited for both personal use and small-scale contact management tasks.

For further customization or enhancement, users can modify the script to fit additional requirements or integrate more advanced features.

## **License**
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### **Disclaimer:**
Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.
