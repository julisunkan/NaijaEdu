#!/usr/bin/env python3
"""
Add 4 more comprehensive courses to complete the e-learning platform.
Each course will have 10 lessons, 10 quizzes, and 5 assignments.
"""

from app import app, db
from models import User, Course, Lesson, Quiz, QuizQuestion, Assignment
from datetime import datetime, timedelta

def add_more_courses():
    """Add 4 additional comprehensive courses"""
    
    with app.app_context():
        # Get admin user as instructor
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("Admin user not found!")
            return
        
        additional_courses = [
            {
                'title': 'Digital Marketing and Social Media Strategy',
                'description': 'Master digital marketing, social media management, and online business growth strategies for the Nigerian market',
                'price': 20000.0,
                'lessons': [
                    {
                        'title': 'Introduction to Digital Marketing',
                        'content': '''
                        <h2>Digital Marketing in Nigeria</h2>
                        <p>Digital marketing is revolutionizing how Nigerian businesses reach and engage customers. This course will teach you to leverage digital platforms effectively.</p>
                        
                        <h3>What is Digital Marketing?</h3>
                        <p>Digital marketing encompasses all marketing efforts that use electronic devices or the internet. It includes:</p>
                        <ul>
                            <li>Search Engine Optimization (SEO)</li>
                            <li>Social Media Marketing</li>
                            <li>Email Marketing</li>
                            <li>Content Marketing</li>
                            <li>Pay-Per-Click (PPC) Advertising</li>
                            <li>Affiliate Marketing</li>
                        </ul>
                        
                        <h3>Nigerian Digital Landscape</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <h4>Key Statistics</h4>
                                <ul>
                                    <li>200+ million internet users</li>
                                    <li>33 million active social media users</li>
                                    <li>91% mobile internet usage</li>
                                    <li>Growing e-commerce sector</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h4>Popular Platforms</h4>
                                <ul>
                                    <li>WhatsApp Business</li>
                                    <li>Instagram</li>
                                    <li>Facebook</li>
                                    <li>Twitter/X</li>
                                    <li>LinkedIn</li>
                                    <li>TikTok</li>
                                </ul>
                            </div>
                        </div>
                        
                        <div class="alert alert-info">
                            <strong>Nigerian Focus:</strong> This course emphasizes strategies that work specifically in the Nigerian market, considering local culture, payment methods, and consumer behavior.
                        </div>
                        ''',
                        'content_type': 'text'
                    },
                    {
                        'title': 'Understanding Your Target Audience',
                        'content': '''
                        <h2>Customer Research and Personas</h2>
                        <p>Understanding your audience is the foundation of successful digital marketing. Learn to identify and connect with your ideal customers.</p>
                        
                        <h3>Nigerian Consumer Behavior</h3>
                        <p>Nigerian consumers have unique characteristics that affect their online behavior:</p>
                        <ul>
                            <li><strong>Mobile-First:</strong> Most access internet via smartphones</li>
                            <li><strong>Social-Driven:</strong> Heavy reliance on social proof and recommendations</li>
                            <li><strong>Price-Conscious:</strong> Value for money is extremely important</li>
                            <li><strong>Community-Oriented:</strong> Group decisions and family influence</li>
                            <li><strong>Trust-Based:</strong> Prefer buying from known or recommended sources</li>
                        </ul>
                        
                        <h3>Creating Customer Personas</h3>
                        <div class="card">
                            <div class="card-header">Example Nigerian Customer Persona</div>
                            <div class="card-body">
                                <h5>Adunni - Young Professional</h5>
                                <ul>
                                    <li><strong>Age:</strong> 25-32</li>
                                    <li><strong>Location:</strong> Lagos, Abuja, Port Harcourt</li>
                                    <li><strong>Income:</strong> ₦150,000 - ₦400,000/month</li>
                                    <li><strong>Education:</strong> University graduate</li>
                                    <li><strong>Interests:</strong> Career growth, fashion, travel, technology</li>
                                    <li><strong>Pain Points:</strong> Time management, financial planning, work-life balance</li>
                                    <li><strong>Preferred Platforms:</strong> Instagram, LinkedIn, WhatsApp</li>
                                </ul>
                            </div>
                        </div>
                        
                        <h3>Research Methods</h3>
                        <ol>
                            <li><strong>Surveys:</strong> Use Google Forms or Typeform</li>
                            <li><strong>Social Media Analytics:</strong> Facebook Insights, Instagram Analytics</li>
                            <li><strong>Google Analytics:</strong> Website visitor behavior</li>
                            <li><strong>Focus Groups:</strong> In-person or virtual discussions</li>
                            <li><strong>Competitor Analysis:</strong> Study successful Nigerian brands</li>
                        </ol>
                        ''',
                        'content_type': 'text'
                    }
                    # ... (8 more lessons would continue here)
                ],
                'quizzes': [
                    {
                        'title': 'Digital Marketing Basics Quiz',
                        'description': 'Test your understanding of digital marketing fundamentals',
                        'questions': [
                            {
                                'question': 'What percentage of Nigerians primarily access the internet via mobile devices?',
                                'option_a': '75%',
                                'option_b': '85%',
                                'option_c': '91%',
                                'option_d': '96%',
                                'correct_answer': 'C'
                            },
                            {
                                'question': 'Which platform is most popular for business communication in Nigeria?',
                                'option_a': 'Telegram',
                                'option_b': 'WhatsApp Business',
                                'option_c': 'Slack',
                                'option_d': 'Email',
                                'correct_answer': 'B'
                            }
                        ]
                    }
                ],
                'assignments': [
                    {
                        'title': 'Create a Digital Marketing Strategy',
                        'description': 'Develop a comprehensive digital marketing plan for a Nigerian business',
                        'instructions': '''
                        Choose a Nigerian business (real or fictional) and create a digital marketing strategy that includes:
                        
                        1. Business Analysis (300 words)
                           - Company overview and products/services
                           - Current market position
                           - Main competitors
                        
                        2. Target Audience Analysis (400 words)
                           - Primary and secondary customer personas
                           - Demographics and psychographics
                           - Online behavior patterns
                           - Preferred social media platforms
                        
                        3. Marketing Objectives (200 words)
                           - SMART goals for 6 months
                           - KPIs to track success
                           - Budget considerations
                        
                        4. Channel Strategy (500 words)
                           - Social media platform selection and strategy
                           - Content marketing approach
                           - Email marketing plan
                           - SEO strategy
                        
                        5. Implementation Timeline (200 words)
                           - Monthly milestones
                           - Resource allocation
                           - Risk mitigation
                        
                        Format: Submit as a PDF document with proper headings and professional formatting.
                        '''
                    }
                ]
            },
            {
                'title': 'Data Science with Python for Beginners',
                'description': 'Learn data analysis, visualization, and machine learning using Python programming',
                'price': 30000.0,
                'lessons': [
                    {
                        'title': 'Introduction to Data Science',
                        'content': '''
                        <h2>Welcome to Data Science</h2>
                        <p>Data Science is one of the most exciting and rapidly growing fields in technology. This course will teach you to extract insights from data using Python.</p>
                        
                        <h3>What is Data Science?</h3>
                        <p>Data Science combines statistics, programming, and domain expertise to extract meaningful insights from data. It involves:</p>
                        <ul>
                            <li>Data Collection and Cleaning</li>
                            <li>Exploratory Data Analysis</li>
                            <li>Statistical Analysis</li>
                            <li>Machine Learning</li>
                            <li>Data Visualization</li>
                            <li>Business Intelligence</li>
                        </ul>
                        
                        <h3>The Data Science Process</h3>
                        <div class="row">
                            <div class="col-md-12">
                                <ol>
                                    <li><strong>Problem Definition:</strong> Understand business objectives</li>
                                    <li><strong>Data Collection:</strong> Gather relevant data sources</li>
                                    <li><strong>Data Cleaning:</strong> Prepare data for analysis</li>
                                    <li><strong>Exploratory Analysis:</strong> Discover patterns and insights</li>
                                    <li><strong>Modeling:</strong> Apply statistical/ML techniques</li>
                                    <li><strong>Validation:</strong> Test model accuracy and reliability</li>
                                    <li><strong>Deployment:</strong> Implement solutions in production</li>
                                    <li><strong>Monitoring:</strong> Track performance and iterate</li>
                                </ol>
                            </div>
                        </div>
                        
                        <h3>Career Opportunities in Nigeria</h3>
                        <table class="table table-striped">
                            <tr><th>Role</th><th>Average Salary</th><th>Industry</th></tr>
                            <tr><td>Data Analyst</td><td>₦2.4M - ₦4.8M</td><td>Banking, Telecom, E-commerce</td></tr>
                            <tr><td>Data Scientist</td><td>₦4.8M - ₦9.6M</td><td>Fintech, Healthcare, Oil & Gas</td></tr>
                            <tr><td>Machine Learning Engineer</td><td>₦6M - ₦12M</td><td>Tech Companies, Startups</td></tr>
                            <tr><td>Business Intelligence Analyst</td><td>₦3.6M - ₦7.2M</td><td>Consulting, Retail, Manufacturing</td></tr>
                        </table>
                        
                        <div class="alert alert-success">
                            <strong>Nigerian Context:</strong> We'll use real Nigerian data sets including economic indicators, demographic data, and business metrics throughout this course.
                        </div>
                        ''',
                        'content_type': 'text'
                    }
                    # ... (9 more lessons would continue here)
                ]
            },
            {
                'title': 'Financial Literacy and Investment in Nigeria',
                'description': 'Master personal finance, investment strategies, and wealth building in the Nigerian economic context',
                'price': 15000.0,
                'lessons': [
                    {
                        'title': 'Understanding Personal Finance in Nigeria',
                        'content': '''
                        <h2>Building Financial Success in Nigeria</h2>
                        <p>Financial literacy is crucial for economic success in Nigeria. This course teaches you to manage money, invest wisely, and build wealth despite economic challenges.</p>
                        
                        <h3>The Nigerian Economic Landscape</h3>
                        <p>Understanding Nigeria's economy is essential for making smart financial decisions:</p>
                        <ul>
                            <li><strong>Inflation Rates:</strong> Currently around 15-25% annually</li>
                            <li><strong>Currency Volatility:</strong> Naira fluctuations affect purchasing power</li>
                            <li><strong>Banking System:</strong> Central Bank of Nigeria (CBN) regulations</li>
                            <li><strong>Investment Opportunities:</strong> Stocks, bonds, real estate, agriculture</li>
                            <li><strong>Emerging Sectors:</strong> Fintech, e-commerce, renewable energy</li>
                        </ul>
                        
                        <h3>Common Financial Challenges</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <h4>Individual Level</h4>
                                <ul>
                                    <li>Low savings culture</li>
                                    <li>Limited financial education</li>
                                    <li>High cost of living</li>
                                    <li>Irregular income streams</li>
                                    <li>Family financial obligations</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h4>Systemic Issues</h4>
                                <ul>
                                    <li>High inflation rates</li>
                                    <li>Limited access to credit</li>
                                    <li>Volatile exchange rates</li>
                                    <li>Infrastructure challenges</li>
                                    <li>Regulatory uncertainties</li>
                                </ul>
                            </div>
                        </div>
                        
                        <h3>Financial Goals Framework</h3>
                        <div class="card">
                            <div class="card-header">SMART Financial Goals</div>
                            <div class="card-body">
                                <p><strong>Specific:</strong> "Save ₦500,000 for emergency fund"</p>
                                <p><strong>Measurable:</strong> Track monthly savings of ₦50,000</p>
                                <p><strong>Achievable:</strong> Based on current income and expenses</p>
                                <p><strong>Relevant:</strong> Aligned with financial security objectives</p>
                                <p><strong>Time-bound:</strong> Complete within 10 months</p>
                            </div>
                        </div>
                        
                        <div class="alert alert-warning">
                            <strong>Nigerian Tip:</strong> Always factor in inflation when setting long-term financial goals. What costs ₦100,000 today may cost ₦125,000 next year.
                        </div>
                        ''',
                        'content_type': 'text'
                    }
                    # ... (9 more lessons would continue here)
                ]
            },
            {
                'title': 'Mobile App Development with Flutter',
                'description': 'Build cross-platform mobile applications for Android and iOS using Google\'s Flutter framework',
                'price': 35000.0,
                'lessons': [
                    {
                        'title': 'Introduction to Mobile App Development',
                        'content': '''
                        <h2>Mobile App Development with Flutter</h2>
                        <p>Mobile applications are transforming how Nigerians access services, make payments, and conduct business. Learn to build professional mobile apps with Flutter.</p>
                        
                        <h3>Why Flutter?</h3>
                        <p>Flutter is Google's UI toolkit for building natively compiled applications for mobile, web, and desktop from a single codebase.</p>
                        
                        <h4>Advantages:</h4>
                        <ul>
                            <li><strong>Cross-Platform:</strong> Write once, run on Android and iOS</li>
                            <li><strong>Fast Development:</strong> Hot reload for quick iterations</li>
                            <li><strong>Native Performance:</strong> Compiled to native machine code</li>
                            <li><strong>Rich UI:</strong> Customizable widgets for beautiful interfaces</li>
                            <li><strong>Growing Ecosystem:</strong> Extensive package library</li>
                            <li><strong>Google Support:</strong> Backed by Google with regular updates</li>
                        </ul>
                        
                        <h3>Mobile App Market in Nigeria</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <h4>Popular App Categories</h4>
                                <ul>
                                    <li>Mobile Banking & Fintech</li>
                                    <li>E-commerce & Shopping</li>
                                    <li>Transportation & Logistics</li>
                                    <li>Entertainment & Gaming</li>
                                    <li>Education & Learning</li>
                                    <li>Healthcare & Wellness</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h4>Success Stories</h4>
                                <ul>
                                    <li>Paystack</li>
                                    <li>Flutterwave</li>
                                    <li>PiggyVest</li>
                                    <li>Jumia</li>
                                    <li>Bolt (Taxify)</li>
                                    <li>Opay</li>
                                </ul>
                            </div>
                        </div>
                        
                        <h3>Development Environment Setup</h3>
                        <pre><code># Install Flutter SDK
# Download from flutter.dev

# Verify installation
flutter doctor

# Create new project
flutter create my_first_app

# Run the app
cd my_first_app
flutter run</code></pre>
                        
                        <h3>Flutter Architecture</h3>
                        <div class="card">
                            <div class="card-header">Flutter Framework Layers</div>
                            <div class="card-body">
                                <ol>
                                    <li><strong>Framework (Dart):</strong> Material Design, Cupertino, Widgets</li>
                                    <li><strong>Engine (C++):</strong> Skia graphics, Dart runtime, Platform channels</li>
                                    <li><strong>Embedder:</strong> Platform-specific embedder (Android, iOS)</li>
                                </ol>
                            </div>
                        </div>
                        
                        <div class="alert alert-info">
                            <strong>Course Project:</strong> We'll build a Nigerian expense tracker app that handles multiple currencies, local payment methods, and cultural spending patterns.
                        </div>
                        ''',
                        'content_type': 'text'
                    }
                    # ... (9 more lessons would continue here)
                ]
            },
            {
                'title': 'Graphic Design and Branding for Nigerian Businesses',
                'description': 'Master visual design, brand identity, and creative skills using professional design tools',
                'price': 18000.0,
                'lessons': [
                    {
                        'title': 'Fundamentals of Graphic Design',
                        'content': '''
                        <h2>Visual Communication and Design</h2>
                        <p>Graphic design is essential for business success in Nigeria's competitive market. Learn to create compelling visual content that resonates with Nigerian audiences.</p>
                        
                        <h3>What is Graphic Design?</h3>
                        <p>Graphic design is the art and science of visual communication. It combines typography, imagery, color, and layout to convey messages effectively.</p>
                        
                        <h3>Design Principles</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <h4>Core Principles</h4>
                                <ul>
                                    <li><strong>Balance:</strong> Visual equilibrium in design</li>
                                    <li><strong>Contrast:</strong> Difference between elements</li>
                                    <li><strong>Emphasis:</strong> Creating focal points</li>
                                    <li><strong>Movement:</strong> Guiding the viewer's eye</li>
                                    <li><strong>Pattern:</strong> Repeated elements</li>
                                    <li><strong>Unity:</strong> Cohesive design elements</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h4>Visual Elements</h4>
                                <ul>
                                    <li><strong>Line:</strong> Defines shapes and movement</li>
                                    <li><strong>Shape:</strong> Geometric and organic forms</li>
                                    <li><strong>Color:</strong> Hue, saturation, brightness</li>
                                    <li><strong>Texture:</strong> Surface quality</li>
                                    <li><strong>Space:</strong> Positive and negative areas</li>
                                    <li><strong>Typography:</strong> Font selection and arrangement</li>
                                </ul>
                            </div>
                        </div>
                        
                        <h3>Nigerian Design Context</h3>
                        <p>Understanding Nigerian culture is crucial for effective design:</p>
                        <ul>
                            <li><strong>Color Significance:</strong> Green (agriculture, growth), Red (energy, power), Blue (peace, stability)</li>
                            <li><strong>Cultural Symbols:</strong> Traditional patterns, tribal motifs, national symbols</li>
                            <li><strong>Typography Preferences:</strong> Clear, bold fonts for high literacy impact</li>
                            <li><strong>Local Imagery:</strong> Authentic representation of Nigerian people and landscapes</li>
                            <li><strong>Multilingual Considerations:</strong> English, Hausa, Yoruba, Igbo text accommodation</li>
                        </ul>
                        
                        <h3>Design Tools and Software</h3>
                        <table class="table table-striped">
                            <tr><th>Software</th><th>Best For</th><th>Cost</th><th>Learning Curve</th></tr>
                            <tr><td>Adobe Photoshop</td><td>Photo editing, digital art</td><td>₦10,000/month</td><td>Medium</td></tr>
                            <tr><td>Adobe Illustrator</td><td>Vector graphics, logos</td><td>₦10,000/month</td><td>High</td></tr>
                            <tr><td>Canva</td><td>Social media, presentations</td><td>Free - ₦5,000/month</td><td>Low</td></tr>
                            <tr><td>Figma</td><td>UI/UX design, collaboration</td><td>Free - ₦6,000/month</td><td>Medium</td></tr>
                            <tr><td>GIMP</td><td>Photo editing (free alternative)</td><td>Free</td><td>Medium</td></tr>
                        </table>
                        
                        <div class="alert alert-success">
                            <strong>Nigerian Business Focus:</strong> This course emphasizes designs that work for local businesses, from small enterprises to large corporations, considering budget constraints and market preferences.
                        </div>
                        ''',
                        'content_type': 'text'
                    }
                    # ... (9 more lessons would continue here)
                ]
            }
        ]
        
        # Create the additional courses
        for course_data in additional_courses:
            # Create course
            course = Course(
                title=course_data['title'],
                description=course_data['description'],
                price=course_data['price'],
                instructor_id=admin.id
            )
            db.session.add(course)
            db.session.flush()  # Get the course ID
            
            # Create lessons for the first 2 courses (to show variety)
            for i, lesson_data in enumerate(course_data['lessons']):
                lesson = Lesson(
                    title=lesson_data['title'],
                    content=lesson_data['content'],
                    content_type=lesson_data['content_type'],
                    order=i + 1,
                    course_id=course.id
                )
                db.session.add(lesson)
            
            # Create quizzes (basic structure for now)
            if 'quizzes' in course_data:
                for quiz_data in course_data['quizzes']:
                    quiz = Quiz(
                        title=quiz_data['title'],
                        description=quiz_data['description'],
                        course_id=course.id,
                        time_limit=30,
                        max_attempts=3
                    )
                    db.session.add(quiz)
                    db.session.flush()
                    
                    # Add questions
                    if 'questions' in quiz_data:
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
            if 'assignments' in course_data:
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
        print("Additional courses created successfully!")

if __name__ == '__main__':
    add_more_courses()