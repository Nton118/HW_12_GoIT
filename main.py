from ab_classes import Name, Phone, Email, Birthday, Record, AddressBook
from functools import wraps
from pathlib import Path
import re


PAGE = 10
DB_FILE_NAME = "phonebook.bin"


def input_error(func):
    @wraps(func)
    def wrapper(*args):
        try:
            result = func(*args)
            return result

        except TypeError:
            if func.__name__ == "handler":
                return "No such command!"
            if func.__name__ == "add" or func.__name__ == "change":
                return f"Give me name and phone please. Minimum phone number length is {Phone.min_len} digits. Maximum {Phone.max_len}.Letters not allowed!"
            if func.__name__ == "add_birthday":
                return "input name and date"
            if func.__name__ == "add_email":
                return "input name and e-mail"
            if func.__name__ == "search":
                return "Command needs only 1 argument"

        except AttributeError:
            return 'No such contact! to add one use "add" command'

        except ValueError:
            if func.__name__ == "add" or func.__name__ == "change":
                return "Name cannot consist of only digits and min name length is 3."
            if func.__name__ == "phone":
                return "Enter contact name"
            if func.__name__ == "show_all":
                return "The Phonebook is empty"
            if func.__name__ == "del_phone":
                return "this contact doesn't have such phone number"
            if func.__name__ == "add_birthday":
                return "use date format DD.MM.YYYY or DD/MM/YYYY"
            if func.__name__ == "add_email":
                return "invalid email format"

        except IndexError:
            if func.__name__ == "add_birthday":
                return "Birth date lready entered, only one allowed"
            if func.__name__ == "search":
                return "Command needs arguments"
            else:
                return "Command needs no arguments"

    return wrapper


@input_error
def greet(book: AddressBook = None, *args):
    if args != ("",):
        raise IndexError
    return "How can I help you?"


@input_error
def add(book: AddressBook, contact: str, phone: str = None):
    contact_new = Name(contact)
    phone_new = Phone(phone) if phone else None
    rec_new = Record(contact_new, phone_new)

    if contact not in book.keys():
        book.add_record(rec_new)
        return f'Added contact "{contact}" with phone number: {phone}'
    else:
        book.get(contact).add_phone(phone_new)
        return f'Updated existing contact "{contact}" with new phone number: {phone}'


@input_error
def add_email(book: AddressBook, contact: str, email: str):
    email_new = Email(email)
    rec = book.get(contact)
    rec.add_email(email_new)
    return f'Updated existing contact "{contact}" with new email: {email}'


@input_error
def add_birthday(book: AddressBook, contact: str, birthday: str):
    b_day = Birthday(birthday)
    rec = book.get(contact)
    rec.add_birthday(b_day)
    return f'Updated existing contact "{contact}" with a birth date: {b_day}'


@input_error
def congrat(book: AddressBook, contact: str):
    rec = book.get(contact)
    return rec.days_to_birthday()


@input_error
def change(book: AddressBook, contact: str, phone: str = None):
    rec = book.get(contact)

    print(book.show_phone(contact))

    if not rec.phones:
        if not phone:
            phone_new = Phone(input("If you want to add the phone enter phone number:"))
        else:
            phone_new = Phone(phone)
        rec.add_phone(phone_new)
        return f'Changed phone number to {phone_new} for contact "{contact}"'

    else:
        if len(rec.phones) == 1:
            num = 1
        if len(rec.phones) > 1:
            num = int(input("which one do yo want to change (enter index):"))
        if not phone:
            phone_new = Phone(input("Please enter new phone number:"))
        else:
            phone_new = Phone(phone)
        old_phone = rec.phones[num - 1]
        rec.edit_phone(phone_new, num)
        return (
            f'Changed phone number {old_phone} to {phone_new} for contact "{contact}"'
        )


@input_error
def del_phone(book: AddressBook, contact: str, phone=None):
    rec = book.get(contact)

    if phone:
        for i, p in enumerate(rec.phones):
            if p == phone:
                num = i + 1
        else:
            raise ValueError
    else:
        print(rec.show_phones())
        if len(rec.phones) == 1:
            num = 1
            ans = None
            while ans != "y":
                ans = input(
                    f"Contact {rec.name} has only 1 phone {rec.phones[0]}. Are you sure? (Y/N)"
                ).lower()
        else:
            num = int(input("which one do yo want to delete (enter index):"))
    return f"Phone {rec.del_phone(num)} deleted!"


@input_error
def del_email(book: AddressBook, contact: str, email=None):
    rec = book.get(contact)
    rec.email = None
    return f"Contact {contact}, email deleted"


@input_error
def del_contact(book: AddressBook, contact: str):
    rec = book.get(contact)
    if not rec:
        raise AttributeError
    ans = None
    while ans != "y":
        ans = input(f"Are you sure to delete contact {contact}? (Y/N)").lower()
    return f"Contact {book.remove_record(contact)} deleted!"


@input_error
def del_birthday(book: AddressBook, contact: str):
    rec = book.get(contact)
    rec.birthday = None
    return f"Contact {contact}, birthday deleted"


@input_error
def phone(book: AddressBook, contact: str):
    return f'Contact "{contact}". {book.show_phone(contact)}'


@input_error
def show_all(book: AddressBook, *args):
    if args != ("",):
        raise IndexError
    if len(book) < PAGE:
        return book.show_all()
    else:
        gen_obj = book.iterator(PAGE)
        for i in gen_obj:
            print(i)
            print("*" * 50)
            input("Press any key")


@input_error
def search(book: AddressBook, pattern: str):
    if not pattern:
        raise IndexError
    result = book.search(pattern)
    if result:
        matches = ""
        for i in result:
            matches += str(i)
        frags = matches.split(pattern)
        highlighted = ""
        for i, fragment in enumerate(frags):
            highlighted += fragment
            if i < len(frags) - 1:
                highlighted += "\033[42m" + pattern + "\033[0m"
        return f"Found {len(result)} match(es):\n" + highlighted
    else:
        return "not found!"


@input_error
def help(book: AddressBook = None, *args):
    if args != ("",):
        raise IndexError
    return f"available commands: {', '.join(k for k in COMMANDS.keys())}"


@input_error
def exit(book: AddressBook, *args):
    if args != ("",):
        raise IndexError
    global is_ended
    is_ended = True
    book.save_to_file(DB_FILE_NAME)
    return "Good bye!"


COMMANDS = {
    "hello": greet,
    "add email": add_email,
    "add b_day": add_birthday,
    "add": add,
    "congrat": congrat,
    "change": change,
    "phone": phone,
    "show all": show_all,
    "search": search,
    "del phone": del_phone,
    "del b_day": del_birthday,
    "del email": del_email,
    "del contact": del_contact,
    "close": exit,
    "good bye": exit,
    "exit": exit,
    "help": help,
}


def command_parser(line: str):
    line_prep = " ".join(line.split())
    for k, v in COMMANDS.items():
        if line_prep.lower().startswith(k + " ") or line_prep.lower() == k:
            return v, re.sub(k, "", line_prep, flags=re.IGNORECASE).strip().rsplit(
                " ", 1
            )
    return None, []


@input_error
def handler(command, book, args):
    return command(book, *args)


is_ended = False


def main():
    book1 = AddressBook()
    if Path(DB_FILE_NAME).exists():
        book1.load_from_file(DB_FILE_NAME)

    while not is_ended:
        s = input(">>>")

        command, args = command_parser(s)
        print(handler(command, book1, args))


if __name__ == "__main__":
    main()
