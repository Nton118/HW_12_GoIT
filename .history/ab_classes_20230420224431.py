from collections import UserDict
from datetime import datetime
from itertools import islice
import pickle
import re


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value


class Name(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if not (value.isnumeric() or len(value) < 3):  # Name validation
            self.__value = value
        else:
            raise ValueError


class Birthday(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        try:
            self.__value = datetime.strptime(value, "%d.%m.%Y")  # Date validaiton "."
        except ValueError:
            self.__value = datetime.strptime(value, "%d/%m/%Y")  # Date validaiton "/"

    def __str__(self) -> str:
        return datetime.strftime(self.value, "%d.%m.%Y")


class Email(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        pattern = (
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"  # Email validation
        )
        if re.match(pattern, value):
            self.__value = value
        else:
            raise ValueError


class Phone(Field):
    min_len = 5
    max_len = 17

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        new_phone = (  # Phone validation
            value.strip()
            .removeprefix("+")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
        )
        if (
            not new_phone.isdecimal()
            or not Phone.min_len <= len(new_phone) <= Phone.max_len
        ):
            raise TypeError
        self.__value = new_phone


class Record:
    def __init__(
        self,
        name: Name,
        phone: Phone = None,
        birthday: Birthday = None,
        email: Email = None,
    ):
        self.name = name
        self.phones = []
        if phone:
            self.phones.append(phone)
        self.birthday = birthday
        self.email = email

    def __str__(self):
        line = "{}: Phones: {}; E-mail:{}; B-day:{} \n"
        return line.format(
            self.name,
            ", ".join([str(phone) for phone in self.phones]),
            self.email,
            self.birthday,
        )

    def __repr__(self):
        line = "{}: Phones: {}; E-mail:{}; B-day:{} \n"
        return line.format(
            self.name,
            ", ".join([str(phone) for phone in self.phones]),
            self.email,
            self.birthday,
        )

    def days_to_birthday(self) -> int:
        if not self.birthday:
            return "Sorry, no birthdate for this contact"
        today = datetime.today()
        compare = self.birthday.value.replace(year=today.year)
        days = int((compare - today).days)
        if days > 0:
            return f"{days} days to birthday"
        elif today.month == compare.month and today.day == compare.day:
            return "It is TODAY!!!"
        else:
            days = int((compare.replace(year=today.year + 1) - today).days)
            return f"{days} days to birthday"

    def add_phone(self, phone: Phone):
        self.phones.append(phone)

    def add_email(self, email: Email):
        self.email = email

    def add_birthday(self, birthday: Birthday):
        if not self.birthday:
            self.birthday = birthday
        else:
            raise IndexError("Birthday already entered")

    def show_phones(self):
        if not self.phones:
            return "this contact has no phones."
        elif len(self.phones) == 1:
            return f"Current phone number is {self.phones[0]}"
        else:
            output = "This contact has several phones:\n"
            for i, phone in enumerate(self.phones, 1):
                output += f"{i}: {phone} "
            return output

    def del_phone(self, num=1):
        if not self.phones:
            raise IndexError
        else:
            return self.phones.pop(num - 1)

    def edit_phone(self, phone_new: Phone, num=1):
        if not self.phones:
            raise IndexError
        else:
            self.phones.pop(num - 1)
            self.phones.insert(num - 1, phone_new)


class AddressBook(UserDict):
    def save_to_file(self, filename):
        with open(filename, "wb") as db:
            pickle.dump(self.data, db)

    def load_from_file(self, filename):
        with open(filename, "rb") as db:
            self.data = pickle.load(db)

    def add_record(self, record: Record):
        self.data.update({record.name.value: record})

    def remove_record(self, contact: str):
        return self.data.pop(contact)

    def show_phone(self, contact: str):
        return self.data.get(contact).show_phones()

    def iterator(self, page):
        start = 0
        while True:
            output = ""
            for i in islice(self.data.values(), start, start + page):
                output += str(i)
            if not output:
                output = f"Total: {len(self.data)} contacts."
                yield output
                break
            yield output
            start += page

    def show_all(self):
        output = ""
        for contact in self.data.values():
            output += str(contact)
        output += f"Total: {len(self.data)} contacts."
        return output

    def search(self, pattern: str) -> list:
        found_recs = []
        if pattern.isnumeric():
            for contact in self.data.values():
                for phone in contact.phones:
                    if re.match(pattern, phone.value):
                        found_recs.append(contact)
        else:
            for contact in self.data.values():
                if re.match(pattern, contact.name.value, flags=re.IGNORECASE):
                    found_recs.append(contact)
        return found_recs
