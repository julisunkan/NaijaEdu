# Admin Course Editing Guide

## Overview
The Nigerian E-Learning Platform now includes comprehensive admin functionality for editing all course content. Admins can modify courses, lessons, quizzes, and assignments through a dedicated management interface.

## Admin Access
- **Username:** admin
- **Password:** admin123
- **Login URL:** http://localhost:5000/login

## Admin Capabilities

### 1. Course Management
**Access:** Admin Dashboard → Manage All Courses → `/admin/courses`

**Features:**
- ✅ View all courses in a comprehensive table
- ✅ Edit course details (title, description, price, category)
- ✅ Toggle course active/inactive status
- ✅ Quick access to manage lessons, quizzes, and assignments
- ✅ See course statistics (lesson count, quiz count, assignment count)

### 2. Lesson Management
**Access:** Course Management → Lessons Icon → `/admin/courses/{id}/lessons`

**Features:**
- ✅ View all lessons for a specific course
- ✅ Edit lesson content (title, description, content, order, duration)
- ✅ Support for different content types (text, PDF, video)
- ✅ Reorder lessons with order field
- ✅ Preview lessons before publishing

### 3. Quiz Management
**Access:** Course Management → Quiz Icon → `/admin/courses/{id}/quizzes`

**Features:**
- ✅ View all quizzes for a specific course
- ✅ Edit quiz settings (title, description, time limit, max attempts)
- ✅ Manage quiz questions with full CRUD operations
- ✅ Add new questions with multiple choice options
- ✅ Edit existing questions and correct answers
- ✅ Set point values for questions

### 4. Assignment Management
**Access:** Course Management → Assignment Icon → `/admin/courses/{id}/assignments`

**Features:**
- ✅ View all assignments for a specific course
- ✅ Edit assignment details (title, description, instructions)
- ✅ Set due dates and maximum points
- ✅ View submission counts and status
- ✅ Manage assignment requirements

## Current Course Content Status
- **6 Courses** available for editing
- **16 Lessons** with editable content
- **60 Quizzes** with 178 questions
- **30 Assignments** with detailed instructions

## Navigation Workflow
1. Login as admin → Dashboard
2. Click "Manage All Courses" 
3. Select course to edit
4. Use action buttons to manage specific content types:
   - 📝 Edit Course (course details)
   - 📖 Manage Lessons (lesson content)
   - ❓ Manage Quizzes (quiz and questions)
   - 📋 Manage Assignments (assignment details)

## Technical Implementation
- **Routes:** 15+ admin-specific routes for content management
- **Templates:** 8 dedicated admin templates for editing interfaces
- **Forms:** Enhanced WTForms with proper validation
- **Security:** Role-based access control with @admin_required decorator
- **UI:** Bootstrap-based responsive admin interface

## Course Editing Examples

### Available Courses for Editing:
1. **Web Development with Python and Flask** (₦25,000)
   - 10 lessons, 10 quizzes (29 questions), 5 assignments

2. **Digital Marketing and Social Media Strategy** (₦20,000)
   - 2 lessons, 10 quizzes (29 questions), 5 assignments

3. **Data Science with Python for Beginners** (₦30,000)
   - 1 lesson, 10 quizzes (30 questions), 5 assignments

4. **Financial Literacy and Investment in Nigeria** (₦15,000)
   - 1 lesson, 10 quizzes (30 questions), 5 assignments

5. **Mobile App Development with Flutter** (₦35,000)
   - 1 lesson, 10 quizzes (30 questions), 5 assignments

6. **Graphic Design and Branding for Nigerian Businesses** (₦18,000)
   - 1 lesson, 10 quizzes (30 questions), 5 assignments

All content is fully editable through the admin interface with immediate database updates.