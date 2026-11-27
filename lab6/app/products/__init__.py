from flask import Blueprint


# Defining a blueprint
post_bp = Blueprint('product', __name__,template_folder="templates/products", static_folder="static",
                  static_url_path="/product-static")

from . import views