#!/usr/bin/env python3
"""
Course categories management system
"""

# Define comprehensive course categories
COURSE_CATEGORIES = [
    ('programming', 'Programming & Development'),
    ('web-development', 'Web Development'),
    ('mobile-development', 'Mobile Development'),
    ('data-science', 'Data Science & Analytics'),
    ('artificial-intelligence', 'Artificial Intelligence & Machine Learning'),
    ('cybersecurity', 'Cybersecurity & Information Security'),
    ('business', 'Business & Entrepreneurship'),
    ('marketing', 'Digital Marketing & Social Media'),
    ('finance', 'Finance & Accounting'),
    ('health', 'Health & Wellness'),
    ('fitness', 'Fitness & Exercise'),
    ('design', 'Graphic Design & Creative Arts'),
    ('photography', 'Photography & Video'),
    ('music', 'Music & Audio Production'),
    ('language', 'Language Learning'),
    ('education', 'Education & Teaching'),
    ('personal-development', 'Personal Development & Productivity'),
    ('cooking', 'Cooking & Culinary Arts'),
    ('crafts', 'Arts & Crafts'),
    ('general', 'General Knowledge')
]

def get_category_choices():
    """Return formatted choices for form fields"""
    return COURSE_CATEGORIES

def get_category_name(category_key):
    """Get the display name for a category key"""
    for key, name in COURSE_CATEGORIES:
        if key == category_key:
            return name
    return 'General Knowledge'

def get_popular_categories():
    """Return most popular categories for homepage display"""
    return [
        'programming',
        'web-development', 
        'business',
        'marketing',
        'data-science',
        'health',
        'design',
        'personal-development'
    ]