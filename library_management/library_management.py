import csv
import os
from abc import ABC, abstractmethod


# ==========================================
# 1. Custom Exceptions
# ==========================================
class BookNotFoundError(Exception):
    """Raised when a requested book cannot be located."""

    pass


class BookUnavailableError(Exception):
    """Raised when attempting to issue an already issued book."""

    pass


class BookNotIssuedError(Exception):
    """Raised when attempting to return a book that was never issued."""

    pass


class DuplicateBookError(Exception):
    """Raised when adding a book with an existing ISBN."""

    pass


# ==========================================
# 2. Abstraction: Base Class
# ==========================================
class LibraryItem(ABC):
    """Abstract base class representing any catalogued library item."""

    def __init__(self, item_id: str, title: str):
        self._item_id = item_id  # Protected attribute
        self._title = title

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not value.strip():
            raise ValueError("Title cannot be empty.")
        self._title = value.strip()

    @abstractmethod
    def get_details(self) -> str:
        """Abstract method to return structured item specifications."""
        pass


# ==========================================
# 3. Inheritance & Encapsulation: Book Class
# ==========================================
class Book(LibraryItem):
    """Derived class representing a physical book."""

    def __init__(
        self,
        isbn: str,
        title: str,
        author: str,
        issued_to: str = "",
        is_issued: bool = False,
    ):
        super().__init__(item_id=isbn, title=title)
        self.__author = author
        self.__is_issued = is_issued
        self.__issued_to = issued_to

    @property
    def isbn(self) -> str:
        return self._item_id

    @property
    def author(self) -> str:
        return self.__author

    @author.setter
    def author(self, value: str):
        if not value.strip():
            raise ValueError("Author cannot be empty.")
        self.__author = value.strip()

    @property
    def is_issued(self) -> bool:
        return self.__is_issued

    @property
    def issued_to(self) -> str:
        return self.__issued_to

    def issue(self, borrower_name: str):
        """Marks the book as issued to a borrower."""
        if self.__is_issued:
            raise BookUnavailableError(
                f"'{self.title}' is currently issued to {self.__issued_to}."
            )
        if not borrower_name.strip():
            raise ValueError("Borrower name cannot be empty.")
        self.__is_issued = True
        self.__issued_to = borrower_name.strip()

    def return_book(self):
        """Marks the book as returned."""
        if not self.__is_issued:
            raise BookNotIssuedError(
                f"'{self.title}' is not currently marked as issued."
            )
        self.__is_issued = False
        self.__issued_to = ""

    def get_details(self) -> str:
        """Concrete implementation of LibraryItem's abstract method."""
        status = f"Issued to {self.__issued_to}" if self.__is_issued else "Available"
        return (
            f"ISBN: {self.isbn:<10} | Title: {self.title:<25} | "
            f"Author: {self.__author:<18} | Status: {status}"
        )


# ==========================================
# 4. Management Class: LibraryManager
# ==========================================
class LibraryManager:
    """Handles book cataloging, issuing, returns, and CSV persistence."""

    def __init__(self, filename: str = "library_books.csv"):
        self.filename = filename
        self.catalog: dict[str, Book] = {}
        self.load_from_file()

    def add_book(self, isbn: str, title: str, author: str):
        if isbn in self.catalog:
            raise DuplicateBookError(f"A book with ISBN '{isbn}' already exists.")
        book = Book(isbn, title, author)
        self.catalog[isbn] = book
        print(f"✓ Book '{title}' added to catalog.")

    def search_books(self, query: str) -> list[Book]:
        """Case-insensitive search across title, author, or ISBN."""
        query = query.lower().strip()
        matches = [
            b
            for b in self.catalog.values()
            if query in b.title.lower()
            or query in b.author.lower()
            or query in b.isbn.lower()
        ]
        return matches

    def issue_book(self, isbn: str, borrower: str):
        if isbn not in self.catalog:
            raise BookNotFoundError(f"Book with ISBN '{isbn}' not found.")
        self.catalog[isbn].issue(borrower)
        print(f"✓ '{self.catalog[isbn].title}' successfully issued to {borrower}.")

    def return_book(self, isbn: str):
        if isbn not in self.catalog:
            raise BookNotFoundError(f"Book with ISBN '{isbn}' not found.")
        self.catalog[isbn].return_book()
        print(f"✓ '{self.catalog[isbn].title}' successfully returned.")

    def display_books(self, only_available: bool = False):
        items = (
            [b for b in self.catalog.values() if not b.is_issued]
            if only_available
            else list(self.catalog.values())
        )

        header = "AVAILABLE BOOKS" if only_available else "FULL CATALOG"
        if not items:
            print(f"No records found for: {header}.")
            return

        print("\n" + "=" * 80)
        print(header.center(80))
        print("=" * 80)
        for b in items:
            print(b.get_details())
        print("=" * 80)

    # --- File Handling (CSV) ---
    def save_to_file(self):
        try:
            with open(self.filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["isbn", "title", "author", "is_issued", "issued_to"])
                for b in self.catalog.values():
                    writer.writerow(
                        [b.isbn, b.title, b.author, str(b.is_issued), b.issued_to]
                    )
            print(f"✓ Catalog saved to '{self.filename}'.")
        except IOError as e:
            print(f"File Error: Could not save catalog ({e}).")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            return

        try:
            with open(self.filename, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    isbn = row["isbn"]
                    title = row["title"]
                    author = row["author"]
                    is_issued = row["is_issued"].lower() == "true"
                    issued_to = row.get("issued_to", "")
                    self.catalog[isbn] = Book(
                        isbn, title, author, issued_to, is_issued
                    )
        except (IOError, KeyError, ValueError) as e:
            print(f"Warning: Issue reading '{self.filename}' ({e}). Starting fresh.")


# ==========================================
# 5. CLI Interface Loop
# ==========================================
def main():
    library = LibraryManager()

    while True:
        print("\n=== LIBRARY MANAGEMENT SYSTEM ===")
        print("1. Add Book")
        print("2. Search Books (Title / Author / ISBN)")
        print("3. Issue Book")
        print("4. Return Book")
        print("5. Display Available Books")
        print("6. Display All Books")
        print("7. Save Records")
        print("8. Save & Exit")

        choice = input("Enter choice (1-8): ").strip()

        try:
            if choice == "1":
                isbn = input("Enter ISBN: ").strip()
                title = input("Enter Title: ").strip()
                author = input("Enter Author: ").strip()
                if not isbn or not title or not author:
                    print("Error: ISBN, Title, and Author cannot be blank.")
                    continue
                library.add_book(isbn, title, author)

            elif choice == "2":
                q = input("Enter search term: ").strip()
                results = library.search_books(q)
                if not results:
                    print("No matching books found.")
                else:
                    print(f"\nFound {len(results)} match(es):")
                    for b in results:
                        print(f"  {b.get_details()}")

            elif choice == "3":
                isbn = input("Enter ISBN to issue: ").strip()
                borrower = input("Enter Borrower Name: ").strip()
                library.issue_book(isbn, borrower)

            elif choice == "4":
                isbn = input("Enter ISBN to return: ").strip()
                library.return_book(isbn)

            elif choice == "5":
                library.display_books(only_available=True)

            elif choice == "6":
                library.display_books(only_available=False)

            elif choice == "7":
                library.save_to_file()

            elif choice == "8":
                library.save_to_file()
                print("Exiting application. Goodbye!")
                break

            else:
                print("Invalid selection. Choose between 1 and 8.")

        except (
            BookNotFoundError,
            BookUnavailableError,
            BookNotIssuedError,
            DuplicateBookError,
        ) as err:
            print(f"Operational Error: {err}")
        except ValueError as ve:
            print(f"Input Error: {ve}")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()