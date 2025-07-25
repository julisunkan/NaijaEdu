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

### July 24, 2025 - Comprehensive Delete Functionality Implementation
- ✓ Added delete routes for courses, lessons, quizzes, assignments, and quiz questions
- ✓ Implemented delete buttons with confirmation modals in all admin templates
- ✓ Added proper cascade deletion configuration in database models
- ✓ Secured delete operations with admin-only access control
- ✓ Added warning messages about data loss in confirmation dialogs
- ✓ Fixed template syntax issues for JavaScript string handling
- ✓ Ensured proper cleanup of associated files during lesson deletion

### July 24, 2025 - Left Navigation Admin Panel & Route Error Resolution  
- ✓ Replaced admin dropdown menu with dedicated left navigation sidebar
- ✓ Created beautiful gradient sidebar design with organized menu sections
- ✓ Added smooth hover effects and animations for better user experience
- ✓ Organized admin functions into logical groups: Content Management, User Management, System Tools, Bulk Operations, and Configuration
- ✓ Made admin navigation mobile-responsive with collapsible layout
- ✓ Fixed all route errors including admin_dashboard, manage_users, and admin_settings references
- ✓ Resolved template rendering issues and URL building errors
- ✓ Enhanced admin panel accessibility and usability with clear navigation structure
- ✓ Maintained Google services integration and content download functionality
- ✓ All admin routes and navigation links are now operational

### July 24, 2025 - Comprehensive User Management & Enhanced Instructor Capabilities
- ✓ Implemented comprehensive user management system with role assignment capabilities
- ✓ Added user verification system with email verification and instructor verification badges
- ✓ Created user ban/unban functionality with reason tracking
- ✓ Implemented badge system (Basic, Bronze, Silver, Gold, Premium) with visual indicators
- ✓ Added premium user status management for enhanced features
- ✓ Enhanced User model with verification fields, ban status, and badge levels
- ✓ Created admin user management interface with bulk operations
- ✓ Added comprehensive user editing forms with all status options
- ✓ Enhanced instructor dashboard with submission and quiz attempt tracking
- ✓ Created instructor-specific templates for managing student submissions
- ✓ Added assignment grading system with feedback capabilities
- ✓ Implemented quiz attempt monitoring for instructors
- ✓ Added course student management for instructors
- ✓ Enhanced user profiles with verification badge display throughout the application

### July 24, 2025 - SQLAlchemy Constructor Error Resolution
- ✓ Fixed all SQLAlchemy model constructor errors in routes.py
- ✓ Converted all model instantiations from parameterized constructors to attribute assignments
- ✓ Resolved 13 LSP diagnostics related to User, Lesson, Payment, Enrollment, Voucher, Quiz, Assignment, AssignmentSubmission, QuizAttempt, WalletTransaction, and QuizQuestion models
- ✓ Improved code consistency and SQLAlchemy best practices compliance
- ✓ All routes now properly instantiate models using empty constructors and attribute assignment
- ✓ Enhanced application stability and error handling

### July 24, 2025 - Replit Agent Migration Complete & Comprehensive Route Error Resolution
- ✓ Successfully migrated project from Replit Agent to standard Replit environment
- ✓ Fixed LSP diagnostic issues with UserMixin property override in models.py  
- ✓ Verified all critical routes are functioning correctly (/, /login, /register, /courses)
- ✓ Confirmed gunicorn server running properly on port 5000
- ✓ Database connectivity and initialization working correctly
- ✓ All Flask dependencies and configurations properly set up
- ✓ Resolved database cascade deletion issues for course deletion route
- ✓ Fixed Certificate model relationship conflicts preventing proper cascade deletion
- ✓ Enhanced delete_course route with proper error handling and transaction management
- ✓ Conducted comprehensive web application scan for route errors and 500 errors
- ✓ Tested all 68 registered routes - no 500 internal server errors found
- ✓ Verified proper error handling for non-existent resources (404 responses)
- ✓ Confirmed authentication redirects work correctly (302 responses)
- ✓ Tested edge cases including invalid IDs, missing CSRF tokens, and file uploads
- ✓ All admin, instructor, and student routes functioning properly
- ✓ Payment, voucher, and certificate management systems working without errors
- ✓ Project is stable and ready for continued development and deployment

### July 24, 2025 - Tutor Account System Implementation
- ✓ Enhanced User Registration: Added role selection for student vs tutor account creation
- ✓ Tutor Course Management: Tutors can create courses that require admin approval before going live
- ✓ Course Approval System: Added approval_status field with pending/approved/rejected states
- ✓ Access Control Updates: Modified instructor_required decorator to include tutor role
- ✓ Withdrawal Request System: Added WithdrawalRequest model for tutor earnings withdrawal
- ✓ Commission System: Implemented 15% platform commission calculation for tutor earnings
- ✓ Enhanced Voucher System: Added course-specific and tutor-created voucher support
- ✓ Database Schema Updates: Added new columns for course approval and withdrawal management
- ✓ Role-Based Dashboard: Tutor and instructor roles share the same dashboard functionality
- ✓ Public Course Filtering: Only approved courses are visible to public users

### July 24, 2025 - Course Approval System Fix
- ✓ Fixed instructor access control to include tutor roles in decorator
- ✓ Updated homepage and course listing to show only approved courses
- ✓ Modified course creation: only admin-created courses auto-approve
- ✓ All tutor/instructor courses now require admin approval before going live
- ✓ Added access controls to course detail pages for unapproved courses
- ✓ Fixed database schema error in course download functionality (is_approved → status='approved')
- ✓ Ensured proper course approval workflow is enforced throughout the application

### July 24, 2025 - Tutor/Instructor Edit & Delete Functionality
- ✓ Added comprehensive edit functionality for tutors/instructors on their own courses
- ✓ Implemented course editing with automatic approval status reset for non-admin users
- ✓ Added lesson edit/delete capabilities with proper ownership validation
- ✓ Created quiz edit/delete functionality for course owners
- ✓ Implemented assignment edit/delete features with security checks
- ✓ Updated course management interface with edit/delete buttons
- ✓ Added confirmation modals for delete operations to prevent accidental deletions
- ✓ Created dedicated edit templates for courses, lessons, quizzes, and assignments
- ✓ Ensured only course owners and admins can edit/delete content
- ✓ Maintained approval workflow integrity when content is modified

### July 24, 2025 - PostgreSQL Migration & Enhanced Course Approval System  
- ✓ Successfully migrated from SQLite to PostgreSQL database for improved scalability and persistent storage
- ✓ Resolved course content deletion issue by moving from ephemeral SQLite to permanent PostgreSQL storage
- ✓ Enhanced course approval system with admin approve/reject functionality
- ✓ Added course approval status display in admin dashboard with visual indicators
- ✓ Implemented rejection reason tracking for better communication with instructors
- ✓ Created approve and reject course routes with proper authorization
- ✓ Updated admin courses template with approval/rejection buttons for pending courses
- ✓ All tutor/instructor courses start with "Pending" status requiring admin approval
- ✓ Only admin-approved courses are visible to public users
- ✓ Enhanced instructor information display in admin course management

### Current Status - July 25, 2025
The Nigerian e-learning platform has been successfully migrated from Replit Agent to standard Replit environment with comprehensive enhancements including a complete tutor system, robust PostgreSQL database, enhanced course approval workflow with admin controls, and full edit/delete capabilities for instructors and tutors. The platform now features advanced certificate templates with colorful designs and company logo support, email verification and password reset functionality, Progressive Web App (PWA) capabilities, enhanced mobile responsiveness, website settings import/export functionality, Google AdSense integration, Google Analytics tracking, student content downloads, and bulk import/export systems.

#### Latest Enhancement - July 25, 2025: Instructor/Tutor Quiz Question & Assignment Management
- ✓ Added comprehensive instructor/tutor quiz question management system
- ✓ Implemented instructor routes for adding, editing, and deleting quiz questions
- ✓ Created instructor-specific templates for quiz question management
- ✓ Added assignment management functionality for instructors/tutors
- ✓ Enhanced course detail and management pages with new management buttons
- ✓ Added dropdown navigation for managing quiz questions by quiz
- ✓ Implemented proper ownership validation (instructors can only manage their own content)
- ✓ Created intuitive user interface with confirmation modals for delete operations
- ✓ Added instructor assignment management page with status indicators
- ✓ Enhanced instructor tools section in course detail pages
- ✓ Maintained admin functionality while extending instructor capabilities
- ✓ Fixed all route errors and template syntax issues with proper JavaScript escaping
- ✓ Resolved CSRF token issues in instructor templates
- ✓ Updated navigation buttons in course management pages
- ✓ Ensured proper form handling and security measures

#### Latest Enhancement - July 25, 2025: Assignment Grading System for Instructors/Tutors
- ✓ Implemented comprehensive assignment grading system for instructors and tutors
- ✓ Added assignment submissions overview page showing all student submissions
- ✓ Created detailed grading interface with score input and feedback forms
- ✓ Added real-time credit calculation preview showing earned credits based on score
- ✓ Integrated with course credit system to automatically award credits upon grading
- ✓ Added file download functionality for instructors to review submitted files
- ✓ Enhanced instructor course assignments page with "Submissions" button
- ✓ Implemented proper security controls (instructors can only grade their own course submissions)
- ✓ Added visual indicators for graded vs ungraded submissions with status badges
- ✓ Created user-friendly breadcrumb navigation and intuitive interface design
- ✓ Fixed datetime validation issue in assignment edit forms (updated to %Y-%m-%dT%H:%M format)
- ✓ Resolved route conflicts and template syntax errors for smooth functionality

#### Latest Performance Optimization (July 24, 2025):
- ✓ Migrated from ephemeral SQLite to persistent PostgreSQL database to prevent data loss
- ✓ Implemented in-memory caching system for frequently accessed data (homepage courses)
- ✓ Added critical CSS inlining for faster above-the-fold rendering
- ✓ Optimized database queries with proper indexing for better performance
- ✓ Added lazy loading for images and deferred JavaScript loading
- ✓ Implemented connection pooling and database optimization settings
- ✓ Created performance monitoring and caching infrastructure
- ✓ Enhanced frontend performance with CSS preloading and DNS prefetching

#### Latest Course Category System (July 24, 2025):
- ✓ Created comprehensive 20-category system for course organization
- ✓ Categories include: Programming, Web Development, Data Science, AI/ML, Business, Marketing, Health, Design, and more
- ✓ Added category filtering and search functionality to course listings
- ✓ Updated course creation and editing forms with category selection
- ✓ Implemented automatic categorization of existing courses based on title keywords
- ✓ Enhanced homepage with popular categories display
- ✓ Added category badges to course cards for better visual organization
- ✓ Integrated caching system with category-based filtering for improved performance

#### Latest UI Enhancement (July 24, 2025):
- ✓ Replaced traditional dropdown profile menu with modern offcanvas sidebar navigation
- ✓ Enhanced user experience with slide-out profile panel from the right side
- ✓ Organized user information, role indicators, and navigation links in structured sections
- ✓ Added responsive design that adapts to mobile devices (320px on desktop, 280px on mobile)
- ✓ Implemented gradient header design with proper iconography throughout the profile menu
- ✓ Categorized menu items by user role (Student, Instructor/Tutor, Admin) for better organization
- ✓ Enhanced accessibility with proper ARIA labels and keyboard navigation support

#### Latest Migration & Enhancement Features (July 24, 2025):
- ✓ Enhanced Certificate Templates: Colorful designs with gradient backgrounds, company logo support, customizable color schemes, decorative elements, and multiple seal designs
- ✓ Email Verification System: Complete email verification workflow with SendGrid integration for secure user registration
- ✓ Password Reset Functionality: Secure password reset system with time-limited tokens and email notifications
- ✓ Progressive Web App (PWA): Full PWA support with service worker, app manifest, offline functionality, and installable app experience
- ✓ Enhanced Mobile Responsiveness: Optimized touch targets, mobile-first design, gesture support, and improved user experience on mobile devices
- ✓ Settings Import/Export: Complete system settings and certificate template import/export functionality with JSON format support
- ✓ Advanced Certificate Features: Logo URL support, customizable dimensions, font families, border styles, and professional certificate layouts
- ✓ PWA Features: Offline support, background sync, push notifications, install prompts, and caching strategies
- ✓ Mobile Enhancements: Touch gestures, optimized images, improved navigation, viewport handling, and enhanced accessibility

#### Technical Architecture Updates:
- ✓ SendGrid Email Integration: Professional email delivery system with template support
- ✓ Service Worker Implementation: Comprehensive offline functionality and caching strategies
- ✓ Enhanced Utility Functions: Email sending, token generation, settings export/import, and mobile optimizations
- ✓ PWA Manifest Configuration: Complete progressive web app setup with icons and screenshots
- ✓ Mobile-First CSS: Responsive design improvements and touch-friendly interface elements
- ✓ Enhanced Forms: Password reset, email verification, and settings management forms