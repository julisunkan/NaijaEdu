import os
import json
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import flash, redirect, url_for, current_app
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def instructor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'instructor']:
            flash('Instructor access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def format_currency(amount):
    """Format amount with Nigerian Naira symbol"""
    return f"₦{amount:,.2f}"

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_token():
    """Generate a secure random token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def send_email(to_email, subject, html_content, text_content=None):
    """Send email using SendGrid"""
    try:
        if 'SENDGRID_API_KEY' not in os.environ:
            current_app.logger.warning("SendGrid API key not configured")
            return False
            
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        sg = SendGridAPIClient(sendgrid_key)
        
        # Get system settings for from email
        from models import SystemSettings
        settings = SystemSettings.query.first()
        from_email = settings.admin_email if settings and settings.admin_email else 'noreply@elearning.com'
        
        message = Mail(
            from_email=Email(from_email),
            to_emails=To(to_email),
            subject=subject
        )
        
        if html_content:
            message.content = Content("text/html", html_content)
        elif text_content:
            message.content = Content("text/plain", text_content)
            
        response = sg.send(message)
        return response.status_code < 300
        
    except Exception as e:
        current_app.logger.error(f"SendGrid error: {e}")
        return False

def send_verification_email(user):
    """Send email verification email"""
    token = generate_token()
    user.email_verification_token = token
    user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    from app import db
    db.session.commit()
    
    # Create verification URL
    from flask import url_for
    verification_url = url_for('verify_email', token=token, _external=True)
    
    html_content = f"""
    <h2>Verify Your Email Address</h2>
    <p>Hello {user.first_name or user.username},</p>
    <p>Please click the link below to verify your email address:</p>
    <p><a href="{verification_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
    <p>This link will expire in 24 hours.</p>
    <p>If you didn't create this account, please ignore this email.</p>
    """
    
    return send_email(user.email, "Verify Your Email Address", html_content)

def send_password_reset_email(user):
    """Send password reset email"""
    token = generate_token()
    user.password_reset_token = token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
    
    from app import db
    db.session.commit()
    
    # Create reset URL
    from flask import url_for
    reset_url = url_for('reset_password', token=token, _external=True)
    
    html_content = f"""
    <h2>Password Reset Request</h2>
    <p>Hello {user.first_name or user.username},</p>
    <p>You requested a password reset. Click the link below to reset your password:</p>
    <p><a href="{reset_url}" style="background-color: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
    <p>This link will expire in 1 hour.</p>
    <p>If you didn't request this reset, please ignore this email.</p>
    """
    
    return send_email(user.email, "Password Reset Request", html_content)

def export_settings_to_json(include_sensitive=False):
    """Export system settings to JSON"""
    from models import SystemSettings, CertificateTemplate
    
    settings = SystemSettings.query.first()
    templates = CertificateTemplate.query.all()
    
    export_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "settings": {},
        "certificate_templates": []
    }
    
    if settings:
        export_data["settings"] = {
            "site_name": settings.site_name,
            "site_description": settings.site_description,
            "currency_symbol": settings.currency_symbol,
            "admin_email": settings.admin_email,
            "bank_name": settings.bank_name,
            "bank_account_name": settings.bank_account_name,
            "bank_account_number": settings.bank_account_number,
            "terms_content": settings.terms_content,
            "privacy_content": settings.privacy_content,
            "about_content": settings.about_content
        }
        
        if include_sensitive:
            export_data["settings"].update({
                "smtp_server": settings.smtp_server,
                "smtp_port": settings.smtp_port,
                "smtp_username": settings.smtp_username,
                "smtp_password": settings.smtp_password
            })
    
    for template in templates:
        template_data = {
            "name": template.name,
            "title": template.title,
            "subtitle": template.subtitle,
            "content_template": template.content_template,
            "signature_line": template.signature_line,
            "background_color": template.background_color,
            "text_color": template.text_color,
            "header_color": template.header_color,
            "accent_color": template.accent_color,
            "gradient_start": template.gradient_start,
            "gradient_end": template.gradient_end,
            "use_gradient": template.use_gradient,
            "company_logo_url": template.company_logo_url,
            "logo_width": template.logo_width,
            "logo_height": template.logo_height,
            "border_style": template.border_style,
            "border_color": template.border_color,
            "font_family": template.font_family,
            "decorative_elements": template.decorative_elements,
            "seal_design": template.seal_design,
            "is_default": template.is_default,
            "is_active": template.is_active
        }
        export_data["certificate_templates"].append(template_data)
    
    return export_data

def import_settings_from_json(json_data):
    """Import system settings from JSON"""
    from models import SystemSettings, CertificateTemplate
    from app import db
    
    try:
        # Import system settings
        if "settings" in json_data:
            settings = SystemSettings.query.first()
            if not settings:
                settings = SystemSettings()
                db.session.add(settings)
            
            settings_data = json_data["settings"]
            for key, value in settings_data.items():
                if hasattr(settings, key) and value is not None:
                    setattr(settings, key, value)
        
        # Import certificate templates
        if "certificate_templates" in json_data:
            for template_data in json_data["certificate_templates"]:
                # Check if template with same name exists
                existing = CertificateTemplate.query.filter_by(name=template_data["name"]).first()
                if existing:
                    # Update existing template
                    template = existing
                else:
                    # Create new template
                    template = CertificateTemplate()
                    db.session.add(template)
                
                for key, value in template_data.items():
                    if hasattr(template, key) and value is not None:
                        setattr(template, key, value)
        
        db.session.commit()
        return True, "Settings imported successfully"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def export_courses_to_json(course_ids=None, include_files=False):
    """Export courses with all content to JSON format"""
    from models import Course, Lesson, Quiz, QuizQuestion, Assignment
    
    if course_ids:
        courses = Course.query.filter(Course.id.in_(course_ids)).all()
    else:
        courses = Course.query.all()
    
    export_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "platform": "Nigerian E-Learning Platform",
        "version": "1.0",
        "courses": []
    }
    
    for course in courses:
        course_data = {
            "title": course.title,
            "description": course.description,
            "price": float(course.price),
            "category": course.category,
            "is_active": course.is_active,
            "min_credits_for_certificate": course.min_credits_for_certificate,
            "total_available_credits": course.total_available_credits,
            "lessons": [],
            "quizzes": [],
            "assignments": []
        }
        
        # Export lessons
        lessons = Lesson.query.filter_by(course_id=course.id).order_by(Lesson.order).all()
        for lesson in lessons:
            lesson_data = {
                "title": lesson.title,
                "description": lesson.description,
                "content_type": lesson.content_type,
                "order": lesson.order,
                "duration": lesson.duration
            }
            
            if lesson.content_type == 'text':
                lesson_data["content"] = lesson.content
            elif lesson.content_type == 'video':
                lesson_data["video_url"] = lesson.video_url
            elif lesson.content_type == 'pdf' and lesson.file_path:
                lesson_data["file_name"] = lesson.file_path
                if include_files:
                    # Note: In production, you'd include the actual file data
                    lesson_data["file_note"] = "File should be uploaded separately"
            
            course_data["lessons"].append(lesson_data)
        
        # Export quizzes
        quizzes = Quiz.query.filter_by(course_id=course.id).all()
        for quiz in quizzes:
            quiz_data = {
                "title": quiz.title,
                "description": quiz.description,
                "time_limit": quiz.time_limit,
                "max_attempts": quiz.max_attempts,
                "max_credits": quiz.max_credits,
                "pass_threshold": float(quiz.pass_threshold),
                "questions": []
            }
            
            questions = QuizQuestion.query.filter_by(quiz_id=quiz.id).all()
            for question in questions:
                question_data = {
                    "question": question.question,
                    "option_a": question.option_a,
                    "option_b": question.option_b,
                    "option_c": question.option_c,
                    "option_d": question.option_d,
                    "correct_answer": question.correct_answer,
                    "points": question.points
                }
                quiz_data["questions"].append(question_data)
            
            course_data["quizzes"].append(quiz_data)
        
        # Export assignments
        assignments = Assignment.query.filter_by(course_id=course.id).all()
        for assignment in assignments:
            assignment_data = {
                "title": assignment.title,
                "description": assignment.description,
                "instructions": assignment.instructions,
                "max_points": assignment.max_points,
                "max_credits": assignment.max_credits,
                "pass_threshold": float(assignment.pass_threshold)
            }
            course_data["assignments"].append(assignment_data)
        
        export_data["courses"].append(course_data)
    
    return export_data

def import_courses_from_json(json_data, replace_existing=False):
    """Import courses from JSON data"""
    from models import Course, Lesson, Quiz, QuizQuestion, Assignment, User
    from app import db
    from flask_login import current_user
    
    try:
        imported_count = 0
        updated_count = 0
        
        if "courses" not in json_data:
            return False, "Invalid format: 'courses' key not found"
        
        for course_data in json_data["courses"]:
            # Check if course exists
            existing_course = Course.query.filter_by(title=course_data["title"]).first()
            
            if existing_course and not replace_existing:
                continue
            
            if existing_course and replace_existing:
                # Delete existing content
                Lesson.query.filter_by(course_id=existing_course.id).delete()
                Quiz.query.filter_by(course_id=existing_course.id).delete()
                Assignment.query.filter_by(course_id=existing_course.id).delete()
                course = existing_course
                updated_count += 1
            else:
                # Create new course
                course = Course()
                db.session.add(course)
                imported_count += 1
            
            # Set course properties
            course.title = course_data["title"]
            course.description = course_data["description"]
            course.price = course_data["price"]
            course.category = course_data.get("category", "General")
            course.is_active = course_data.get("is_active", True)
            course.min_credits_for_certificate = course_data.get("min_credits_for_certificate", 70)
            course.total_available_credits = course_data.get("total_available_credits", 100)
            course.instructor_id = current_user.id
            
            db.session.flush()  # Get course ID
            
            # Import lessons
            for lesson_data in course_data.get("lessons", []):
                lesson = Lesson()
                lesson.course_id = course.id
                lesson.title = lesson_data["title"]
                lesson.description = lesson_data.get("description", "")
                lesson.content_type = lesson_data["content_type"]
                lesson.order = lesson_data.get("order", 1)
                lesson.duration = lesson_data.get("duration", 30)
                
                if lesson.content_type == 'text':
                    lesson.content = lesson_data.get("content", "")
                elif lesson.content_type == 'video':
                    lesson.video_url = lesson_data.get("video_url", "")
                # Note: PDF files need to be uploaded separately
                
                db.session.add(lesson)
            
            # Import quizzes
            for quiz_data in course_data.get("quizzes", []):
                quiz = Quiz()
                quiz.course_id = course.id
                quiz.title = quiz_data["title"]
                quiz.description = quiz_data.get("description", "")
                quiz.time_limit = quiz_data["time_limit"]
                quiz.max_attempts = quiz_data["max_attempts"]
                quiz.max_credits = quiz_data.get("max_credits", 10)
                quiz.pass_threshold = quiz_data.get("pass_threshold", 70.0)
                db.session.add(quiz)
                db.session.flush()
                
                # Import questions
                for question_data in quiz_data.get("questions", []):
                    question = QuizQuestion()
                    question.quiz_id = quiz.id
                    question.question = question_data["question"]
                    question.option_a = question_data["option_a"]
                    question.option_b = question_data["option_b"]
                    question.option_c = question_data["option_c"]
                    question.option_d = question_data["option_d"]
                    question.correct_answer = question_data["correct_answer"]
                    question.points = question_data.get("points", 1)
                    db.session.add(question)
            
            # Import assignments
            for assignment_data in course_data.get("assignments", []):
                assignment = Assignment()
                assignment.course_id = course.id
                assignment.title = assignment_data["title"]
                assignment.description = assignment_data["description"]
                assignment.instructions = assignment_data.get("instructions", "")
                assignment.max_points = assignment_data.get("max_points", 100)
                assignment.max_credits = assignment_data.get("max_credits", 15)
                assignment.pass_threshold = assignment_data.get("pass_threshold", 60.0)
                db.session.add(assignment)
        
        db.session.commit()
        return True, f"Successfully imported {imported_count} new courses and updated {updated_count} existing courses"
        
    except Exception as e:
        db.session.rollback()
        return False, f"Import failed: {str(e)}"

def generate_course_download_package(course_id, user_id):
    """Generate a downloadable package of course content"""
    import zipfile
    import tempfile
    import os
    from models import Course, Lesson, Enrollment
    
    # Check if user is enrolled
    enrollment = Enrollment.query.filter_by(course_id=course_id, user_id=user_id, is_approved=True).first()
    if not enrollment:
        return None, "You are not enrolled in this course"
    
    course = Course.query.get(course_id)
    if not course:
        return None, "Course not found"
    
    # Check download settings
    from models import SystemSettings
    settings = SystemSettings.query.first()
    if settings and not settings.allow_content_download:
        return None, "Content downloads are not allowed"
    
    if settings and settings.download_requires_completion:
        # Check if user has completed the course
        # This would need additional logic to check completion status
        pass
    
    # Create temporary zip file
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"course_{course_id}_content.zip")
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add course info
            course_info = f"""Course: {course.title}
Description: {course.description}
Category: {course.category}
Downloaded: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

This content is for personal use only.
Redistribution is prohibited.
"""
            zipf.writestr("course_info.txt", course_info)
            
            # Add lessons
            lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
            for lesson in lessons:
                lesson_content = f"""Lesson {lesson.order}: {lesson.title}
Duration: {lesson.duration} minutes
Description: {lesson.description or 'No description'}

Content:
{lesson.content if lesson.content_type == 'text' else f'Content Type: {lesson.content_type}'}

{'Video URL: ' + lesson.video_url if lesson.video_url else ''}
"""
                zipf.writestr(f"lessons/lesson_{lesson.order:02d}_{lesson.title[:50]}.txt", lesson_content)
                
                # Add PDF files if they exist
                if lesson.content_type == 'pdf' and lesson.file_path:
                    pdf_path = os.path.join('uploads', lesson.file_path)
                    if os.path.exists(pdf_path):
                        zipf.write(pdf_path, f"lessons/lesson_{lesson.order:02d}_{lesson.title[:30]}.pdf")
        
        return zip_path, None
        
    except Exception as e:
        return None, f"Failed to create download package: {str(e)}"
