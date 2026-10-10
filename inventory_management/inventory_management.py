import csv
import os
from abc import ABC, abstractmethod


# ==========================================
# 1. Custom Exceptions
# ==========================================
class ProductNotFoundError(Exception):
    """Raised when an item code cannot be located."""

    pass


class DuplicateProductError(Exception):
    """Raised when an item code already exists."""

    pass


class InvalidStockError(Exception):
    """Raised when quantity or price values violate boundaries."""

    pass


# ==========================================
# 2. Abstraction: Base Class
# ==========================================
class Item(ABC):
    """Abstract base class representing any inventoriable item."""

    def __init__(self, item_id: str, name: str):
        self._item_id = item_id  # Protected
        self._name = name

    @property
    def item_id(self) -> str:
        return self._item_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value.strip():
            raise ValueError("Item name cannot be empty.")
        self._name = value.strip()

    @abstractmethod
    def calculate_value(self) -> float:
        """Calculates total monetary value of current stock."""
        pass

    @abstractmethod
    def get_details(self) -> str:
        """Formats item inventory details."""
        pass


# ==========================================
# 3. Inheritance & Encapsulation: Subclasses
# ==========================================
class Product(Item):
    """Standard non-perishable product."""

    def __init__(
        self, item_id: str, name: str, category: str, price: float, quantity: int
    ):
        super().__init__(item_id, name)
        self._category = category
        self.set_price(price)
        self.set_quantity(quantity)

    @property
    def category(self) -> str:
        return self._category

    @property
    def price(self) -> float:
        return self.__price

    def set_price(self, value: float):
        if value <= 0:
            raise InvalidStockError("Price must be greater than zero.")
        self.__price = round(value, 2)

    @property
    def quantity(self) -> int:
        return self.__quantity

    def set_quantity(self, value: int):
        if value < 0:
            raise InvalidStockError("Quantity cannot be negative.")
        self.__quantity = value

    def adjust_stock(self, delta: int):
        """Adds or removes stock safely."""
        if self.__quantity + delta < 0:
            raise InvalidStockError(
                f"Cannot reduce stock below zero. Current stock: {self.__quantity}."
            )
        self.__quantity += delta

    def calculate_value(self) -> float:
        return round(self.__quantity * self.__price, 2)

    def get_details(self) -> str:
        return (
            f"ID: {self.item_id:<8} | Name: {self.name:<20} | Category: {self.category:<12} | "
            f"Price: ₹{self.__price:<8.2f} | Stock: {self.__quantity:<5} | Value: ₹{self.calculate_value():<10.2f}"
        )


class PerishableProduct(Product):
    """Product with an expiration date."""

    def __init__(
        self,
        item_id: str,
        name: str,
        category: str,
        price: float,
        quantity: int,
        expiry_date: str,
    ):
        super().__init__(item_id, name, category, price, quantity)
        self.__expiry_date = expiry_date

    @property
    def expiry_date(self) -> str:
        return self.__expiry_date

    @expiry_date.setter
    def expiry_date(self, value: str):
        if not value.strip():
            raise ValueError("Expiry date cannot be blank.")
        self.__expiry_date = value.strip()

    def get_details(self) -> str:
        return (
            f"ID: {self.item_id:<8} | Name: {self.name:<20} | Category: {self.category:<12} | "
            f"Price: ₹{self.price:<8.2f} | Stock: {self.quantity:<5} | Exp: {self.__expiry_date:<10} | "
            f"Value: ₹{self.calculate_value():<10.2f}"
        )


# ==========================================
# 4. Management Class: InventoryManager
# ==========================================
class InventoryManager:
    """Coordinates inventory tracking, reporting, and CSV persistence."""

    def __init__(self, filename: str = "inventory.csv"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, filename)
        self.items: dict[str, Product] = {}
        self.load_from_file()

    def add_product(
        self,
        item_id: str,
        name: str,
        category: str,
        price: float,
        quantity: int,
        expiry_date: str = "",
    ):
        if item_id in self.items:
            raise DuplicateProductError(f"Item ID '{item_id}' is already registered.")

        if expiry_date:
            product = PerishableProduct(
                item_id, name, category, price, quantity, expiry_date
            )
        else:
            product = Product(item_id, name, category, price, quantity)

        self.items[item_id] = product
        print(f"✓ Added '{name}' (ID: {item_id}) to inventory.")

    def search_product(self, item_id: str) -> Product:
        if item_id not in self.items:
            raise ProductNotFoundError(f"Product '{item_id}' not found.")
        return self.items[item_id]

    def update_stock(self, item_id: str, delta: int):
        product = self.search_product(item_id)
        product.adjust_stock(delta)
        print(f"✓ Stock for '{product.name}' updated. New Quantity: {product.quantity}")

    def update_price(self, item_id: str, new_price: float):
        product = self.search_product(item_id)
        product.set_price(new_price)
        print(f"✓ Price for '{product.name}' updated to ₹{product.price:.2f}")

    def delete_product(self, item_id: str):
        self.search_product(item_id)
        del self.items[item_id]
        print(f"✓ Product '{item_id}' deleted from inventory.")

    def display_report(self, low_stock_threshold: int | None = None):
        if not self.items:
            print("Inventory is completely empty.")
            return

        items_to_show = self.items.values()
        header = "FULL INVENTORY REPORT"
        if low_stock_threshold is not None:
            items_to_show = [i for i in items_to_show if i.quantity <= low_stock_threshold]
            header = f"LOW STOCK REPORT (<= {low_stock_threshold} units)"

        print("\n" + "=" * 90)
        print(header.center(90))
        print("=" * 90)
        total_val = 0.0
        for item in items_to_show:
            print(item.get_details())
            total_val += item.calculate_value()
        print("-" * 90)
        print(f"Total Valuation of Displayed Inventory: ₹{total_val:,.2f}")
        print("=" * 90)

    # --- File Handling (CSV) ---
    def save_to_file(self):
        try:
            with open(self.filename, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["type", "item_id", "name", "category", "price", "quantity", "expiry_date"]
                )
                for item in self.items.values():
                    is_perishable = isinstance(item, PerishableProduct)
                    writer.writerow(
                        [
                            "Perishable" if is_perishable else "Standard",
                            item.item_id,
                            item.name,
                            item.category,
                            item.price,
                            item.quantity,
                            item.expiry_date if is_perishable else "",
                        ]
                    )
            print(f"✓ Inventory records saved to '{os.path.basename(self.filename)}'.")
        except IOError as e:
            print(f"File Error: Could not save inventory ({e}).")

    def load_from_file(self):
        if not os.path.exists(self.filename):
            print(f"Notice: '{os.path.basename(self.filename)}' not found. Starting with empty records.")
            return

        try:
            with open(self.filename, mode="r", newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames:
                    reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

                for row in reader:
                    cleaned = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items() if k}
                    p_type = cleaned.get("type", "").capitalize()
                    item_id = cleaned.get("item_id", "")
                    name = cleaned.get("name", "")
                    cat = cleaned.get("category", "")
                    price = float(cleaned.get("price", 0.0))
                    qty = int(cleaned.get("quantity", 0))
                    expiry = cleaned.get("expiry_date", "")

                    if item_id:
                        if p_type == "Perishable":
                            self.items[item_id] = PerishableProduct(
                                item_id, name, cat, price, qty, expiry
                            )
                        else:
                            self.items[item_id] = Product(
                                item_id, name, cat, price, qty
                            )

            print(f"✓ Loaded {len(self.items)} inventory item(s) from '{os.path.basename(self.filename)}'.")
        except Exception as e:
            print(f"Warning: Issue reading '{self.filename}' ({e}). Starting fresh.")


# ==========================================
# 5. CLI Interface Loop
# ==========================================
def main():
    manager = InventoryManager()

    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM ===")
        print("1. Add Standard Product")
        print("2. Add Perishable Product")
        print("3. Search Product")
        print("4. Adjust Stock Quantity (+/-)")
        print("5. Update Product Price")
        print("6. Delete Product")
        print("7. Display Inventory Report")
        print("8. Display Low Stock Alert (< 10 units)")
        print("9. Save Records")
        print("10. Save & Exit")

        choice = input("Enter choice (1-10): ").strip()

        try:
            if choice in ("1", "2"):
                item_id = input("Product ID / SKU: ").strip()
                name = input("Product Name: ").strip()
                cat = input("Category: ").strip()
                price = float(input("Unit Price: ").strip())
                qty = int(input("Initial Stock Quantity: ").strip())
                expiry = ""
                if choice == "2":
                    expiry = input("Expiry Date (YYYY-MM-DD): ").strip()
                manager.add_product(item_id, name, cat, price, qty, expiry)

            elif choice == "3":
                item_id = input("Enter Product ID: ").strip()
                item = manager.search_product(item_id)
                print(f"\n{item.get_details()}")

            elif choice == "4":
                item_id = input("Enter Product ID: ").strip()
                delta = int(
                    input("Enter stock adjustment (positive to add, negative to sell): ").strip()
                )
                manager.update_stock(item_id, delta)

            elif choice == "5":
                item_id = input("Enter Product ID: ").strip()
                new_price = float(input("Enter New Unit Price: ").strip())
                manager.update_price(item_id, new_price)

            elif choice == "6":
                item_id = input("Enter Product ID to delete: ").strip()
                manager.delete_product(item_id)

            elif choice == "7":
                manager.display_report()

            elif choice == "8":
                manager.display_report(low_stock_threshold=10)

            elif choice == "9":
                manager.save_to_file()

            elif choice == "10":
                manager.save_to_file()
                print("Exiting application. Goodbye!")
                break

            else:
                print("Invalid choice. Please select from 1 to 10.")

        except (ProductNotFoundError, DuplicateProductError, InvalidStockError) as err:
            print(f"Inventory Error: {err}")
        except ValueError as ve:
            print(f"Input Error: Please provide valid numerical inputs ({ve}).")
        except Exception as e:
            print(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()