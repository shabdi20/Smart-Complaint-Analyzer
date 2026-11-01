import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-change-this-before-deployment'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + str(BASE_DIR / 'instance' / 'complaints.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_FOLDER = str(BASE_DIR / 'instance' / 'uploads')
    MODEL_PATH = str(BASE_DIR / 'ml' / 'saved_model' / 'classifier.joblib')
    MODEL_CONFIDENCE_THRESHOLD = float(os.environ.get('MODEL_CONFIDENCE_THRESHOLD', '0.50'))
    SIMILARITY_THRESHOLD = float(os.environ.get('SIMILARITY_THRESHOLD', '0.48'))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE') == '1'

    NOTIFICATIONS_ENABLED = os.environ.get('NOTIFICATIONS_ENABLED', '0') == '1'
    NOTIFY_ALL_AUTHORITIES = os.environ.get('NOTIFY_ALL_AUTHORITIES', '1') == '1'
    SMTP_HOST = os.environ.get('SMTP_HOST', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USER = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    SMTP_FROM = os.environ.get('SMTP_FROM', '')
    SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', '0') == '1'
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_SMS_FROM = os.environ.get('TWILIO_SMS_FROM', '')
    TWILIO_WHATSAPP_FROM = os.environ.get('TWILIO_WHATSAPP_FROM', '')
    TWILIO_WHATSAPP_CONTENT_SID = os.environ.get('TWILIO_WHATSAPP_CONTENT_SID', '')
