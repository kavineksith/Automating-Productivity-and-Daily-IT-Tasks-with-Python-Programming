import sys
import time
from geopy.geocoders import Nominatim
import gps

# Custom Exceptions
class AddressNotFoundError(Exception):
    """Exception raised when the address cannot be found for given coordinates."""
    def __init__(self, message="Address not found for the given coordinates."):
        self.message = message
        super().__init__(self.message)

class GPSFixNotFoundError(Exception):
    """Exception raised when GPS fix cannot be obtained."""
    def __init__(self, message="Unable to get GPS fix. Try again later."):
        self.message = message
        super().__init__(self.message)

class GPSDataFetchError(Exception):
    """Exception raised when GPS data cannot be fetched."""
    def __init__(self, message="Failed to fetch GPS data."):
        self.message = message
        super().__init__(self.message)

# GeoLocationService Class
class GeoLocationService:
    def __init__(self):
        """Initialize the GeoLocationService class with a geolocator."""
        self.geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    def get_address_from_coordinates(self, lat, lon):
        """Get address from latitude and longitude."""
        try:
            location = self.geolocator.reverse((lat, lon))
            if location:
                print(f"Coordinates: Latitude: {lat}, Longitude: {lon}")
                print(f"Address: {location.address}")
            else:
                raise AddressNotFoundError(f"Address not found for coordinates: Latitude {lat}, Longitude {lon}")
        except AddressNotFoundError as e:
            print(f"Error: {e.message}")
        except Exception as e:
            print(f"An unexpected error occurred while getting the address: {e}")

# GPSService Class
class GPSService:
    def __init__(self):
        """Initialize the GPSService class with gpsd."""
        self.session = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    
    def get_gps_coordinates(self):
        """Get real-time GPS coordinates using gpsd."""
        print("Fetching GPS coordinates... Press Ctrl+C to stop.")
        try:
            while True:
                # Read GPS data
                self.session.next()
                if self.session.fix.mode >= 2:  # Only proceed if GPS has a fix
                    lat = self.session.fix.latitude
                    lon = self.session.fix.longitude
                    print(f"Latitude: {lat}, Longitude: {lon}")
                    return lat, lon
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopped GPS data collection.")
            return None, None
        except Exception as e:
            raise GPSDataFetchError(f"An error occurred while fetching GPS data: {e}")

# Main Application Class
class GeoApp:
    def __init__(self):
        """Initialize the application with GeoLocationService and GPSService."""
        self.geo_service = GeoLocationService()
        self.gps_service = GPSService()
    
    def run(self):
        """Run the main functionality of the application."""
        try:
            lat, lon = self.gps_service.get_gps_coordinates()
            if lat and lon:
                self.geo_service.get_address_from_coordinates(lat, lon)
            else:
                raise GPSFixNotFoundError("No GPS fix found. Cannot retrieve coordinates.")
        except GPSFixNotFoundError as e:
            print(f"Error: {e.message}")
        except GPSDataFetchError as e:
            print(f"Error: {e.message}")
        except KeyboardInterrupt:
            print("\nProgram interrupted. Exiting gracefully...")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Running the Application
if __name__ == "__main__":
    app = GeoApp()
    app.run()
    sys.exit(0)
