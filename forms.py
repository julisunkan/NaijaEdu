from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SelectField, FloatField, IntegerField, DateTimeField, BooleanField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, EqualTo
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    role = SelectField('Account Type', choices=[('student', 'Student'), ('tutor', 'Tutor/Instructor')], default='student')

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', widget=TextArea())
    price = FloatField('Price (₦)', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', 
                          choices=[],  # Will be populated in the view
                          validators=[DataRequired()])
    is_active = BooleanField('Active Status', default=True)
    # Credit system fields
    min_credits_for_certificate = IntegerField('Minimum Credits for Certificate', validators=[DataRequired(), NumberRange(min=1)], default=70)
    total_available_credits = IntegerField('Total Available Credits', validators=[DataRequired(), NumberRange(min=1)], default=100)

class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()])
    content_type = SelectField('Content Type', choices=[('text', 'Text Content'), ('pdf', 'PDF Upload'), ('video', 'Video URL')])
    content = TextAreaField('Text Content', widget=TextArea())
    pdf_file = FileField('PDF File', validators=[FileAllowed(['pdf'], 'PDF files only!')])
    video_url = StringField('Video URL (YouTube/Vimeo)')
    order = IntegerField('Lesson Order', validators=[Optional(), NumberRange(min=0)])
    duration = IntegerField('Duration (minutes)', validators=[Optional(), NumberRange(min=1)])

class PaymentForm(FlaskForm):
    course_id = HiddenField()
    amount = FloatField('Amount (₦)', validators=[DataRequired(), NumberRange(min=0)])
    payment_type = SelectField('Payment Type', choices=[('course', 'Course Payment'), ('wallet_topup', 'Wallet Top-up')])
    proof_file = FileField('Payment Proof', validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDF only!')])

class VoucherForm(FlaskForm):
    code = StringField('Voucher Code', validators=[DataRequired(), Length(max=50)])
    discount_type = SelectField('Discount Type', choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount'), ('free', 'Free Access')])
    discount_value = FloatField('Discount Value', validators=[NumberRange(min=0)])
    max_uses = IntegerField('Maximum Uses', validators=[DataRequired(), NumberRange(min=1)])
    expires_at = DateTimeField('Expiry Date', format='%Y-%m-%d %H:%M:%S', validators=[Optional()])
    course_id = SelectField('Apply to Course', choices=[], coerce=int, validators=[Optional()])

class WithdrawalRequestForm(FlaskForm):
    amount = FloatField('Withdrawal Amount (₦)', validators=[DataRequired(), NumberRange(min=100)])
    bank_name = StringField('Bank Name', validators=[DataRequired(), Length(max=100)])
    account_number = StringField('Account Number', validators=[DataRequired(), Length(min=10, max=20)])
    account_name = StringField('Account Name', validators=[DataRequired(), Length(max=100)])
    request_reason = TextAreaField('Reason for Withdrawal', validators=[Optional()])

class WithdrawalApprovalForm(FlaskForm):
    status = SelectField('Status', choices=[('approved', 'Approve'), ('rejected', 'Reject'), ('paid', 'Mark as Paid')])
    admin_notes = TextAreaField('Admin Notes', validators=[Optional()])

class RedeemVoucherForm(FlaskForm):
    voucher_code = StringField('Voucher Code', validators=[DataRequired()])
    course_id = HiddenField()

class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    time_limit = IntegerField('Time Limit (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    max_attempts = IntegerField('Maximum Attempts', validators=[DataRequired(), NumberRange(min=1)])
    # Credit system fields
    max_credits = IntegerField('Maximum Credits', validators=[DataRequired(), NumberRange(min=1)], default=10)
    pass_threshold = FloatField('Pass Threshold (%)', validators=[DataRequired(), NumberRange(min=0, max=100)], default=70.0)

class QuizQuestionForm(FlaskForm):
    question = TextAreaField('Question', validators=[DataRequired()])
    option_a = StringField('Option A', validators=[DataRequired(), Length(max=200)])
    option_b = StringField('Option B', validators=[DataRequired(), Length(max=200)])
    option_c = StringField('Option C', validators=[DataRequired(), Length(max=200)])
    option_d = StringField('Option D', validators=[DataRequired(), Length(max=200)])
    correct_answer = SelectField('Correct Answer', choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=1)], default=1)

class AssignmentForm(FlaskForm):
    title = StringField('Assignment Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    instructions = TextAreaField('Detailed Instructions', validators=[Optional()])
    due_date = DateTimeField('Due Date', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    max_points = IntegerField('Maximum Points', validators=[DataRequired(), NumberRange(min=1)], default=100)
    # Credit system fields
    max_credits = IntegerField('Maximum Credits', validators=[DataRequired(), NumberRange(min=1)], default=15)
    pass_threshold = FloatField('Pass Threshold (%)', validators=[DataRequired(), NumberRange(min=0, max=100)], default=60.0)

class UserManagementForm(FlaskForm):
    role = SelectField('Role', choices=[('student', 'Student'), ('instructor', 'Instructor'), ('admin', 'Admin')])
    active = BooleanField('Active Status')
    banned = BooleanField('Banned')
    ban_reason = TextAreaField('Ban Reason', validators=[Optional()])
    email_verified = BooleanField('Email Verified')
    instructor_verified = BooleanField('Instructor Verified')
    premium_user = BooleanField('Premium User')
    badge_level = SelectField('Badge Level', choices=[
        ('basic', 'Basic'),
        ('bronze', 'Bronze'), 
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('premium', 'Premium')
    ])

class BanUserForm(FlaskForm):
    ban_reason = TextAreaField('Reason for Ban', validators=[DataRequired()], render_kw={"rows": 3})

class AssignmentSubmissionForm(FlaskForm):
    content = TextAreaField('Submission Text')
    file = FileField('Upload File', validators=[FileAllowed(['pdf', 'doc', 'docx', 'txt'], 'Documents only!')])

class SystemSettingsForm(FlaskForm):
    site_name = StringField('Site Name', validators=[DataRequired(), Length(max=100)])
    site_description = TextAreaField('Site Description')
    admin_email = StringField('Admin Email', validators=[Email()])
    smtp_server = StringField('SMTP Server')
    smtp_port = IntegerField('SMTP Port', validators=[Optional(), NumberRange(min=1, max=65535)])
    smtp_username = StringField('SMTP Username')
    smtp_password = PasswordField('SMTP Password')
    bank_name = StringField('Bank Name')
    bank_account_name = StringField('Account Name')
    bank_account_number = StringField('Account Number')
    terms_content = TextAreaField('Terms of Service', widget=TextArea())
    privacy_content = TextAreaField('Privacy Policy', widget=TextArea())
    about_content = TextAreaField('About Us', widget=TextArea())
    # Google Services Integration
    google_adsense_code = TextAreaField('Google AdSense Code', 
                                       render_kw={"placeholder": "Paste your AdSense ad unit code here", "rows": 5})
    google_analytics_code = TextAreaField('Google Analytics Code', 
                                         render_kw={"placeholder": "Paste your GA4 measurement code here", "rows": 5})
    # Content Download Settings
    allow_content_download = BooleanField('Allow Students to Download Course Content', default=True)
    download_requires_completion = BooleanField('Require Course Completion for Downloads', default=False)

class CertificateTemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(max=200)])
    title = StringField('Certificate Title', validators=[DataRequired(), Length(max=300)], default='Certificate of Completion')
    subtitle = StringField('Subtitle', validators=[DataRequired(), Length(max=300)], default='This is to certify that')
    content_template = TextAreaField('Content Template', validators=[DataRequired()], 
                                   default='{{student_name}} has successfully completed the course {{course_title}} on {{completion_date}}',
                                   render_kw={"rows": 4, "placeholder": "Use {{student_name}}, {{course_title}}, {{completion_date}}, {{instructor_name}} as placeholders"})
    signature_line = StringField('Signature Line', validators=[DataRequired(), Length(max=200)], default='Instructor Signature')
    
    # Enhanced colorful design options
    background_color = StringField('Background Color', validators=[DataRequired(), Length(7, 7)], default='#ffffff')
    text_color = StringField('Text Color', validators=[DataRequired(), Length(7, 7)], default='#000000')
    header_color = StringField('Header Color', validators=[DataRequired(), Length(7, 7)], default='#2E86AB')
    accent_color = StringField('Accent Color', validators=[DataRequired(), Length(7, 7)], default='#A23B72')
    gradient_start = StringField('Gradient Start Color', validators=[Optional(), Length(7, 7)], default='#667eea')
    gradient_end = StringField('Gradient End Color', validators=[Optional(), Length(7, 7)], default='#764ba2')
    use_gradient = BooleanField('Use Gradient Background')
    
    # Company logo support
    company_logo_url = StringField('Company Logo URL', validators=[Optional(), Length(max=500)], 
                                  render_kw={"placeholder": "https://example.com/logo.png"})
    logo_width = IntegerField('Logo Width (px)', validators=[Optional(), NumberRange(min=50, max=300)], default=100)
    logo_height = IntegerField('Logo Height (px)', validators=[Optional(), NumberRange(min=50, max=300)], default=100)
    
    # Additional styling
    border_style = SelectField('Border Style', choices=[('solid', 'Solid'), ('dashed', 'Dashed'), ('dotted', 'Dotted')], default='solid')
    border_color = StringField('Border Color', validators=[DataRequired(), Length(7, 7)], default='#000000')
    font_family = SelectField('Font Family', choices=[
        ('serif', 'Serif (Times New Roman)'),
        ('sans-serif', 'Sans Serif (Arial)'),
        ('cursive', 'Cursive'),
        ('fantasy', 'Fantasy'),
        ('monospace', 'Monospace')
    ], default='serif')
    decorative_elements = BooleanField('Show Decorative Elements', default=True)
    seal_design = SelectField('Seal Design', choices=[
        ('classic', 'Classic'),
        ('modern', 'Modern'),
        ('minimal', 'Minimal')
    ], default='classic')
    
    is_default = BooleanField('Set as Default Template')
    is_active = BooleanField('Active', default=True)

# Email verification and password reset forms
class ForgotPasswordForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Password Reset Email')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    password_confirm = PasswordField('Confirm New Password', 
                                   validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Reset Password')

class ResendVerificationForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Resend Verification Email')

# Website settings import/export forms
class SettingsImportForm(FlaskForm):
    settings_file = FileField('Settings File (JSON)', validators=[DataRequired(), FileAllowed(['json'], 'JSON files only!')])
    submit = SubmitField('Import Settings')

class SettingsExportForm(FlaskForm):
    include_sensitive = BooleanField('Include Sensitive Data (SMTP passwords, etc.)')
    submit = SubmitField('Export Settings')

class BulkCourseImportForm(FlaskForm):
    course_file = FileField('Course Data File (JSON)', validators=[DataRequired(), FileAllowed(['json'], 'JSON files only!')])
    replace_existing = BooleanField('Replace Existing Courses with Same Title')
    submit = SubmitField('Import Courses')

class BulkCourseExportForm(FlaskForm):
    include_content_files = BooleanField('Include PDF/Media Files', default=False)
    selected_courses = StringField('Course IDs (comma-separated)', 
                                  render_kw={"placeholder": "Leave empty to export all courses"})
    submit = SubmitField('Export Courses')
