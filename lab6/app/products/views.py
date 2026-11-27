import os
import uuid

from flask import render_template, abort, flash, redirect, url_for, request, current_app
from werkzeug.utils import secure_filename

from . import post_bp
from ..utils.repo import product_repo
from .forms import ProductForm, DeleteForm


def save_image(file_storage):
    """Зберігає зображення в static/uploads/ під UUID-іменем, повертає відносний шлях."""
    if not file_storage or not file_storage.filename:
        return None
    ext = secure_filename(file_storage.filename).rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, filename))
    return f"uploads/{filename}"


def remove_image(rel_path):
    if rel_path:
        path = os.path.join(os.path.dirname(current_app.config["UPLOAD_FOLDER"]), rel_path)
        if os.path.isfile(path):
            os.remove(path)


def get_or_404(product_id):
    product = product_repo.get_by_id(product_id)
    if product is None:
        abort(404)
    return product


@post_bp.route("/product")
def get_products():
    return render_template("products.html", products=product_repo.get_all())


@post_bp.route("/product/<int:id>")
def detail_post(id):
    return render_template("detail_post.html", product=get_or_404(id), delete_form=DeleteForm())


@post_bp.route("/product/add", methods=["GET", "POST"])
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "content": form.content.data,
            "price": float(form.price.data),
            "category": form.category.data,
            "quantity": form.quantity.data,
            "image": save_image(form.image.data),
        }
        product = product_repo.create(data)
        flash(f"Товар «{product['name']}» додано.", "success")
        return redirect(url_for(".detail_post", id=product["id"]))
    if request.method == "POST":
        flash("Помилка у формі. Перевірте поля.", "danger")
    return render_template("product_form.html", form=form, title="Додати товар")


@post_bp.route("/product/<int:id>/edit", methods=["GET", "POST"])
def edit_product(id):
    product = get_or_404(id)
    form = ProductForm(data=product) if request.method == "GET" else ProductForm()
    if form.validate_on_submit():
        data = {
            "name": form.name.data,
            "content": form.content.data,
            "price": float(form.price.data),
            "category": form.category.data,
            "quantity": form.quantity.data,
        }
        new_image = save_image(form.image.data)
        if new_image:  # нове зображення замінює старе, інакше лишається попереднє
            remove_image(product.get("image"))
            data["image"] = new_image
        product_repo.update(id, data)
        flash("Зміни збережено.", "success")
        return redirect(url_for(".detail_post", id=id))
    if request.method == "POST":
        flash("Помилка у формі. Перевірте поля.", "danger")
    return render_template("product_form.html", form=form, title="Редагувати товар", product=product)


@post_bp.route("/product/<int:id>/delete", methods=["POST"])
def delete_product(id):
    product = get_or_404(id)
    if DeleteForm().validate_on_submit():
        remove_image(product.get("image"))
        product_repo.delete(id)
        flash(f"Товар «{product['name']}» видалено.", "warning")
    else:
        flash("Не вдалося підтвердити видалення.", "danger")
    return redirect(url_for(".get_products"))
