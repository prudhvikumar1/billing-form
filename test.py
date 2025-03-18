import sys
import mysql.connector
from mysql.connector import Error
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)

# DatabaseHandler class for connecting and interacting with MySQL
class DatabaseHandler:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                user='root',              # Update with your username
                password='password112', # Update with your password
                database='billing_db'     # Ensure this DB exists or adjust accordingly
            )
            if self.connection.is_connected():
                self.create_tables()
        except Error as e:
            print("Error connecting to MySQL", e)

    def create_tables(self):
        cursor = self.connection.cursor()
        # Create customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone BIGINT
            )
        """)
        # Create bills table with a foreign key to customers
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT,
                amount DECIMAL(10,2),
                bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)
        self.connection.commit()

    def insert_customer(self, name, phone):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO customers (name, phone) VALUES (%s, %s)", (name, phone))
        self.connection.commit()
        return cursor.lastrowid

    def insert_bill(self, customer_id, amount):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO bills (customer_id, amount) VALUES (%s, %s)", (customer_id, amount))
        self.connection.commit()

    def get_all_bills(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT bills.id, customers.name, customers.phone, bills.amount, bills.bill_date 
            FROM bills 
            JOIN customers ON bills.customer_id = customers.id
        """)
        return cursor.fetchall()

# Main application window
class BillingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing Application")
        self.setGeometry(100, 100, 600, 400)
        self.db = DatabaseHandler()  # Initialize the database handler

        self.initUI()

    def initUI(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Billing form elements
        layout.addWidget(QLabel("Customer Name:"))
        self.customer_name = QLineEdit()
        layout.addWidget(self.customer_name)

        layout.addWidget(QLabel("Customer Phone:"))
        self.customer_phone = QLineEdit()
        layout.addWidget(self.customer_phone)

        layout.addWidget(QLabel("Bill Amount:"))
        self.bill_amount = QLineEdit()
        layout.addWidget(self.bill_amount)

        self.submit_button = QPushButton("Save Bill")
        self.submit_button.clicked.connect(self.save_bill)
        layout.addWidget(self.submit_button)

        # Button to retrieve bills
        self.retrieve_button = QPushButton("Retrieve Bills")
        self.retrieve_button.clicked.connect(self.retrieve_bills)
        layout.addWidget(self.retrieve_button)

        # Table to display retrieved bills and customer info
        self.table = QTableWidget()
        layout.addWidget(self.table)

        central_widget.setLayout(layout)

    def save_bill(self):
        # Get values from form
        name = self.customer_name.text().strip()
        phone = self.customer_phone.text().strip()
        amount = self.bill_amount.text().strip()

        if not name or not phone or not amount:
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")
            return

        try:
            # Insert customer and then the bill record
            customer_id = self.db.insert_customer(name, phone)
            self.db.insert_bill(customer_id, amount)
            QMessageBox.information(self, "Success", "Bill saved successfully!")
            # Clear fields after saving
            self.customer_name.clear()
            self.customer_phone.clear()
            self.bill_amount.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving bill: {str(e)}")

    def retrieve_bills(self):
        try:
            data = self.db.get_all_bills()
            # Setup table with retrieved data
            self.table.setRowCount(len(data))
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["Bill ID", "Customer Name", "Phone", "Amount", "Bill Date"])
            for row_idx, row in enumerate(data):
                for col_idx, item in enumerate(row):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(item)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error retrieving bills: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BillingApp()
    window.show()
    sys.exit(app.exec())