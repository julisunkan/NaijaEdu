#!/usr/bin/env python3
"""
Update existing courses with appropriate categories based on their titles
"""
import sqlite3
import os

def categorize_existing_courses():
    """Update existing courses with appropriate categories"""
    db_path = os.path.join(os.getcwd(), "instance", "elearning.db")
    
    if not os.path.exists(db_path):
        print("Database file doesn't exist yet")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Category mapping based on course titles
    category_mappings = {
        'programming': ['Python', 'Programming', 'Development', 'Code', 'Software'],
        'web-development': ['Web Development', 'HTML', 'CSS', 'JavaScript', 'Flask', 'Django'],
        'mobile-development': ['Mobile', 'App Development', 'Flutter', 'React Native', 'Android', 'iOS'],
        'data-science': ['Data Science', 'Analytics', 'Machine Learning', 'AI', 'Statistics'],
        'artificial-intelligence': ['Artificial Intelligence', 'Machine Learning', 'AI', 'Deep Learning'],
        'cybersecurity': ['Security', 'Cybersecurity', 'Network Security', 'Ethical Hacking'],
        'business': ['Business', 'Entrepreneurship', 'Management', 'Leadership', 'Strategy'],
        'marketing': ['Marketing', 'Digital Marketing', 'Social Media', 'SEO', 'Advertising'],
        'finance': ['Finance', 'Financial', 'Investment', 'Accounting', 'Banking', 'Money'],
        'health': ['Health', 'Wellness', 'Medical', 'Healthcare', 'Nutrition'],
        'fitness': ['Fitness', 'Exercise', 'Workout', 'Gym', 'Training'],
        'design': ['Design', 'Graphic Design', 'UI', 'UX', 'Creative', 'Branding'],
        'photography': ['Photography', 'Photo', 'Video', 'Editing', 'Visual'],
        'music': ['Music', 'Audio', 'Sound', 'Production', 'Recording'],
        'language': ['Language', 'English', 'Communication', 'Writing', 'Speaking'],
        'education': ['Education', 'Teaching', 'Learning', 'Academic', 'Training'],
        'personal-development': ['Personal Development', 'Productivity', 'Self', 'Growth'],
        'cooking': ['Cooking', 'Culinary', 'Food', 'Recipe', 'Kitchen'],
        'crafts': ['Arts', 'Crafts', 'DIY', 'Handmade', 'Creative']
    }
    
    try:
        # Get all courses
        cursor.execute("SELECT id, title, description FROM course")
        courses = cursor.fetchall()
        
        for course_id, title, description in courses:
            category = 'general'  # default category
            
            # Check title and description for keywords
            content = f"{title} {description or ''}".lower()
            
            for cat_key, keywords in category_mappings.items():
                if any(keyword.lower() in content for keyword in keywords):
                    category = cat_key
                    break
            
            # Update course category
            cursor.execute("UPDATE course SET category = ? WHERE id = ?", (category, course_id))
            print(f"Updated course '{title}' with category '{category}'")
        
        conn.commit()
        print("All courses categorized successfully!")
        
    except sqlite3.Error as e:
        print(f"Error categorizing courses: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    categorize_existing_courses()