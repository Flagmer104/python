from flask import Blueprint

products_bp = Blueprint("products", __name__)

from . import models  # noqa: E402,F401
