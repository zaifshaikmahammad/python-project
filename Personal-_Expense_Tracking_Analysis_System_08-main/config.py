import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration parameters for MySQL."""
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError('Set a strong, private SECRET_KEY environment variable before starting the app.')
    
    # MySQL Database Connection Settings from .env
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'expense_tracker_db')
    
    # SSL/TLS Settings for TiDB Cloud / Remote MySQL
    MYSQL_SSL_CA = os.getenv('MYSQL_SSL_CA', '')
    MYSQL_SSL_DISABLED = os.getenv('MYSQL_SSL_DISABLED', '').lower() in ('true', '1', 'yes')
    MYSQL_USE_SSL = os.getenv('MYSQL_USE_SSL', '').lower() in ('true', '1', 'yes')

