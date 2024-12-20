import sqlite3

# Database file path
DB_PATH = "./database/database.db"

# SQL schema for suppliers and communications
schema = """
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    rating FLOAT NOT NULL,
    product TEXT NOT NULL,
    price_per_unit FLOAT NOT NULL,
    quantity_available INTEGER NOT NULL,
    agreement_status TEXT DEFAULT 'Pending'
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    email_subject TEXT NOT NULL,
    email_body TEXT NOT NULL,
    email_status TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
);
"""

# Initial data for suppliers
initial_data = [
    ("Supplier_1", "supplier1@example.com", 3.5, "Wheat", 250.0, 500, "Pending"),
    ("Supplier_2", "supplier2@example.com", 4.2, "Mustard Seed", 300.0, 400, "Pending"),
    ("Supplier_3", "supplier3@example.com", 3.8, "Soybean", 220.0, 600, "Pending"),
]

# Initialize the database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Execute schema creation
    cursor.executescript(schema)

    # Insert initial data if table is empty
    cursor.execute("SELECT COUNT(*) FROM suppliers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO suppliers (name, email, rating, product, price_per_unit, quantity_available, agreement_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            initial_data,
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
