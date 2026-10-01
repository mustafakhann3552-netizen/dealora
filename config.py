import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)


class Config:

    # ==========================================
    # Flask
    # ==========================================

    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")

    # ==========================================
    # AI Affiliate System API
    # ==========================================

    AI_WEBSITE_API_TOKEN = os.getenv(
        "AI_WEBSITE_API_TOKEN",
        "",
    ).strip()

    WEBSITE_PUBLIC_BASE_URL = os.getenv(
        "WEBSITE_PUBLIC_BASE_URL",
        "",
    ).strip().rstrip("/")

    # ==========================================
    # Database
    # ==========================================

    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ==========================================
    # Upload Folder
    # ==========================================

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")

    # ==========================================
    # Gmail SMTP
    # ==========================================

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        MAIL_USERNAME,
    )
