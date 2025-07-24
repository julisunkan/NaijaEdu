from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SelectField, FloatField, IntegerField, DateTimeField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', widget=TextArea())
    price = FloatField('Price (₦)', validators=[DataRequired(), NumberRange(min=0)])
    category = StringField('Category', validators=[Optional(), Length(max=100)])
    is_active = BooleanField('Active Status', default=True)

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

class RedeemVoucherForm(FlaskForm):
    voucher_code = StringField('Voucher Code', validators=[DataRequired()])
    course_id = HiddenField()

class QuizForm(FlaskForm):
    title = StringField('Quiz Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    time_limit = IntegerField('Time Limit (minutes)', validators=[DataRequired(), NumberRange(min=1)])
    max_attempts = IntegerField('Maximum Attempts', validators=[DataRequired(), NumberRange(min=1)])

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
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M:%S', validators=[Optional()])
    max_points = IntegerField('Maximum Points', validators=[DataRequired(), NumberRange(min=1)], default=100)

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

class CertificateTemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(max=200)])
    title = StringField('Certificate Title', validators=[DataRequired(), Length(max=300)], default='Certificate of Completion')
    subtitle = StringField('Subtitle', validators=[DataRequired(), Length(max=300)], default='This is to certify that')
    content_template = TextAreaField('Content Template', validators=[DataRequired()], 
                                   default='{{student_name}} has successfully completed the course {{course_title}} on {{completion_date}}',
                                   render_kw={"rows": 4, "placeholder": "Use {{student_name}}, {{course_title}}, {{completion_date}}, {{instructor_name}} as placeholders"})
    signature_line = StringField('Signature Line', validators=[DataRequired(), Length(max=200)], default='Instructor Signature')
    background_color = StringField('Background Color', validators=[DataRequired(), Length(7, 7)], default='#ffffff')
    text_color = StringField('Text Color', validators=[DataRequired(), Length(7, 7)], default='#000000')
    border_style = SelectField('Border Style', choices=[('solid', 'Solid'), ('dashed', 'Dashed'), ('dotted', 'Dotted')], default='solid')
    border_color = StringField('Border Color', validators=[DataRequired(), Length(7, 7)], default='#000000')
    is_default = BooleanField('Set as Default Template')
    is_active = BooleanField('Active', default=True)
