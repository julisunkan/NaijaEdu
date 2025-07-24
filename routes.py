import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from datetime import datetime as dt
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import *
from forms import *
from utils import admin_required, instructor_required

@app.route('/')
def index():
    courses = Course.query.filter_by(is_active=True).all()
    return render_template('index.html', courses=courses)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
        elif User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                role=form.role.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return render_template('dashboard/admin.html')
    elif current_user.role == 'instructor':
        return render_template('dashboard/instructor.html')
    else:
        return render_template('dashboard/student.html')

# Course routes
@app.route('/courses')
def courses():
    courses = Course.query.filter_by(is_active=True).all()
    return render_template('courses/list.html', courses=courses)

@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    user_enrolled = False
    if current_user.is_authenticated:
        user_enrolled = current_user.can_access_course(course)
    return render_template('courses/detail.html', course=course, user_enrolled=user_enrolled)

@app.route('/courses/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_course():
    form = CourseForm()
    if form.validate_on_submit():
        course = Course()
        course.title = form.title.data
        course.description = form.description.data
        course.price = form.price.data
        course.instructor_id = current_user.id
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('manage_courses'))
    return render_template('courses/create.html', form=form)

@app.route('/courses/manage')
@login_required
@instructor_required
def manage_courses():
    if current_user.role == 'admin':
        courses = Course.query.all()
    else:
        courses = current_user.courses_created.all()
    return render_template('courses/manage.html', courses=courses)

@app.route('/courses/<int:course_id>/lessons/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_lesson(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = LessonForm()
    if form.validate_on_submit():
        lesson = Lesson(
            title=form.title.data,
            content_type=form.content_type.data,
            order=form.order.data or 0,
            course_id=course_id
        )
        
        if form.content_type.data == 'text':
            lesson.content = form.content.data
        elif form.content_type.data == 'pdf' and form.pdf_file.data:
            if form.pdf_file.data.filename:
                filename = secure_filename(form.pdf_file.data.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pdfs', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                form.pdf_file.data.save(file_path)
                lesson.file_path = file_path
        elif form.content_type.data == 'video':
            lesson.video_url = form.video_url.data
        
        db.session.add(lesson)
        db.session.commit()
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('lessons/create.html', form=form, course=course)

@app.route('/lessons/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    if not current_user.can_access_course(lesson.course):
        flash('You need to enroll in this course first', 'warning')
        return redirect(url_for('course_detail', course_id=lesson.course_id))
    return render_template('lessons/view.html', lesson=lesson)

# Payment routes
@app.route('/courses/<int:course_id>/enroll', methods=['GET', 'POST'])
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.status == 'approved':
            flash('You are already enrolled in this course', 'info')
            return redirect(url_for('course_detail', course_id=course_id))
        elif existing_enrollment.status == 'pending':
            flash('Your enrollment is pending approval', 'warning')
            return redirect(url_for('course_detail', course_id=course_id))
    
    form = PaymentForm()
    form.course_id.data = course_id
    form.amount.data = course.price
    form.payment_type.data = 'course'
    
    if form.validate_on_submit():
        # Save payment proof
        if form.proof_file.data and form.proof_file.data.filename:
            filename = secure_filename(form.proof_file.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'payments', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            form.proof_file.data.save(file_path)
        else:
            file_path = None
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            course_id=course_id,
            amount=form.amount.data,
            payment_type='course',
            proof_file=file_path
        )
        db.session.add(payment)
        
        # Create enrollment record
        enrollment = Enrollment(
            user_id=current_user.id,
            course_id=course_id,
            enrollment_method='payment'
        )
        db.session.add(enrollment)
        
        db.session.commit()
        flash('Payment submitted for verification. You will be notified once approved.', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('payments/manual.html', form=form, course=course)

@app.route('/payments/manage')
@login_required
@admin_required
def manage_payments():
    payments = Payment.query.filter_by(status='pending').all()
    return render_template('payments/manage.html', payments=payments)

@app.route('/payments/<int:payment_id>/approve')
@login_required
@admin_required
def approve_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    payment.status = 'approved'
    payment.processed_at = datetime.utcnow()
    
    if payment.payment_type == 'course':
        # Approve enrollment
        enrollment = Enrollment.query.filter_by(
            user_id=payment.user_id,
            course_id=payment.course_id
        ).first()
        if enrollment:
            enrollment.status = 'approved'
            enrollment.approved_at = datetime.utcnow()
    elif payment.payment_type == 'wallet_topup':
        # Add to wallet
        user = payment.user
        user.wallet_balance += payment.amount
        transaction = WalletTransaction(
            user_id=user.id,
            amount=payment.amount,
            transaction_type='credit',
            description='Wallet top-up approved'
        )
        db.session.add(transaction)
    
    db.session.commit()
    flash('Payment approved successfully', 'success')
    return redirect(url_for('manage_payments'))

@app.route('/payments/<int:payment_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    payment.status = 'rejected'
    payment.processed_at = datetime.utcnow()
    payment.admin_notes = request.form.get('notes', '')
    
    # Reject enrollment if exists
    if payment.payment_type == 'course':
        enrollment = Enrollment.query.filter_by(
            user_id=payment.user_id,
            course_id=payment.course_id
        ).first()
        if enrollment:
            enrollment.status = 'rejected'
    
    db.session.commit()
    flash('Payment rejected', 'warning')
    return redirect(url_for('manage_payments'))

# Voucher routes
@app.route('/vouchers/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_voucher():
    form = VoucherForm()
    if form.validate_on_submit():
        voucher = Voucher(
            code=form.code.data.upper() if form.code.data else '',
            discount_type=form.discount_type.data,
            discount_value=form.discount_value.data,
            max_uses=form.max_uses.data,
            expires_at=form.expires_at.data
        )
        db.session.add(voucher)
        db.session.commit()
        flash('Voucher created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('vouchers/create.html', form=form)

@app.route('/courses/<int:course_id>/redeem', methods=['GET', 'POST'])
@login_required
def redeem_voucher(course_id):
    course = Course.query.get_or_404(course_id)
    form = RedeemVoucherForm()
    form.course_id.data = course_id
    
    if form.validate_on_submit():
        voucher_code = form.voucher_code.data
        voucher = Voucher.query.filter_by(code=voucher_code.upper() if voucher_code else '').first()
        
        if not voucher or not voucher.is_valid():
            flash('Invalid or expired voucher code', 'danger')
        else:
            discount = voucher.calculate_discount(course.price)
            final_amount = course.price - discount
            
            # Create enrollment
            enrollment = Enrollment(
                user_id=current_user.id,
                course_id=course_id,
                enrollment_method='voucher',
                status='approved' if final_amount == 0 else 'pending',
                approved_at=datetime.utcnow() if final_amount == 0 else None
            )
            db.session.add(enrollment)
            
            # Update voucher usage
            voucher.current_uses += 1
            
            if final_amount == 0:
                flash('Voucher redeemed successfully! You are now enrolled.', 'success')
            else:
                flash(f'Voucher applied! Please pay the remaining ₦{final_amount:.2f}', 'success')
            
            db.session.commit()
            return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('vouchers/redeem.html', form=form, course=course)

# Wallet routes
@app.route('/wallet/topup', methods=['GET', 'POST'])
@login_required
def wallet_topup():
    form = PaymentForm()
    form.payment_type.data = 'wallet_topup'
    
    if form.validate_on_submit():
        # Save payment proof
        if form.proof_file.data and form.proof_file.data.filename:
            filename = secure_filename(form.proof_file.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'payments', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            form.proof_file.data.save(file_path)
        else:
            file_path = None
        
        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            amount=form.amount.data,
            payment_type='wallet_topup',
            proof_file=file_path
        )
        db.session.add(payment)
        db.session.commit()
        
        flash('Top-up request submitted for verification', 'success')
        return redirect(url_for('wallet_history'))
    
    return render_template('wallet/topup.html', form=form)

@app.route('/wallet/history')
@login_required
def wallet_history():
    transactions = current_user.wallet_transactions.order_by(WalletTransaction.created_at.desc()).all()
    return render_template('wallet/history.html', transactions=transactions)

# Quiz routes
@app.route('/courses/<int:course_id>/quizzes/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_quiz(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(
            title=form.title.data,
            description=form.description.data,
            course_id=course_id,
            time_limit=form.time_limit.data,
            max_attempts=form.max_attempts.data
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('quizzes/create.html', form=form, course=course)

@app.route('/quizzes/<int:quiz_id>/take')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if not current_user.can_access_course(quiz.course):
        flash('You need to enroll in this course first', 'warning')
        return redirect(url_for('course_detail', course_id=quiz.course_id))
    
    # Check attempt limit
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).count()
    if attempts >= quiz.max_attempts:
        flash('You have reached the maximum number of attempts for this quiz', 'warning')
        return redirect(url_for('course_detail', course_id=quiz.course_id))
    
    questions = quiz.questions.all()
    from forms import FlaskForm
    form = FlaskForm()  # Create empty form for CSRF token
    return render_template('quizzes/take.html', quiz=quiz, questions=questions, form=form)

@app.route('/quizzes/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if not current_user.can_access_course(quiz.course):
        flash('You need to enroll in this course first', 'warning')
        return redirect(url_for('course_detail', course_id=quiz.course_id))
    
    # Check attempt limit
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).count()
    if attempts >= quiz.max_attempts:
        flash('You have reached the maximum number of attempts for this quiz', 'warning')
        return redirect(url_for('course_detail', course_id=quiz.course_id))
    
    # Calculate score
    questions = quiz.questions.all()
    total_score = 0
    max_score = len(questions)
    
    for question in questions:
        answer_key = f'question_{question.id}'
        user_answer = request.form.get(answer_key)
        if user_answer and user_answer == question.correct_answer:
            total_score += 1
    
    # Save attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz_id,
        score=total_score,
        max_score=max_score,
        completed_at=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.commit()
    
    flash(f'Quiz completed! You scored {total_score}/{max_score}', 'success')
    return redirect(url_for('course_detail', course_id=quiz.course_id))

# Assignment routes
@app.route('/courses/<int:course_id>/assignments/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_assignment(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            course_id=course_id,
            due_date=form.due_date.data,
            max_points=form.max_points.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('assignments/create.html', form=form, course=course)

@app.route('/assignments/<int:assignment_id>/submit', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if not current_user.can_access_course(assignment.course):
        flash('You need to enroll in this course first', 'warning')
        return redirect(url_for('course_detail', course_id=assignment.course_id))
    
    # Check if already submitted
    existing_submission = AssignmentSubmission.query.filter_by(
        user_id=current_user.id,
        assignment_id=assignment_id
    ).first()
    
    form = AssignmentSubmissionForm()
    if form.validate_on_submit():
        file_path = None
        if form.file.data and form.file.data.filename:
            filename = secure_filename(form.file.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'assignments', filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            form.file.data.save(file_path)
        
        if existing_submission:
            existing_submission.content = form.content.data
            existing_submission.file_path = file_path
            existing_submission.submitted_at = datetime.utcnow()
        else:
            submission = AssignmentSubmission(
                user_id=current_user.id,
                assignment_id=assignment_id,
                content=form.content.data,
                file_path=file_path
            )
            db.session.add(submission)
        
        db.session.commit()
        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('course_detail', course_id=assignment.course_id))
    
    return render_template('assignments/submit.html', form=form, assignment=assignment, submission=existing_submission, now=dt.utcnow())

# Admin Course Management
@app.route('/admin/courses')
@login_required
@admin_required
def admin_courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

@app.route('/admin/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    
    if form.validate_on_submit():
        form.populate_obj(course)
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/edit_course.html', form=form, course=course)

@app.route('/admin/courses/<int:course_id>/lessons')
@login_required
@admin_required
def admin_course_lessons(course_id):
    course = Course.query.get_or_404(course_id)
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    return render_template('admin/course_lessons.html', course=course, lessons=lessons)

@app.route('/admin/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    form = LessonForm(obj=lesson)
    
    if form.validate_on_submit():
        form.populate_obj(lesson)
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('admin_course_lessons', course_id=lesson.course_id))
    
    return render_template('admin/edit_lesson.html', form=form, lesson=lesson)

@app.route('/admin/courses/<int:course_id>/quizzes')
@login_required
@admin_required
def admin_course_quizzes(course_id):
    course = Course.query.get_or_404(course_id)
    quizzes = Quiz.query.filter_by(course_id=course_id).all()
    return render_template('admin/course_quizzes.html', course=course, quizzes=quizzes)

@app.route('/admin/quizzes/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    form = QuizForm(obj=quiz)
    
    if form.validate_on_submit():
        form.populate_obj(quiz)
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('admin_course_quizzes', course_id=quiz.course_id))
    
    return render_template('admin/edit_quiz.html', form=form, quiz=quiz)

@app.route('/admin/quizzes/<int:quiz_id>/questions')
@login_required
@admin_required
def admin_quiz_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    return render_template('admin/quiz_questions.html', quiz=quiz, questions=questions)

@app.route('/admin/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    question = QuizQuestion.query.get_or_404(question_id)
    form = QuizQuestionForm(obj=question)
    
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin_quiz_questions', quiz_id=question.quiz_id))
    
    return render_template('admin/edit_question.html', form=form, question=question)

@app.route('/admin/courses/<int:course_id>/assignments')
@login_required
@admin_required
def admin_course_assignments(course_id):
    course = Course.query.get_or_404(course_id)
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    return render_template('admin/course_assignments.html', course=course, assignments=assignments)

@app.route('/admin/assignments/<int:assignment_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    form = AssignmentForm(obj=assignment)
    
    if form.validate_on_submit():
        form.populate_obj(assignment)
        db.session.commit()
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('admin_course_assignments', course_id=assignment.course_id))
    
    return render_template('admin/edit_assignment.html', form=form, assignment=assignment)

@app.route('/admin/quizzes/<int:quiz_id>/questions/add', methods=['POST'])
@login_required
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    question = QuizQuestion(
        quiz_id=quiz_id,
        question=request.form['question'],
        option_a=request.form['option_a'],
        option_b=request.form['option_b'],
        option_c=request.form['option_c'],
        option_d=request.form['option_d'],
        correct_answer=request.form['correct_answer'],
        points=int(request.form.get('points', 1))
    )
    
    db.session.add(question)
    db.session.commit()
    flash('Question added successfully!', 'success')
    return redirect(url_for('admin_quiz_questions', quiz_id=quiz_id))

# Admin settings
@app.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_settings():
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        db.session.add(settings)
        db.session.commit()
    
    form = SystemSettingsForm(obj=settings)
    if form.validate_on_submit():
        form.populate_obj(settings)
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('admin_settings'))
    
    return render_template('settings/admin.html', form=form)

# File serving
@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
