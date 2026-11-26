import logging
import os

from flask import Flask

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(__name__)
app.secret_key = "secret_key_12345"
app.config["WTF_CSRF_ENABLED"] = True
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 МБ на завантаження
app.config["CONTACT_LOG"] = os.path.join(BASE_DIR, "logs", "contacts.log")
app.config["PRODUCTS_DB"] = os.path.join(BASE_DIR, "data", "products.json")
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "app", "products", "static", "uploads")

# окремий логер для даних контактної форми
os.makedirs(os.path.dirname(app.config["CONTACT_LOG"]), exist_ok=True)
contact_logger = logging.getLogger("contacts")
contact_logger.setLevel(logging.INFO)
if not contact_logger.handlers:
    _h = logging.FileHandler(app.config["CONTACT_LOG"], encoding="utf-8")
    _h.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    contact_logger.addHandler(_h)

from .utils.repo import product_repo
product_repo.init(app.config["PRODUCTS_DB"])

from . import views

from .products import post_bp
app.register_blueprint(post_bp)
