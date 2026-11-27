import unittest

from sqlalchemy import event
from sqlalchemy.orm import joinedload, selectinload

from app import create_app, db
from app.posts.models import Post, Tag, User


class RelationsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.ctx.pop()

    def seed(self):
        u1 = User(username="user1", email="u1@ex.com", password="x")
        u2 = User(username="user2", email="u2@ex.com", password="x")
        tech, art, sci = Tag(name="Tech"), Tag(name="Art"), Tag(name="Science")
        posts = [
            Post(title=f"P{i}", content="c", user=(u1 if i % 2 else u2)) for i in range(1, 6)
        ]
        posts[0].tags = [tech, art, sci]  # один пост — кілька тегів
        posts[1].tags = [tech]            # один тег — кілька постів
        posts[2].tags = [art]
        db.session.add_all(posts)
        db.session.commit()
        db.session.expunge_all()
        return u1, u2

    # --- User <-> Post (1:N) ---
    def test_user_posts_and_back_reference(self):
        self.seed()
        user = db.session.scalar(db.select(User).where(User.username == "user1"))
        self.assertEqual(len(user.posts), 3)
        self.assertEqual(user.posts[0].user, user)

    def test_delete_user_cascades_to_posts(self):
        self.seed()
        user = db.session.scalar(db.select(User).where(User.username == "user1"))
        db.session.delete(user)
        db.session.commit()
        self.assertEqual(len(db.session.scalars(db.select(Post)).all()), 2)

    def test_password_is_hashed(self):
        user = User(username="a", email="a@ex.com")
        user.set_password("secret")
        self.assertNotEqual(user.password, "secret")
        self.assertTrue(user.check_password("secret"))
        self.assertFalse(user.check_password("other"))

    # --- Post <-> Tag (M:N) ---
    def test_many_to_many_both_directions(self):
        self.seed()
        post = db.session.scalar(db.select(Post).where(Post.title == "P1"))
        self.assertEqual(sorted(t.name for t in post.tags), ["Art", "Science", "Tech"])
        tech = db.session.scalar(db.select(Tag).where(Tag.name == "Tech"))
        self.assertEqual(sorted(p.title for p in tech.posts), ["P1", "P2"])

    def test_tag_name_unique(self):
        db.session.add_all([Tag(name="x"), Tag(name="x")])
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()

    # --- форма ---
    def test_form_lists_authors_and_tags_from_db(self):
        self.seed()
        html = self.client.get("/post/create").get_data(as_text=True)
        for text in ("user1", "user2", "Tech", "Art", "Science"):
            self.assertIn(text, html)

    def test_create_post_with_multiple_tags(self):
        u1, _ = self.seed()
        ids = [t.id for t in db.session.scalars(db.select(Tag).where(Tag.name.in_(["Tech", "Art"])))]
        r = self.client.post("/post/create", data={
            "title": "With tags", "content": "text", "enabled": "y",
            "publish_date": "2025-01-15T10:30", "category": "tech",
            "author_id": "1", "tags": [str(i) for i in ids],
        })
        self.assertEqual(r.status_code, 302)
        post = db.session.scalar(db.select(Post).where(Post.title == "With tags"))
        self.assertEqual(sorted(t.name for t in post.tags), ["Art", "Tech"])

    def test_detail_shows_tags(self):
        self.seed()
        post = db.session.scalar(db.select(Post).where(Post.title == "P1"))
        html = self.client.get(f"/post/{post.id}").get_data(as_text=True)
        for name in ("Tech", "Art", "Science"):
            self.assertIn(name, html)

    # --- оптимізація завантаження ---
    def count_selects(self, stmt):
        queries = []

        def before(conn, cursor, statement, *a):
            if statement.lstrip().upper().startswith("SELECT"):
                queries.append(statement)

        event.listen(db.engine, "before_cursor_execute", before)
        try:
            for post in db.session.scalars(stmt).all():
                post.user.username
                [t.name for t in post.tags]
        finally:
            event.remove(db.engine, "before_cursor_execute", before)
        return len(queries)

    def test_eager_loading_uses_fewer_selects(self):
        self.seed()
        lazy = self.count_selects(db.select(Post).order_by(Post.id.desc()))
        db.session.expunge_all()
        eager = self.count_selects(
            db.select(Post).options(joinedload(Post.user), selectinload(Post.tags)).order_by(Post.id.desc())
        )
        self.assertEqual(eager, 2)
        self.assertGreater(lazy, eager)


if __name__ == "__main__":
    unittest.main()
