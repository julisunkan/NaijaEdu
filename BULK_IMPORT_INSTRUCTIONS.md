# Bulk Course Import/Export Instructions

## Overview
The Nigerian E-Learning Platform supports bulk import and export of courses, including lessons, quizzes, and assignments. This feature allows administrators to quickly populate the platform with content or backup existing courses.

## Features Added

### Google AdSense Integration
- **Location**: Admin Settings → Google Services Integration
- **Purpose**: Display ad banners throughout the platform for monetization
- **Configuration**: Paste your Google AdSense ad unit code in the settings
- **Display**: Ad banners appear on homepage, course listings, and other key pages

### Google Analytics Integration
- **Location**: Admin Settings → Google Services Integration  
- **Purpose**: Track user behavior, course engagement, and platform analytics
- **Configuration**: Paste your Google Analytics (GA4) measurement code in the settings
- **Features**: Automatic tracking of course enrollments, lesson completions, quiz attempts, downloads, and certificate views

### Content Download System
- **Location**: Admin Settings → Content Download Settings
- **Purpose**: Allow students to download course content as ZIP packages
- **Options**:
  - Enable/disable content downloads globally
  - Require course completion before allowing downloads
- **Access**: Download buttons appear on course detail pages for enrolled students
- **Content**: Includes lesson text, video URLs, PDF files, and course information

### Bulk Import/Export System
- **Export**: Create JSON files containing course data with all content
- **Import**: Upload JSON files to create multiple courses at once
- **Access**: Admin panel → Bulk Import/Export buttons
- **Sample File**: Download sample import file to see the correct format

## Export Process

### Steps to Export Courses:
1. Navigate to Admin Settings → Quick Actions → "Bulk Export Courses"
2. Optional: Enter specific course IDs (comma-separated) to export only certain courses
3. Choose whether to include file references
4. Click "Export Courses" to download JSON file

### Export Content Includes:
- Course details (title, description, price, category, credits)
- All lessons with content (text, video URLs, file references)
- Quizzes with all questions and answers
- Assignments with instructions and grading criteria
- Student data and submissions are NOT included for privacy

## Import Process

### Steps to Import Courses:
1. Download the sample import file first to understand the format
2. Navigate to Admin Settings → Quick Actions → "Bulk Import Courses"
3. Upload your JSON file
4. Choose whether to replace existing courses with same titles
5. Click "Import Courses" to process

### Important Notes:
- **Backup First**: Always backup your database before importing
- **Test Small**: Start with a small test import to verify format
- **PDF Files**: PDF files must be uploaded separately after import
- **Unique Titles**: Courses with duplicate titles will be skipped unless "Replace Existing" is checked
- **Processing Time**: Large imports may take several minutes

## JSON Format Requirements

### Required Fields:
- **Course**: title, description, price
- **Lesson**: title, content_type, order
- **Quiz**: title, time_limit, max_attempts
- **Question**: question, option_a, option_b, option_c, option_d, correct_answer
- **Assignment**: title, description, max_points

### Sample Structure:
```json
{
  "courses": [
    {
      "title": "Course Title",
      "description": "Course description",
      "price": 15000.00,
      "category": "Programming",
      "lessons": [
        {
          "title": "Lesson 1",
          "content_type": "text",
          "content": "Lesson content...",
          "order": 1,
          "duration": 45
        }
      ],
      "quizzes": [
        {
          "title": "Quiz 1",
          "time_limit": 30,
          "max_attempts": 3,
          "questions": [
            {
              "question": "What is 2+2?",
              "option_a": "3",
              "option_b": "4",
              "option_c": "5", 
              "option_d": "6",
              "correct_answer": "B",
              "points": 5
            }
          ]
        }
      ],
      "assignments": [
        {
          "title": "Assignment 1",
          "description": "Complete the project",
          "max_points": 100
        }
      ]
    }
  ]
}
```

## Content Types Supported

### Lessons:
- **Text**: Direct text content in the JSON
- **Video**: YouTube, Vimeo, or direct video URLs
- **PDF**: File references (files must be uploaded separately)

### Quiz Questions:
- Multiple choice with exactly 4 options (A, B, C, D)
- Points allocation per question
- Automatic grading based on correct answers

### Assignments:
- Text instructions and requirements
- File submission support
- Manual grading by instructors

## Best Practices

### Before Importing:
1. Validate your JSON format using a JSON validator
2. Ensure all required fields are present
3. Check that course titles are unique or set replacement option
4. Prepare any PDF files for separate upload

### During Import:
1. Do not refresh the page during processing
2. Monitor for error messages and flash notifications
3. Large imports may take several minutes to complete

### After Import:
1. Verify courses were created correctly
2. Upload any referenced PDF files to lessons
3. Test course enrollment and content access
4. Set courses as active if they were imported as inactive

## Troubleshooting

### Common Issues:
- **Invalid JSON**: Use a JSON validator to check file format
- **Missing Fields**: Ensure all required fields are present
- **Large Files**: Split very large imports into smaller batches
- **Special Characters**: Ensure proper UTF-8 encoding

### Error Messages:
- "Invalid format": Check JSON structure and required fields
- "Duplicate title": Course title already exists (use replace option)
- "Import failed": Check server logs for detailed error information

## Security Considerations

### Data Privacy:
- Student data and submissions are never exported
- Only course content and structure are included
- Sensitive settings can be excluded from exports

### File Security:
- PDF and media files are not included in JSON exports
- File paths are referenced but content must be uploaded separately
- Ensure proper file permissions after upload

## Integration with Other Features

### Works With:
- Credit system (imports credit allocations)
- Certificate system (imports completion requirements)
- Payment system (imports course prices in Naira)
- User roles (instructors assigned to imported courses)

### Requirements:
- Admin role for access to import/export features
- Proper database permissions for bulk operations
- Sufficient server storage for temporary ZIP files (downloads)

## Support

For technical issues or questions about bulk import/export:
1. Check the sample import file format
2. Review error messages in the admin interface
3. Test with small data sets first
4. Contact system administrator for database-level issues