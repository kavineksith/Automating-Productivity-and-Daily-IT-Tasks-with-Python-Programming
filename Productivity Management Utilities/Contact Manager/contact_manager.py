import json
import re
import sys

class ContactManager:
    def __init__(self, filename):
        self.filename = filename
        self.contacts = self.load_contacts()

    def load_contacts(self):
        """Load contacts from a JSON file."""
        try:
            with open(self.filename, 'r') as file:
                contacts = json.load(file)
            return contacts
        except FileNotFoundError:
            print(f"Warning: Contacts file '{self.filename}' not found. Creating new file.")
            return []
        except json.JSONDecodeError:
            raise ValueError("Error: Unable to load contacts. Invalid JSON format.")

    def save_contacts(self):
        """Save contacts to a JSON file."""
        try:
            with open(self.filename, 'w') as file:
                json.dump(self.contacts, file, indent=4)
        except Exception as e:
            raise IOError(f"Error occurred while saving contacts: {e}")

    def add_contact(self, name, phone, email):
        """Add a new contact."""
        contact = {'name': name, 'phone': phone, 'email': email}
        self.contacts.append(contact)
        self.save_contacts()

    def delete_contact(self, index):
        """Delete a contact by index."""
        if 0 <= index < len(self.contacts):
            del self.contacts[index]
            self.save_contacts()
        else:
            raise ValueError("Error: Invalid contact index.")

    def update_contact(self, index, name=None, phone=None, email=None):
        """Update contact details by index."""
        if 0 <= index < len(self.contacts):
            contact = self.contacts[index]
            if name is not None:
                contact['name'] = name
            if phone is not None:
                contact['phone'] = phone
            if email is not None:
                contact['email'] = email
            self.save_contacts()
        else:
            raise ValueError("Error: Invalid contact index.")

    def search_contacts(self, pattern):
        """Search for contacts based on regex pattern."""
        regex = re.compile(pattern, re.IGNORECASE)
        matches = [contact for contact in self.contacts if regex.search(contact['name']) or
                   regex.search(contact['phone']) or
                   regex.search(contact['email'])]
        return matches

    def display_contacts(self):
        """Display all contacts."""
        if self.contacts:
            print("Contacts:")
            for i, contact in enumerate(self.contacts):
                print(f"{i+1}. Name: {contact['name']}, Phone: {contact['phone']}, Email: {contact['email']}")
        else:
            print("No contacts available.")

def main():
    filename = "contacts.json"
    contact_manager = ContactManager(filename)

    while True:
        print("\nContact Manager")
        print("1. Add Contact")
        print("2. Delete Contact")
        print("3. Update Contact")
        print("4. Search Contacts")
        print("5. Display Contacts")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter name: ")
            phone = input("Enter phone number: ")
            email = input("Enter email address: ")
            contact_manager.add_contact(name, phone, email)
            print("Contact added successfully.")
        elif choice == '2':
            try:
                index = int(input("Enter index of contact to delete: ")) - 1
                contact_manager.delete_contact(index)
                print("Contact deleted successfully.")
            except ValueError:
                print("Error: Invalid index. Please enter a valid integer.")
        elif choice == '3':
            try:
                index = int(input("Enter index of contact to update: ")) - 1
                name = input("Enter new name (leave blank to keep unchanged): ")
                phone = input("Enter new phone number (leave blank to keep unchanged): ")
                email = input("Enter new email address (leave blank to keep unchanged): ")
                contact_manager.update_contact(index, name if name else None, phone if phone else None, email if email else None)
                print("Contact updated successfully.")
            except ValueError:
                print("Error: Invalid index. Please enter a valid integer.")
        elif choice == '4':
            pattern = input("Enter search pattern (regex): ")
            results = contact_manager.search_contacts(pattern)
            if results:
                print("Search Results:")
                for i, contact in enumerate(results):
                    print(f"{i+1}. Name: {contact['name']}, Phone: {contact['phone']}, Email: {contact['email']}")
            else:
                print("No contacts matched the search criteria.")
        elif choice == '5':
            contact_manager.display_contacts()
        elif choice == '6':
            print("Exiting...")
            break
        else:
            print("Error: Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
    sys.exit(0)
