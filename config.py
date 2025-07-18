import os
import secrets

class Config:
    # Generate a secure secret key if not provided
    SECRET_KEY = os.environ.get('SECRET_KEY', 'yoursecretkey')
    
    # Upload settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

    # Email config (Gmail SMTP)
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # should be 'apikey'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # your SendGrid API key
    
    # Database config
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'database.db'
    
    # Admin settings
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'RUNSA2025'  # Change this in production!
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS