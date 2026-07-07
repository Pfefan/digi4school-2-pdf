import getpass

import requests

from .authentication import AuthAndTokenHandler
from .book_fetcher import BookDataRetriever
from .config_handler import ConfigHandler


class CommandHandler:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:152.0) Gecko/20100101 Firefox/152.0'
        })
        self.auth = AuthAndTokenHandler()
        self.digi4school = BookDataRetriever()

        self.commands = {
            "list-books": self.list_books,
            "download": self.download,
            "help": self.help,
        }

    def main(self):
        config_handler = ConfigHandler()
        validconfig = config_handler.check_config()
        if validconfig:
            login_success = self.auth.login_user(self.session)
            if login_success:
                self.handler()
            else:
                print("Login failed. Please check your credentials and try again.")
        else:
            print("No or Invalid Config. Please enter valid credentials:")
            email = input("Email: ")
            password = getpass.getpass("Password: ")
            config_handler.write_config(email, password)
            print("\n")
            self.main()

    def handler(self):
        print("Welcome to digi4school-2-pdf!!!\n")
        while True:
            command = input("Enter command >: ")
            self.execute_command(command)

    def execute_command(self, command):
        if not command.strip():
            return
        command_name, *args = command.split()
        if command_name in self.commands:
            try:
                self.commands[command_name](*args)
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Invalid command. Please try again.")

    def help(self):
        print("List of available commands:")
        print("- list-books - List all available books")
        print("- download book <book_id> - Download a specific book")
        print("- download all - Download all books")
        print("- download book <book_id> page <start_page> [<end_page>] [--disable-check] - Download specific page(s) from a book.")
        print("- help - Display this help message \n")

    def list_books(self):
        data = self.digi4school.get_book_list(self.session)
        if len(data) > 0:
            print("   ID                 Book Name")
            print("-" * 50)
            counter = 1
            for book in data:
                print(f"{str(counter).strip():>4}   {book[2].strip()}")
                counter += 1
            print("-" * 50)
        else:
            print("No data found!!\n")

    def download(self, *args):
        if args[0] == "book" and len(args) == 2:
            book_id = args[1]
            self.download_book(book_id)
        elif args[0] == "book" and args[2] == "page":
            book_id = args[1]
            start_page = args[3]
            end_page = None
            disable_titlepage_check = False
            if len(args) > 4:
                if args[4].isdigit():
                    end_page = args[4]
                elif args[4] == "--disable-check":
                    disable_titlepage_check = True
            if len(args) > 5 and args[5] == "--disable-check":
                disable_titlepage_check = True
            self.download_page(book_id, start_page, end_page, disable_titlepage_check)
        elif args[0] == "all" and len(args) == 1:
            self.download_all_books()
        else:
            print("Invalid arguments. Please try again.")

    def download_book(self, book_id):
        if int(book_id) < 0:
            print("Invalid book_id")
            return

        data = self.digi4school.get_book_list(self.session)[int(book_id)-1]
        self.digi4school.download_single_book(data, self.session)

    def download_all_books(self):
        data = self.digi4school.get_book_list(self.session)
        self.digi4school.download_all_books(data, self.session)

    def download_page(self, book_id, start_page, end_page=None, disable_titlepage_check=False):
        if int(book_id) < 0:
            print("Invalid book_id")
            return

        # TODO: Add check for valid page numbers
        data = self.digi4school.get_book_list(self.session)[int(book_id)-1]
        self.digi4school.download_page(data, self.session, int(start_page), int(end_page) if end_page else None, disable_titlepage_check)
