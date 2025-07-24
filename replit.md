# Nigerian E-Learning Platform

## Overview

This is a comprehensive Flask-based e-learning platform designed specifically for the Nigerian market, with all transactions handled in Nigerian Naira (₦). The platform supports multiple user roles (admin, instructor, student) and provides a complete learning management system with manual payment processing, voucher systems, and wallet functionality.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLite (development) with support for PostgreSQL (production)
- **Authentication**: Flask-Login with role-based access control
- **Forms**: WTForms with CSRF protection
- **File Handling**: Werkzeug secure file uploads
- **Security**: Password hashing with Werkzeug

### Frontend Architecture
- **Template Engine**: Jinja2 with template inheritance
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Feather Icons
- **JavaScript**: Vanilla JS with Bootstrap components
- **Responsive Design**: Mobile-first approach

### Key Components

1. **User Management System**
   - Three-tier role system: admin, instructor, student
   - User registration and authentication
   - Profile management with Nigerian-specific fields

2. **Course Management**
   - Course creation with title, description, and Naira pricing
   - Multi-content lesson support (text, PDF, video URLs)
   - Course enrollment system with approval workflow

3. **Payment Processing**
   - Manual payment system with proof of payment uploads
   - Bank transfer receipts verification by admin
   - All amounts displayed and processed in Nigerian Naira (₦)

4. **Voucher System**
   - Admin-created discount codes
   - Support for percentage, fixed amount, and free access vouchers
   - Usage limits and expiry dates

5. **Wallet System**
   - User wallet balances maintained in Naira
   - Manual top-up with payment proof verification
   - Transaction history tracking

6. **Assessment System**
   - Quiz creation with multiple-choice questions
   - Assignment submission with file uploads
   - Auto-grading for quizzes, manual grading for assignments

7. **Administrative Panel**
   - System-wide settings management
   - User and payment verification
   - Course and content management

## Data Flow

### Enrollment Process
1. Student browses available courses
2. Student initiates enrollment by choosing payment method:
   - Manual bank transfer with proof upload
   - Voucher code redemption
   - Wallet balance usage
3. Admin verifies payment (for manual payments)
4. System creates enrollment record upon approval
5. Student gains access to course content

### Content Delivery
1. Enrolled students access course dashboard
2. Lessons are delivered based on content type:
   - Text content rendered directly
   - PDF files served through secure file endpoints
   - Video URLs embedded as iframes
3. Progress tracking maintained per student

### Assessment Workflow
1. Instructors create quizzes and assignments
2. Students take assessments within course context
3. Quizzes auto-grade upon submission
4. Assignments require manual instructor review
5. Results and feedback stored in database

## External Dependencies

### Python Packages
- Flask and Flask extensions (SQLAlchemy, Login, WTF)
- Werkzeug for security and file handling
- WTForms for form validation

### Frontend Libraries
- Bootstrap 5.3.0 (CDN)
- Feather Icons 4.28.0 (CDN)

### File Storage
- Local filesystem for uploaded files
- Uploads directory with security restrictions
- Support for PDF, image, and document files

## Deployment Strategy

### Environment Configuration
- Environment variables for sensitive settings
- SQLite for development, PostgreSQL ready for production
- File upload limits and security configurations
- Proxy fix for deployment behind reverse proxies

### Security Measures
- CSRF protection on all forms
- Secure file upload handling
- Password hashing
- Role-based access control decorators
- File type validation and size limits

### Scalability Considerations
- Database connection pooling configured
- Static file serving optimization ready
- Template caching through Jinja2
- Modular route organization for maintainability

### Nigerian Market Adaptations
- Currency display consistently shows ₦ symbol
- Bank details integration for local payment methods
- Manual payment verification workflow
- Naira-specific number formatting throughout the application

## Recent Changes

### July 24, 2025 - Replit Migration & Currency Formatting Enhancement
- ✓ Successfully migrated project from Replit Agent to standard Replit environment
- ✓ Implemented comma separators for all currency displays (₦25,000.00 format)
- ✓ Added custom currency filter to Jinja2 templates
- ✓ Updated all templates to use consistent comma-separated currency formatting
- ✓ Enhanced JavaScript currency formatting with Nigerian locale
- ✓ Confirmed comprehensive admin course editing functionality is fully operational
- ✓ Admin can edit courses, lessons, quizzes, questions, and assignments through dedicated interfaces

### July 24, 2025 - Render Deployment Preparation
- ✓ Created production deployment configuration files (render.yaml, Procfile, runtime.txt)
- ✓ Updated app.py for environment-aware database configuration
- ✓ Modified main.py to support Render's PORT environment variable
- ✓ Fixed UserMixin conflicts and database schema issues
- ✓ Added deployment guide (DEPLOYMENT.md) with step-by-step instructions
- ✓ Configured secure session management with SESSION_SECRET environment variable
- ✓ Maintained SQLite database compatibility for Render deployment

### July 24, 2025 - Admin Course Editing System & Error Resolution
- ✓ Fixed all route errors including missing submit_quiz route
- ✓ Resolved template errors (moment function and date comparison issues)
- ✓ Implemented comprehensive admin course management system
- ✓ Added admin routes for editing courses, lessons, quizzes, and assignments
- ✓ Created admin templates with full CRUD functionality for course content
- ✓ Added quiz question management with add/edit capabilities
- ✓ Updated admin dashboard with course management navigation
- ✓ Enhanced forms with all necessary fields for content editing
- ✓ Fixed database schema by adding missing description and duration columns to lessons
- ✓ Resolved CSRF token configuration for Flask-WTF forms
- ✓ Fixed all LSP diagnostics related to file upload handling and null safety
- ✓ Corrected template issues with missing variables and undefined attributes
- ✓ Updated SQLite database schema for lesson model compatibility

### Current Status - July 24, 2025
The Nigerian e-learning platform is fully operational with comprehensive admin functionality. All admin pages for course content management are working correctly. The application handles Nigerian Naira currency formatting with comma separators, provides secure payment processing with file uploads, and offers complete course management capabilities for administrators.