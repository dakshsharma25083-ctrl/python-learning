import sqlite3
import os
import time
from datetime import datetime

# Database setup
DATABASE = 'ecommerce.db'

class EcommerceSQLite:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.cart = {}
        self.init_database()
        self.connect()

    def connect(self):
        """Database se connect karo"""
        self.conn = sqlite3.connect(DATABASE)
        self.cursor = self.conn.cursor()

    def init_database(self):
        """Database aur tables create karo"""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL NOT NULL,
                items TEXT NOT NULL
            )
        ''')

        # Order items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')

        # Check if products table is empty, if yes add sample data
        cursor.execute('SELECT COUNT(*) FROM products')
        if cursor.fetchone()[0] == 0:
            self.add_sample_products(cursor)

        conn.commit()
        conn.close()

    def add_sample_products(self, cursor):
        """Sample products add karo"""
        products = [
            ('Wireless Headphones', 99.99, 15, 'High-quality wireless headphones with noise cancellation'),
            ('USB-C Cable', 12.99, 50, 'Durable USB-C charging cable, 2 meters long'),
            ('Phone Case', 19.99, 30, 'Protective phone case with shockproof design'),
            ('Screen Protector', 9.99, 100, 'Tempered glass screen protector'),
            ('Power Bank', 34.99, 20, 'Fast charging 20000mAh power bank'),
            ('Laptop Stand', 44.99, 25, 'Adjustable aluminum laptop stand'),
            ('Mouse Pad', 14.99, 40, 'Large gaming mouse pad with non-slip base'),
            ('Keyboard', 79.99, 12, 'Mechanical gaming keyboard with RGB lighting'),
        ]

        cursor.executemany('''
            INSERT INTO products (name, price, stock, description)
            VALUES (?, ?, ?, ?)
        ''', products)

    def clear_screen(self):
        """Terminal screen clear karo"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Header print karo"""
        print("\n" + "="*60)
        print("          🛍️  SHOPHUB - E-COMMERCE STORE  🛍️")
        print("="*60 + "\n")

    def print_separator(self):
        """Separator print karo"""
        print("-"*60)

    def view_products(self):
        """Sabhi products dikhaao"""
        self.clear_screen()
        self.print_header()
        
        self.cursor.execute('SELECT id, name, price, stock, description FROM products ORDER BY id')
        products = self.cursor.fetchall()

        print("📦 AVAILABLE PRODUCTS:\n")
        
        for product in products:
            product_id, name, price, stock, description = product
            stock_status = f"✓ In Stock ({stock})" if stock > 0 else "✗ Out of Stock"
            
            print(f"ID: {product_id} | {name}")
            print(f"   Price: ₹{price} | Status: {stock_status}")
            print(f"   Description: {description}")
            print()

        self.print_separator()

    def add_to_cart(self):
        """Cart mein product add karo"""
        self.view_products()
        
        try:
            product_id = int(input("\n➤ Enter Product ID to add: "))
            quantity = int(input("➤ Enter Quantity: "))

            # Check if product exists aur stock hai
            self.cursor.execute('SELECT name, price, stock FROM products WHERE id = ?', (product_id,))
            product = self.cursor.fetchone()

            if not product:
                print("\n❌ Product not found!")
                return

            name, price, stock = product

            if quantity > stock:
                print(f"\n❌ Only {stock} items available!")
                return

            # Add to cart
            if product_id in self.cart:
                self.cart[product_id]['quantity'] += quantity
            else:
                self.cart[product_id] = {
                    'name': name,
                    'price': price,
                    'quantity': quantity
                }

            print(f"\n✓ Added {quantity} x {name} to cart!")
            time.sleep(1)

        except ValueError:
            print("\n❌ Invalid input!")
            time.sleep(1)

    def view_cart(self):
        """Cart dikhaao"""
        self.clear_screen()
        self.print_header()

        if not self.cart:
            print("❌ Cart is empty!\n")
            input("Press Enter to continue...")
            return

        print("🛒 SHOPPING CART:\n")

        total = 0
        item_count = 1

        for product_id, item in self.cart.items():
            item_total = item['price'] * item['quantity']
            total += item_total

            print(f"{item_count}. {item['name']}")
            print(f"   Price: ₹{item['price']} x {item['quantity']} = ₹{item_total:.2f}")
            print()
            item_count += 1

        self.print_separator()
        print(f"💰 TOTAL: ₹{total:.2f}\n")

    def update_cart(self):
        """Cart update karo"""
        if not self.cart:
            print("\n❌ Cart is empty!")
            time.sleep(1)
            return

        self.view_cart()

        try:
            product_id = int(input("➤ Enter Product ID to update: "))

            if product_id not in self.cart:
                print("\n❌ Product not in cart!")
                time.sleep(1)
                return

            quantity = int(input("➤ Enter new quantity (0 to remove): "))

            if quantity == 0:
                del self.cart[product_id]
                print("\n✓ Product removed from cart!")
            else:
                # Check stock
                self.cursor.execute('SELECT stock FROM products WHERE id = ?', (product_id,))
                stock = self.cursor.fetchone()[0]

                if quantity > stock:
                    print(f"\n❌ Only {stock} items available!")
                    time.sleep(1)
                    return

                self.cart[product_id]['quantity'] = quantity
                print("\n✓ Cart updated!")

            time.sleep(1)

        except ValueError:
            print("\n❌ Invalid input!")
            time.sleep(1)

    def remove_from_cart(self):
        """Cart se product remove karo"""
        if not self.cart:
            print("\n❌ Cart is empty!")
            time.sleep(1)
            return

        self.view_cart()

        try:
            product_id = int(input("➤ Enter Product ID to remove: "))

            if product_id in self.cart:
                removed_item = self.cart[product_id]['name']
                del self.cart[product_id]
                print(f"\n✓ {removed_item} removed from cart!")
            else:
                print("\n❌ Product not in cart!")

            time.sleep(1)

        except ValueError:
            print("\n❌ Invalid input!")
            time.sleep(1)

    def checkout(self):
        """Order complete karo"""
        if not self.cart:
            print("\n❌ Cart is empty! Add products first.")
            time.sleep(1)
            return

        self.view_cart()

        confirm = input("➤ Confirm order? (yes/no): ").lower()

        if confirm != 'yes':
            print("\n❌ Order cancelled!")
            time.sleep(1)
            return

        try:
            # Calculate total
            total = 0
            order_items = []

            for product_id, item in self.cart.items():
                item_total = item['price'] * item['quantity']
                total += item_total
                order_items.append(f"{item['name']} x{item['quantity']}")

                # Update stock
                self.cursor.execute('''
                    UPDATE products 
                    SET stock = stock - ? 
                    WHERE id = ?
                ''', (item['quantity'], product_id))

            items_str = ', '.join(order_items)

            # Create order
            self.cursor.execute('''
                INSERT INTO orders (total_amount, items)
                VALUES (?, ?)
            ''', (total, items_str))

            order_id = self.cursor.lastrowid

            # Insert order items
            for product_id, item in self.cart.items():
                item_total = item['price'] * item['quantity']
                self.cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, price)
                    VALUES (?, ?, ?, ?)
                ''', (order_id, product_id, item['quantity'], item['price']))

            self.conn.commit()

            # Clear cart
            self.cart = {}

            self.clear_screen()
            self.print_header()
            print(f"✓ ORDER PLACED SUCCESSFULLY!")
            print(f"  Order ID: #{order_id}")
            print(f"  Total Amount: ₹{total:.2f}")
            print(f"  Items: {items_str}")
            print()
            
            input("Press Enter to continue...")

        except Exception as e:
            print(f"\n❌ Error placing order: {e}")
            time.sleep(1)

    def view_orders(self):
        """Sabhi orders dikhaao"""
        self.clear_screen()
        self.print_header()

        self.cursor.execute('SELECT id, order_date, total_amount, items FROM orders ORDER BY id DESC')
        orders = self.cursor.fetchall()

        if not orders:
            print("❌ No orders found!\n")
            input("Press Enter to continue...")
            return

        print("📋 ALL ORDERS:\n")

        for order_id, order_date, total, items in orders:
            print(f"Order ID: #{order_id}")
            print(f"Date: {order_date}")
            print(f"Total: ₹{total:.2f}")
            print(f"Items: {items}")
            print()

        self.print_separator()
        input("\nPress Enter to continue...")

    def search_product(self):
        """Product search karo"""
        self.clear_screen()
        self.print_header()

        search_term = input("🔍 Enter product name to search: ").lower()

        self.cursor.execute('''
            SELECT id, name, price, stock, description 
            FROM products 
            WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ?
        ''', (f'%{search_term}%', f'%{search_term}%'))

        products = self.cursor.fetchall()

        if not products:
            print("\n❌ No products found!")
            time.sleep(1)
            return

        print(f"\n🔍 Search Results for '{search_term}':\n")

        for product_id, name, price, stock, description in products:
            stock_status = f"✓ In Stock ({stock})" if stock > 0 else "✗ Out of Stock"
            
            print(f"ID: {product_id} | {name}")
            print(f"   Price: ₹{price} | Status: {stock_status}")
            print(f"   Description: {description}")
            print()

        self.print_separator()
        input("\nPress Enter to continue...")

    def show_menu(self):
        """Main menu dikhaao"""
        while True:
            self.clear_screen()
            self.print_header()

            cart_count = sum(item['quantity'] for item in self.cart.values())
            cart_display = f"(Items: {cart_count})" if cart_count > 0 else ""

            print("📌 MAIN MENU:\n")
            print("1. 👀 View All Products")
            print("2. 🔍 Search Products")
            print("3. 🛒 Add to Cart")
            print("4. 📦 View Cart " + cart_display)
            print("5. ✏️  Update Cart")
            print("6. 🗑️  Remove from Cart")
            print("7. 💳 Checkout")
            print("8. 📋 View Orders")
            print("9. 🚪 Exit")
            print()

            choice = input("➤ Enter your choice (1-9): ")

            if choice == '1':
                self.view_products()
                input("\nPress Enter to continue...")
            elif choice == '2':
                self.search_product()
            elif choice == '3':
                self.add_to_cart()
            elif choice == '4':
                self.view_cart()
                input("\nPress Enter to continue...")
            elif choice == '5':
                self.update_cart()
            elif choice == '6':
                self.remove_from_cart()
            elif choice == '7':
                self.checkout()
            elif choice == '8':
                self.view_orders()
            elif choice == '9':
                self.clear_screen()
                print("\n👋 Thank you for shopping at ShopHub!")
                print("   Goodbye!\n")
                break
            else:
                print("\n❌ Invalid choice! Please try again.")
                time.sleep(1)

    def close(self):
        """Database connection close karo"""
        if self.conn:
            self.conn.close()


def main():
    """Main function"""
    app = EcommerceSQLite()
    try:
        app.show_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    finally:
        app.close()


if __name__ == '__main__':
    main()