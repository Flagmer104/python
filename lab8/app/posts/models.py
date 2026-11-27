import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from werkzeug.security import check_password_hash, generate_password_hash

from .. import db


class Category(enum.Enum):
    news = "news"
    publication = "publication"
    tech = "tech"
    other = "other"


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)  # хеш, не відкритий пароль

    # Один користувач — багато постів; видалення користувача видаляє його пости
    posts: Mapped[list["Post"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def set_password(self, raw):
        self.password = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)

    def __repr__(self):
        return f"User({self.username!r}, {self.email!r})"


class Post(db.Model):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    posted: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    category: Mapped[Category] = mapped_column(
        Enum(Category, values_callable=lambda e: [m.value for m in e], name="category"),
        default=Category.other,
    )
    # server_default потрібен, щоб міграція могла додати NOT NULL колонки до таблиці з даними
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    # nullable: пости, створені до появи користувачів, лишаються без автора
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    user: Mapped["User | None"] = relationship(back_populates="posts")

    def __repr__(self):
        return f"<Post {self.id}: {self.title!r}>"
