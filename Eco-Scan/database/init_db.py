import sqlite3
import os

def initialize_database():
    """Initialize the SQLite database with required tables"""
    
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)
    
    conn = sqlite3.connect('database/waste_analysis.db')
    cursor = conn.cursor()
    
    # Create analyses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            waste_type TEXT NOT NULL,
            category TEXT NOT NULL,
            confidence REAL NOT NULL,
            disposal_guide TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create waste categories reference table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS waste_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT UNIQUE NOT NULL,
            color_code TEXT,
            icon_name TEXT
        )
    ''')
    
    # Insert default waste categories
    categories = [
        ('Biodegradable', '#28a745', 'leaf'),
        ('Recyclable', '#007bff', 'recycle'),
        ('General Waste', '#6c757d', 'trash'),
        ('Medical Waste', '#dc3545', 'biohazard'),
        ('Hazardous Waste', '#ffc107', 'exclamation-triangle'),
        ('E-Waste', '#17a2b8', 'laptop')
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO waste_categories (category_name, color_code, icon_name)
        VALUES (?, ?, ?)
    ''', categories)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    initialize_database()