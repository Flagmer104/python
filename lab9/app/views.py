import logging
from datetime import timedelta

from flask import (
    Blueprint, flash, make_response, redirect, render_template, request, session, url_for,
)

from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .forms import ContactForm, LoginForm, RegistrationForm
from .posts.models import User

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return redirect(url_for("posts.all_posts"))


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.account"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower())
        user.set_password(form.password.data)  # bcrypt-хеш перед збереженням
        db.session.add(user)
        db.session.commit()
        flash(f"Акаунт «{user.username}» створено. Тепер можна увійти.", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", form=form)


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.account"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.email == form.email.data.lower()))
        if user and user.check_password(form.password.data):  # порівняння хешів
            login_user(user, remember=form.remember.data)
            session["username"] = user.username
            flash("Ви успішно увійшли.", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)
            return redirect(url_for("main.account"))
        flash("Невірний email або пароль.", "danger")
    return render_template("login.html", form=form)


@main_bp.route("/account")
@login_required
def account():
    return render_template("account.html", username=session.get("username", current_user.username))


@main_bp.route("/users")
@login_required
def users():
    all_users = db.session.scalars(db.select(User).order_by(User.id)).all()
    return render_template("users.html", users=all_users, count=len(all_users))


@main_bp.route("/logout")
def logout():
    logout_user()
    session.pop("username", None)
    flash("Ви вийшли з акаунта.", "info")
    return redirect(url_for("main.index"))


# ---------------------------------------------------------------------------
# Маршрути з лаби 5 (сторінки, кукі, контактна форма на Flask-WTF)
# ---------------------------------------------------------------------------


@main_bp.route("/homepage")
def home():
    """View for the Home page of your website."""
    user_agent = str(request.user_agent)[:10]
    return render_template("home.html", agent=user_agent)


@main_bp.route("/hi/")
@main_bp.route("/hi/<string:name>")  # /hi/ivan?age=30
def greetings(name=None):
    name = (name or "").upper()
    age = request.args.get("age", 0, type=int)
    return render_template("hi.html", name=name, age=age)


@main_bp.route("/admin")
def admin():
    return redirect(url_for("main.greetings", name="administrator", _external=True))


@main_bp.route("/set_cookie")
def set_cookie():
    response = make_response("Кука встановлена")
    response.set_cookie("username", "student", max_age=timedelta(seconds=60))
    response.set_cookie("color", "", max_age=timedelta(seconds=60))
    return response


@main_bp.route("/get_cookie")
def get_cookie():
    return f"Користувач: {request.cookies.get('username')}"


@main_bp.route("/delete_cookie")
def delete_cookie():
    response = make_response("Кука видалена")
    response.delete_cookie("color")
    return response


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        try:
            logging.getLogger("contacts").info(
                "name=%s | email=%s | phone=%s | topic=%s | message=%s",
                form.name.data, form.email.data, form.phone.data or "-",
                form.topic.data, form.message.data.replace("\n", " "),
            )
        except OSError:
            flash("Не вдалося зберегти ваше повідомлення. Спробуйте пізніше.", "danger")
        else:
            flash("Дякуємо! Ваше повідомлення надіслано й збережено.", "success")
        return redirect(url_for("main.contact"))  # Post/Redirect/Get
    if request.method == "POST":
        flash("Форму заповнено з помилками. Перевірте виділені поля.", "danger")
    return render_template("contact.html", form=form)
