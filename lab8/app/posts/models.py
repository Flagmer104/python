import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, String, Text, DateTime, Enum
from sqlalchemy.sql import true
from sqlalchemy.orm import Mapped, mapped_column

from .. import db


class Category(enum.Enum):
    news = "news"
    publication = "publication"
    tech = "tech"
    other = "other"


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


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
    author: Mapped[str] = mapped_column(String(20), default="Anonymous", server_default="Anonymous")

    def __repr__(self):
        return f"<Post {self.id}: {self.title!r}>"
