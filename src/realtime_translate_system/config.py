from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

class Language:
    TW = "Traditional Chinese"
    EN = "English"
    DE = "German"
    JP = "Japanese"

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False

    BASE_DIR = Path(__file__).resolve().parent
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    GLOSSARY_FOLDER = BASE_DIR / "glossaries"
    FILE_PATHS = {
        Language.TW: GLOSSARY_FOLDER / "cmn-Hant-TW.csv",
        Language.EN: GLOSSARY_FOLDER / "en-US.csv",
        Language.DE: GLOSSARY_FOLDER / "de-DE.csv",
        Language.JP: GLOSSARY_FOLDER / "ja-JP.csv",
    }

    # Google Cloud environment variables
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
    LOCATION = "us-central1"

    ALLOWED_EXTENSIONS = {"wav"}
    TERM_MATCHER_THRESHOLD = 60


class DevelopmentConfig(Config):
    DEBUG = True

    # PostgreSQL 連線設定
    DB_CONFIG = {
        "dbname": "meetings_db",
        "user": "postgres",
        "password": "postgres",
        "host": "127.0.0.1",  # Cloud SQL Proxy 連線
        "port": "5433"
    }

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{Config.BASE_DIR}/prod.db"
    )


# 選擇環境
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
