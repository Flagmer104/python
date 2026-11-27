import logging
from datetime import timedelta

from flask import (
    Blueprint, flash, make_response, redirect, render_template, request, session, url_for,
)

from .forms import ContactForm

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return redirect(url_for("posts.all_posts"))


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("login", "").strip()
        if username:
            session["username"] = username[:20]
            return redirect(url_for("main.profile"))
    return render_template("login.html")


@main_bp.route("/profile")
def profile():
    if "username" in session:
        return render_template("profile.html", username=session["username"])
    return redirect(url_for("main.login"))


@main_bp.route("/logout")
def logout():
    session.pop("username", None)
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
