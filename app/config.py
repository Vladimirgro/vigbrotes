#config.py
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'vladimir'),
    'db': os.getenv('DB_NAME', 'brotes')
}


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limitar el tamaño de los archivos a 16 MB  
    