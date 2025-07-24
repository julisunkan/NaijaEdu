import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET")
    
    # CSRF configuration for Flask-WTF
    app.config['WTF_CSRF_ENABLED'] = True
    
    # Database configuration - use environment DATABASE_URL if available, otherwise SQLite
    if os.environ.get("DATABASE_URL"):
        database_url = os.environ.get("DATABASE_URL")
    else:
        # Use absolute path for SQLite in development
        db_path = os.path.join(os.getcwd(), "instance", "elearning.db")
        database_url = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # File upload configuration
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
    app.config["UPLOAD_FOLDER"] = "uploads"
    
    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    # Ensure instance directory exists for SQLite database
    os.makedirs("instance", exist_ok=True)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"  # type: ignore
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"
    
    # Proxy fix for deployment
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Add template filters
    @app.template_filter('currency')
    def currency_filter(amount):
        """Format amount with Nigerian Naira symbol and comma separators"""
        if amount is None:
            return "₦0.00"
        return f"₦{amount:,.2f}"
    
    return app

# Create app instance
app = create_app()

# Import models and routes after app creation to avoid circular imports
with app.app_context():
    import models
    import routes  # Import routes to register them
    db.create_all()
    
    # Create default admin user if not exists
    from werkzeug.security import generate_password_hash
    from models import User, SystemSettings
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User()
        admin.username = 'admin'
        admin.email = 'admin@example.com'
        admin.password_hash = generate_password_hash('admin123')
        admin.role = 'admin'
        admin.active = True
        db.session.add(admin)
    
    # Create default system settings
    settings = SystemSettings.query.first()
    if not settings:
        settings = SystemSettings()
        settings.site_name = 'Nigerian E-Learning Platform'
        settings.site_description = 'Learn with the best courses in Nigeria'
        settings.currency_symbol = '₦'
        settings.admin_email = 'admin@example.com'
        db.session.add(settings)
    
    db.session.commit()
    logging.info("Database initialized successfully")

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))
