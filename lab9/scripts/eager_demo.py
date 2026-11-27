"""Порівняння завантаження зв'язків: `eager_demo.py lazy` та `eager_demo.py eager`.

Кожен режим запускається в окремому процесі (нова ORM-сесія). SQL-журнал вмикається
через SQLALCHEMY_ECHO. Рахуються лише SELECT, виконані під час отримання дописів і циклу.
"""
import os
import sys
from pathlib import Path

os.environ["SQL_ECHO"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import event, select  # noqa: E402
from sqlalchemy.orm import joinedload, selectinload  # noqa: E402

from app import create_app, db  # noqa: E402
from app.posts.models import Post  # noqa: E402

mode = sys.argv[1]
app = create_app("development")

with app.app_context():
    selects = []

    @event.listens_for(db.engine, "before_cursor_execute")
    def count_select(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            selects.append(statement)

    if mode == "lazy":
        stmt = select(Post).order_by(Post.id.desc())
    else:
        stmt = (
            select(Post)
            .options(joinedload(Post.user), selectinload(Post.tags))
            .order_by(Post.id.desc())
        )

    print(f"--- {mode}: початок вибірки ---")
    posts = db.session.scalars(stmt).all()
    for post in posts:
        print(
            post.title,
            post.user.username,
            [tag.name for tag in post.tags],
        )
    print(f"--- кількість дописів: {len(posts)}; кількість SELECT: {len(selects)} ---")
