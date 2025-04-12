# Documentation for Geolocation and Plus Code Application

## Application Name: **GeoPlusCode**

**GeoPlusCode** is a Python-based application that provides comprehensive geolocation services, enabling the conversion of:
- Addresses to latitude and longitude.
- Latitude and longitude to addresses.
- Latitude and longitude to Plus Codes (Open Location Code).
- Plus Codes to latitude and longitude.

By utilizing external libraries such as `geopy` for geocoding and `openlocationcode` for Plus Code operations, **GeoPlusCode** offers an efficient and user-friendly solution for various geospatial tasks.

### Key Features:
- **Address to Coordinates**: Converts an address into latitude and longitude using the `geopy` library.
- **Coordinates to Address**: Converts latitude and longitude back into a human-readable address.
- **Coordinates to Plus Code**: Converts latitude and longitude into a Plus Code, providing an open-source alternative to traditional addressing.
- **Plus Code to Coordinates**: Converts a Plus Code back into latitude and longitude.
- **Error Handling**: Includes custom error handling for invalid addresses, coordinates, and Plus Codes.

## Requirements

- Python 3.10 or higher.
- The `geopy` library for geocoding services.
- The `openlocationcode` library for working with Plus Codes.

### Installation

To install the required dependencies, run the following command:
```bash
pip install geopy openlocationcode
```

## Architecture

### Key Components:

1. **GeoLocationService**: Provides methods for geocoding addresses and converting coordinates into various formats.
2. **Menu**: A simple command-line interface for interacting with the user, offering them options for geolocation-related tasks.
3. **Custom Error Handling**: Defined error classes to handle issues related to invalid addresses, coordinates, and Plus Codes.

Each class has a single responsibility, and errors are handled in a user-friendly manner, ensuring smooth user interaction.

## Custom Error Classes

The application defines several custom exceptions to handle specific error scenarios:

### 1. **AddressNotFoundError**
**Description**: Raised when an address cannot be found for the given input.

#### Constructor:
```python
def __init__(self, message):
    self.message = message
    super().__init__(self.message)
```
- **`message`**: Custom error message detailing why the address could not be found.

**Usage Example**:
```python
raise AddressNotFoundError("Address '123 Unknown St' not found.")
```

### 2. **CoordinatesNotFoundError**
**Description**: Raised when no coordinates can be found for a given address.

#### Constructor:
```python
def __init__(self, message):
    self.message = message
    super().__init__(self.message)
```
- **`message`**: Custom message indicating the issue with the coordinates search.

**Usage Example**:
```python
raise CoordinatesNotFoundError("No coordinates found for the given address.")
```

### 3. **InvalidPlusCodeError**
**Description**: Raised when an invalid Plus Code is provided, or the Plus Code cannot be decoded into coordinates.

#### Constructor:
```python
def __init__(self, message):
    self.message = message
    super().__init__(self.message)
```
- **`message`**: Custom message explaining the invalid Plus Code issue.

**Usage Example**:
```python
raise InvalidPlusCodeError("Invalid Plus Code: 7FG9V5X8+X4")
```

## Class Definitions

### 1. **GeoLocationService**

The **GeoLocationService** class is the heart of the application, handling all geolocation and Plus Code operations.

#### Constructor
```python
def __init__(self):
    """Initialize the GeoLocationService class with a geolocator."""
    self.geolocator = Nominatim(user_agent="GeoPlusCodeApp")
```
- **`self.geolocator`**: Initializes the `Nominatim` geocoder from `geopy`, which is used for geocoding addresses and reverse geocoding.

#### Method: `get_coordinates`
```python
def get_coordinates(self, address):
    """Convert an address to latitude and longitude."""
```
- **Arguments**:
  - `address`: The address to geocode.
- **Returns**: Prints the latitude and longitude of the address if found. If not, it raises an `AddressNotFoundError`.

**Usage Example**:
```python
geo_service = GeoLocationService()
geo_service.get_coordinates("1600 Pennsylvania Ave NW, Washington, DC")
```

#### Method: `get_address_from_coordinates`
```python
def get_address_from_coordinates(self, lat, lon):
    """Convert latitude and longitude to address."""
```
- **Arguments**:
  - `lat`: Latitude of the location.
  - `lon`: Longitude of the location.
- **Returns**: Prints the address corresponding to the coordinates. If no address is found, it raises a `CoordinatesNotFoundError`.

**Usage Example**:
```python
geo_service.get_address_from_coordinates(38.8977, -77.0365)
```

#### Method: `get_plus_code_from_coordinates`
```python
def get_plus_code_from_coordinates(self, lat, lon):
    """Convert latitude and longitude to Plus Code."""
```
- **Arguments**:
  - `lat`: Latitude of the location.
  - `lon`: Longitude of the location.
- **Returns**: Prints the Plus Code corresponding to the coordinates.

**Usage Example**:
```python
geo_service.get_plus_code_from_coordinates(38.8977, -77.0365)
```

#### Method: `get_coordinates_from_plus_code`
```python
def get_coordinates_from_plus_code(self, plus_code):
    """Convert Plus Code to latitude and longitude."""
```
- **Arguments**:
  - `plus_code`: The Plus Code to decode.
- **Returns**: Prints the latitude and longitude corresponding to the Plus Code. If invalid, it raises an `InvalidPlusCodeError`.

**Usage Example**:
```python
geo_service.get_coordinates_from_plus_code("7FG9V5X8+X4")
```

### 2. **Menu**

The **Menu** class provides a simple user interface for interacting with the application. The user can choose between different geolocation services.

#### Constructor
```python
def __init__(self):
    self.geo_service = GeoLocationService()
```
- **`self.geo_service`**: Initializes an instance of the `GeoLocationService` class for use within the menu.

#### Method: `show_menu`
```python
def show_menu(self):
    """Display the menu options."""
```
- **Description**: Displays a list of available actions for the user.

**Usage Example**:
```python
menu.show_menu()
```

#### Method: `get_user_choice`
```python
def get_user_choice(self):
    """Get user choice from the menu."""
```
- **Description**: Prompts the user for their choice and returns the selected option.

**Usage Example**:
```python
choice = menu.get_user_choice()
```

#### Method: `handle_choice`
```python
def handle_choice(self, choice):
    """Handle the user's choice."""
```
- **Arguments**:
  - `choice`: The choice made by the user (1-4).
- **Description**: Based on the user's choice, the corresponding geolocation operation is performed.

**Usage Example**:
```python
menu.handle_choice(1)
```

## Main Functionality

### `main`
```python
def main():
    """Main function to run the menu-driven program."""
```
- **Description**: The `main` function initiates the menu and handles user interactions. The program runs in a loop, allowing the user to perform multiple operations until they choose to exit.

**Usage Example**:
```python
main()
```

## Error Handling

The application includes robust error handling to ensure smooth user interaction. Each custom exception provides a clear message if something goes wrong during geolocation operations:

- **`AddressNotFoundError`**: Raised when the provided address cannot be geocoded.
- **`CoordinatesNotFoundError`**: Raised when no address is found for the given coordinates.
- **`InvalidPlusCodeError`**: Raised when an invalid Plus Code is provided.

Additionally, general exceptions are caught, and unexpected errors are reported to the user in a user-friendly manner.

## Example Workflow

Here is an example of how the application works:

1. The user runs the program and is presented with a menu of options.
2. They choose an option, e.g., converting an address to coordinates.
3. They enter the necessary input (e.g., an address) and the application returns the corresponding latitude and longitude.
4. If any error occurs (e.g., invalid address or Plus Code), an appropriate error message is displayed.

### Example Output:
```
Choose an option:
1. Find Latitude and Longitude from Address
2. Find Address from Latitude and Longitude
3. Find Plus Code from Latitude and Longitude
4. Find Latitude and Longitude from Plus Code
Enter your choice (1/2/3/4): 1
Enter an address: 1600 Pennsylvania Ave NW, Washington, DC
Address: 1600 Pennsylvania Ave NW, Washington, DC
Latitude: 38.8977
Longitude: -77.0365
Do you want to perform another operation? (y/n): y
```

## Running the Application

To run the application, execute the following command:
```bash
python geopluscode.py
```

## Conclusion

The **GeoPlusCode** application offers a comprehensive solution for geolocation services, including address to coordinates, coordinates to address, and Plus Code conversions. With its user-friendly interface, robust error handling, and integration of geospatial technologies, it serves as a powerful tool for developers and geolocation enthusiasts alike.

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### **Disclaimer:**

Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.