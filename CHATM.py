import mysql.connector as msc
from datetime import date, datetime

# Database connection and setup
mcon = msc.connect(host="localhost", user="root", passwd="123456")
mc = mcon.cursor()

# Create database and tables if they don't exist
mc.execute("CREATE DATABASE IF NOT EXISTS shop_management_system")
mc.execute('USE shop_management_system')
mc.execute('''CREATE TABLE IF NOT EXISTS login (username VARCHAR(25) NOT NULL,password VARCHAR(25) NOT NULL)''')
mc.execute('''CREATE TABLE IF NOT EXISTS stock (pcode INT NOT NULL AUTO_INCREMENT,pname CHAR(25) NOT NULL,quantity INT NOT NULL,price INT NOT NULL,PRIMARY KEY (pcode))''')
mc.execute('''CREATE TABLE IF NOT EXISTS transaction (sno INT AUTO_INCREMENT PRIMARY KEY,odate DATETIME NOT NULL,name VARCHAR(25) NOT NULL,pname VARCHAR(150) NOT NULL,cphno VARCHAR(20) NOT NULL,orderid INT NOT NULL,payment_method VARCHAR(25),amount INT NOT NULL)''')
mc.execute('''CREATE TABLE IF NOT EXISTS distributor (dcode VARCHAR(20) ,dname VARCHAR(200) NOT NULL,dphone VARCHAR(25),address VARCHAR(200),pname VARCHAR(50),orderquantity INT,price INT NOT NULL)''')
mcon.commit()

# Insert default credentials into login table if empty
mc.execute('SELECT COUNT(*) FROM login')
if mc.fetchone()[0] == 0:
    mc.execute("INSERT INTO login (username, password) VALUES ('shop', '123456')")
    mcon.commit()

def login():  # Handles user login.
    un = input("Enter username: ")
    pw = input("Enter password: ")   
    mc.execute("SELECT * FROM login WHERE username = %s AND password = %s", (un, pw))
    if mc.fetchone() is not None:
        print("Login successful!")
        return True
    else:
        print("Invalid username or password.")
        return False

def newp():  # Adds a new product to the stock table
    pname = input('Enter the product name: ')
    quantity = int(input('Enter the quantity available: '))
    price = int(input('Enter the price of the product: '))   
    mc.execute("INSERT INTO stock (pname, quantity, price) VALUES (%s, %s, %s)", (pname, quantity, price))
    mcon.commit()
    print('Product added successfully!')

def update():  # Updates the price, quantity, or name of an existing product in the stock table
    pcode = int(input('Enter the product code to update: '))
    while True:
        what_to_change = input("Enter what you want to change (price/quantity/name), or 'exit' to finish: ").lower()
        if what_to_change == "quantity":
            newq = int(input("Enter the new quantity: "))
            mc.execute("UPDATE stock SET quantity = %s WHERE pcode = %s", (newq, pcode))
            mcon.commit()
            print("Product quantity updated successfully!")
        elif what_to_change == "price":
            newp = int(input("Enter the new price: "))
            mc.execute("UPDATE stock SET price = %s WHERE pcode = %s", (newp, pcode))
            mcon.commit()
            print("Product price updated successfully!")
        elif what_to_change == "name":
            newn = input("Enter the new name: ")
            mc.execute("UPDATE stock SET pname = %s WHERE pcode = %s", (newn, pcode))
            mcon.commit()
            print("Product name updated successfully!")
        elif what_to_change == "exit":
            print("Exiting update menu.")
            break
        else:
            print("Invalid choice.")

def delete():  # Deletes a product from the stock table
    pcode = int(input('Enter the product code to delete: '))    
    mc.execute("DELETE FROM stock WHERE pcode = %s", (pcode,))
    mcon.commit()
    print('Product deleted successfully!')

def displayall():  # Displays all products in the stock table
    mc.execute('SELECT pcode, pname, quantity, price FROM stock')
    print('Code\t\tName\t\tQuantity\t\tPrice')
    for pcode, pname, quantity, price in mc.fetchall():
        print(f'{pcode}\t\t{pname}\t\t{quantity}\t\t{price}')

def displaylow():  # Displays products with quantity less than 15
    print('Products whose quantity are less than 15:')
    mc.execute('SELECT pcode, pname, quantity, price FROM stock WHERE quantity < 15')
    print('Code\t\tName\t\tQuantity\t\tPrice')
    for pcode, pname, quantity, price in mc.fetchall():
        print(f'{pcode}\t\t{pname}\t\t{quantity}\t\t{price}')

def search():  # Searches for a stock item by code or name
    s = input("Enter product code or name to search: ")
    mc.execute("SELECT pcode, pname, quantity, price FROM stock WHERE pcode = %s OR pname LIKE %s", (s, f'%{s}%'))    
    res = mc.fetchall()
    if res:
        print('Code\t\tName\t\tQuantity\t\tPrice')
        for pcode, pname, quantity, price in res:
            print(f'{pcode}\t\t{pname}\t\t{quantity}\t\t{price}')
    else:
        print("No product found.")

def changepw():  # Changes the login password
    oldpw = input('Enter the current password: ')
    mc.execute('SELECT password FROM login')
    currentpw = mc.fetchone()[0]   
    if oldpw == currentpw:
        newpw = input('Enter the new password: ')
        mc.execute("UPDATE login SET password = %s", (newpw,))
        mcon.commit()
        print('Password changed successfully!')
    else:
        print('Incorrect current password.')

def transaction():  # Auditing a transaction
    c_name = input("Customer's name: ")
    c_phone = input("Customer's phone number: ")
    o_id = int(input("Order ID: "))
    pay_method = input("Payment method (Cash, Card, UPI): ")
    prods = []
    total = 0
    n_products = int(input("How many products to buy: "))
    for i in range(n_products):
        p_code = int(input("Product code: "))
        qty = int(input("Quantity: "))
        mc.execute("SELECT pname, price, quantity FROM stock WHERE pcode = %s", (p_code,))
        prod = mc.fetchone()
        if prod and prod[2] >= qty:
            p_name, price, stock_qty = prod
            amt = price * qty
            total += amt
            prods.append((p_name, qty, amt))
            mc.execute("UPDATE stock SET quantity = %s WHERE pcode = %s", (stock_qty - qty, p_code))
        else:
            print(f'Insufficient stock for product code {p_code}. SORRY!.')
            continue
    tax = total * 0.03
    total_with_tax = total + tax
    mc.execute("INSERT INTO transaction (odate, name, pname, cphno, orderid, payment_method, amount) VALUES (NOW(), %s, %s, %s, %s, %s, %s)", (c_name, ', '.join([p[0] for p in prods]), c_phone, o_id, pay_method, total_with_tax))
    mcon.commit()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    print("\nTransaction Summary")
    print('-------------------------------------------------------------------------')
    print('Essentials Market')
    print('-------------------------------------------------------------------------')
    print('''Essentials Market,
Near Lakshmi Narayan Mandir,
Sector 36, Nerul West,
Navi Mumbai, 400706''')
    print('-------------------------------------------------------------------------')
    print("Order ID:", o_id)
    print("Customer Name:", c_name)
    print("Date:", date_str, "  II  Time:", time_str)
    print("Customer Phone No.:", c_phone)
    print('-------------------------------------------------------------------------')
    print("Payment Method:", pay_method)
    print('-------------------------------------------------------------------------')
    print("Product\t\tQuantity\t\tAmount")
    for p_name, qty, amt in prods:
        print(f'{p_name}\t\t{qty}\t\t{amt}')
    print('-------------------------------------------------------------------------')
    print("Subtotal:", total)
    print("Tax (3%):", round(tax, 2))
    print("Total Amount:", round(total_with_tax, 2))
    print('-------------------------------------------------------------------------')
    print('THANK YOU AND VISIT AGAIN')
    print('-------------------------------------------------------------------------')

def display_recent_transactions():
    """Displays recent transactions in a formatted list."""
    print("\nRecent Transactions")
    print('------------------------------------------')
    print('Essentials Market')
    print('------------------------------------------')
    print('''Essentials Market,
Near Lakshmi Narayan Mandir,
Sector 36, Nerul West,
Navi Mumbai, 400706''')
    print('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')

    mc.execute("SELECT odate, orderid, name, cphno, payment_method, amount FROM transaction ORDER BY odate DESC LIMIT 5")
    trans = mc.fetchall()

    if trans:
        for odate, orderid, name, cphno, pay_method, amount in trans:
            if isinstance(odate, datetime):
                date_str = odate.strftime("%Y-%m-%d")
                time_str = odate.strftime("%H:%M:%S")
                print(f"Date: {date_str}, Time: {time_str}, Order ID: {orderid}, Name: {name}, Phone: {cphno}, Payment Method: {pay_method}, Amount: {amount}")
                print('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')

    else:
        print("No transactions found.")

def new_d(): 
    dcode = input("Distributor code: ")
    dname = input("Distributor name: ")
    dphone = input("Phone number: ")
    address = input("Address: ")

    num_products = int(input("How many products is the distributor supplying? "))
    
    for _ in range(num_products):
        pname = input("Product name: ")
        orderquantity = int(input(f"Order quantity for {pname}: "))
        price = float(input(f"Total price for {pname}: "))  # Ensure price is float
        mc.execute(
            "INSERT INTO distributor (dcode, dname, dphone, address, pname, orderquantity, price) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (dcode, dname, dphone, address, pname, orderquantity, price)
        )
        mcon.commit()  # Commit the insertion
        
        # Attempt to update stock for each product
        mc.execute("UPDATE stock SET quantity = quantity + %s WHERE pname = %s", (orderquantity, pname))
        if mc.rowcount == 0:  # If no rows were affected, the product does not exist
            # Insert the product into stock if it does not exist
            mc.execute("INSERT INTO stock (pname, quantity, price) VALUES (%s, %s, %s)", (pname, orderquantity, price))
            mcon.commit()  # Commit the stock insertion
    
    print("Distributor and stock updated for all products.")



def display_d(): 
    # Execute the query and fetch data
    mc.execute('SELECT * FROM distributor')
    res = mc.fetchall()
    
    # Dictionary to store distributor information
    distributors = {}
    
    # Organize data by distributor code
    for record in res:
        t_c, t_n, t_p, t_a, t_pn, t_q, t_pr = record
        
        if t_c not in distributors:
            distributors[t_c] = {
                'name': t_n,
                'phone': t_p,
                'address': t_a,
                'products': []
            }
        
        # Append product details to the distributor's list
        distributors[t_c]['products'].append({
            'name': t_pn,
            'quantity': t_q,
            'price': t_pr
        })
    
    # Display each distributor's information
    for dcode, info in distributors.items():
        print("----------------------------------------------------------------------------------------------")
        print(f"| DISTRIBUTOR CODE: {dcode}    |  DISTRIBUTOR NAME: {info['name']}")
        print(f"| DISTRIBUTOR PHONE: {info['phone']}")
        print(f"| ADDRESS: {info['address']}")
        print(f"| PRODUCTS PURCHASED: ")
        
        # Display each product for the distributor
        for product in info['products']:
            print(f"    |  PRODUCT NAME: {product['name']}    |  ORDER QUANTITY: {product['quantity']}    |  TOTAL PRICE: {product['price']}")
        
        print("----------------------------------------------------------------------------------------------\n")


def search_d():  # Search distributor by name or code
    term = input("Enter distributor name or code to search: ")
    mc.execute("SELECT dcode, dname, dphone, address, pname, orderquantity, price FROM distributor WHERE dname LIKE %s OR dcode LIKE %s", (f'%{term}%', f'%{term}%'))    
    res = mc.fetchall()
    
    if res:
        for dc, dn, dp, ad, pn, oq, pr in res:
            print(f"| DISTRIBUTOR CODE: {dc}    |  DISTRIBUTOR NAME: {dn}")
            print(f"| DISTRIBUTOR PHONE: {dp}")
            print(f"| ADDRESS: {ad}")
            print(f"| PRODUCTS PURCHASED: {pn} | ORDER QUANTITY: {oq} | PRICE: {pr}")
            print("-" * 80)  # Separator for clarity
    else:
        print("No distributor found.")

def update_d():
    dc = input("Enter distributor code to update: ")

    # Check if distributor exists
    mc.execute("SELECT * FROM distributor WHERE dcode = %s", (dc,))
    result = mc.fetchall()  # Use fetchall() to consume all results
    if not result:
        print("Distributor not found.")
        return

    # Get new details for the distributor
    nn = input("Enter new name (leave blank to skip): ")
    np = input("Enter new phone (leave blank to skip): ")
    na = input("Enter new address (leave blank to skip): ")

    # Create a list of update queries and values
    updates = []
    if nn:
        updates.append(("dname", nn))
    if np:
        updates.append(("dphone", np))
    if na:
        updates.append(("address", na))

    # Update distributor information in a single query
    if updates:
        update_str = ", ".join(f"{col} = %s" for col, _ in updates)
        update_values = [val for _, val in updates] + [dc]
        mc.execute(f"UPDATE distributor SET {update_str} WHERE dcode = %s", update_values)

    # Fetch results after the update
    mc.execute("SELECT * FROM distributor WHERE dcode = %s", (dc,))
    result = mc.fetchall()  # Again, use fetchall() to consume results
    if not result:
        print("Distributor not found after update.")
        return

    # Handle product updates
    while True:
        pn = input("Enter new product name (leave blank to skip): ")
        if not pn:
            break

        oq = input("Enter new order quantity (leave blank to skip): ")
        pr = input("Enter new price (leave blank to skip): ")

        if oq and pr:
            mc.execute("UPDATE product SET orderquantity = %s, price = %s WHERE dcode = %s AND pname = %s",
                       (int(oq), float(pr), dc, pn))
        else:
            print("Both order quantity and price must be provided to update a product.")

    mcon.commit()
    print("Distributor details updated successfully.")

def delete_d():  # Delete distributor
    dc = input('Enter the distributor code to delete: ')    
    mc.execute("DELETE FROM distributor WHERE dcode = %s", (dc,))
    mcon.commit()
    print('Distributor deleted successfully!')


while True:
    #if login():
        print('''
**************************************************************************
*                                                                                                     *
*            WELCOME TO SHOP MANAGEMENT SYSTEM          *
*                                                                                                     *
**************************************************************************
''')
        while True:
            print("""1. Manage Stock
2. Record Transaction
3. Display Recent Transactions
4. Manage Distributor
5. Exit
""")            
            ch = input("Enter choice: ")            
            if ch == '1':
                while True:
                    print("""
1. Add Product
2. Update Product Details
3. Delete Product
4. Display All Products
5. Display Low Quantity Products
6. Search Product
7. Change Password
8. Return to Main Menu
""")                    
                    stock_choice = input("Enter choice: ")                    
                    if stock_choice == '1':
                        newp()
                    elif stock_choice == '2':
                        update()
                    elif stock_choice == '3':
                        delete()
                    elif stock_choice == '4':
                        displayall()
                    elif stock_choice == '5':
                        displaylow()
                    elif stock_choice == '6':
                        search()
                    elif stock_choice == '7':
                        changepw()
                    elif stock_choice == '8':
                        break
                    else:
                        print("Invalid choice.")            
            elif ch == '2':
                transaction()

            elif ch=='3':
                display_recent_transactions()
            elif ch == '4':
                while True:
                    print("""1. Add Distributor
2. Display All Distributors
3. Search Distributor
4. Update Distributor
5. Delete Distributor
6. Return to Main Menu""")
                    distributor_choice = input("Enter choice: ")                    
                    if distributor_choice == '1':
                        new_d()
                    elif distributor_choice == '2':
                        display_d()
                    elif distributor_choice == '3':
                        search_d()
                    elif distributor_choice == '4':
                        update_d()
                    elif distributor_choice == '5':
                        delete_d()
                    elif distributor_choice == '6':
                        break
                    else:
                        print("Invalid choice.")
            elif ch == '5':
                print("Exiting program...")
                break
            else:
                print("Invalid choice.")
        break#
   
