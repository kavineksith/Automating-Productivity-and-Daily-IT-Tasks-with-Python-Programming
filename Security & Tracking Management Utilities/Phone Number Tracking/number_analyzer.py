import phonenumbers
from phonenumbers import geocoder, carrier, timezone

class PhoneNumberError(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidPhoneNumberError(PhoneNumberError):
    """Exception raised for invalid phone numbers."""
    def __init__(self, number):
        self.message = f"The phone number '{number}' is invalid."
        super().__init__(self.message)

class InvalidRegionCodeError(PhoneNumberError):
    """Exception raised for invalid region codes."""
    def __init__(self, region):
        self.message = f"The region code '{region}' is invalid."
        super().__init__(self.message)

class PhoneNumberInfo:
    def __init__(self, number, region="US"):
        """
        Initialize the PhoneNumberInfo object with a phone number and region.
        
        :param number: The phone number (including country code if possible).
        :param region: The default region code for parsing (default is "US").
        """
        self.number = number
        self.region = region
        self._validate_region(region)  # Validate the region code
        self.parsed_number = self.parse_number()

    def _validate_region(self, region):
        """
        Validates if the region code is valid.
        
        :param region: The region code to validate.
        """
        if not phonenumbers.is_valid_region(region):
            raise InvalidRegionCodeError(region)
    
    def parse_number(self):
        try:
            # Parse the number with the specified region code
            parsed = phonenumbers.parse(self.number, self.region)
            if not phonenumbers.is_valid_number(parsed):
                raise InvalidPhoneNumberError(self.number)
            return parsed
        except phonenumbers.NumberParseException:
            raise InvalidPhoneNumberError(self.number)

    def get_location(self):
        try:
            # Fetch location for the parsed number
            return geocoder.description_for_number(self.parsed_number, "en") or "Location not found."
        except Exception as e:
            return f"Error retrieving location: {str(e)}"

    def get_carrier(self):
        try:
            # Fetch carrier information for the parsed number
            return carrier.name_for_number(self.parsed_number, "en") or "Carrier not found."
        except Exception as e:
            return f"Error retrieving carrier: {str(e)}"

    def get_timezones(self):
        try:
            # Fetch geographical and alternative timezones
            zone = timezone.time_zones_for_geographical_number(self.parsed_number)
            alterzone = timezone.time_zones_for_number(self.parsed_number)
            return zone or ["No geographical timezones found."], alterzone or ["No alternative timezones found."]
        except Exception as e:
            return f"Error retrieving timezones: {str(e)}"

    def validate_number(self):
        """Validates the phone number format and checks if it is possible to dial."""
        if not self.number:
            raise InvalidPhoneNumberError(self.number)
        if not phonenumbers.is_possible_number(self.parsed_number):
            raise InvalidPhoneNumberError(self.number)


def main():
    # Ask the user for the phone number and an optional region (e.g., "US", "IN", "LK")
    number = input("Enter a phone number (with country code): ")
    region = input("Enter a region code (e.g., 'US', 'IN', 'LK') or press Enter to use default (US): ")
    
    if not region:
        region = "US"  # Default to "US" if no region is provided
    
    try:
        # Create a PhoneNumberInfo object with the provided number and region
        phone_info = PhoneNumberInfo(number, region)
        phone_info.validate_number()  # Validate the number before proceeding
        print("Location:", phone_info.get_location())
        print("Carrier:", phone_info.get_carrier())
        zone, alterzone = phone_info.get_timezones()
        print("Geographical Timezones:", zone)
        print("Alternative Timezones:", alterzone)
    except PhoneNumberError as e:
        print(e.message)

if __name__ == "__main__":
    main()
