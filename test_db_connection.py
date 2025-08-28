import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'instance', 'phone_store.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print(f"Database created and table 'test_table' created successfully at {db_path}")
except sqlite3.Error as e:
    print(f"Error connecting to or creating database: {e}")