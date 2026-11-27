import unittest

from app import bcrypt, create_app, db
from app.posts.models import User


def reg(**over):
    data = {
        "username": "vlad",
        "email": "vlad@example.com",
        "password": "secret12",
        "confirm_password": "secret12",
    }
    data.update(over)
    return data


class AuthTestCase(unittest.TestCase):
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

    def register(self, **over):
        return self.client.post("/register", data=reg(**over), follow_redirects=True)

    def login(self, email="vlad@example.com", password="secret12"):
        return self.client.post("/login", data={"email": email, "password": password}, follow_redirects=True)

    # --- Views Tests: сторінки реєстрації та входу ---
    def test_register_page_loads(self):
        r = self.client.get("/register")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Реєстрація", r.get_data(as_text=True))

    def test_login_page_loads(self):
        r = self.client.get("/login")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Вхід", r.get_data(as_text=True))

    # --- збереження користувача у БД при реєстрації ---
    def test_registration_saves_user_with_hashed_password(self):
        r = self.register()
        self.assertEqual(r.status_code, 200)
        user = db.session.scalar(db.select(User).where(User.username == "vlad"))
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "vlad@example.com")
        self.assertNotEqual(user.password, "secret12")  # у БД лежить хеш
        self.assertTrue(user.password.startswith("$2b$"))
        self.assertTrue(bcrypt.check_password_hash(user.password, "secret12"))
        self.assertFalse(bcrypt.check_password_hash(user.password, "wrong"))

    def test_duplicate_username_and_email_rejected(self):
        self.register()
        r = self.register(username="vlad", email="other@example.com")
        self.assertIn("вже зайняте", r.get_data(as_text=True))
        r = self.register(username="other", email="vlad@example.com")
        self.assertIn("уже існує", r.get_data(as_text=True))
        self.assertEqual(len(db.session.scalars(db.select(User)).all()), 1)

    def test_invalid_registration_data(self):
        r = self.register(email="not-an-email", confirm_password="different", password="123")
        html = r.get_data(as_text=True)
        self.assertIn("Невірний формат email", html)
        self.assertIn("Паролі не збігаються", html)
        self.assertIn("щонайменше 6 символів", html)
        self.assertEqual(db.session.scalars(db.select(User)).all(), [])

    # --- вхід і вихід ---
    def test_login_and_logout(self):
        self.register()
        r = self.login()
        html = r.get_data(as_text=True)
        self.assertIn("Профіль", html)
        self.assertIn("vlad@example.com", html)
        with self.client.session_transaction() as s:
            self.assertEqual(s["username"], "vlad")
            self.assertIn("_user_id", s)  # Flask-Login записав id користувача
        r = self.client.get("/logout", follow_redirects=True)
        self.assertIn("Ви вийшли", r.get_data(as_text=True))
        with self.client.session_transaction() as s:
            self.assertNotIn("_user_id", s)
            self.assertNotIn("username", s)

    def test_wrong_password_rejected(self):
        self.register()
        r = self.login(password="nope")
        self.assertIn("Невірний email або пароль", r.get_data(as_text=True))
        self.assertEqual(self.client.get("/account").status_code, 302)

    # --- захист сторінок (@login_required) ---
    def test_protected_pages_redirect_to_login(self):
        for url in ("/account", "/users"):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302)
            self.assertIn("/login?next=", r.headers["Location"])

    def test_users_list_and_count(self):
        self.register()
        self.register(username="anna", email="anna@example.com")
        self.login()
        html = self.client.get("/users").get_data(as_text=True)
        self.assertIn("vlad@example.com", html)
        self.assertIn("anna@example.com", html)
        self.assertIn('badge bg-secondary">2<', html)

    # --- меню та редіректи для авторизованих ---
    def test_menu_changes_after_login(self):
        html = self.client.get("/login").get_data(as_text=True)
        self.assertIn("Реєстрація", html)
        self.assertNotIn("Вихід", html)
        self.register()
        self.login()
        html = self.client.get("/account").get_data(as_text=True)
        self.assertIn("Вихід", html)
        self.assertIn("Профіль (vlad)", html)
        self.assertNotIn(">Реєстрація<", html)

    def test_authenticated_user_redirected_from_register_and_login(self):
        self.register()
        self.login()
        for url in ("/register", "/login"):
            r = self.client.get(url)
            self.assertEqual(r.status_code, 302)
            self.assertTrue(r.headers["Location"].endswith("/account"))


if __name__ == "__main__":
    unittest.main()
