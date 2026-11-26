from flask import Blueprint, render_template, request, redirect, url_for, session

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
