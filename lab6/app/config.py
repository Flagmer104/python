import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    """Базова конфігурація для всіх середовищ."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///data.sqlite")
    WTF_CSRF_ENABLED = True
    # --- з лаби 5: контактна форма та товари (TinyDB) ---
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2 МБ на завантаження
    CONTACT_LOG = os.path.join(BASE_DIR, "logs", "contacts.log")
    PRODUCTS_DB = os.path.join(BASE_DIR, "data", "products.json")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "products", "static", "uploads")


class DevelopmentConfig(Config):
    """Режим розробки (за замовчуванням)."""
    DEBUG = True


class TestingConfig(Config):
    """Тести: in-memory SQLite, без CSRF."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Продакшн: секрет та БД обов'язково зі змінних середовища."""
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
