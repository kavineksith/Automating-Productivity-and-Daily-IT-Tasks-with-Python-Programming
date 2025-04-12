# **Wi-Fi Connector Script Documentation**

## **Overview**
This Python script allows users to create a Wi-Fi profile, save it to an XML configuration file, and connect to a Wi-Fi network. To ensure security, the Wi-Fi password is encrypted before being stored in the XML file, preventing sensitive data from being stored in clear text. The script utilizes AES encryption (CBC mode) to securely store the password, with a decryption function provided for when the password is needed for network operations.

## **Features**
- **Displays available Wi-Fi networks** using the `netsh wlan show networks` command.
- **Creates a Wi-Fi connection profile** in XML format, storing network credentials (SSID and encrypted password).
- **Encrypts the password** before storing it in the XML file using AES encryption.
- **Connects to a specified Wi-Fi network** using the `netsh wlan connect` command.
- **Logs all operations** (including successful and failed commands) to a log file (`network_operations.log`).

## **Dependencies**
The following libraries are required for this script:
- **cryptography**: For encrypting and decrypting the Wi-Fi password.
  
You can install it using:
```bash
pip install cryptography
```

## **Custom Exceptions**
- **FileWriteError**: Raised when there is an error while writing the XML file.
- **ConnectionError**: Raised when there is an error executing system commands for network operations.

## **Classes and Functions**

### `NetworkManager`
The `NetworkManager` class handles network operations, such as creating Wi-Fi profiles, connecting to networks, and executing system commands.

#### **Methods**:
- **`__init__(self, name, ssid, password, secret_key='mysecretkey')`**:
    - Initializes the `NetworkManager` instance with Wi-Fi profile name, SSID, password, and an optional encryption secret key (default is `'mysecretkey'`).
  
- **`create_new_connection(self)`**:
    - Encrypts the Wi-Fi password and creates a new connection profile in XML format.
    - Writes the profile to a file (profile name is the same as the Wi-Fi name, with `.xml` extension).
    - Executes the `netsh wlan add profile` command to add the Wi-Fi profile to the system.

- **`connect(self)`**:
    - Attempts to connect to the specified Wi-Fi network using the `netsh wlan connect` command.

- **`display_available_networks(self)`**:
    - Displays the available Wi-Fi networks using the `netsh wlan show networks` command.

- **`execute_command(self, command)`**:
    - Executes a system command and logs the result.
    - If the command fails, it raises a `ConnectionError` exception.

### `encrypt_password(password: str, secret_key: str) -> str`
Encrypts the provided password using AES encryption (CBC mode) and returns the base64-encoded encrypted password, including the initialization vector (IV).

#### **Parameters**:
- **`password`**: The password to encrypt.
- **`secret_key`**: The encryption key used for AES encryption. It is recommended to store the key securely (e.g., environment variable).

#### **Returns**:
- A base64-encoded string containing the IV and the encrypted password.

### `decrypt_password(encrypted_password: str, secret_key: str) -> str`
Decrypts the previously encrypted password.

#### **Parameters**:
- **`encrypted_password`**: The base64-encoded encrypted password string.
- **`secret_key`**: The encryption key used for AES decryption.

#### **Returns**:
- The decrypted plain-text password.

### `main()`
The main function of the script:
- Displays available networks.
- Prompts the user for the Wi-Fi profile name, SSID, and password.
- Creates a `NetworkManager` instance and attempts to create a new Wi-Fi connection.
- Handles exceptions and outputs error messages if the profile creation or connection fails.

## **Usage Instructions**
1. **Run the script**: 
   Execute the script by running it in your terminal or IDE:
   ```bash
   python wifi_connector.py
   ```

2. **Enter Wi-Fi details**: 
   When prompted, input the following details:
   - **Wi-Fi profile name** (a name for the profile, typically a recognizable network name).
   - **Wi-Fi SSID** (the name of the Wi-Fi network).
   - **Wi-Fi password** (the password for the network).

3. **Script actions**: 
   The script will:
   - Display available Wi-Fi networks.
   - Create a profile XML file with an encrypted password.
   - Add the profile using the `netsh wlan add profile` command.
   - Attempt to connect to the Wi-Fi network.

4. **Error handling**: 
   If any errors occur during file writing or network operations, the script will log them and display an appropriate error message to the user.

## **Security Considerations**
- **Password Encryption**: 
   The script ensures that the Wi-Fi password is encrypted before being stored in the XML file. AES encryption (CBC mode) is used with a random IV for each password to enhance security.
   
- **Secret Key**: 
   The encryption key (`secret_key`) used for AES encryption is stored as a static string in the code for simplicity. **In production**, it is important to securely manage the encryption key, such as by using environment variables or a key management service.

- **Logging**: 
   The script logs all operations, including any errors encountered during file creation or network command execution, to a log file (`network_operations.log`).

## **Example Output**
```plaintext
Enter Wi-Fi profile name: MyWiFiNetwork
Enter Wi-Fi SSID: MyWiFiSSID
Enter Wi-Fi password: MySecurePassword

Successfully created profile file: MyWiFiNetwork.xml
Executing command: netsh wlan add profile filename="MyWiFiNetwork.xml" interface=Wi-Fi
Command executed successfully: netsh wlan add profile filename="MyWiFiNetwork.xml" interface=Wi-Fi
Executing command: netsh wlan connect name="MyWiFiNetwork" ssid="MyWiFiSSID" interface=Wi-Fi
Command executed successfully: netsh wlan connect name="MyWiFiNetwork" ssid="MyWiFiSSID" interface=Wi-Fi
If you aren't connected to this network, try connecting with the correct password!
```

## **Log File Example (`network_operations.log`)**
```plaintext
2025-01-27 10:00:01,123 - INFO - Executing command: netsh wlan add profile filename="MyWiFiNetwork.xml" interface=Wi-Fi
2025-01-27 10:00:01,678 - INFO - Command executed successfully: netsh wlan add profile filename="MyWiFiNetwork.xml" interface=Wi-Fi
2025-01-27 10:00:02,234 - INFO - Executing command: netsh wlan connect name="MyWiFiNetwork" ssid="MyWiFiSSID" interface=Wi-Fi
2025-01-27 10:00:02,789 - INFO - Command executed successfully: netsh wlan connect name="MyWiFiNetwork" ssid="MyWiFiSSID" interface=Wi-Fi
```

## **Conclusion**
This script provides a secure and easy way to create Wi-Fi profiles and connect to Wi-Fi networks while ensuring that sensitive information, like passwords, is stored securely. By encrypting the password, this script mitigates the risk of exposing clear-text credentials. Make sure to manage the encryption key securely to maintain the overall security of the system.

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## **Disclaimer**

Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.
