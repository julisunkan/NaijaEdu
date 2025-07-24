from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # admin, instructor, student
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)
    wallet_balance = db.Column(db.Float, default=0.0)
    course_credits = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    courses_created = db.relationship('Course', backref='instructor', lazy='dynamic')
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic')
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    wallet_transactions = db.relationship('WalletTransaction', backref='user', lazy='dynamic')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic')
    assignment_submissions = db.relationship('AssignmentSubmission', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role):
        return self.role == role
    
    def can_access_course(self, course):
        if self.role in ['admin', 'instructor']:
            return True
        enrollment = Enrollment.query.filter_by(
            user_id=self.id, 
            course_id=course.id, 
            status='approved'
        ).first()
        return enrollment is not None
    
    # Override UserMixin's is_active property to use our database field
    @property
    def is_active(self):
        return self.active

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False, default=0.0)
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')
    quizzes = db.relationship('Quiz', backref='course', lazy='dynamic')
    assignments = db.relationship('Assignment', backref='course', lazy='dynamic')

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    content_type = db.Column(db.String(20), nullable=False)  # text, pdf, video
    file_path = db.Column(db.String(500))  # for PDF uploads
    video_url = db.Column(db.String(500))  # for video embeds
    order = db.Column(db.Integer, default=0)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    questions = db.relationship('QuizQuestion', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', backref='quiz', lazy='dynamic')

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
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructions = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    due_date = db.Column(db.DateTime)
    max_points = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy='dynamic')

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
