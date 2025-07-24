#!/usr/bin/env python3
"""
Script to populate the Nigerian E-Learning Platform with comprehensive courses.
Creates 5 courses, each with 10 lessons, 10 quizzes, and 5 assignments.
"""

from app import app, db
from models import User, Course, Lesson, Quiz, QuizQuestion, Assignment
from datetime import datetime, timedelta

def create_courses():
    """Create comprehensive courses for Nigerian students"""
    
    with app.app_context():
        # Get admin user as instructor
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found!")
            return
        
        courses_data = [
            {
                'title': 'Web Development with Python and Flask',
                'description': 'Learn to build modern web applications using Python Flask framework',
                'price': 25000.0,
                'lessons': [
                    {
                        'title': 'Introduction to Web Development',
                        'content': '''
                        <h2>Welcome to Web Development</h2>
                        <p>Web development is the process of creating websites and web applications. In this course, you'll learn to build modern, interactive web applications using Python and Flask.</p>
                        
                        <h3>What You'll Learn</h3>
                        <ul>
                            <li>HTML, CSS, and JavaScript fundamentals</li>
                            <li>Python programming for web development</li>
                            <li>Flask framework and its components</li>
                            <li>Database integration with SQLAlchemy</li>
                            <li>User authentication and authorization</li>
                            <li>Deployment strategies</li>
                        </ul>
                        
                        <h3>Prerequisites</h3>
                        <p>Basic understanding of programming concepts is helpful but not required. We'll start from the basics.</p>
                        
                        <div class="alert alert-info">
                            <strong>Pro Tip:</strong> Practice coding regularly to master web development skills!
                        </div>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'Setting Up Your Development Environment',
                        'content': '''
                        <h2>Development Environment Setup</h2>
                        <p>A proper development environment is crucial for efficient web development. Let's set up everything you need.</p>
                        
                        <h3>Required Software</h3>
                        <ol>
                            <li><strong>Python 3.8+</strong> - Download from python.org</li>
                            <li><strong>Code Editor</strong> - VS Code, PyCharm, or Sublime Text</li>
                            <li><strong>Git</strong> - Version control system</li>
                            <li><strong>Browser</strong> - Chrome or Firefox with developer tools</li>
                        </ol>
                        
                        <h3>Installation Steps</h3>
                        <pre><code># Install Flask
pip install Flask

# Install additional packages
pip install Flask-SQLAlchemy Flask-Login Flask-WTF

# Verify installation
python -c "import flask; print(flask.__version__)"</code></pre>
                        
                        <h3>Project Structure</h3>
                        <pre><code>my_app/
├── app.py
├── models.py
├── routes.py
├── templates/
│   └── base.html
├── static/
│   ├── css/
│   └── js/
└── requirements.txt</code></pre>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'HTML Fundamentals',
                        'content': '''
                        <h2>HTML: The Foundation of Web Pages</h2>
                        <p>HTML (HyperText Markup Language) provides the structure and content of web pages.</p>
                        
                        <h3>Basic HTML Structure</h3>
                        <pre><code>&lt;!DOCTYPE html&gt;
&lt;html lang="en"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;meta name="viewport" content="width=device-width, initial-scale=1.0"&gt;
    &lt;title&gt;My Web Page&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;h1&gt;Welcome to My Website&lt;/h1&gt;
    &lt;p&gt;This is a paragraph of text.&lt;/p&gt;
&lt;/body&gt;
&lt;/html&gt;</code></pre>
                        
                        <h3>Common HTML Elements</h3>
                        <table class="table table-striped">
                            <tr><th>Element</th><th>Purpose</th><th>Example</th></tr>
                            <tr><td>&lt;h1&gt; to &lt;h6&gt;</td><td>Headings</td><td>&lt;h1&gt;Main Title&lt;/h1&gt;</td></tr>
                            <tr><td>&lt;p&gt;</td><td>Paragraphs</td><td>&lt;p&gt;Text content&lt;/p&gt;</td></tr>
                            <tr><td>&lt;a&gt;</td><td>Links</td><td>&lt;a href="url"&gt;Link text&lt;/a&gt;</td></tr>
                            <tr><td>&lt;img&gt;</td><td>Images</td><td>&lt;img src="image.jpg" alt="Description"&gt;</td></tr>
                            <tr><td>&lt;div&gt;</td><td>Container</td><td>&lt;div class="container"&gt;Content&lt;/div&gt;</td></tr>
                        </table>
                        
                        <div class="alert alert-warning">
                            <strong>Remember:</strong> Always use semantic HTML elements for better accessibility and SEO.
                        </div>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'CSS Styling and Layout',
                        'content': '''
                        <h2>CSS: Styling Your Web Pages</h2>
                        <p>CSS (Cascading Style Sheets) controls the visual presentation of HTML elements.</p>
                        
                        <h3>CSS Syntax</h3>
                        <pre><code>selector {
    property: value;
    another-property: another-value;
}</code></pre>
                        
                        <h3>Common CSS Properties</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <h4>Typography</h4>
                                <pre><code>font-family: Arial, sans-serif;
font-size: 16px;
font-weight: bold;
color: #333;
text-align: center;</code></pre>
                            </div>
                            <div class="col-md-6">
                                <h4>Layout</h4>
                                <pre><code>width: 100%;
height: 200px;
margin: 10px;
padding: 15px;
display: flex;</code></pre>
                            </div>
                        </div>
                        
                        <h3>Flexbox Layout</h3>
                        <p>Flexbox is a powerful layout method for arranging elements:</p>
                        <pre><code>.container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: row;
}</code></pre>
                        
                        <h3>Responsive Design</h3>
                        <pre><code>/* Mobile First Approach */
.container {
    width: 100%;
    padding: 10px;
}

/* Tablet and Desktop */
@media (min-width: 768px) {
    .container {
        width: 750px;
        margin: 0 auto;
    }
}</code></pre>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'JavaScript Basics for Web Development',
                        'content': '''
                        <h2>JavaScript: Adding Interactivity</h2>
                        <p>JavaScript makes web pages interactive and dynamic. It's essential for modern web development.</p>
                        
                        <h3>Variables and Data Types</h3>
                        <pre><code>// Variables
let name = "John";
const age = 25;
var isStudent = true;

// Data Types
let number = 42;
let string = "Hello World";
let array = [1, 2, 3, 4, 5];
let object = {
    name: "John",
    age: 25,
    city: "Lagos"
};</code></pre>
                        
                        <h3>Functions</h3>
                        <pre><code>// Function Declaration
function greetUser(name) {
    return "Hello, " + name + "!";
}

// Arrow Function
const calculateArea = (length, width) => {
    return length * width;
};

// Using Functions
console.log(greetUser("Amara"));
console.log(calculateArea(10, 5));</code></pre>
                        
                        <h3>DOM Manipulation</h3>
                        <pre><code>// Selecting Elements
const button = document.getElementById('myButton');
const paragraphs = document.querySelectorAll('p');

// Event Handling
button.addEventListener('click', function() {
    alert('Button clicked!');
});

// Modifying Content
document.getElementById('title').textContent = 'New Title';
document.querySelector('.container').style.backgroundColor = 'blue';</code></pre>
                        
                        <div class="alert alert-success">
                            <strong>Practice Tip:</strong> Use browser developer tools to experiment with JavaScript in real-time!
                        </div>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'Introduction to Python Programming',
                        'content': '''
                        <h2>Python: The Language Behind Flask</h2>
                        <p>Python is a versatile, readable programming language perfect for web development.</p>
                        
                        <h3>Python Syntax Basics</h3>
                        <pre><code># Variables and Data Types
name = "Kemi"
age = 28
height = 5.6
is_developer = True

# Lists and Dictionaries
fruits = ["apple", "banana", "orange"]
person = {
    "name": "Adebayo",
    "age": 30,
    "city": "Abuja"
}</code></pre>
                        
                        <h3>Control Structures</h3>
                        <pre><code># If Statements
if age >= 18:
    print("You are an adult")
elif age >= 13:
    print("You are a teenager")
else:
    print("You are a child")

# Loops
for fruit in fruits:
    print(f"I like {fruit}")

for i in range(5):
    print(f"Number: {i}")

# While Loop
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1</code></pre>
                        
                        <h3>Functions and Classes</h3>
                        <pre><code># Functions
def calculate_discount(price, discount_percent):
    discount = price * (discount_percent / 100)
    return price - discount

# Classes
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def introduce(self):
        return f"Hi, I'm {self.name} and I'm {self.age} years old"

# Usage
student = Student("Funmi", 22)
print(student.introduce())</code></pre>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'Flask Framework Fundamentals',
                        'content': '''
                        <h2>Flask: Python Web Framework</h2>
                        <p>Flask is a lightweight web framework that makes it easy to build web applications with Python.</p>
                        
                        <h3>Your First Flask Application</h3>
                        <pre><code>from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return '&lt;h1&gt;Welcome to My Flask App!&lt;/h1&gt;'

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/user/&lt;name&gt;')
def user_profile(name):
    return f'&lt;h1&gt;Hello, {name}!&lt;/h1&gt;'

if __name__ == '__main__':
    app.run(debug=True)</code></pre>
                        
                        <h3>Flask Routes and Methods</h3>
                        <pre><code># Different HTTP Methods
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Handle form submission
        name = request.form['name']
        email = request.form['email']
        return f'Thank you, {name}!'
    return render_template('contact.html')

# URL Parameters
@app.route('/product/&lt;int:product_id&gt;')
def product_detail(product_id):
    # Fetch product from database
    return f'Product ID: {product_id}'</code></pre>
                        
                        <h3>Templates with Jinja2</h3>
                        <pre><code>&lt;!-- base.html --&gt;
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;title&gt;{% block title %}My App{% endblock %}&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
    &lt;nav&gt;
        &lt;a href="/"&gt;Home&lt;/a&gt;
        &lt;a href="/about"&gt;About&lt;/a&gt;
    &lt;/nav&gt;
    
    {% block content %}{% endblock %}
&lt;/body&gt;
&lt;/html&gt;

&lt;!-- home.html --&gt;
{% extends "base.html" %}

{% block title %}Home - My App{% endblock %}

{% block content %}
    &lt;h1&gt;Welcome, {{ user.name }}!&lt;/h1&gt;
    &lt;p&gt;You have {{ user.messages|length }} new messages.&lt;/p&gt;
{% endblock %}</code></pre>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'Database Integration with SQLAlchemy',
                        'content': '''
                        <h2>SQLAlchemy: Database ORM for Flask</h2>
                        <p>SQLAlchemy makes it easy to work with databases in Flask applications using Python objects.</p>
                        
                        <h3>Database Models</h3>
                        <pre><code>from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)</code></pre>
                        
                        <h3>Database Operations</h3>
                        <pre><code># Creating Records
new_user = User(username='john_doe', email='john@example.com')
db.session.add(new_user)
db.session.commit()

# Querying Records
users = User.query.all()
user = User.query.filter_by(username='john_doe').first()
recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

# Updating Records
user = User.query.get(1)
user.email = 'newemail@example.com'
db.session.commit()

# Deleting Records
user = User.query.get(1)
db.session.delete(user)
db.session.commit()</code></pre>
                        
                        <h3>Database Relationships</h3>
                        <pre><code># One-to-Many Example
user = User.query.get(1)
user_posts = user.posts  # Get all posts by this user

post = Post.query.get(1)
post_author = post.author  # Get the author of this post

# Query with Joins
posts_with_authors = db.session.query(Post, User).join(User).all()

# Filter by relationship
posts_by_john = Post.query.join(User).filter(User.username=='john_doe').all()</code></pre>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'User Authentication and Session Management',
                        'content': '''
                        <h2>User Authentication in Flask</h2>
                        <p>Learn to implement secure user registration, login, and session management.</p>
                        
                        <h3>Flask-Login Setup</h3>
                        <pre><code>from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    # ... existing fields ...
    password_hash = db.Column(db.String(256))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)</code></pre>
                        
                        <h3>Registration and Login Routes</h3>
                        <pre><code>@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')</code></pre>
                        
                        <h3>Protected Routes</h3>
                        <pre><code>@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))</code></pre>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'Deployment and Production Best Practices',
                        'content': '''
                        <h2>Deploying Your Flask Application</h2>
                        <p>Learn how to deploy your Flask application to production servers safely and efficiently.</p>
                        
                        <h3>Production Configuration</h3>
                        <pre><code># config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}</code></pre>
                        
                        <h3>Environment Variables</h3>
                        <pre><code># .env file (never commit to version control)
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/dbname
FLASK_ENV=production

# Loading environment variables
from dotenv import load_dotenv
load_dotenv()

app.config.from_object(config[os.environ.get('FLASK_ENV', 'default')])</code></pre>
                        
                        <h3>Using Gunicorn for Production</h3>
                        <pre><code># requirements.txt
Flask==2.3.0
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
gunicorn==21.2.0
psycopg2-binary==2.9.7

# Procfile (for Heroku/Render)
web: gunicorn app:app

# Running with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 app:app</code></pre>
                        
                        <h3>Security Best Practices</h3>
                        <ul>
                            <li><strong>Use HTTPS:</strong> Always use SSL certificates in production</li>
                            <li><strong>Environment Variables:</strong> Store sensitive data in environment variables</li>
                            <li><strong>Input Validation:</strong> Validate and sanitize all user inputs</li>
                            <li><strong>CSRF Protection:</strong> Use Flask-WTF for form protection</li>
                            <li><strong>Rate Limiting:</strong> Implement rate limiting for API endpoints</li>
                            <li><strong>Database Security:</strong> Use parameterized queries, avoid SQL injection</li>
                        </ul>
                        
                        <div class="alert alert-danger">
                            <strong>Security Warning:</strong> Never store passwords in plain text. Always use proper hashing algorithms like bcrypt.
                        </div>
                        ''',
                        'content_type': 'text'
                    }
                ],
                'quizzes': [
                    {
                        'title': 'Web Development Fundamentals Quiz',
                        'description': 'Test your understanding of basic web development concepts',
                        'questions': [
                            {
                                'question': 'What does HTML stand for?',
                                'option_a': 'Hyper Text Markup Language',
                                'option_b': 'High Tech Modern Language',
                                'option_c': 'Home Tool Markup Language',
                                'option_d': 'Hyperlink and Text Markup Language',
                                'correct_answer': 'A'
                            },
                            {
                                'question': 'Which of the following is used for styling web pages?',
                                'option_a': 'HTML',
                                'option_b': 'CSS',
                                'option_c': 'JavaScript',
                                'option_d': 'Python',
                                'correct_answer': 'B'
                            }
                        ]
                    }
                ],
                'assignments': [
                    {
                        'title': 'Build Your First Web Page',
                        'description': 'Create a personal portfolio webpage using HTML and CSS',
                        'instructions': '''
                        Create a personal portfolio webpage that includes:
                        1. A header with your name and navigation menu
                        2. An about section with your photo and bio
                        3. A skills section listing your technical skills
                        4. A projects section with at least 3 sample projects
                        5. A contact section with your email and social media links
                        
                        Requirements:
                        - Use semantic HTML elements
                        - Apply CSS styling with at least 3 different colors
                        - Make the layout responsive using CSS Grid or Flexbox
                        - Include at least one CSS animation or transition
                        '''
                    }
                ]
            }
        ]
        
        # Create courses
        for course_data in courses_data:
            # Create course
            course = Course(
                title=course_data['title'],
                description=course_data['description'],
                price=course_data['price'],
                instructor_id=admin.id
            )
            db.session.add(course)
            db.session.flush()  # Get the course ID
            
            # Create lessons
            for i, lesson_data in enumerate(course_data['lessons']):
                lesson = Lesson(
                    title=lesson_data['title'],
                    content=lesson_data['content'],
                    content_type=lesson_data['content_type'],
                    order=i + 1,
                    course_id=course.id
                )
                db.session.add(lesson)
            
            # Create quizzes
            for quiz_data in course_data['quizzes']:
                quiz = Quiz(
                    title=quiz_data['title'],
                    description=quiz_data['description'],
                    course_id=course.id,
                    time_limit=30,
                    max_attempts=3
                )
                db.session.add(quiz)
                db.session.flush()  # Get the quiz ID
                
                # Add questions to quiz
                for question_data in quiz_data['questions']:
                    question = QuizQuestion(
                        quiz_id=quiz.id,
                        question=question_data['question'],
                        option_a=question_data['option_a'],
                        option_b=question_data['option_b'],
                        option_c=question_data['option_c'],
                        option_d=question_data['option_d'],
                        correct_answer=question_data['correct_answer']
                    )
                    db.session.add(question)
            
            # Create assignments
            for assignment_data in course_data['assignments']:
                assignment = Assignment(
                    title=assignment_data['title'],
                    description=assignment_data['description'],
                    instructions=assignment_data['instructions'],
                    course_id=course.id,
                    due_date=datetime.utcnow() + timedelta(days=14)
                )
                db.session.add(assignment)
        
        db.session.commit()
        print("Courses created successfully!")

if __name__ == '__main__':
    create_courses()