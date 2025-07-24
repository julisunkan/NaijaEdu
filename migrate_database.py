#!/usr/bin/env python3
"""
Database migration script to add new Google services and download settings columns
"""

import sqlite3
import os

def migrate_database():
    """Add new columns to system_settings table"""
    db_path = os.path.join('instance', 'elearning.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Creating new database with updated schema.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(system_settings)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add new columns if they don't exist
        new_columns = [
            ('google_adsense_code', 'TEXT'),
            ('google_analytics_code', 'TEXT'),
            ('allow_content_download', 'BOOLEAN DEFAULT 1'),
            ('download_requires_completion', 'BOOLEAN DEFAULT 0')
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE system_settings ADD COLUMN {column_name} {column_type}")
                    print(f"Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"Column {column_name} might already exist: {e}")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_database()