from flask import render_template, redirect, url_for, flash, request
from sqlalchemy.orm import joinedload, selectinload

from . import post_bp
from .forms import PostForm, DeleteForm
from .models import Post, Category, Tag
from .. import db


def load_tags(ids):
    if not ids:
        return []
    return list(db.session.scalars(db.select(Tag).where(Tag.id.in_(ids))))


@post_bp.route("")
def all_posts():
    # Оптимізація: автори одним JOIN, теги одним додатковим SELECT ... IN (без N+1)
    stmt = (
        db.select(Post)
        .options(joinedload(Post.user), selectinload(Post.tags))
        .where(Post.is_active.is_(True))
        .order_by(Post.posted.desc())
    )
    posts = db.session.scalars(stmt).all()
    return render_template("all_posts.html", posts=posts)


@post_bp.route("/<int:id>")
def detail_post(id):
    post = db.get_or_404(Post, id)
    return render_template("detail_post.html", post=post)


@post_bp.route("/create", methods=["GET", "POST"])
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            posted=form.publish_date.data,
            category=Category(form.category.data),
            is_active=form.enabled.data,
            user_id=form.author_id.data,
            tags=load_tags(form.tags.data),
        )
        db.session.add(post)
        db.session.commit()
        flash("Post added successfully", "success")
        return redirect(url_for("posts.detail_post", id=post.id))  # PRG
    if request.method == "POST":
        flash("Помилка у формі. Перевірте поля.", "danger")
    return render_template("add_post.html", form=form, title="Add Post")


@post_bp.route("/<int:id>/update", methods=["GET", "POST"])
def update_post(id):
    post = db.get_or_404(Post, id)
    if request.method == "GET":
        # імена полів форми та моделі різні (enabled/is_active, publish_date/posted)
        form = PostForm(data={
            "title": post.title,
            "content": post.content,
            "enabled": post.is_active,
            "publish_date": post.posted,
            "category": post.category.value,
            "author_id": post.user_id,
            "tags": [t.id for t in post.tags],
        })
    else:
        form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.is_active = form.enabled.data
        post.posted = form.publish_date.data
        post.category = Category(form.category.data)
        post.user_id = form.author_id.data
        post.tags = load_tags(form.tags.data)
        db.session.commit()
        flash("Post updated successfully", "success")
        return redirect(url_for("posts.detail_post", id=post.id))
    if request.method == "POST":
        flash("Помилка у формі. Перевірте поля.", "danger")
    return render_template("add_post.html", form=form, title="Edit Post", post=post)


@post_bp.route("/<int:id>/delete", methods=["GET", "POST"])
def delete_post(id):
    post = db.get_or_404(Post, id)
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted", "warning")
        return redirect(url_for("posts.all_posts"))
    return render_template("delete_confirm.html", post=post, form=form)
