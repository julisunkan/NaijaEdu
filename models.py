from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, instructor, tutor, student
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)
    banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.Text)
    email_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100))
    # Enhanced authentication fields
    password_reset_token = db.Column(db.String(100))
    password_reset_expires = db.Column(db.DateTime)
    email_verification_token = db.Column(db.String(100))
    email_verification_expires = db.Column(db.DateTime)
    premium_user = db.Column(db.Boolean, default=False)
    instructor_verified = db.Column(db.Boolean, default=False)
    badge_level = db.Column(db.String(20), default='basic')  # basic, bronze, silver, gold, premium
    wallet_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    courses_created = db.relationship('Course', foreign_keys='Course.instructor_id', backref='instructor', lazy='dynamic')
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    wallet_transactions = db.relationship('WalletTransaction', backref='user', lazy='dynamic')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic')
    assignment_submissions = db.relationship('AssignmentSubmission', backref='user', lazy='dynamic')
    course_credits = db.relationship('CourseCredit', backref='student_credit', lazy='dynamic')
    withdrawal_requests = db.relationship('WithdrawalRequest', foreign_keys='WithdrawalRequest.tutor_id', backref='tutor', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        return self.role == role
    
    def can_access_course(self, course):
        if self.role in ['admin', 'instructor', 'tutor']:
            return True
        enrollment = Enrollment.query.filter_by(
            user_id=self.id, 
            course_id=course.id, 
            status='approved'
        ).first()
        return enrollment is not None
    
    # Check if user account is active (for Flask-Login compatibility)
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    # Override Flask-Login's is_active property
    def is_active(self):
        return bool(self.active and not self.banned)
    
    def is_account_active(self) -> bool:
        return bool(self.active and not self.banned)
    
    def get_badge_info(self):
        badges = {
            'basic': {'name': 'Basic', 'color': 'secondary', 'icon': 'user'},
            'bronze': {'name': 'Bronze', 'color': 'warning', 'icon': 'award'},
            'silver': {'name': 'Silver', 'color': 'info', 'icon': 'star'},
            'gold': {'name': 'Gold', 'color': 'warning', 'icon': 'crown'},
            'premium': {'name': 'Premium', 'color': 'success', 'icon': 'zap'}
        }
        return badges.get(self.badge_level, badges['basic'])
    
    def get_verification_badges(self):
        badges = []
        if self.email_verified:
            badges.append({'name': 'Verified Email', 'color': 'success', 'icon': 'check-circle'})
        if self.instructor_verified and self.role in ['instructor', 'tutor']:
            badge_name = 'Verified Instructor' if self.role == 'instructor' else 'Verified Tutor'
            badges.append({'name': badge_name, 'color': 'primary', 'icon': 'book'})
        if self.premium_user:
            badges.append({'name': 'Premium', 'color': 'warning', 'icon': 'star'})
        return badges

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), default='General')  # Added missing category field
    price = db.Column(db.Float, nullable=False, default=0.0)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    # Course approval system for tutor-created courses
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # admin who approved
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    # Credit system fields
    min_credits_for_certificate = db.Column(db.Integer, default=70)  # Minimum credits needed for certificate
    total_available_credits = db.Column(db.Integer, default=100)     # Total credits available in course
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with cascade deletions
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    course_credits = db.relationship('CourseCredit', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    course_vouchers = db.relationship('Voucher', foreign_keys='Voucher.course_id', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_student_credits(self, user_id):
        """Get total credits earned by a student in this course"""
        total_credits = db.session.query(db.func.sum(CourseCredit.credits_earned)).filter_by(
            user_id=user_id, course_id=self.id
        ).scalar() or 0
        return total_credits
    
    def is_eligible_for_certificate(self, user_id):
        """Check if student has earned enough credits for certificate"""
        earned_credits = self.get_student_credits(user_id)
        return earned_credits >= self.min_credits_for_certificate

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)  # Added description field
    content = db.Column(db.Text)
    content_type = db.Column(db.String(20), nullable=False)  # text, pdf, video
    file_path = db.Column(db.String(500))  # for PDF uploads
    video_url = db.Column(db.String(500))  # for video embeds
    order = db.Column(db.Integer, default=0)
    duration = db.Column(db.Integer)  # Added duration field for templates
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    enrollment_method = db.Column(db.String(20))  # payment, voucher, wallet, credits
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # course, wallet_topup
    proof_file = db.Column(db.String(500))  # path to uploaded proof
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)

class Voucher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed, free
    discount_value = db.Column(db.Float, default=0.0)
    max_uses = db.Column(db.Integer, default=1)
    current_uses = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    # Tutor-specific voucher fields
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))  # Specific course or null for all courses
    tutor_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Tutor who created this voucher
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        if self.current_uses >= self.max_uses:
            return False
        return True
    
    def calculate_discount(self, amount):
        if not self.is_valid():
            return 0.0
        
        if self.discount_type == 'free':
            return amount
        elif self.discount_type == 'percentage':
            return amount * (self.discount_value / 100)
        elif self.discount_type == 'fixed':
            return min(self.discount_value, amount)
        return 0.0

class WithdrawalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, paid
    request_reason = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def get_available_balance(self):
        """Calculate tutor's available balance for withdrawal"""
        # Get total earnings from course sales
        total_earnings = 0
        courses = Course.query.filter_by(instructor_id=self.tutor_id, approval_status='approved').all()
        
        for course in courses:
            successful_payments = Payment.query.filter_by(
                course_id=course.id, 
                status='approved'
            ).all()
            
            for payment in successful_payments:
                # Calculate earnings after platform commission (e.g., 15% commission)
                commission_rate = 0.15  # 15% platform commission
                tutor_share = payment.amount * (1 - commission_rate)
                total_earnings += tutor_share
        
        # Subtract already requested/approved withdrawals
        total_withdrawals = db.session.query(db.func.sum(WithdrawalRequest.amount)).filter(
            WithdrawalRequest.tutor_id == self.tutor_id,
            WithdrawalRequest.status.in_(['approved', 'paid'])
        ).scalar() or 0
        
        return max(0, total_earnings - total_withdrawals)

class WalletTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # credit, debit
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    time_limit = db.Column(db.Integer, default=30)  # minutes
    max_attempts = db.Column(db.Integer, default=3)
    is_active = db.Column(db.Boolean, default=True)
    # Credit system fields
    max_credits = db.Column(db.Integer, default=10)  # Maximum credits for this quiz
    pass_threshold = db.Column(db.Float, default=70.0)  # Minimum percentage to earn credits
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('QuizQuestion', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    
    def calculate_credits_earned(self, score, total_points):
        """Calculate credits earned based on quiz performance"""
        if not score or not total_points or total_points == 0:
            return 0
        
        percentage = (score / total_points) * 100
        if percentage >= self.pass_threshold:
            # Award credits proportional to performance
            credit_percentage = percentage / 100
            return int(self.max_credits * credit_percentage)
        return 0

class QuizQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, D
    points = db.Column(db.Integer, default=1)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Float, default=0.0)
    total_points = db.Column(db.Integer, default=0)
    answers = db.Column(db.Text)  # JSON string of answers
    attempt_number = db.Column(db.Integer, default=1)
    correct_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    attempt_number = db.Column(db.Integer, default=1)
    correct_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    due_date = db.Column(db.DateTime)
    max_points = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    # Credit system fields
    max_credits = db.Column(db.Integer, default=15)  # Maximum credits for this assignment
    pass_threshold = db.Column(db.Float, default=60.0)  # Minimum percentage to earn credits
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy='dynamic', cascade='all, delete-orphan')
    
    def calculate_credits_earned(self, score, max_points):
        """Calculate credits earned based on score"""
        if not score or not max_points or max_points == 0:
            return 0
        
        percentage = (score / max_points) * 100
        if percentage >= self.pass_threshold:
            # Award credits proportional to performance above threshold
            credit_percentage = percentage / 100
            return int(self.max_credits * credit_percentage)
        return 0

class AssignmentSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    graded_at = db.Column(db.DateTime)

class CourseCredit(db.Model):
    """Track credits earned by students for quizzes and assignments"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # 'quiz' or 'assignment'
    item_id = db.Column(db.Integer, nullable=False)  # quiz_id or assignment_id
    credits_earned = db.Column(db.Integer, default=0)
    max_credits = db.Column(db.Integer, default=0)
    score_percentage = db.Column(db.Float, default=0.0)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Create composite unique constraint to prevent duplicate credit records
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', 'item_type', 'item_id'),)
    
    # Relationships are handled by backref in User model
    
    @staticmethod
    def award_quiz_credits(user_id, quiz_id, quiz_attempt):
        """Award credits for a completed quiz"""
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return 0
            
        # Calculate percentage score
        percentage = (quiz_attempt.score / quiz_attempt.total_points * 100) if quiz_attempt.total_points > 0 else 0
        
        # Check if student passed the threshold
        credits_earned = 0
        if percentage >= quiz.pass_threshold:
            # Award credits proportional to performance
            credit_percentage = percentage / 100
            credits_earned = int(quiz.max_credits * credit_percentage)
        
        # Create or update credit record
        credit_record = CourseCredit.query.filter_by(
            user_id=user_id,
            course_id=quiz.course_id,
            item_type='quiz',
            item_id=quiz_id
        ).first()
        
        if credit_record:
            # Update existing record with best performance
            if credits_earned > credit_record.credits_earned:
                credit_record.credits_earned = credits_earned
                credit_record.score_percentage = percentage
                credit_record.earned_at = datetime.utcnow()
        else:
            # Create new credit record
            credit_record = CourseCredit()
            credit_record.user_id = user_id
            credit_record.course_id = quiz.course_id
            credit_record.item_type = 'quiz'
            credit_record.item_id = quiz_id
            credit_record.credits_earned = credits_earned
            credit_record.max_credits = quiz.max_credits
            credit_record.score_percentage = percentage
            db.session.add(credit_record)
        
        db.session.commit()
        return credits_earned
    
    @staticmethod
    def award_assignment_credits(user_id, assignment_id, submission):
        """Award credits for a graded assignment"""
        assignment = Assignment.query.get(assignment_id)
        if not assignment or not submission.score:
            return 0
        
        # Calculate credits earned
        credits_earned = assignment.calculate_credits_earned(submission.score, assignment.max_points)
        percentage = (submission.score / assignment.max_points * 100) if assignment.max_points > 0 else 0
        
        # Create or update credit record
        credit_record = CourseCredit.query.filter_by(
            user_id=user_id,
            course_id=assignment.course_id,
            item_type='assignment',
            item_id=assignment_id
        ).first()
        
        if credit_record:
            # Update existing record
            credit_record.credits_earned = credits_earned
            credit_record.score_percentage = percentage
            credit_record.earned_at = datetime.utcnow()
        else:
            # Create new credit record
            credit_record = CourseCredit()
            credit_record.user_id = user_id
            credit_record.course_id = assignment.course_id
            credit_record.item_type = 'assignment'
            credit_record.item_id = assignment_id
            credit_record.credits_earned = credits_earned
            credit_record.max_credits = assignment.max_credits
            credit_record.score_percentage = percentage
            db.session.add(credit_record)
        
        db.session.commit()
        return credits_earned

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default='E-Learning Platform')
    site_description = db.Column(db.Text)
    currency_symbol = db.Column(db.String(5), default='₦')
    admin_email = db.Column(db.String(120))
    smtp_server = db.Column(db.String(100))
    smtp_port = db.Column(db.Integer)
    smtp_username = db.Column(db.String(100))
    smtp_password = db.Column(db.String(256))
    bank_name = db.Column(db.String(100))
    bank_account_name = db.Column(db.String(100))
    bank_account_number = db.Column(db.String(20))
    terms_content = db.Column(db.Text)
    privacy_content = db.Column(db.Text)
    about_content = db.Column(db.Text)
    # Google Services Integration
    google_adsense_code = db.Column(db.Text)
    google_analytics_code = db.Column(db.Text)
    # Content Download Settings
    allow_content_download = db.Column(db.Boolean, default=True)
    download_requires_completion = db.Column(db.Boolean, default=False)

class CertificateTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(300), default='Certificate of Completion')
    subtitle = db.Column(db.String(300), default='This is to certify that')
    content_template = db.Column(db.Text, default='{{student_name}} has successfully completed the course {{course_title}} on {{completion_date}}')
    signature_line = db.Column(db.String(200), default='Instructor Signature')
    background_color = db.Column(db.String(7), default='#ffffff')  # Hex color
    text_color = db.Column(db.String(7), default='#000000')  # Hex color
    border_style = db.Column(db.String(50), default='solid')  # solid, dashed, dotted
    border_color = db.Column(db.String(7), default='#000000')
    # Enhanced colorful design options
    header_color = db.Column(db.String(7), default='#2E86AB')  # Header background
    accent_color = db.Column(db.String(7), default='#A23B72')  # Accent elements
    gradient_start = db.Column(db.String(7), default='#667eea')  # Gradient start
    gradient_end = db.Column(db.String(7), default='#764ba2')  # Gradient end
    use_gradient = db.Column(db.Boolean, default=False)
    # Company logo support
    company_logo_url = db.Column(db.String(500))  # URL to company logo
    logo_width = db.Column(db.Integer, default=100)  # Logo width in pixels
    logo_height = db.Column(db.Integer, default=100)  # Logo height in pixels
    # Additional styling
    font_family = db.Column(db.String(100), default='serif')
    decorative_elements = db.Column(db.Boolean, default=True)
    seal_design = db.Column(db.String(50), default='classic')  # classic, modern, minimal
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    certificates = db.relationship('Certificate', backref='template', lazy='dynamic')

class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('certificate_template.id'), nullable=False)
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    student_name = db.Column(db.String(200), nullable=False)
    course_title = db.Column(db.String(200), nullable=False)
    completion_date = db.Column(db.DateTime, nullable=False)
    instructor_name = db.Column(db.String(200))
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_valid = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('certificates', lazy='dynamic'))
    course = db.relationship('Course', backref=db.backref('certificates', lazy='dynamic', cascade='all, delete-orphan'))
    
    def generate_certificate_number(self):
        """Generate a unique certificate number"""
        import secrets
        import string
        timestamp = datetime.utcnow().strftime('%Y%m%d')
        random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return f'CERT-{timestamp}-{random_part}'
