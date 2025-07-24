#!/usr/bin/env python3
"""
Migration script to add category column to existing Course table
"""
import sqlite3
import os

def add_category_column():
    # Database path
    db_path = os.path.join(os.getcwd(), "instance", "elearning.db")
    
    if not os.path.exists(db_path):
        print("Database file doesn't exist yet, column will be created when app starts")
        return
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if category column already exists
        cursor.execute("PRAGMA table_info(course)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'category' not in columns:
            print("Adding category column to course table...")
            cursor.execute("ALTER TABLE course ADD COLUMN category VARCHAR(100) DEFAULT 'General'")
            
            # Update existing courses to have a default category
            cursor.execute("UPDATE course SET category = 'General' WHERE category IS NULL")
            
            conn.commit()
            print("Successfully added category column and updated existing courses")
        else:
            print("Category column already exists")
            
    except sqlite3.Error as e:
        print(f"Error adding category column: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_category_column()