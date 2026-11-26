from flask import render_template

from . import post_bp
from .models import Post
from .. import db


@post_bp.route("")
def all_posts():
    posts = db.session.scalars(db.select(Post).order_by(Post.posted.desc())).all()
    return render_template("all_posts.html", posts=posts)


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    return render_template("all_posts.html", posts=[])
