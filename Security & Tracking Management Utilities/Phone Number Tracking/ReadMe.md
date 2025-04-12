## **Phone Number Information Retrieval Module Documentation**

### **Overview**
This module allows users to enter a phone number (with country code) and retrieve various details such as the location, carrier, timezones, and region validation. It also validates the phone number format and checks if it is possible to dial. The module uses the `phonenumbers` library for phone number parsing and validation, and supports validating the region code associated with the phone number.

### **Classes**

#### 1. **PhoneNumberError (Base Class)**
   **Description**:  
   The base exception class for all exceptions in this module.

   **Constructor**:
   ```python
   def __init__(self, message):
       self.message = message
       super().__init__(self.message)
   ```

   **Attributes**:
   - `message` (str): The error message associated with the exception.

#### 2. **InvalidPhoneNumberError (Derived from PhoneNumberError)**
   **Description**:  
   Raised when a phone number is invalid or cannot be parsed.

   **Constructor**:
   ```python
   def __init__(self, number):
       self.message = f"The phone number '{number}' is invalid."
       super().__init__(self.message)
   ```

   **Attributes**:
   - `number` (str): The invalid phone number.

#### 3. **InvalidRegionCodeError (Derived from PhoneNumberError)**
   **Description**:  
   Raised when an invalid region code is provided.

   **Constructor**:
   ```python
   def __init__(self, region):
       self.message = f"The region code '{region}' is invalid."
       super().__init__(self.message)
   ```

   **Attributes**:
   - `region` (str): The invalid region code provided by the user.

#### 4. **PhoneNumberInfo**
   **Description**:  
   This class handles the parsing, validation, and retrieval of phone number information. It retrieves the location, carrier, timezones, and validates both the phone number and the provided region code.

   **Constructor**:
   ```python
   def __init__(self, number, region="US"):
       self.number = number
       self.region = region
       self._validate_region(region)  # Validate the region code
       self.parsed_number = self.parse_number()
   ```

   **Parameters**:
   - `number` (str): The phone number to be validated and parsed (including the country code if available).
   - `region` (str): The default region code used for parsing the phone number (default is `"US"`).

   **Methods**:

   - **`_validate_region(self, region)`**:  
     Validates if the provided region code is valid using `phonenumbers.is_valid_region(region)`.  
     If the region code is invalid, an `InvalidRegionCodeError` is raised.

   - **`parse_number(self)`**:  
     Parses the provided phone number and checks if it is valid. If invalid, it raises an `InvalidPhoneNumberError`.

   - **`get_location(self)`**:  
     Returns the location (description) associated with the parsed phone number. If unavailable, it returns `"Location not found."`.

   - **`get_carrier(self)`**:  
     Returns the carrier name associated with the parsed phone number. If unavailable, it returns `"Carrier not found."`.

   - **`get_timezones(self)`**:  
     Retrieves both geographical and alternative timezones for the parsed phone number.  
     Returns `"No geographical timezones found."` and `"No alternative timezones found."` if no timezones are found.

   - **`validate_number(self)`**:  
     Validates whether the phone number is in a possible format and can be dialed. If invalid, it raises an `InvalidPhoneNumberError`.

### **Functions**

#### **main()**
   **Description**:  
   The main function that serves as the entry point of the program. It prompts the user to enter a phone number and an optional region code. It then validates the number, retrieves the location, carrier, and timezones, and handles any errors gracefully.

   **Functionality**:
   1. Prompts the user for a phone number and region code (defaults to `"US"` if not provided).
   2. Validates the phone number and region code.
   3. Retrieves and displays the location, carrier, and timezones associated with the number.
   4. Handles invalid inputs such as invalid phone numbers or invalid region codes and provides user-friendly error messages.

---

### **Usage Example**

```bash
Enter a phone number (with country code): +14155552671
Enter a region code (e.g., 'US', 'IN', 'LK') or press Enter to use default (US): 
Location: United States
Carrier: Verizon Wireless
Geographical Timezones: ['America/New_York']
Alternative Timezones: ['America/New_York']
```

#### Example 2: **Valid Region Code (India)**

```bash
Enter a phone number (with country code): +919167895432
Enter a region code (e.g., 'US', 'IN', 'LK') or press Enter to use default (US): IN
Location: India
Carrier: Idea Cellular
Geographical Timezones: ['Asia/Kolkata']
Alternative Timezones: ['Asia/Kolkata']
```

#### Example 3: **Invalid Region Code**

```bash
Enter a phone number (with country code): +919167895432
Enter a region code (e.g., 'US', 'IN', 'LK') or press Enter to use default (US): XY
The region code 'XY' is invalid.
```

#### Example 4: **Invalid Phone Number**

```bash
Enter a phone number (with country code): 12345
Enter a region code (e.g., 'US', 'IN', 'LK') or press Enter to use default (US): 
The phone number '12345' is invalid.
```

---

### **How the Code Works**

1. **Phone Number Parsing**:
   - The provided phone number is parsed using the `phonenumbers.parse()` method, which also takes into account the region code for proper parsing.
   - The region code is validated by calling the `phonenumbers.is_valid_region(region)` method to ensure it corresponds to a valid region.

2. **Region Validation**:
   - Before parsing the number, the region code is validated using the `_validate_region()` method. If the region code is invalid, the program raises an `InvalidRegionCodeError` with an appropriate error message.

3. **Location, Carrier, and Timezones**:
   - Once the phone number is parsed successfully, the program fetches the location, carrier, and timezones associated with the number. These details are retrieved using `phonenumbers`' `geocoder`, `carrier`, and `timezone` modules.

4. **Error Handling**:
   - The program gracefully handles various errors, such as invalid phone numbers and invalid region codes, by raising exceptions and providing meaningful feedback to the user.

### **Error Handling**
   - **Invalid Phone Number**: The program raises an `InvalidPhoneNumberError` if the phone number cannot be parsed or if it's invalid.
   - **Invalid Region Code**: If the user provides an invalid region code, the program raises an `InvalidRegionCodeError`.
   - The program will catch these errors and display the appropriate error messages.

---

### **Dependencies**
- `phonenumbers`: Python library for parsing, formatting, and validating phone numbers.
  - Install it via pip:
    ```bash
    pip install phonenumbers
    ```

---

### **Conclusion**
This module provides an advanced solution for validating and retrieving detailed information about phone numbers, including region validation, location, carrier, and timezone information. It is particularly useful for applications that need to process phone numbers from multiple regions and ensure that the inputs are correctly parsed and validated.


## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## **Disclaimer:**

Kindly note that this project is developed solely for educational purposes, not intended for industrial use, as its sole intention lies within the realm of education. We emphatically underscore that this endeavor is not sanctioned for industrial application. It is imperative to bear in mind that any utilization of this project for commercial endeavors falls outside the intended scope and responsibility of its creators. Thus, we explicitly disclaim any liability or accountability for such usage.