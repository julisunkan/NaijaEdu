import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, make_response, send_file
from datetime import datetime as dt
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import *
from forms import *
from utils import admin_required, instructor_required
from cache import cache
from course_categories import get_category_choices, get_category_name, get_popular_categories

@app.route('/')
def index():
    # Check cache first
    cached_data = cache.get('homepage_data', 300)  # 5 minutes cache
    if cached_data is None:
        # Optimize with limit for better performance
        courses = Course.query.filter_by(is_active=True, approval_status='approved')\
                        .limit(12).all()
        popular_categories = get_popular_categories()
        cached_data = {
            'courses': courses,
            'popular_categories': popular_categories,
            'get_category_name': get_category_name
        }
        cache.set('homepage_data', cached_data)
    
    # Get basic stats
    stats = {
        'total_courses': Course.query.filter_by(approval_status='approved').count(),
        'total_students': User.query.filter_by(role='student').count(),
        'total_instructors': User.query.filter(User.role.in_(['instructor', 'tutor'])).count(),
        'total_certificates': 0  # Will be updated later
    }
    
    return render_template('index_new.html', 
                         courses=cached_data['courses'],
                         recent_courses=cached_data['courses'],
                         popular_categories=cached_data['popular_categories'],
                         get_category_name=cached_data['get_category_name'],
                         stats=stats)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.active:
            login_user(user)
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('auth/login_new.html', form=form)

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
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            # Set role based on form selection
            if form.role.data == 'tutor':
                user.role = 'tutor'
                flash('Tutor account created! You can now create courses that require admin approval before going live.', 'success')
            else:
                user.role = 'student'
                flash('Student account created successfully!', 'success')
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('auth/register_new.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Additional dashboard routes for navigation consistency
@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return redirect(url_for('dashboard'))

@app.route('/instructor/dashboard')
@login_required
@instructor_required
def instructor_dashboard():
    return redirect(url_for('dashboard'))

@app.route('/profile')
@login_required
def profile():
    return render_template('settings/profile.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        # Get vouchers and users for admin dashboard
        vouchers = Voucher.query.order_by(Voucher.created_at.desc()).all()
        users = User.query.all()
        
        # Calculate stats for admin dashboard
        stats = {
            'total_users': User.query.count(),
            'total_courses': Course.query.count(),
            'total_revenue': db.session.query(db.func.sum(Payment.amount)).filter_by(status='completed').scalar() or 0,
            'pending_payments': Payment.query.filter_by(status='pending').count()
        }
        
        return render_template('dashboard/admin_new.html', vouchers=vouchers, User=User, stats=stats)
    elif current_user.role in ['instructor', 'tutor']:
        # Get instructor's courses and submissions
        instructor_courses = Course.query.filter_by(instructor_id=current_user.id).all()
        recent_submissions = AssignmentSubmission.query.join(Assignment).join(Course).filter(
            Course.instructor_id == current_user.id
        ).order_by(AssignmentSubmission.submitted_at.desc()).limit(10).all()
        recent_quiz_attempts = QuizAttempt.query.join(Quiz).join(Course).filter(
            Course.instructor_id == current_user.id
        ).order_by(QuizAttempt.completed_at.desc()).limit(10).all()
        # Calculate total students across all courses
        total_students = sum(course.enrollments.count() for course in instructor_courses)
        
        return render_template('dashboard/instructor_new.html', 
                             courses=instructor_courses,
                             recent_submissions=recent_submissions,
                             recent_quiz_attempts=recent_quiz_attempts,
                             total_students=total_students)
    else:
        # Get student-specific data
        enrolled_courses = Enrollment.query.filter_by(user_id=current_user.id, status='approved').all()
        completed_courses = [e for e in enrolled_courses if e.progress >= 100]
        in_progress_courses = [e for e in enrolled_courses if e.progress < 100]
        certificates = []  # Will be populated when certificates are available
        recent_activities = []  # Mock data for now
        achievements = []  # Mock data for now
        
        return render_template('dashboard/student_new.html',
                             enrolled_courses=enrolled_courses,
                             completed_courses=completed_courses,
                             in_progress_courses=in_progress_courses,
                             certificates=certificates,
                             recent_activities=recent_activities,
                             achievements=achievements)

# Course routes
@app.route('/courses')
def courses():
    category = request.args.get('category')
    search = request.args.get('search', '').strip()
    
    query = Course.query.filter_by(is_active=True, approval_status='approved')
    
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            Course.title.contains(search) | 
            Course.description.contains(search)
        )
    
    courses = query.all()
    categories = get_category_choices()
    return render_template('courses/list_new.html', 
                         courses=courses, 
                         categories=categories,
                         selected_category=category,
                         search_term=search,
                         get_category_name=get_category_name)

@app.route('/courses/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    # Only allow access to approved courses for public users
    if not current_user.is_authenticated or current_user.role not in ['admin', 'instructor', 'tutor']:
        if course.approval_status != 'approved':
            flash('Course not available', 'danger')
            return redirect(url_for('courses'))
    # Tutors can only see their own pending courses
    elif current_user.role == 'tutor' and course.instructor_id != current_user.id and course.approval_status != 'approved':
        flash('Course not available', 'danger')
        return redirect(url_for('courses'))
    
    user_enrolled = False
    if current_user.is_authenticated:
        user_enrolled = current_user.can_access_course(course)
    return render_template('courses/detail_new.html', course=course, user_enrolled=user_enrolled)

@app.route('/courses/create', methods=['GET', 'POST'])
@login_required
@instructor_required
def create_course():
    form = CourseForm()
    form.category.choices = get_category_choices()
    if form.validate_on_submit():
        course = Course()
        course.title = form.title.data
        course.description = form.description.data
        course.price = form.price.data
        course.category = form.category.data  # Set category from form
        course.instructor_id = current_user.id
        # Set approval status based on user role - only admins can auto-approve
        if current_user.role == 'admin':
            course.approval_status = 'approved'
            flash('Course created successfully!', 'success')
        else:
            course.approval_status = 'pending'
            flash('Course created and submitted for admin approval!', 'success')
        db.session.add(course)
        db.session.commit()
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

@app.route('/courses/<int:course_id>/instructor_edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def instructor_edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    # Only allow editing own courses (or admin can edit any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only edit your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    form = CourseForm(obj=course)
    form.category.choices = get_category_choices()
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.price = form.price.data
        course.category = form.category.data  # Update category
        
        # If tutor/instructor edits course, reset to pending approval
        if current_user.role != 'admin' and course.approval_status == 'approved':
            course.approval_status = 'pending'
            flash('Course updated and resubmitted for admin approval!', 'success')
        else:
            flash('Course updated successfully!', 'success')
        
        db.session.commit()
        return redirect(url_for('manage_courses'))
    return render_template('courses/edit.html', form=form, course=course)

@app.route('/courses/<int:course_id>/instructor_delete', methods=['POST'])
@login_required
@instructor_required
def instructor_delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    # Only allow deleting own courses (or admin can delete any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only delete your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    try:
        # Delete course and all related content
        db.session.delete(course)
        db.session.commit()
        flash('Course deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting course. Please try again.', 'danger')
    
    return redirect(url_for('manage_courses'))

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
        lesson = Lesson()
        lesson.title = form.title.data
        lesson.content_type = form.content_type.data
        lesson.order = form.order.data or 0
        lesson.course_id = course_id
        
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

@app.route('/lessons/<int:lesson_id>/instructor_edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def instructor_edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course
    # Only allow editing own course lessons (or admin can edit any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only edit lessons from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    form = LessonForm(obj=lesson)
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.content_type = form.content_type.data
        lesson.order = form.order.data or 0
        
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
        
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course.id))
    return render_template('lessons/edit.html', form=form, lesson=lesson, course=course)

@app.route('/lessons/<int:lesson_id>/instructor_delete', methods=['POST'])
@login_required
@instructor_required
def instructor_delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = lesson.course
    # Only allow deleting own course lessons (or admin can edit any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only delete lessons from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    try:
        # Delete lesson file if exists
        if lesson.file_path and os.path.exists(lesson.file_path):
            os.remove(lesson.file_path)
        
        db.session.delete(lesson)
        db.session.commit()
        flash('Lesson deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting lesson. Please try again.', 'danger')
    
    return redirect(url_for('course_detail', course_id=course.id))

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
        payment = Payment()
        payment.user_id = current_user.id
        payment.course_id = course_id
        payment.amount = form.amount.data
        payment.payment_type = 'course'
        payment.proof_file = file_path
        db.session.add(payment)
        
        # Create enrollment record
        enrollment = Enrollment()
        enrollment.user_id = current_user.id
        enrollment.course_id = course_id
        enrollment.enrollment_method = 'payment'
        db.session.add(enrollment)
        
        db.session.commit()
        flash('Payment submitted for verification. You will be notified once approved.', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('payments/manual.html', form=form, course=course)

@app.route('/courses/<int:course_id>/enroll/wallet', methods=['POST'])
@login_required
def enroll_with_wallet(course_id):
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
    
    # Check if user has sufficient wallet balance
    if current_user.wallet_balance < course.price:
        flash(f'Insufficient wallet balance. You need ₦{course.price:.2f} but have ₦{current_user.wallet_balance:.2f}', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Deduct amount from wallet
    current_user.wallet_balance -= course.price
    
    # Create wallet transaction record
    transaction = WalletTransaction()
    transaction.user_id = current_user.id
    transaction.amount = -course.price  # Negative for debit
    transaction.transaction_type = 'course_purchase'
    transaction.description = f'Purchased course: {course.title}'
    db.session.add(transaction)
    
    # Create enrollment record (approved immediately since payment is confirmed)
    enrollment = Enrollment()
    enrollment.user_id = current_user.id
    enrollment.course_id = course_id
    enrollment.enrollment_method = 'wallet'
    enrollment.status = 'approved'
    enrollment.approved_at = datetime.utcnow()
    db.session.add(enrollment)
    
    # Create payment record for tracking
    payment = Payment()
    payment.user_id = current_user.id
    payment.course_id = course_id
    payment.amount = course.price
    payment.payment_type = 'wallet'
    payment.status = 'approved'
    payment.processed_at = datetime.utcnow()
    db.session.add(payment)
    
    db.session.commit()
    
    flash(f'Successfully enrolled in {course.title} using wallet balance! Your new balance is ₦{current_user.wallet_balance:.2f}', 'success')
    return redirect(url_for('course_detail', course_id=course_id))

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
        transaction = WalletTransaction()
        transaction.user_id = user.id
        transaction.amount = payment.amount
        transaction.transaction_type = 'credit'
        transaction.description = 'Wallet top-up approved'
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
        voucher = Voucher()
        voucher.code = form.code.data.upper() if form.code.data else ''
        voucher.discount_type = form.discount_type.data
        voucher.discount_value = form.discount_value.data
        voucher.max_uses = form.max_uses.data
        voucher.expires_at = form.expires_at.data
        db.session.add(voucher)
        db.session.commit()
        flash('Voucher created successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('vouchers/create.html', form=form)

@app.route('/admin/vouchers/<int:voucher_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_voucher(voucher_id):
    voucher = Voucher.query.get_or_404(voucher_id)
    voucher.is_active = not voucher.is_active
    db.session.commit()
    
    status = "activated" if voucher.is_active else "deactivated"
    flash(f'Voucher "{voucher.code}" has been {status}!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/vouchers/<int:voucher_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_voucher(voucher_id):
    voucher = Voucher.query.get_or_404(voucher_id)
    voucher_code = voucher.code
    
    db.session.delete(voucher)
    db.session.commit()
    
    flash(f'Voucher "{voucher_code}" has been deleted permanently!', 'success')
    return redirect(url_for('dashboard'))

# User Management Routes
@app.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserManagementForm(obj=user)
    
    if form.validate_on_submit():
        old_role = user.role
        user.role = form.role.data
        user.active = form.active.data
        user.banned = form.banned.data
        user.ban_reason = form.ban_reason.data if form.banned.data else None
        user.email_verified = form.email_verified.data
        user.instructor_verified = form.instructor_verified.data
        user.premium_user = form.premium_user.data
        user.badge_level = form.badge_level.data
        
        db.session.commit()
        
        # Log role change
        if old_role != user.role:
            flash(f'User {user.username} role changed from {old_role} to {user.role}', 'info')
        
        flash(f'User "{user.username}" updated successfully!', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@app.route('/admin/users/<int:user_id>/ban', methods=['POST'])
@login_required
@admin_required
def ban_user(user_id):
    user = User.query.get_or_404(user_id)
    ban_reason = request.form.get('ban_reason', '')
    
    user.banned = True
    user.ban_reason = ban_reason
    db.session.commit()
    
    flash(f'User "{user.username}" has been banned!', 'warning')
    return redirect(url_for('manage_users'))

@app.route('/admin/users/<int:user_id>/unban', methods=['POST'])
@login_required
@admin_required
def unban_user(user_id):
    user = User.query.get_or_404(user_id)
    user.banned = False
    user.ban_reason = None
    db.session.commit()
    
    flash(f'User "{user.username}" has been unbanned!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/users/<int:user_id>/promote-instructor', methods=['POST'])
@login_required
@admin_required
def promote_to_instructor(user_id):
    """Quick action to promote a user to instructor"""
    user = User.query.get_or_404(user_id)
    
    if user.role == 'instructor':
        flash(f'{user.username} is already an instructor', 'warning')
    elif user.role == 'admin':
        flash(f'{user.username} is an admin and cannot be demoted to instructor', 'warning')
    else:
        old_role = user.role
        user.role = 'instructor'
        user.instructor_verified = True
        db.session.commit()
        flash(f'{user.username} has been promoted from {old_role} to instructor', 'success')
    
    return redirect(url_for('manage_users'))

@app.route('/admin/users/<int:user_id>/verify-email', methods=['POST'])
@login_required
@admin_required
def verify_user_email(user_id):
    user = User.query.get_or_404(user_id)
    user.email_verified = True
    db.session.commit()
    
    flash(f'Email verified for user "{user.username}"!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/users/<int:user_id>/verify-instructor', methods=['POST'])
@login_required
@admin_required
def verify_instructor(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'instructor':
        user.instructor_verified = True
        db.session.commit()
        flash(f'Instructor "{user.username}" verified!', 'success')
    else:
        flash('User must be an instructor to be verified!', 'error')
    
    return redirect(url_for('manage_users'))

@app.route('/admin/users/<int:user_id>/toggle-premium', methods=['POST'])
@login_required
@admin_required
def toggle_premium(user_id):
    user = User.query.get_or_404(user_id)
    user.premium_user = not user.premium_user
    db.session.commit()
    
    status = "granted" if user.premium_user else "revoked"
    flash(f'Premium status {status} for user "{user.username}"!', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/users/<int:user_id>/change-badge', methods=['POST'])
@login_required
@admin_required
def change_user_badge(user_id):
    user = User.query.get_or_404(user_id)
    new_badge = request.form.get('badge_level')
    
    if new_badge in ['basic', 'bronze', 'silver', 'gold', 'premium']:
        user.badge_level = new_badge
        db.session.commit()
        flash(f'Badge level changed to {new_badge.title()} for user "{user.username}"!', 'success')
    else:
        flash('Invalid badge level!', 'error')
    
    return redirect(url_for('manage_users'))

# Instructor Management Routes
@app.route('/instructor/submissions')
@login_required
@instructor_required
def instructor_submissions():
    # Get all assignment submissions for instructor's courses
    submissions = AssignmentSubmission.query.join(Assignment).join(Course).filter(
        Course.instructor_id == current_user.id
    ).order_by(AssignmentSubmission.submitted_at.desc()).all()
    
    return render_template('instructor/submissions.html', submissions=submissions)

@app.route('/instructor/quiz-attempts')
@login_required
@instructor_required
def instructor_quiz_attempts():
    # Get all quiz attempts for instructor's courses
    quiz_attempts = QuizAttempt.query.join(Quiz).join(Course).filter(
        Course.instructor_id == current_user.id
    ).order_by(QuizAttempt.completed_at.desc()).all()
    
    return render_template('instructor/quiz_attempts.html', quiz_attempts=quiz_attempts)

@app.route('/instructor/submissions/<int:submission_id>/grade', methods=['POST'])
@login_required
@instructor_required
def instructor_quick_grade_submission(submission_id):
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    
    # Verify instructor owns the course
    if submission.assignment.course.instructor_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('instructor_submissions'))
    
    grade = request.form.get('grade', type=int)
    feedback = request.form.get('feedback', '')
    
    if grade is not None and 0 <= grade <= submission.assignment.max_points:
        submission.score = grade
        submission.feedback = feedback
        submission.graded_at = datetime.utcnow()
        db.session.commit()
        
        # Award credits for the graded assignment
        credits_earned = CourseCredit.award_assignment_credits(
            submission.user_id, 
            submission.assignment_id, 
            submission
        )
        
        if credits_earned > 0:
            flash(f'Assignment graded successfully! Student earned {credits_earned} credits.', 'success')
        else:
            percentage = (submission.score / submission.assignment.max_points * 100) if submission.assignment.max_points > 0 else 0
            flash(f'Assignment graded successfully! Score: {percentage:.1f}% (Need {submission.assignment.pass_threshold}% for credits)', 'success')
    else:
        flash('Invalid grade value!', 'error')
    
    return redirect(url_for('instructor_submissions'))

@app.route('/instructor/courses/<int:course_id>/students')
@login_required
@instructor_required
def course_students(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Verify instructor owns the course
    if course.instructor_id != current_user.id:
        flash('Unauthorized access!', 'error')
        return redirect(url_for('dashboard'))
    
    enrollments = Enrollment.query.filter_by(course_id=course.id, status='approved').all()
    return render_template('instructor/course_students.html', course=course, enrollments=enrollments)

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
            enrollment = Enrollment()
            enrollment.user_id = current_user.id
            enrollment.course_id = course_id
            enrollment.enrollment_method = 'voucher'
            enrollment.status = 'approved' if final_amount == 0 else 'pending'
            enrollment.approved_at = datetime.utcnow() if final_amount == 0 else None
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
        payment = Payment()
        payment.user_id = current_user.id
        payment.amount = form.amount.data
        payment.payment_type = 'wallet_topup'
        payment.proof_file = file_path
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
        quiz = Quiz()
        quiz.title = form.title.data
        quiz.description = form.description.data
        quiz.course_id = course_id
        quiz.time_limit = form.time_limit.data
        quiz.max_attempts = form.max_attempts.data
        quiz.max_credits = form.max_credits.data
        quiz.pass_threshold = form.pass_threshold.data
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('quizzes/create.html', form=form, course=course)

@app.route('/quizzes/<int:quiz_id>/instructor_edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def instructor_edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = quiz.course
    # Only allow editing own course quizzes (or admin can edit any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only edit quizzes from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    form = QuizForm(obj=quiz)
    if form.validate_on_submit():
        quiz.title = form.title.data
        quiz.description = form.description.data
        quiz.time_limit = form.time_limit.data
        quiz.max_attempts = form.max_attempts.data
        quiz.max_credits = form.max_credits.data
        quiz.pass_threshold = form.pass_threshold.data
        
        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course.id))
    return render_template('quizzes/edit.html', form=form, quiz=quiz, course=course)

@app.route('/quizzes/<int:quiz_id>/instructor_delete', methods=['POST'])
@login_required
@instructor_required
def instructor_delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = quiz.course
    # Only allow deleting own course quizzes (or admin can delete any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only delete quizzes from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    try:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting quiz. Please try again.', 'danger')
    
    return redirect(url_for('course_detail', course_id=course.id))

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
    attempt = QuizAttempt()
    attempt.user_id = current_user.id
    attempt.quiz_id = quiz_id
    attempt.score = total_score
    attempt.total_points = max_score
    attempt.completed_at = datetime.utcnow()
    db.session.add(attempt)
    db.session.commit()
    
    # Award credits for quiz completion
    credits_earned = CourseCredit.award_quiz_credits(current_user.id, quiz_id, attempt)
    
    if credits_earned > 0:
        flash(f'Quiz completed! You scored {total_score}/{max_score} and earned {credits_earned} credits!', 'success')
    else:
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        flash(f'Quiz completed! You scored {total_score}/{max_score} ({percentage:.1f}%). You need {quiz.pass_threshold}% to earn credits.', 'warning')
    
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
        assignment = Assignment()
        assignment.title = form.title.data
        assignment.description = form.description.data
        assignment.instructions = form.instructions.data
        assignment.course_id = course_id
        assignment.due_date = form.due_date.data
        assignment.max_points = form.max_points.data
        assignment.max_credits = form.max_credits.data
        assignment.pass_threshold = form.pass_threshold.data
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('course_detail', course_id=course_id))
    
    return render_template('assignments/create.html', form=form, course=course)

@app.route('/assignments/<int:assignment_id>/instructor_edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def instructor_edit_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course = assignment.course
    # Only allow editing own course assignments (or admin can edit any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only edit assignments from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    form = AssignmentForm(obj=assignment)
    if request.method == 'POST':
        print(f"POST request received for assignment {assignment_id}")
        if form.errors:
            print(f"Form errors: {form.errors}")
    
    if form.validate_on_submit():
        try:
            assignment.title = form.title.data
            assignment.description = form.description.data
            assignment.instructions = form.instructions.data
            assignment.due_date = form.due_date.data
            assignment.max_points = form.max_points.data
            assignment.max_credits = form.max_credits.data
            assignment.pass_threshold = form.pass_threshold.data
            
            db.session.commit()
            flash('Assignment updated successfully!', 'success')
            return redirect(url_for('course_detail', course_id=course.id))
        except Exception as e:
            db.session.rollback()
            print(f"Error updating assignment: {e}")
            flash('Error updating assignment. Please try again.', 'danger')
    
    return render_template('assignments/edit.html', form=form, assignment=assignment, course=course)

@app.route('/assignments/<int:assignment_id>/instructor_delete', methods=['POST'])
@login_required
@instructor_required
def instructor_delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course = assignment.course
    # Only allow deleting own course assignments (or admin can delete any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only delete assignments from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    try:
        db.session.delete(assignment)
        db.session.commit()
        flash('Assignment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting assignment. Please try again.', 'danger')
    
    return redirect(url_for('course_detail', course_id=course.id))

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
            submission = AssignmentSubmission()
            submission.user_id = current_user.id
            submission.assignment_id = assignment_id
            submission.content = form.content.data
            submission.file_path = file_path
            db.session.add(submission)
        
        db.session.commit()
        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('course_detail', course_id=assignment.course_id))
    
    return render_template('assignments/submit.html', form=form, assignment=assignment, submission=existing_submission, now=dt.utcnow())

@app.route('/assignments/<int:assignment_id>/submissions')
@login_required
@instructor_required
def assignment_submissions(assignment_id):
    """View all submissions for an assignment (instructor/tutor only)"""
    assignment = Assignment.query.get_or_404(assignment_id)
    course = assignment.course
    
    # Only allow viewing submissions for own courses (or admin can view any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only view submissions for your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    submissions = AssignmentSubmission.query.filter_by(assignment_id=assignment_id).order_by(AssignmentSubmission.submitted_at.desc()).all()
    
    return render_template('instructor/assignment_submissions.html', 
                         assignment=assignment, 
                         course=course, 
                         submissions=submissions)

@app.route('/submissions/<int:submission_id>/grade', methods=['GET', 'POST'])
@login_required
@instructor_required
def instructor_grade_submission(submission_id):
    """Grade a specific assignment submission"""
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    assignment = submission.assignment
    course = assignment.course
    
    # Only allow grading submissions for own courses (or admin can grade any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only grade submissions for your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    form = AssignmentGradingForm(obj=submission)
    if form.validate_on_submit():
        try:
            submission.score = form.score.data
            submission.feedback = form.feedback.data
            submission.graded_at = datetime.utcnow()
            
            # Calculate and award credits based on score
            credits_earned = assignment.calculate_credits_earned(form.score.data, assignment.max_points)
            
            # Create or update course credit record
            credit_record = CourseCredit.query.filter_by(
                user_id=submission.user_id,
                course_id=course.id,
                item_type='assignment',
                item_id=assignment.id
            ).first()
            
            if credit_record:
                # Update existing record with new grade
                credit_record.credits_earned = credits_earned
                credit_record.max_credits = assignment.max_credits
                credit_record.score_percentage = (form.score.data / assignment.max_points) * 100 if assignment.max_points > 0 else 0
                credit_record.earned_at = datetime.utcnow()
            else:
                # Create new credit record
                credit_record = CourseCredit()
                credit_record.user_id = submission.user_id
                credit_record.course_id = course.id
                credit_record.item_type = 'assignment'
                credit_record.item_id = assignment.id
                credit_record.credits_earned = credits_earned
                credit_record.max_credits = assignment.max_credits
                credit_record.score_percentage = (form.score.data / assignment.max_points) * 100 if assignment.max_points > 0 else 0
                db.session.add(credit_record)
            
            db.session.commit()
            flash(f'Assignment graded successfully! Student earned {credits_earned} credits.', 'success')
            return redirect(url_for('assignment_submissions', assignment_id=assignment.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error grading submission: {e}")
            flash('Error grading assignment. Please try again.', 'danger')
    
    return render_template('instructor/grade_submission.html', 
                         form=form, 
                         submission=submission, 
                         assignment=assignment, 
                         course=course)

@app.route('/submissions/<int:submission_id>/download')
@login_required
@instructor_required
def download_submission_file(submission_id):
    """Download assignment submission file"""
    submission = AssignmentSubmission.query.get_or_404(submission_id)
    assignment = submission.assignment
    course = assignment.course
    
    # Only allow downloading files for own courses (or admin can download any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only download files for your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    if not submission.file_path or not os.path.exists(submission.file_path):
        flash('File not found', 'danger')
        return redirect(url_for('assignment_submissions', assignment_id=assignment.id))
    
    return send_file(submission.file_path, as_attachment=True)

# Withdrawal routes
@app.route('/instructor/earnings')
@login_required
@instructor_required
def instructor_earnings():
    """Display tutor/instructor earnings and withdrawal options"""
    # Calculate total earnings
    total_earnings = 0
    commission_rate = 0.15  # 15% platform commission
    
    courses = Course.query.filter_by(instructor_id=current_user.id, approval_status='approved').all()
    
    for course in courses:
        successful_payments = Payment.query.filter_by(
            course_id=course.id, 
            status='approved'
        ).all()
        
        for payment in successful_payments:
            tutor_share = payment.amount * (1 - commission_rate)
            total_earnings += tutor_share
    
    # Calculate total withdrawals
    total_withdrawals = db.session.query(db.func.sum(WithdrawalRequest.amount)).filter(
        WithdrawalRequest.tutor_id == current_user.id,
        WithdrawalRequest.status.in_(['approved', 'paid'])
    ).scalar() or 0
    
    available_balance = max(0, total_earnings - total_withdrawals)
    
    # Get withdrawal history
    withdrawal_history = WithdrawalRequest.query.filter_by(tutor_id=current_user.id).order_by(WithdrawalRequest.requested_at.desc()).all()
    
    return render_template('instructor/earnings.html', 
                         total_earnings=total_earnings,
                         total_withdrawals=total_withdrawals,
                         available_balance=available_balance,
                         withdrawal_history=withdrawal_history,
                         commission_rate=commission_rate * 100)

@app.route('/instructor/withdraw', methods=['GET', 'POST'])
@login_required
@instructor_required
def request_withdrawal():
    """Submit withdrawal request"""
    form = WithdrawalRequestForm()
    
    # Calculate available balance
    total_earnings = 0
    commission_rate = 0.15
    
    courses = Course.query.filter_by(instructor_id=current_user.id, approval_status='approved').all()
    
    for course in courses:
        successful_payments = Payment.query.filter_by(
            course_id=course.id, 
            status='approved'
        ).all()
        
        for payment in successful_payments:
            tutor_share = payment.amount * (1 - commission_rate)
            total_earnings += tutor_share
    
    total_withdrawals = db.session.query(db.func.sum(WithdrawalRequest.amount)).filter(
        WithdrawalRequest.tutor_id == current_user.id,
        WithdrawalRequest.status.in_(['approved', 'paid'])
    ).scalar() or 0
    
    available_balance = max(0, total_earnings - total_withdrawals)
    
    if form.validate_on_submit():
        # Validate withdrawal amount
        if form.amount.data and form.amount.data > available_balance:
            flash(f'Insufficient balance. Available: ₦{available_balance:,.2f}', 'error')
            return render_template('instructor/withdraw.html', form=form, available_balance=available_balance)
        
        # Create withdrawal request
        withdrawal = WithdrawalRequest()
        withdrawal.tutor_id = current_user.id
        withdrawal.amount = form.amount.data
        withdrawal.bank_name = form.bank_name.data
        withdrawal.account_number = form.account_number.data
        withdrawal.account_name = form.account_name.data
        withdrawal.request_reason = form.request_reason.data
        
        db.session.add(withdrawal)
        db.session.commit()
        
        flash('Withdrawal request submitted successfully! It will be reviewed by admin.', 'success')
        return redirect(url_for('instructor_earnings'))
    
    return render_template('instructor/withdraw.html', form=form, available_balance=available_balance)

@app.route('/admin/withdrawals')
@login_required
@admin_required
def admin_withdrawals():
    """Admin view of all withdrawal requests"""
    withdrawals = WithdrawalRequest.query.order_by(WithdrawalRequest.requested_at.desc()).all()
    return render_template('admin/withdrawals.html', withdrawals=withdrawals)

@app.route('/admin/withdrawals/<int:withdrawal_id>/process', methods=['GET', 'POST'])
@login_required
@admin_required
def process_withdrawal(withdrawal_id):
    """Process withdrawal request (approve/reject/mark as paid)"""
    withdrawal = WithdrawalRequest.query.get_or_404(withdrawal_id)
    form = WithdrawalApprovalForm()
    
    if form.validate_on_submit():
        withdrawal.status = form.status.data
        withdrawal.admin_notes = form.admin_notes.data
        withdrawal.approved_by = current_user.id
        withdrawal.processed_at = datetime.utcnow()
        
        db.session.commit()
        
        status_messages = {
            'approved': 'Withdrawal request approved!',
            'rejected': 'Withdrawal request rejected.',
            'paid': 'Withdrawal marked as paid.'
        }
        
        flash(status_messages.get(form.status.data, 'Withdrawal status updated.'), 'success')
        return redirect(url_for('admin_withdrawals'))
    
    return render_template('admin/process_withdrawal.html', form=form, withdrawal=withdrawal)

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
    form.category.choices = get_category_choices()  # Populate category choices
    
    if form.validate_on_submit():
        form.populate_obj(course)
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/edit_course.html', form=form, course=course)

@app.route('/admin/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    course_title = course.title
    
    try:
        # Delete related certificates first to avoid constraint issues
        Certificate.query.filter_by(course_id=course_id).delete()
        
        # Delete course (cascade will handle other related records)
        db.session.delete(course)
        db.session.commit()
        
        flash(f'Course "{course_title}" and all its content deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting course: {str(e)}', 'danger')
    
    return redirect(url_for('admin_courses'))

@app.route('/admin/courses/<int:course_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Update course approval status
    course.approval_status = 'approved'
    course.approved_by = current_user.id
    course.approved_at = datetime.utcnow()
    course.rejection_reason = None  # Clear any previous rejection reason
    
    db.session.commit()
    
    flash(f'Course "{course.title}" has been approved and is now live!', 'success')
    return redirect(url_for('admin_courses'))

@app.route('/admin/courses/<int:course_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Get rejection reason from form data
    rejection_reason = request.form.get('rejection_reason', 'No reason provided')
    
    # Update course approval status
    course.approval_status = 'rejected'
    course.approved_by = current_user.id
    course.approved_at = datetime.utcnow()
    course.rejection_reason = rejection_reason
    
    db.session.commit()
    
    flash(f'Course "{course.title}" has been rejected.', 'warning')
    return redirect(url_for('admin_courses'))

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

@app.route('/admin/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.course_id
    lesson_title = lesson.title
    
    # Delete associated file if exists
    if lesson.file_path and os.path.exists(lesson.file_path):
        os.remove(lesson.file_path)
    
    db.session.delete(lesson)
    db.session.commit()
    
    flash(f'Lesson "{lesson_title}" deleted successfully!', 'success')
    return redirect(url_for('admin_course_lessons', course_id=course_id))

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

@app.route('/admin/quizzes/<int:quiz_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course_id = quiz.course_id
    quiz_title = quiz.title
    
    # Delete quiz (cascade will handle questions and attempts)
    db.session.delete(quiz)
    db.session.commit()
    
    flash(f'Quiz "{quiz_title}" and all its questions deleted successfully!', 'success')
    return redirect(url_for('admin_course_quizzes', course_id=course_id))

@app.route('/admin/quizzes/<int:quiz_id>/questions')
@login_required
@admin_required
def admin_quiz_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    form = QuizQuestionForm()  # Add form for CSRF token
    return render_template('admin/quiz_questions.html', quiz=quiz, questions=questions, form=form)

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

@app.route('/admin/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_question(question_id):
    question = QuizQuestion.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin_quiz_questions', quiz_id=quiz_id))

@app.route('/admin/courses/<int:course_id>/assignments')
@login_required
@admin_required
def admin_course_assignments(course_id):
    course = Course.query.get_or_404(course_id)
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    return render_template('admin/course_assignments.html', course=course, assignments=assignments, now=datetime.utcnow())

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

@app.route('/admin/assignments/<int:assignment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course_id = assignment.course_id
    assignment_title = assignment.title
    
    # Delete assignment (cascade will handle submissions)
    db.session.delete(assignment)
    db.session.commit()
    
    flash(f'Assignment "{assignment_title}" and all submissions deleted successfully!', 'success')
    return redirect(url_for('admin_course_assignments', course_id=course_id))

@app.route('/admin/quizzes/<int:quiz_id>/questions/add', methods=['POST'])
@login_required
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    question = QuizQuestion()
    question.quiz_id = quiz_id
    question.question = request.form['question']
    question.option_a = request.form['option_a']
    question.option_b = request.form['option_b']
    question.option_c = request.form['option_c']
    question.option_d = request.form['option_d']
    question.correct_answer = request.form['correct_answer']
    question.points = int(request.form.get('points', 1))
    
    db.session.add(question)
    db.session.commit()
    flash('Question added successfully!', 'success')
    return redirect(url_for('admin_quiz_questions', quiz_id=quiz_id))

# Instructor/Tutor Quiz Question Management Routes
@app.route('/instructor/quizzes/<int:quiz_id>/questions')
@login_required
@instructor_required
def instructor_quiz_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = quiz.course
    
    # Only allow viewing own course quiz questions (or admin can view any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only manage questions from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    form = QuizQuestionForm()  # For CSRF token
    return render_template('instructor/quiz_questions.html', quiz=quiz, questions=questions, form=form)

@app.route('/instructor/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@instructor_required
def instructor_edit_question(question_id):
    question = QuizQuestion.query.get_or_404(question_id)
    quiz = question.quiz
    course = quiz.course
    
    # Only allow editing own course questions (or admin can edit any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only edit questions from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    form = QuizQuestionForm(obj=question)
    
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('instructor_quiz_questions', quiz_id=question.quiz_id))
    
    return render_template('instructor/edit_question.html', form=form, question=question, quiz=quiz)

@app.route('/instructor/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@instructor_required
def instructor_delete_question(question_id):
    question = QuizQuestion.query.get_or_404(question_id)
    quiz = question.quiz
    course = quiz.course
    quiz_id = question.quiz_id
    
    # Only allow deleting own course questions (or admin can delete any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only delete questions from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    db.session.delete(question)
    db.session.commit()
    
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('instructor_quiz_questions', quiz_id=quiz_id))

@app.route('/instructor/quizzes/<int:quiz_id>/questions/add', methods=['GET', 'POST'])
@login_required
@instructor_required
def instructor_add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    course = quiz.course
    
    # Only allow adding questions to own course quizzes (or admin can add to any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only add questions to your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    form = QuizQuestionForm()
    
    if form.validate_on_submit():
        question = QuizQuestion()
        question.quiz_id = quiz_id
        form.populate_obj(question)
        
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('instructor_quiz_questions', quiz_id=quiz_id))
    
    return render_template('instructor/add_question.html', form=form, quiz=quiz)

# Instructor/Tutor Assignment Management Routes
@app.route('/instructor/courses/<int:course_id>/assignments')
@login_required
@instructor_required
def instructor_course_assignments(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Only allow viewing own course assignments (or admin can view any)
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('You can only manage assignments from your own courses', 'danger')
        return redirect(url_for('manage_courses'))
    
    assignments = Assignment.query.filter_by(course_id=course_id).all()
    from forms import AssignmentForm
    form = AssignmentForm()  # For CSRF token
    return render_template('instructor/course_assignments.html', course=course, assignments=assignments, now=datetime.utcnow(), form=form)

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

@app.context_processor
def inject_settings():
    """Make settings available to all templates"""
    settings = SystemSettings.query.first()
    return dict(settings=settings)

# File serving
@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Credit tracking routes
@app.route('/courses/<int:course_id>/credits')
@login_required
def course_credits(course_id):
    """View credit progress for a specific course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user is enrolled
    if not current_user.can_access_course(course):
        flash('You need to enroll in this course first', 'warning')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Get user's credits for this course
    credits = CourseCredit.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).all()
    
    # Calculate totals
    total_earned = sum(credit.credits_earned for credit in credits)
    quiz_credits = sum(credit.credits_earned for credit in credits if credit.item_type == 'quiz')
    assignment_credits = sum(credit.credits_earned for credit in credits if credit.item_type == 'assignment')
    
    # Check completion status
    can_get_certificate = check_course_completion(current_user.id, course_id)
    
    return render_template('courses/credits.html', 
                         course=course, 
                         credits=credits,
                         total_earned=total_earned,
                         quiz_credits=quiz_credits,
                         assignment_credits=assignment_credits,
                         can_get_certificate=can_get_certificate)

# Certificate functionality
def check_course_completion(user_id, course_id):
    """Check if a user has completed all requirements for a course based on credits"""
    course = Course.query.get(course_id)
    if not course:
        return False
    
    # Check if user is enrolled and approved
    enrollment = Enrollment.query.filter_by(
        user_id=user_id, 
        course_id=course_id, 
        status='approved'
    ).first()
    if not enrollment:
        return False
    
    # Calculate total credits earned by the user for this course
    total_credits = db.session.query(db.func.sum(CourseCredit.credits_earned)).filter_by(
        user_id=user_id,
        course_id=course_id
    ).scalar() or 0
    
    # Check if user has earned minimum required credits
    min_credits_required = course.min_credits_for_certificate or 70
    
    return total_credits >= min_credits_required

def issue_certificate(user_id, course_id):
    """Issue a certificate for course completion"""
    # Check if certificate already exists
    existing_cert = Certificate.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()
    
    if existing_cert:
        return existing_cert
    
    if not check_course_completion(user_id, course_id):
        return None
    
    user = User.query.get(user_id)
    course = Course.query.get(course_id)
    
    if not user or not course:
        return None
    
    # Get default certificate template
    template = CertificateTemplate.query.filter_by(is_default=True, is_active=True).first()
    if not template:
        # Create a default template if none exists
        template = CertificateTemplate()
        template.name = 'Default Template'
        template.is_default = True
        db.session.add(template)
        db.session.commit()
    
    # Create certificate
    certificate = Certificate()
    certificate.user_id = user_id
    certificate.course_id = course_id
    certificate.template_id = template.id
    certificate.certificate_number = certificate.generate_certificate_number()
    certificate.student_name = f"{user.first_name} {user.last_name}" if user.first_name and user.last_name else user.username
    certificate.course_title = course.title
    certificate.completion_date = datetime.utcnow()
    certificate.instructor_name = f"{course.instructor.first_name} {course.instructor.last_name}" if course.instructor and course.instructor.first_name and course.instructor.last_name else course.instructor.username if course.instructor else "Course Instructor"
    
    db.session.add(certificate)
    db.session.commit()
    
    return certificate

@app.route('/certificates')
@login_required
def my_certificates():
    """View user's certificates"""
    certificates = current_user.certificates.filter_by(is_valid=True).all()
    return render_template('certificates/my_certificates.html', certificates=certificates)

@app.route('/certificate/<certificate_number>')
def view_certificate(certificate_number):
    """View and print certificate by certificate number"""
    certificate = Certificate.query.filter_by(certificate_number=certificate_number, is_valid=True).first_or_404()
    return render_template('certificates/view_certificate.html', certificate=certificate)

@app.route('/courses/<int:course_id>/certificate')
@login_required
def get_course_certificate(course_id):
    """Request/view certificate for a completed course"""
    course = Course.query.get_or_404(course_id)
    
    # Check if user can access course
    if not current_user.can_access_course(course):
        flash('You must be enrolled in this course to get a certificate', 'warning')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Check if course is completed
    if not check_course_completion(current_user.id, course_id):
        flash('You must complete all course requirements to receive a certificate', 'warning')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # Issue or retrieve certificate
    certificate = issue_certificate(current_user.id, course_id)
    if not certificate:
        flash('Unable to issue certificate. Please contact support.', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))
    
    flash('Certificate issued successfully!', 'success')
    return redirect(url_for('view_certificate', certificate_number=certificate.certificate_number))

# Admin Certificate Template Management
@app.route('/admin/certificate-templates')
@login_required
@admin_required
def manage_certificate_templates():
    """Manage certificate templates"""
    templates = CertificateTemplate.query.order_by(CertificateTemplate.created_at.desc()).all()
    return render_template('admin/certificate_templates.html', templates=templates)

@app.route('/admin/certificate-templates/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_certificate_template():
    """Create new certificate template"""
    form = CertificateTemplateForm()
    
    if form.validate_on_submit():
        # If setting as default, unset other defaults
        if form.is_default.data:
            CertificateTemplate.query.filter_by(is_default=True).update({'is_default': False})
        
        template = CertificateTemplate()
        form.populate_obj(template)
        db.session.add(template)
        db.session.commit()
        
        flash('Certificate template created successfully!', 'success')
        return redirect(url_for('manage_certificate_templates'))
    
    return render_template('admin/create_certificate_template.html', form=form)

@app.route('/admin/certificate-templates/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_certificate_template(template_id):
    """Edit certificate template"""
    template = CertificateTemplate.query.get_or_404(template_id)
    form = CertificateTemplateForm(obj=template)
    
    if form.validate_on_submit():
        # If setting as default, unset other defaults
        if form.is_default.data and not template.is_default:
            CertificateTemplate.query.filter_by(is_default=True).update({'is_default': False})
        
        form.populate_obj(template)
        db.session.commit()
        
        flash('Certificate template updated successfully!', 'success')
        return redirect(url_for('manage_certificate_templates'))
    
    return render_template('admin/edit_certificate_template.html', form=form, template=template)

@app.route('/admin/certificate-templates/<int:template_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_certificate_template(template_id):
    """Delete certificate template"""
    template = CertificateTemplate.query.get_or_404(template_id)
    
    # Check if template is being used
    if template.certificates.count() > 0:
        flash('Cannot delete template that has been used for certificates', 'danger')
        return redirect(url_for('manage_certificate_templates'))
    
    db.session.delete(template)
    db.session.commit()
    
    flash('Certificate template deleted successfully!', 'success')
    return redirect(url_for('manage_certificate_templates'))

@app.route('/admin/certificate-templates/<int:template_id>/preview')
@login_required
@admin_required
def preview_certificate_template(template_id):
    """Preview certificate template with sample data"""
    template = CertificateTemplate.query.get_or_404(template_id)
    
    # Create sample certificate data for preview
    preview_data = {
        'template': template,
        'certificate_number': 'CERT-PREVIEW-123456',
        'student_name': 'John Doe',
        'course_title': 'Sample Course Title',
        'completion_date': datetime.utcnow(),
        'instructor_name': 'Jane Smith',
        'issued_at': datetime.utcnow()
    }
    
    return render_template('certificates/preview_template.html', **preview_data)

# Google AdSense, Analytics, Content Download, and Bulk Import/Export Routes

@app.route('/download_course/<int:course_id>')
@login_required
def download_course_content(course_id):
    """Allow students to download course content as a ZIP file"""
    from utils import generate_course_download_package
    zip_path, error = generate_course_download_package(course_id, current_user.id)
    
    if error:
        flash(error, 'danger')
        return redirect(url_for('course_detail', course_id=course_id))
    
    try:
        if zip_path:
            return send_file(zip_path, as_attachment=True, 
                            download_name=f"course_{course_id}_content.zip",
                            mimetype='application/zip')
        else:
            flash('Download failed: Unable to create course package', 'danger')
            return redirect(url_for('course_detail', course_id=course_id))
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'danger')
        return redirect(url_for('course_detail', course_id=course_id))

@app.route('/admin/bulk_export', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_export_courses():
    """Export courses in bulk to JSON format"""
    from utils import export_courses_to_json
    form = BulkCourseExportForm()
    
    if form.validate_on_submit():
        try:
            course_ids = None
            if form.selected_courses.data:
                course_ids = [int(id.strip()) for id in form.selected_courses.data.split(',') if id.strip().isdigit()]
            
            export_data = export_courses_to_json(course_ids, form.include_content_files.data)
            
            # Create response with JSON file
            response = make_response(json.dumps(export_data, indent=2))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=courses_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
            flash('Courses exported successfully!', 'success')
            return response
            
        except Exception as e:
            flash(f'Export failed: {str(e)}', 'danger')
    
    courses = Course.query.all()
    return render_template('admin/bulk_export.html', form=form, courses=courses)

@app.route('/admin/bulk_import', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_import_courses():
    """Import courses in bulk from JSON format"""
    from utils import import_courses_from_json
    form = BulkCourseImportForm()
    
    if form.validate_on_submit():
        try:
            file = form.course_file.data
            json_data = json.loads(file.read().decode('utf-8'))
            
            success, message = import_courses_from_json(json_data, form.replace_existing.data)
            
            if success:
                flash(message, 'success')
                return redirect(url_for('admin_courses'))
            else:
                flash(message, 'danger')
                
        except json.JSONDecodeError:
            flash('Invalid JSON file format', 'danger')
        except Exception as e:
            flash(f'Import failed: {str(e)}', 'danger')
    
    return render_template('admin/bulk_import.html', form=form)

@app.route('/admin/sample_import')
@login_required
@admin_required
def download_sample_import():
    """Download sample import file"""
    try:
        return send_file('sample_course_import.json', as_attachment=True,
                        download_name='sample_course_import.json',
                        mimetype='application/json')
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'danger')
        return redirect(url_for('bulk_import_courses'))

# Additional missing routes to prevent 500 errors - only add if they don't exist
@app.route('/admin/certificate_templates')
@login_required
@admin_required
def certificate_templates():
    """Alias for manage_certificate_templates"""
    return redirect(url_for('manage_certificate_templates'))


# Alias routes for bulk operations
@app.route('/admin/bulk_import')
@login_required
@admin_required
def bulk_import():
    return redirect(url_for('bulk_import_courses'))

@app.route('/admin/bulk_export')
@login_required
@admin_required
def bulk_export():
    return redirect(url_for('bulk_export_courses'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
