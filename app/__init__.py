import logging
import os

from flask import Flask

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(__name__)
app.secret_key = "secret_key_12345"
app.config["WTF_CSRF_ENABLED"] = True
app.config["CONTACT_LOG"] = os.path.join(BASE_DIR, "logs", "contacts.log")

# окремий логер для даних контактної форми
os.makedirs(os.path.dirname(app.config["CONTACT_LOG"]), exist_ok=True)
contact_logger = logging.getLogger("contacts")
contact_logger.setLevel(logging.INFO)
if not contact_logger.handlers:
    _h = logging.FileHandler(app.config["CONTACT_LOG"], encoding="utf-8")
    _h.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    contact_logger.addHandler(_h)

from . import views

from .products import post_bp
app.register_blueprint(post_bp, url_prefix="/shop")
