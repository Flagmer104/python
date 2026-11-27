from flask import Blueprint

# Блюпринт products з лаби 5. Шаблони лежать у products/templates/products/,
# тому імена шаблонів мають префікс "products/" (інакше detail_post.html
# конфліктує з однойменним шаблоном блюпринта posts).
product_bp = Blueprint(
    "product",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/product-static",
)

from . import views  # noqa: E402,F401
