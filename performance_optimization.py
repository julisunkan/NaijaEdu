#!/usr/bin/env python3
"""
Performance optimization script to improve database queries and caching
"""
import sqlite3
import os

def optimize_database():
    """Add indexes to improve query performance"""
    db_path = os.path.join(os.getcwd(), "instance", "elearning.db")
    
    if not os.path.exists(db_path):
        print("Database file doesn't exist yet")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Add indexes for common queries
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_course_active_approved ON course(is_active, approval_status)",
            "CREATE INDEX IF NOT EXISTS idx_enrollment_user_status ON enrollment(user_id, status)",
            "CREATE INDEX IF NOT EXISTS idx_lesson_course ON lesson(course_id)",
            "CREATE INDEX IF NOT EXISTS idx_quiz_course ON quiz(course_id)",
            "CREATE INDEX IF NOT EXISTS idx_assignment_course ON assignment(course_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_role ON user(role)",
            "CREATE INDEX IF NOT EXISTS idx_payment_user ON payment(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_wallet_transaction_user ON wallet_transaction(user_id)"
        ]
        
        for index_sql in indexes:
            print(f"Creating index: {index_sql}")
            cursor.execute(index_sql)
        
        # Optimize database
        cursor.execute("ANALYZE")
        cursor.execute("PRAGMA optimize")
        
        conn.commit()
        print("Database optimization completed successfully")
        
    except sqlite3.Error as e:
        print(f"Error optimizing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    optimize_database()