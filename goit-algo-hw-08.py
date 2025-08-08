import pickle


class AddressBook:
    def __init__(self):
        self.data = {}  # тут зберігатимуться записи адресної книги

    def add_record(self, name, phone):
        self.data[name] = phone

    def show_all(self):
        for name, phone in self.data.items():
            print(f"{name}: {phone}")


# ---------- Функції для збереження та відновлення ----------
def save_data(book, filename="addressbook.pkl"):
    """Зберігає AddressBook у файл."""
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    """Завантажує AddressBook з файлу або створює нову, якщо файл відсутній."""
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    # При запуску програми пробуємо відновити книгу
    book = load_data()

    while True:
        command = input("Введіть команду (add/show/exit): ").strip().lower()

        if command == "add":
            name = input("Ім'я: ")
            phone = input("Телефон: ")
            book.add_record(name, phone)

        elif command == "show":
            book.show_all()

        elif command == "exit":
            save_data(book)  # зберігаємо перед виходом
            print("Дані збережено. Вихід...")
            break

        else:
            print("Невідома команда")