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
