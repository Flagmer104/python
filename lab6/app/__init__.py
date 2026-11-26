import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from .config import config


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()


def create_app(config_name=None):
    """Application factory: створює застосунок для вказаного середовища."""
    load_dotenv()
    config_name = config_name or os.getenv("FLASK_CONFIG", "default")
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    if config_name == "production" and not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY must be set in production")

    db.init_app(app)
    migrate.init_app(app, db)

    from .posts import post_bp
    from .views import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(post_bp, url_prefix="/post")

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    return app
