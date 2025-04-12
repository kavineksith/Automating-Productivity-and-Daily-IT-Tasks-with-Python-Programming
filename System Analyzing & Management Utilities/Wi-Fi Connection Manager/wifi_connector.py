import os
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64

# Setup logging
logging.basicConfig(filename="network_operations.log", level=logging.DEBUG, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Custom Exceptions
class ConnectionError(Exception):
    """Custom exception for connection-related errors."""
    def __init__(self, message):
        super().__init__(message)

class FileWriteError(Exception):
    """Custom exception for file writing errors."""
    def __init__(self, message):
        super().__init__(message)

# Utility function to encrypt data (password)
def encrypt_password(password: str, secret_key: str) -> str:
    """Encrypt the Wi-Fi password using AES encryption."""
    key = secret_key.encode('utf-8')[:32]  # AES requires a 32-byte key
    iv = os.urandom(16)  # Generate random IV for AES encryption

    # Pad the password to ensure it's a multiple of the block size (128-bit)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(password.encode()) + padder.finalize()

    # Encrypt the password
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Return the IV and the encrypted password, base64-encoded for storage
    return base64.b64encode(iv + encrypted_data).decode('utf-8')

# Utility function to decrypt password
def decrypt_password(encrypted_password: str, secret_key: str) -> str:
    """Decrypt the encrypted password."""
    encrypted_data = base64.b64decode(encrypted_password)
    
    # Extract the IV from the first 16 bytes
    iv = encrypted_data[:16]
    
    # Get the actual encrypted password
    encrypted_password = encrypted_data[16:]
    
    key = secret_key.encode('utf-8')[:32]  # AES requires a 32-byte key

    # Decrypt the password
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_password) + decryptor.finalize()

    # Unpad the decrypted data
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return unpadded_data.decode('utf-8')

# NetworkManager class handles network operations
class NetworkManager:
    
    def __init__(self, name, ssid, password, secret_key='mysecretkey'):
        self.name = name
        self.ssid = ssid
        self.password = password
        self.secret_key = secret_key  # The key used to encrypt passwords

    def create_new_connection(self):
        """Creates a new Wi-Fi connection with encrypted password."""
        # Encrypt the password before saving it to the XML file
        encrypted_password = encrypt_password(self.password, self.secret_key)
        
        # XML configuration to save the profile
        config = f"""<?xml version="1.0"?>
        <WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
            <name>{self.name}</name>
            <SSIDConfig>
                <SSID>
                    <name>{self.ssid}</name>
                </SSID>
            </SSIDConfig>
            <connectionType>ESS</connectionType>
            <connectionMode>auto</connectionMode>
            <MSM>
                <security>
                    <authEncryption>
                        <authentication>WPA2PSK</authentication>
                        <encryption>AES</encryption>
                        <useOneX>false</useOneX>
                    </authEncryption>
                    <sharedKey>
                        <keyType>passPhrase</keyType>
                        <protected>false</protected>
                        <keyMaterial>{encrypted_password}</keyMaterial>
                    </sharedKey>
                </security>
            </MSM>
        </WLANProfile>"""
        
        try:
            file_name = f"{self.name}.xml"
            with open(file_name, 'w') as file:
                file.write(config)
            logging.info(f"Successfully created profile file: {file_name}")
        except Exception as e:
            logging.error(f"Error while writing XML file: {str(e)}")
            raise FileWriteError(f"Failed to write file {self.name}.xml")

        # Add the profile using netsh
        command = f"netsh wlan add profile filename=\"{self.name}.xml\" interface=Wi-Fi"
        self.execute_command(command)
    
    def connect(self):
        """Connects to the network."""
        command = f"netsh wlan connect name=\"{self.name}\" ssid=\"{self.ssid}\" interface=Wi-Fi"
        self.execute_command(command)
    
    def display_available_networks(self):
        """Displays available Wi-Fi networks."""
        command = "netsh wlan show networks interface=Wi-Fi"
        self.execute_command(command)
    
    def execute_command(self, command):
        """Executes system command and logs the result."""
        try:
            logging.info(f"Executing command: {command}")
            result = os.system(command)
            if result != 0:
                raise ConnectionError(f"Failed to execute command: {command}")
            logging.info(f"Command executed successfully: {command}")
        except Exception as e:
            logging.error(f"Error executing command: {str(e)}")
            raise ConnectionError(f"Error occurred while executing command: {command}")

# Main function to interact with the user
def main():
    # Display available networks
    network_manager = NetworkManager('', '', '')
    network_manager.display_available_networks()

    # Input Wi-Fi name, SSID, and password
    name = input("Enter Wi-Fi profile name: ")
    ssid = input("Enter Wi-Fi SSID: ")
    password = input("Enter Wi-Fi password: ")

    # Ensure all required fields are filled in
    if not name or not ssid or not password:
        print("Error: Wi-Fi name, SSID, and password are required!")
        return

    # Create network manager with the user's input
    network_manager = NetworkManager(name, ssid, password)
    
    try:
        # Establish new connection
        network_manager.create_new_connection()

        # Connect to the network
        network_manager.connect()
        print("If you aren't connected to this network, try connecting with the correct password!")
    except FileWriteError as e:
        print(f"Error while writing the Wi-Fi profile: {e}")
    except ConnectionError as e:
        print(f"Error while connecting to the network: {e}")

if __name__ == "__main__":
    main()
