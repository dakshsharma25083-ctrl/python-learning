import sqlite3


conn = sqlite3.connect("store.db")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    stock INTEGER
    status TEXT DEFAULT 'available'
)
""")

conn.commit()



class Store:

    
    def add_product(self):

        name = input("Enter Product Name: ")
        price = float(input("Enter Price: "))
        stock = int(input("Enter Stock: "))

        cursor.execute(
            "INSERT INTO products(name, price, stock) VALUES(?,?,?)",
            (name, price, stock)
        )

        conn.commit()

        print("Product Added Successfully")


    
    def show_products(self):

        cursor.execute("SELECT * FROM products")

        products = cursor.fetchall()

        print("\n📦 PRODUCTS")
        print("-" * 40)

        for product in products:
            print(product)


    
    def buy_product(self):

        product_id = int(input("Enter Product ID: "))
        quantity = int(input("Enter Quantity: "))

        cursor.execute(
            "SELECT * FROM products WHERE id=?",
            (product_id,)
        )

        product = cursor.fetchone()

        
        if product is None:
            print(" Product Not Found")
            return

        stock = product[3]

        
        if quantity > stock:
            print("Not Enough Stock")
            return

        
        new_stock = stock - quantity

        cursor.execute(
            "UPDATE products SET stock=? WHERE id=?",
            (new_stock, product_id)
        )

        conn.commit()

        
        total = product[2] * quantity

        
        print("\n" + "=" * 40)
        print("🧾 STORE BILL")
        print("=" * 40)

        print("Product Name :", product[1])
        print("Price        :", product[2])
        print("Quantity     :", quantity)
        print("-" * 40)
        print("Total Bill   : ₹", total)

        print("=" * 40)
        print(" Thank You For Shopping")
        print("=" * 40)



s = Store()

while True:

    print("\n====== STORE MENU ======")
    print("1. Add Product")
    print("2. Show Products")
    print("3. Buy Product")
    print("4. Exit")

    choice = input("Enter Choice: ")

    if choice == "1":
        s.add_product()

    elif choice == "2":
        s.show_products()

    elif choice == "3":
        s.buy_product()

    elif choice == "4":
        print(" Bye")
        break

    else:
        print(" Invalid Choice")