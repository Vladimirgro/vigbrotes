#config.py
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'vladimir'),
    'db': os.getenv('DB_NAME', 'brotes'),
    'ssl_ca': "/path/to/ca-cert.pem",
    'charset': "utf8mb4"
}


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'f43afbca9a1a7d436fc1baf66e20cda47fb300f73a25b1c5')
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limitar el tamaño de los archivos a 16 MB 
    