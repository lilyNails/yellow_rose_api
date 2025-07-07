import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'yellow_rose.db')
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.fetchall()
        finally:
            conn.close()
    
    def execute_insert(self, query, params):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

# Product operations
class ProductManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_all_products(self):
        query = """
        SELECT p.product_id, p.name, p.price, p.quantity, p.image_url, c.category_name
        FROM Products p
        JOIN Categories c ON p.category_id = c.category_id
        """
        return self.db.execute_query(query)
    
    def get_product_by_id(self, product_id):
        query = "SELECT * FROM Products WHERE product_id = ?"
        result = self.db.execute_query(query, (product_id,))
        return result[0] if result else None
    
    def add_product(self, name, category_id, price, quantity, image_url=None):
        query = "INSERT INTO Products (name, category_id, price, quantity, image_url) VALUES (?, ?, ?, ?, ?)"
        return self.db.execute_insert(query, (name, category_id, price, quantity, image_url))
    
    def update_product_quantity(self, product_id, new_quantity):
        query = "UPDATE Products SET quantity = ? WHERE product_id = ?"
        self.db.execute_query(query, (new_quantity, product_id))

# Category operations
class CategoryManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_all_categories(self):
        query = "SELECT * FROM Categories"
        return self.db.execute_query(query)
    
    def add_category(self, category_name):
        query = "INSERT INTO Categories (category_name) VALUES (?)"
        return self.db.execute_insert(query, (category_name,))

# Customer operations
class CustomerManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_customer_by_phone(self, phone_number):
        query = "SELECT * FROM Customers WHERE phone_number = ?"
        result = self.db.execute_query(query, (phone_number,))
        return result[0] if result else None
    
    def add_customer(self, name, phone_number):
        query = "INSERT INTO Customers (name, phone_number) VALUES (?, ?)"
        return self.db.execute_insert(query, (name, phone_number))
    
    def update_customer_stats(self, customer_id, total_amount, points_earned):
        query = """
        UPDATE Customers 
        SET total_visits = total_visits + 1,
            total_purchases = total_purchases + ?,
            loyalty_points = loyalty_points + ?,
            last_purchase_date = ?
        WHERE customer_id = ?
        """
        self.db.execute_query(query, (total_amount, points_earned, datetime.now(), customer_id))

# Sales operations
class SalesManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def create_sale(self, invoice_number, customer_id, total_amount, payment_method, points_earned):
        query = """
        INSERT INTO Sales (invoice_number, customer_id, total_amount, payment_method, points_earned)
        VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute_insert(query, (invoice_number, customer_id, total_amount, payment_method, points_earned))
    
    def add_sale_product(self, sale_id, product_id, quantity, unit_price):
        query = "INSERT INTO Sales_Products (sale_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)"
        self.db.execute_insert(query, (sale_id, product_id, quantity, unit_price))
    
    def get_sales_by_date(self, start_date, end_date):
        query = """
        SELECT s.*, c.name as customer_name, c.phone_number
        FROM Sales s
        JOIN Customers c ON s.customer_id = c.customer_id
        WHERE DATE(s.date) BETWEEN ? AND ?
        ORDER BY s.date DESC
        """
        return self.db.execute_query(query, (start_date, end_date))

# User operations
class UserManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def authenticate_user(self, username, password):
        query = "SELECT * FROM Users WHERE username = ? AND password_hash = ?"
        result = self.db.execute_query(query, (username, password))
        return result[0] if result else None
    
    def add_user(self, username, password_hash, role):
        query = "INSERT INTO Users (username, password_hash, role) VALUES (?, ?, ?)"
        return self.db.execute_insert(query, (username, password_hash, role))

# Settings operations
class SettingsManager:
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_setting(self, setting_name):
        query = "SELECT setting_value FROM Settings WHERE setting_name = ?"
        result = self.db.execute_query(query, (setting_name,))
        return result[0][0] if result else None
    
    def set_setting(self, setting_name, setting_value):
        query = "INSERT OR REPLACE INTO Settings (setting_name, setting_value) VALUES (?, ?)"
        self.db.execute_insert(query, (setting_name, setting_value))

