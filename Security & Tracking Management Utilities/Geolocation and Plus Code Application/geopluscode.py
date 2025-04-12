from geopy.geocoders import Nominatim
import openlocationcode
import sys

# Custom Error Classes
class AddressNotFoundError(Exception):
    """Exception raised when an address cannot be found."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CoordinatesNotFoundError(Exception):
    """Exception raised when coordinates cannot be found for an address."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidPlusCodeError(Exception):
    """Exception raised when an invalid Plus Code is provided."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class GeoLocationService:
    def __init__(self):
        """Initialize the GeoLocationService class with a geolocator."""
        self.geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    def get_coordinates(self, address):
        """Convert an address to latitude and longitude."""
        try:
            location = self.geolocator.geocode(address)
            if location:
                print(f"Address: {address}")
                print(f"Latitude: {location.latitude}")
                print(f"Longitude: {location.longitude}")
            else:
                raise AddressNotFoundError(f"Address '{address}' not found.")
        except AddressNotFoundError as e:
            # Provide a meaningful error message when address is not found
            print(f"Error: {e.message}")
        except Exception as e:
            # Catching all other unexpected errors
            print(f"An unexpected error occurred while geocoding the address: {e}")
    
    def get_address_from_coordinates(self, lat, lon):
        """Convert latitude and longitude to address."""
        try:
            location = self.geolocator.reverse((lat, lon))
            if location:
                print(f"Coordinates: Latitude: {lat}, Longitude: {lon}")
                print(f"Address: {location.address}")
            else:
                raise CoordinatesNotFoundError(f"No address found for coordinates: Latitude {lat}, Longitude {lon}")
        except CoordinatesNotFoundError as e:
            # Handle case where no address is found for coordinates
            print(f"Error: {e.message}")
        except Exception as e:
            # Catching any other unexpected errors
            print(f"An unexpected error occurred while reverse geocoding the coordinates: {e}")
    
    def get_plus_code_from_coordinates(self, lat, lon):
        """Convert latitude and longitude to Plus Code."""
        try:
            plus_code = openlocationcode.encode(lat, lon)
            if plus_code:
                print(f"Coordinates: Latitude: {lat}, Longitude: {lon}")
                print(f"Plus Code: {plus_code}")
            else:
                print("Error: Plus Code could not be generated for these coordinates.")
        except Exception as e:
            # Handle any errors encountered while generating Plus Code
            print(f"An error occurred while generating Plus Code: {e}")
    
    def get_coordinates_from_plus_code(self, plus_code):
        """Convert Plus Code to latitude and longitude."""
        try:
            location = openlocationcode.decode(plus_code)
            if location:
                print(f"Given Plus Code: {plus_code}")
                print(f"Coordinates: Latitude: {location.latitude}, Longitude: {location.longitude}")
            else:
                raise InvalidPlusCodeError(f"Invalid Plus Code: {plus_code}. No corresponding coordinates found.")
        except InvalidPlusCodeError as e:
            # Handle specific error if Plus Code is invalid
            print(f"Error: {e.message}")
        except ValueError:
            # Handle case for invalid format of Plus Code
            print("Error: Invalid Plus Code format.")
        except Exception as e:
            # Handle any other unexpected errors
            print(f"An unexpected error occurred while decoding the Plus Code: {e}")

# Main menu class
class Menu:
    def __init__(self):
        self.geo_service = GeoLocationService()
    
    def show_menu(self):
        """Display the menu options."""
        print("Choose an option:")
        print("1. Find Latitude and Longitude from Address")
        print("2. Find Address from Latitude and Longitude")
        print("3. Find Plus Code from Latitude and Longitude")
        print("4. Find Latitude and Longitude from Plus Code")
    
    def get_user_choice(self):
        """Get user choice from the menu."""
        try:
            choice = int(input("Enter your choice (1/2/3/4): ").strip())
            return choice
        except ValueError:
            print("Invalid choice. Please enter a number between 1 and 4.")
            return None
    
    def handle_choice(self, choice):
        """Handle the user's choice."""
        if choice == 1:
            address = input("Enter an address: ")
            self.geo_service.get_coordinates(address)
        elif choice == 2:
            try:
                lat = float(input("Enter Latitude: "))
                lon = float(input("Enter Longitude: "))
                self.geo_service.get_address_from_coordinates(lat, lon)
            except ValueError:
                print("Invalid coordinates. Please enter valid numbers.")
        elif choice == 3:
            try:
                lat = float(input("Enter Latitude: "))
                lon = float(input("Enter Longitude: "))
                self.geo_service.get_plus_code_from_coordinates(lat, lon)
            except ValueError:
                print("Invalid coordinates. Please enter valid numbers.")
        elif choice == 4:
            plus_code = input("Enter a Plus Code: ")
            self.geo_service.get_coordinates_from_plus_code(plus_code)
        else:
            print("Invalid choice. Please enter a valid number between 1 and 4.")

def main():
    """Main function to run the menu-driven program."""
    menu = Menu()
    
    while True:
        try:
            menu.show_menu()
            choice = menu.get_user_choice()
            if choice is not None:
                menu.handle_choice(choice)

            # Ask user if they want to perform another action
            confirmation  = input("Do you want to perform another operation? (y/n): ").strip().lower()
            if confirmation != 'y':
                print("Exiting the program.")
                break
        except KeyboardInterrupt:
            # Handle keyboard interrupt gracefully
            print("\nProgram interrupted. Exiting gracefully...")
            break
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
    sys.exit(0)
