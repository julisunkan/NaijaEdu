#!/usr/bin/env python3
"""
Migration script to add credit system columns to existing database
"""

import sqlite3
import os

def migrate_database():
    """Add credit system columns to the database"""
    db_path = 'instance/elearning.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. It will be created with new schema.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding credit system columns...")
        
        # Add credit system columns to course table
        cursor.execute('ALTER TABLE course ADD COLUMN min_credits_for_certificate INTEGER DEFAULT 70')
        cursor.execute('ALTER TABLE course ADD COLUMN total_available_credits INTEGER DEFAULT 100')
        print("✓ Added credit columns to course table")
        
        # Add credit system columns to quiz table
        cursor.execute('ALTER TABLE quiz ADD COLUMN max_credits INTEGER DEFAULT 10')
        cursor.execute('ALTER TABLE quiz ADD COLUMN pass_threshold REAL DEFAULT 70.0')
        print("✓ Added credit columns to quiz table")
        
        # Add credit system columns to assignment table
        cursor.execute('ALTER TABLE assignment ADD COLUMN max_credits INTEGER DEFAULT 15')
        cursor.execute('ALTER TABLE assignment ADD COLUMN pass_threshold REAL DEFAULT 60.0')
        print("✓ Added credit columns to assignment table")
        
        # Create course_credit table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS course_credit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                item_type VARCHAR(20) NOT NULL,
                item_id INTEGER NOT NULL,
                credits_earned INTEGER DEFAULT 0,
                max_credits INTEGER DEFAULT 0,
                score_percentage REAL DEFAULT 0.0,
                earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (course_id) REFERENCES course (id),
                UNIQUE (user_id, course_id, item_type, item_id)
            )
        ''')
        print("✓ Created course_credit table")
        
        conn.commit()
        print("✅ Migration completed successfully!")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"⚠️  Column already exists: {e}")
        else:
            print(f"❌ Error during migration: {e}")
            conn.rollback()
            raise
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()