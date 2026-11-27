import os


class Config:
    """Базова конфігурація для всіх середовищ."""
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///data.sqlite")
    WTF_CSRF_ENABLED = True


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
