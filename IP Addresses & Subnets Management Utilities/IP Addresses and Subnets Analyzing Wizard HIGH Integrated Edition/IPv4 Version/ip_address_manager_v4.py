import ipaddress
import datetime
import json
import time
import os
import sys

# Custom Exception
class IPAddressError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

# Screen Manager Class
class ScreenManager:
    def __init__(self):
        self.clear_command = 'cls' if os.name == 'nt' else 'clear'

    def clear_screen(self):
        try:
            os.system(self.clear_command)
        except OSError as e:
            raise IPAddressError(f"Error clearing the screen: {e}")
        except KeyboardInterrupt:
            raise IPAddressError("Process interrupted by the user.")
        except Exception as e:
            raise IPAddressError(f"An error occurred: {e}")

# IPAddressConverter Class
class IPAddressConverter:
    def __init__(self, ip):
        self.ip = ip

    def to_decimal_and_hex(self):
        try:
            decimal_ip = int(ipaddress.ip_address(self.ip))
            hex_ip = hex(decimal_ip)
            return decimal_ip, hex_ip
        except ValueError as ve:
            raise IPAddressError(f"Error in to_decimal_and_hex: {ve}")

    def to_binary(self):
        try:
            binary_ip = format(int(ipaddress.ip_address(self.ip)), '032b')
            return binary_ip
        except ValueError as ve:
            raise IPAddressError(f"Error in to_binary: {ve}")

# SubnetCalculator Class
class SubnetCalculator:
    def __init__(self, ip, cidr):
        self.ip = ip
        self.cidr = cidr

    def calculate_subnet(self):
        try:
            network = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False)
            return network.network_address, network.netmask
        except ValueError as ve:
            raise IPAddressError(f"Error in calculate_subnet: {ve}")

    def subnet_mask_binary(self):
        try:
            subnet_mask = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False).netmask
            return bin(int(subnet_mask))
        except ValueError as ve:
            raise IPAddressError(f"Error in subnet_mask_binary: {ve}")

    def host_mask_calculator(self):
        try:
            host_mask = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False).hostmask
            return host_mask
        except ValueError as ve:
            raise IPAddressError(f"Error in host_mask_calculator: {ve}")

    def host_mask_binary(self):
        try:
            host_mask = self.host_mask_calculator()
            # Determine IP version
            ip_version = ipaddress.ip_address(self.ip).version
            if ip_version == 4:
                # For IPv4, use 32 bits
                return "{0:032b}".format(int(host_mask))
            else:
                raise ValueError("Invalid IP version")
        except ValueError as ve:
            raise IPAddressError(f"Error in host_mask_binary: {ve}")

    def subnet_binary(self):
        try:
            subnet = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False).network_address
            return format(int(subnet), '032b')
        except ValueError as ve:
            raise IPAddressError(f"Error in subnet_binary: {ve}")

    def usable_host_ip_range(self):
        try:
            network = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False)
            usable_hosts = list(network.hosts())
            first_host, last_host = usable_hosts[0], usable_hosts[-1]
            ip_range_str = f"{first_host} - {last_host}"
            return ip_range_str
        except ValueError as ve:
            raise IPAddressError(f"Error in usable_host_ip_range: {ve}")

    def broadcast_address(self):
        try:
            network = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False)
            return network.broadcast_address
        except ValueError as ve:
            raise IPAddressError(f"Error in broadcast_address: {ve}")

    def total_number_of_hosts(self):
        try:
            network = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False)
            return network.num_addresses
        except ValueError as ve:
            raise IPAddressError(f"Error in total_number_of_hosts: {ve}")

    def number_of_usable_hosts(self):
        try:
            network = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False)
            check_host_count = network.num_addresses - 2
            if check_host_count <= 0:
                return '0'
            else:
                return check_host_count
        except ValueError as ve:
            raise IPAddressError(f"Error in number_of_usable_hosts: {ve}")

    def network_address(self):
        try:
            network = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False)
            return network.network_address
        except ValueError as ve:
            raise IPAddressError(f"Error in network_address: {ve}")

    def cidr_notation(self):
        return self.cidr

    def ip_type(self):
        try:
            ip_obj = ipaddress.ip_address(self.ip)
            if isinstance(ip_obj, ipaddress.IPv4Address):
                if ip_obj.is_private:
                    return "Private IPv4"
                elif ip_obj.is_loopback:
                    return "Loopback IPv4"
                elif ip_obj.is_link_local:
                    return "Link-local IPv4"
                elif ip_obj.is_reserved:
                    return "Reserved IPv4"
                elif ip_obj.is_unspecified:
                    return "APIPA (Automatic Private IP Addressing) IPv4"
                elif ip_obj.is_multicast:
                    return "Multicast IPv4"
                elif ip_obj.is_global:
                    return "Public IPv4"
            else:
                return "Other IPv4"
        except ValueError:
            return None
        
    def ip_addresses_range(self):
        try:
            network = ipaddress.ip_network(self.ip + '/' + str(self.cidr), strict=False)
            usable_hosts = list(network.hosts())
            with open('./list.txt', 'a', encoding='utf-8') as ip_list:
                for host_ip in usable_hosts:
                    data = f'{str(host_ip)}\n'
                    ip_list.writelines(data)
                ip_list.close()
        except Exception as e:
            raise IPAddressError(f"Error in ip_addresses_range: {e}")


# Function to validate IP address format
def validate_ip_address(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


# Function to validate IPv4 class
def validate_ipv4_class(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        if isinstance(ip_obj, ipaddress.IPv4Address):
            first_octet = int(ip.split('.')[0])
            if 1 <= first_octet <= 126:
                return 'A'
            elif 128 <= first_octet <= 191:
                return 'B'
            elif 192 <= first_octet <= 223:
                return 'C'
            elif first_octet == 127:
                return 'Loopback'
            elif first_octet == 0 or first_octet == 255:
                return 'Reserved'
            else:
                return 'Unknown'
    except ValueError:
        return None


# Function to validate user input
def validate_input(ip_version, ip_address, cidr):
    try:
        if not ip_version or ip_version.lower() not in ['ipv4']:
            raise IPAddressError(f"Invalid {ip_version} address.")

        if not ip_address:
            raise IPAddressError(f"Invalid {ip_version} address.")

        if not validate_ip_address(ip_address):
            raise IPAddressError(f"Invalid {ip_version} address.")

        cidr = int(cidr)  # convert cidr string to integer value

        if cidr < 0 or (ip_version == 'ipv4' and cidr > 32):
            raise IPAddressError("Invalid CIDR notation")

        return ip_address, cidr
    except Exception as e:
        raise IPAddressError(f"Input validation error: {e}")


# Function to chunk string into parts
def chunkstring(string, length):
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def timestamp_for_export_results():
    formatted_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime


def result_to_txt_and_csv_save(file_formating_name, labels, data, type):
    try:
        if len(labels) != len(data):
            raise IPAddressError("Lengths of labels and data do not match.")

        # Specify the file path where you want to write the data
        export_name = f'{timestamp_for_export_results()}-{file_formating_name}'
        if type == 'txt':
            file_name = f'{export_name}.txt'
        else:
            file_name = f'{export_name}.csv'
        
        file_path = f'./exports/{file_name}'

        # Check if the file exists and is not empty
        file_exists = os.path.isfile(file_path)
        file_empty = os.stat(file_path).st_size == 0 if file_exists else True

        # Open the file in append mode ('a') and specify newline='' to manage newlines manually
        with open(file_path, 'a', encoding='utf-8', newline='') as csv_file:
            if file_empty:
                # Write labels as the first line if the file is empty
                labels_line = ','.join(labels)
                csv_file.write(labels_line + '\n')
            
            # Write data as subsequent lines
            data_line = ','.join(data)
            csv_file.write(data_line + '\n')
    except Exception as e:
        raise IPAddressError(f"Unexpected error in result_to_txt_and_csv_save: {e}")


def result_to_json_save(file_formating_name, labels, data):
    try:
        if len(labels) != len(data):
            raise IPAddressError("Lengths of labels and data do not match.")
        
        # Specify the file path where you want to write the data
        export_name = f'{timestamp_for_export_results()}-{file_formating_name}'
        file_name = f'{export_name}.json'
        file_path = f'./exports/{file_name}'
        
        # Create a dictionary from labels and data
        json_data = {label: value for label, value in zip(labels, data)}

        # Serialize dictionary to JSON format
        json_output = json.dumps(json_data, indent=4, ensure_ascii=False)
        
        # Write JSON data to file
        with open(file_path, 'a', encoding='utf-8') as json_file:
            json_file.write(json_output)
    except Exception as e:
        raise IPAddressError(f"Unexpected error in result_to_json_save: {e}")


# Function to format results for display as a plain text
def result_to_plain_text_display(labels, data):
    try:
        if len(labels) != len(data):
            raise IPAddressError("Lengths of labels and data do not match.")
        
        # Join labels and data into a single string with a delimiter (newline in this case)
        result = '\n'.join([f"{label}: {value}" for label, value in zip(labels, data)])

        print(f'{result}')

    except Exception as e:
        raise IPAddressError(f"Error in result_to_plain_text_display: {e}")


# Function to format results for display as a json object
def result_to_json_format_display(labels, data):
    try:
        if len(labels) != len(data):
            raise IPAddressError("Lengths of labels and data do not match.")

        # Join labels and data into separate strings with each pair on a new line
        json_data = {label: value for label, value in zip(labels, data)}

        json_output = json.dumps(json_data, indent=4)

        print(f'{json_output}')
    except Exception as e:
        raise IPAddressError(f"Error in result_to_json_format_display: {e}")


# Function to format results for display as a csv format
def result_to_csv_format_display(labels, data):
    try:
        if len(labels) != len(data):
            raise IPAddressError("Lengths of labels and data do not match.")
        
        # Join labels and data into separate strings with each pair on a new line
        result = ','.join([f"{label}: {value}" for label, value in zip(labels, data)])

        print(f'{result}')
    except Exception as e:
        raise IPAddressError(f"Error in result_to_csv_format_display: {e}")


def multiple_ip_management():
    try:
        # Specify the file path where you want to read the data
        source_file = input('Enter the file path: ').strip()
        if not os.path.exists(source_file):
            raise IPAddressError(f'Cannot find {source_file} location')
        with open(source_file, 'r', encoding='utf-8') as ip_list:
            ip_list_items = ip_list.readlines()

        for ip_value_item in ip_list_items:
            data_process(ip_value_item.strip())
    except Exception as e:
        raise IPAddressError(f"Error in result_to_csv_format_display: {e}")


def result_saving_and_displaying(format_name, labels, data):
    try:
        output_category = input('Which method would you like (view/save): ').strip()

        if output_category.lower() == 'view':
            output_choice = input('Which output format would you like (txt/csv/json): ').strip().lower()

            if output_choice == 'txt':
                result_to_plain_text_display(labels, data)
            elif output_choice == 'csv':
                result_to_csv_format_display(labels, data)
            elif output_choice == 'json':
                result_to_json_format_display(labels, data)
            else:
                raise IPAddressError("Invalid output format choice")
        
        elif output_category.lower() == 'save':
            output_choice = input('Which output format would you like (txt/csv/json): ').strip().lower()

            if output_choice == 'txt':
                result_to_txt_and_csv_save(format_name, labels, data, 'txt')
            elif output_choice == 'csv':
                result_to_txt_and_csv_save(format_name, labels, data, 'csv')
            elif output_choice == 'json':
                result_to_json_save(format_name, labels, data)
            else:
                raise IPAddressError("Invalid output format choice")
        else:
            raise IPAddressError("Invalid operation choice")
    except Exception as e:
        raise IPAddressError(f"Error in result_to_csv_format_display: {e}")


def ip_address_range_wizard():
    usr_ip_address = input("Enter IP address and CIDR notation (e.g., 192.168.1.1/24): ").strip()

    given_ip_address, given_cidr = usr_ip_address.strip().split('/')
    ip_address, cidr = validate_input("ipv4", given_ip_address, given_cidr)

    ip_class = validate_ipv4_class(ip_address)

    if ip_class:
        subnet_calculator = SubnetCalculator(ip_address, int(cidr))
        subnet_calculator.ip_addresses_range()
    else:
        raise IPAddressError(f'Please enter IPv4 Class IP Address insted {ip_address}....')


# Function to process data for an IP address
def data_process(usr_ip_address):
    try:
        given_ip_address, given_cidr = usr_ip_address.strip().split('/')
        ip_address, cidr = validate_input("ipv4", given_ip_address, given_cidr)

        ip_class = validate_ipv4_class(ip_address)

        subnet_calculator = SubnetCalculator(ip_address, int(cidr))
        ip_converter = IPAddressConverter(ip_address)

        ip_type = subnet_calculator.ip_type()
        network_address = subnet_calculator.network_address()
        broadcast_address = subnet_calculator.broadcast_address()
        total_hosts = subnet_calculator.total_number_of_hosts()
        usable_hosts = subnet_calculator.number_of_usable_hosts()
        cidr_notation = subnet_calculator.cidr_notation()
        usable_host_range = subnet_calculator.usable_host_ip_range()

        decimal_ip, hex_ip = ip_converter.to_decimal_and_hex()
        binary_ip = ip_converter.to_binary()

        subnet, subnet_mask = subnet_calculator.calculate_subnet()
        host_mask = subnet_calculator.host_mask_calculator()
        subnet_mask_bin = subnet_calculator.subnet_mask_binary()
        subnet_bin = subnet_calculator.subnet_binary()
        host_mask_bin = subnet_calculator.host_mask_binary()

        labels = [
            "IPv4 address",
            "IPv4 class",
            "IPv4 Type",
            "Network Address",
            "Broadcast Address",
            "Total Number of Hosts",
            "Number of Usable Hosts",
            "CIDR Notation",
            "Usable Host IP Range",
            "Decimal representation",
            "Hexadecimal representation",
            "Binary representation",
            "Subnet",
            "Subnet mask",
            "Host mask",
            "Subnet binary",
            "Subnet mask binary",
            "Host mask binary"
        ]

        data = [
            str(ip_address),
            str(ip_class),
            str(ip_type),
            str(network_address),
            str(broadcast_address),
            str(total_hosts),
            str(usable_hosts),
            f'/{cidr_notation}',
            str(usable_host_range),
            str(decimal_ip),
            str(hex_ip),
            '.'.join(chunkstring(binary_ip[0:], 8)),
            f'{subnet}/{cidr}',
            str(subnet_mask),
            str(host_mask),
            '.'.join(chunkstring(subnet_bin[0:], 8)),
            '.'.join(chunkstring(subnet_mask_bin[2:], 8)),
            '.'.join(chunkstring(host_mask_bin, 8))
        ]

        formatted_file_name = f'{given_ip_address}({given_cidr})'
        result_saving_and_displaying(formatted_file_name, labels, data)
    
    except Exception as e:
        raise IPAddressError(f"Error in data_process: {e}")


# Main function to handle user input and process IPs
def main():
    try:
        while True:
            usr_ip_address = input("Enter IP address and CIDR notation (e.g., 192.168.1.1/24): ").strip()

            if usr_ip_address.lower() == "clear":
                ScreenManager().clear_screen()
                continue
            elif usr_ip_address.lower() == "exit":
                print("Script Terminated...!!")
                time.sleep(2)
                ScreenManager().clear_screen()
                sys.exit(0)
            elif usr_ip_address.lower() == "multiple":
                multiple_ip_management()
            elif usr_ip_address.lower() == "addresses":
                ip_address_range_wizard()
            else:
                data_process(usr_ip_address)

    except KeyboardInterrupt:
        print("\nProcess interrupted by the user.")
        sys.exit(1)
    except IPAddressError as ipade:
        print(f'Error processing {usr_ip_address}: {ipade.message}')
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred processing {usr_ip_address}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.exit(0)
