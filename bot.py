import sys
from typing import List
from models import Record, AddressBook, Name, Phone, Birthday
from datetime import datetime
import pickle

address_book = AddressBook()


def save_address_book(filename):
    try:
        with open(filename, 'wb') as file:
            pickle.dump(address_book.data, file)
    except IOError:
        print("Error: Failed to save the address book.")


def load_address_book(filename):
    try:
        with open(filename, 'rb') as file:
            address_book.data = pickle.load(file)
        print("Address book loaded successfully.")
    except (IOError, pickle.UnpicklingError):
        print("Error: Failed to load the address book")


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except KeyError:
            return "Contact not found"
        except ValueError:
            return "Invalid input"
        except IndexError:
            return "Missing input"
    return inner


@input_error
def add_contact(name: str, phones: List[str]) -> str:
    name_field = Name(name)
    record = Record(name_field)

    for phone in phones:
        phone_field = Phone(phone)
        phone_field.value = phone   # setter
        record.add_phone(phone_field)

    address_book.add_record(record)
    return "Contact added"


@input_error
def change_phone(name: str, old_phone: str, new_phone: str) -> str:
    record = address_book.data.get(name)
    if not record:
        return "Contact not found"

    for phone in record.phones:
        if phone.value == old_phone:
            phone.value = new_phone
            return "Phone number updated"

    return "Old phone number not found for the contact"


@input_error
def get_phone(name: str) -> str:
    record = address_book.data.get(name)
    if record:
        phones = record.phones
        if phones:
            return phones[0]
    return "Phone number not found"


@input_error
def set_birthday(name: str, birthday: Birthday) -> str:
    record = address_book.data.get(name)
    if not record:
        return "Contact not found"

    try:
        birthday_date_str = birthday.value.strftime("%d-%m-%Y")
        birthday_date = datetime.strptime(birthday_date_str, "%d-%m-%Y").date()
        birthday_field = Birthday(birthday_date)
        record.set_birthday(birthday_field)
        return "Birthday set"
    except ValueError:
        return f"Invalid date format. Please use the format: DD-MM-YYYY. Birthday: {birthday.value}"


def show_all() -> str:
    if not address_book.data:
        return "No contacts found"
    output = ""
    for name, record in address_book.data.items():
        phones = [phone.value for phone in record.phones]
        phones_str = ", ".join(phones)
        birthday_info = ""
        if record.birthday:
            days_to_birthday = record.days_to_birthday()
            if days_to_birthday == 0:
                birthday_info = " (Today is their birthday!)"
            elif days_to_birthday > 0:
                birthday_info = f" ({days_to_birthday} days until their birthday)"
            else:
                birthday_info = f" (Their birthday has already passed)"
        output += f"{name}: {phones_str}{birthday_info}\n"
    return output


def paginate_contacts(page_size: int) -> str:
    output = ""
    for page in address_book.paginate(page_size):
        for name, record in page:
            phones = [phone.value for phone in record.phones]
            phones_str = ", ".join(phones)
            if record.birthday:
                birthday = record.birthday.strftime("%d-%m-%Y")
                output += f"{name}: {phones_str}(Birthday: {birthday})\n"
            else:
                output += f"{name}: {phones_str}\n"
        output += "---\n"
    return output


def search_contacts(query):
    matching_contacts = []
    for record in address_book.data.values():
        name = record.name.value
        phone_numbers = [phone.value for phone in record.phones]
        if query in name or any(query in number for number in phone_numbers):
            matching_contacts.append(record)

    if len(matching_contacts) == 0:
        return "No matching contacts found."

    output = ""
    for record in matching_contacts:
        name = record.name.value
        phones = ", ".join(phone.value for phone in record.phones)
        output += f"Name: {name}\nPhone Numbers: {phones}\n\n"

    return output


def close_program() -> None:
    print("Good bye!")
    sys.exit()


def handle_command(command: str) -> str:
    parts = command.split()
    if parts[0].lower() == "hello":
        return "How can I help you?"

    elif parts[0].lower() == "add":
        if len(parts) < 3:
            return "Missing input"
        name = parts[1]
        phones = parts[2:]
        return add_contact(name, phones)

    elif parts[0].lower() == "change":
        if len(parts) < 4:
            return "Missing input"
        name = parts[1]
        old_phone = parts[2]
        new_phone = parts[3]
        return change_phone(name, old_phone, new_phone)

    elif parts[0].lower() == "phone":
        if len(parts) < 2:
            return "Missing input"
        name = parts[1]
        return get_phone(name)

    elif len(parts) >= 2 and parts[0].lower() == "show" and parts[1].lower() == "all":
        return show_all()

    elif parts[0].lower() == "birthday":
        if len(parts) < 3:
            return "Missing input"
        name = parts[1]
        birthday_str = parts[2]
        try:
            birthday = datetime.strptime(birthday_str, "%d-%m-%Y").date()
            birthday_field = Birthday(birthday)
            return set_birthday(name, birthday_field)
        except ValueError:
            return "Invalid date format. Please use the format: DD-MM-YYYY"

    elif parts[0].lower() == "paginate":
        if len(parts) < 2:
            return "Missing input"
        page_size = int(parts[1])
        return paginate_contacts(page_size)

    elif parts[0].lower() == "search":
        if len(parts) < 2:
            return "Missing input"
        search_query = " ".join(parts[1:])
        search_result = search_contacts(search_query)
        return search_result

    elif parts[0].lower() in ["close", "exit"] \
            or (len(parts) >= 2 and parts[0].lower() == "good" and parts[1].lower() == "bye"):
        close_program()
    else:
        return "Invalid command"


def main() -> None:
    print("Welcome to the assistant bot!")
    load_address_book("address_book.json")
    while True:
        command = input("Enter command: ")
        response = handle_command(command)
        print(response)
        save_address_book("address_book.json")


if __name__ == '__main__':
    main()