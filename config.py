import os
import secrets

class Config:
    # Generate a secure secret key if not provided
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))
    
    # Base directory (absolute path of your project)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

    # ✅ Email config (Gmail SMTP)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'samuelolokor228@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'wxdh wydd gdjs rzrz')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    # Database config
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'database.db'
    
    # Admin settings
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'RUNSA2025'  # Change this in production!
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
