import random
import re
import pickle
from datetime import datetime, timedelta
from collections import UserDict

# ------------------------------
# Утилітарні функції
# ------------------------------

def get_days_from_today(date_str):
    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.today().date()
        return (today - input_date).days
    except ValueError:
        return None

def get_numbers_ticket(min_value, max_value, quantity):
    if not (1 <= min_value <= max_value <= 1000):
        return []
    if not (min_value <= quantity <= max_value):
        return []
    numbers = random.sample(range(min_value, max_value + 1), quantity)
    return sorted(numbers)

def normalize_phone(phone_number):
    cleaned = re.sub(r"[^\d+]", "", phone_number)
    if cleaned.startswith('+'):
        if not cleaned.startswith('+380'):
            return cleaned
        return cleaned
    else:
        if cleaned.startswith('380'):
            return '+' + cleaned
        else:
            return '+38' + cleaned

# ------------------------------
# Класи для адресної книги
# ------------------------------

class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError("Номер телефону має містити 10 цифр")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Невірний формат дати. Використовуйте ДД.ММ.РРРР")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old, new):
        for i, p in enumerate(self.phones):
            if p.value == old:
                self.phones[i] = Phone(new)
                return True
        return False

    def add_birthday(self, bday):
        self.birthday = Birthday(bday)

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday.replace(year=today.year)
                if today <= bday_this_year <= today + timedelta(days=7):
                    greet_day = bday_this_year
                    if greet_day.weekday() >= 5:
                        greet_day += timedelta(days=(7 - greet_day.weekday()))
                    upcoming.append({"name": record.name.value, "birthday": greet_day.strftime("%d.%m.%Y")})
        return upcoming

    def save(self, filename="addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)

    def load(self, filename="addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = {}

# ------------------------------
# Обробники команд
# ------------------------------

def input_error(func):
    def wrapper(*args):
        try:
            return func(*args)
        except (IndexError, ValueError) as e:
            return f"Помилка: {str(e)}"
    return wrapper

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record and record.edit_phone(old_phone, new_phone):
        return "Номер оновлено."
    return "Контакт або номер не знайдено."

@input_error
def show_phones(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return ", ".join([p.value for p in record.phones])
    return "Контакт не знайдено."

def show_all(book):
    if not book.data:
        return "Адресна книга порожня."
    result = ["Ім'я контакту | Телефони | День народження"]
    result.append("-" * 40)
    for record in book.data.values():
        phones = ", ".join([p.value for p in record.phones])
        bday = record.birthday.value if record.birthday else ""
        result.append(f"{record.name.value} | {phones} | {bday}")
    return "\n".join(result)

@input_error
def add_birthday(args, book):
    name, bday = args
    record = book.find(name)
    if not record:
        return "Контакт не знайдено."
    record.add_birthday(bday)
    return "День народження додано."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value
    return "День народження не встановлено або контакт не знайдено."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "Немає найближчих днів народження."
    return "\n".join([f"{p['name']}: {p['birthday']}" for p in upcoming])

def parse_input(user_input):
    parts = user_input.strip().split()
    return parts[0].lower(), parts[1:]

def print_commands():
    print("\nЛаскаво просимо до помічника!")
    print("Доступні команди:")
    print(" add [ім'я] [телефон]             - Додати контакт або номер")
    print(" change [ім'я] [старий] [новий]   - Змінити номер телефону")
    print(" phone [ім'я]                     - Показати телефони контакту")
    print(" all                              - Показати всі контакти")
    print(" add-birthday [ім'я] [дата]       - Додати день народження (ДД.ММ.РРРР)")
    print(" show-birthday [ім'я]             - Показати день народження контакту")
    print(" birthdays                        - Дні народження на найближчі 7 днів")
    print(" hello                            - Привітання")
    print(" close / exit                     - Вийти з програми\n")

# ------------------------------
# Запуск адресної книги
# ------------------------------

def run_address_book():
    book = AddressBook()
    book.load()
    print_commands()

    while True:
        user_input = input("Введіть команду: ").strip()
        if not user_input:
            continue

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            book.save()
            print("Дані збережено. Вихід...")
            break
        elif command == "hello":
            print("Привіт! Чим можу допомогти?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phones(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Невірна команда. Введіть 'hello' для допомоги.")

# ------------------------------
# Головне меню вибору режиму
# ------------------------------

def main():
    print("Виберіть режим роботи програми:")
    print("1 - Приклади з датами, номерами, телефонами")
    print("2 - Адресна книга")

    choice = input("Ваш вибір (1/2): ").strip()
    if choice == "1":
        print("Дні з дати 2024-01-01:", get_days_from_today("2024-01-01"))
        print("Випадкові числа:", get_numbers_ticket(1, 49, 6))
        print("Номер:", normalize_phone("067 123 4567"))
        print("Номер:", normalize_phone("+380671234567"))
    elif choice == "2":
        run_address_book()
    else:
        print("Невірний вибір.")

if __name__ == "__main__":
    main()
