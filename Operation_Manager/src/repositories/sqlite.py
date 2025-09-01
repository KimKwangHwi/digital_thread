# sqlite.py

import sqlite3

def init_db():
    """Initialize the SQLite database and create necessary tables."""
    conn = sqlite3.connect("cnc_status.db")
    cursor = conn.cursor()
    
    # Create a sample table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()