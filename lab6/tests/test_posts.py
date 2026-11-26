import unittest
from datetime import datetime, timedelta

from app import create_app, db
from app.posts.models import Post, Category


def form_data(**over):
    data = {
        "title": "Hello",
        "content": "Some content for the post",
        "enabled": "y",
        "publish_date": "2025-01-15T10:30",
        "category": "news",
    }
    data.update(over)
    return data


class PostsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def make_post(self, **over):
        fields = dict(title="T", content="C", category=Category.other)
        fields.update(over)
        post = Post(**fields)
        db.session.add(post)
        db.session.commit()
        return post

    # --- конфігурація ---
    def test_testing_config(self):
        self.assertTrue(self.app.config["TESTING"])
        self.assertEqual(self.app.config["SQLALCHEMY_DATABASE_URI"], "sqlite:///:memory:")

    # --- model ---
    def test_model_defaults_and_repr(self):
        post = self.make_post()
        self.assertTrue(post.is_active)
        self.assertEqual(post.author, "Anonymous")
        self.assertIsNotNone(post.posted)
        self.assertIn("Post", repr(post))

    # --- CREATE ---
    def test_create_get_form(self):
        r = self.client.get("/post/create")
        self.assertEqual(r.status_code, 200)

    def test_create_post_redirects_and_saves(self):
        r = self.client.post("/post/create", data=form_data())
        self.assertEqual(r.status_code, 302)  # PRG
        post = db.session.scalar(db.select(Post))
        self.assertEqual(post.title, "Hello")
        self.assertEqual(post.category, Category.news)
        self.assertEqual(post.posted, datetime(2025, 1, 15, 10, 30))
        self.assertTrue(post.is_active)

    def test_create_flash_success(self):
        r = self.client.post("/post/create", data=form_data(), follow_redirects=True)
        self.assertIn("Post added successfully", r.get_data(as_text=True))

    def test_create_author_anonymous_by_default(self):
        self.client.post("/post/create", data=form_data())
        self.assertEqual(db.session.scalar(db.select(Post)).author, "Anonymous")

    def test_create_author_from_session(self):
        with self.client.session_transaction() as s:
            s["username"] = "vlad"
        self.client.post("/post/create", data=form_data())
        self.assertEqual(db.session.scalar(db.select(Post)).author, "vlad")

    def test_create_invalid_does_not_save(self):
        r = self.client.post("/post/create", data=form_data(title="", content=""))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(db.session.scalars(db.select(Post)).all(), [])

    def test_create_invalid_category(self):
        r = self.client.post("/post/create", data=form_data(category="bogus"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(db.session.scalars(db.select(Post)).all(), [])

    def test_create_title_too_long(self):
        r = self.client.post("/post/create", data=form_data(title="x" * 151))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(db.session.scalars(db.select(Post)).all(), [])

    def test_create_disabled_post(self):
        data = form_data()
        del data["enabled"]
        self.client.post("/post/create", data=data)
        self.assertFalse(db.session.scalar(db.select(Post)).is_active)

    # --- READ list ---
    def test_list_empty(self):
        r = self.client.get("/post")
        self.assertEqual(r.status_code, 200)

    def test_list_sorted_desc_by_date(self):
        now = datetime(2025, 1, 1)
        self.make_post(title="Old", posted=now)
        self.make_post(title="Newest", posted=now + timedelta(days=2))
        self.make_post(title="Middle", posted=now + timedelta(days=1))
        html = self.client.get("/post").get_data(as_text=True)
        self.assertLess(html.index("Newest"), html.index("Middle"))
        self.assertLess(html.index("Middle"), html.index("Old"))

    def test_list_hides_inactive(self):
        self.make_post(title="Visible")
        self.make_post(title="Hidden", is_active=False)
        html = self.client.get("/post").get_data(as_text=True)
        self.assertIn("Visible", html)
        self.assertNotIn("Hidden", html)

    def test_list_truncates_content(self):
        self.make_post(content="a" * 100 + "TAILMARK")
        self.assertNotIn("TAILMARK", self.client.get("/post").get_data(as_text=True))

    # --- READ detail ---
    def test_detail(self):
        post = self.make_post(title="Detail title", content="Full content text")
        r = self.client.get(f"/post/{post.id}")
        html = r.get_data(as_text=True)
        self.assertEqual(r.status_code, 200)
        self.assertIn("Detail title", html)
        self.assertIn("Full content text", html)

    def test_detail_not_found_uses_404_template(self):
        r = self.client.get("/post/999")
        self.assertEqual(r.status_code, 404)
        self.assertIn("404", r.get_data(as_text=True))

    def test_unknown_url_404(self):
        self.assertEqual(self.client.get("/no-such-page").status_code, 404)

    # --- UPDATE ---
    def test_update_get_prefilled(self):
        post = self.make_post(title="Prefilled", posted=datetime(2025, 3, 4, 5, 6))
        html = self.client.get(f"/post/{post.id}/update").get_data(as_text=True)
        self.assertIn("Prefilled", html)
        self.assertIn("2025-03-04T05:06", html)

    def test_update_saves_and_redirects(self):
        post = self.make_post(title="Before")
        r = self.client.post(
            f"/post/{post.id}/update",
            data=form_data(title="After", category="tech"),
            follow_redirects=True,
        )
        self.assertIn("Post updated successfully", r.get_data(as_text=True))
        db.session.expire_all()
        updated = db.session.get(Post, post.id)
        self.assertEqual(updated.title, "After")
        self.assertEqual(updated.category, Category.tech)

    def test_update_keeps_author(self):
        post = self.make_post(author="orig")
        self.client.post(f"/post/{post.id}/update", data=form_data())
        db.session.expire_all()
        self.assertEqual(db.session.get(Post, post.id).author, "orig")

    def test_update_invalid(self):
        post = self.make_post(title="Keep")
        r = self.client.post(f"/post/{post.id}/update", data=form_data(title=""))
        self.assertEqual(r.status_code, 200)
        db.session.expire_all()
        self.assertEqual(db.session.get(Post, post.id).title, "Keep")

    def test_update_not_found(self):
        self.assertEqual(self.client.post("/post/42/update", data=form_data()).status_code, 404)

    # --- DELETE ---
    def test_delete_get_shows_confirmation(self):
        post = self.make_post(title="To remove")
        r = self.client.get(f"/post/{post.id}/delete")
        self.assertEqual(r.status_code, 200)
        self.assertIn("To remove", r.get_data(as_text=True))
        self.assertIsNotNone(db.session.get(Post, post.id))  # GET нічого не видаляє

    def test_delete_post_removes(self):
        post = self.make_post()
        r = self.client.post(f"/post/{post.id}/delete", follow_redirects=True)
        self.assertIn("Post deleted", r.get_data(as_text=True))
        db.session.expire_all()
        self.assertIsNone(db.session.get(Post, post.id))

    def test_delete_not_found(self):
        self.assertEqual(self.client.post("/post/42/delete").status_code, 404)


if __name__ == "__main__":
    unittest.main()
