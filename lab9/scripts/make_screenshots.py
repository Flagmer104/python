"""UI-скріншоти лаби 9: реєстрація, вхід, профіль, список користувачів.

Піднімає сервер на :5059 з порожньою тимчасовою БД (flask db upgrade), знімає сторінки Playwright + Edge.
Запуск: python scripts/make_screenshots.py
"""
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "screenshots"
OUT.mkdir(exist_ok=True)
PORT = 5059
BASE = f"http://127.0.0.1:{PORT}"

tmp = tempfile.mkdtemp()
env = dict(os.environ, FLASK_APP="run.py", FLASK_CONFIG="development",
           DATABASE_URL="sqlite:///" + Path(tmp, "demo.sqlite").as_posix(), SECRET_KEY="demo")
subprocess.run([sys.executable, "-m", "flask", "db", "upgrade"], cwd=ROOT, env=env, check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
server = subprocess.Popen([sys.executable, "-m", "flask", "run", "-p", str(PORT)], cwd=ROOT, env=env,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try:
            urllib.request.urlopen(BASE + "/login", timeout=1)
            break
        except Exception:
            time.sleep(0.2)

    def shot(page, name):
        page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
        print("saved", name)

    def fill_register(page, username, email, password, confirm):
        page.goto(f"{BASE}/register")
        page.fill("#username", username)
        page.fill("#email", email)
        page.fill("#password", password)
        page.fill("#confirm_password", confirm)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge")
        page = browser.new_page(viewport={"width": 1100, "height": 700})

        page.goto(f"{BASE}/register")
        shot(page, "01_register_form")

        # успішна реєстрація -> редірект на вхід з flash
        fill_register(page, "vlad", "vlad@example.com", "secret12", "secret12")
        page.click("#submit")
        shot(page, "02_register_success")

        # користувач уже існує + помилки валідації
        fill_register(page, "vlad", "vlad@example.com", "secret12", "secret12")
        page.click("#submit")
        shot(page, "03_register_user_exists")
        fill_register(page, "ab", "not-an-email", "123", "321")
        page.click("#submit")
        shot(page, "04_register_validation_errors")

        # захищена сторінка без входу -> редірект на login?next=
        page.goto(f"{BASE}/users")
        shot(page, "05_login_required_redirect")

        # невірний пароль
        page.fill("#email", "vlad@example.com")
        page.fill("#password", "wrong-password")
        page.click("#submit")
        shot(page, "06_login_wrong_password")

        # вхід -> /account
        page.goto(f"{BASE}/login")
        page.fill("#email", "vlad@example.com")
        page.fill("#password", "secret12")
        page.click("#submit")
        shot(page, "07_account_after_login")

        # другий користувач у списку
        ctx2 = browser.new_context(viewport={"width": 1100, "height": 700})
        page2 = ctx2.new_page()
        page2.goto(f"{BASE}/register")
        page2.fill("#username", "anna")
        page2.fill("#email", "anna@example.com")
        page2.fill("#password", "secret12")
        page2.fill("#confirm_password", "secret12")
        page2.click("#submit")
        ctx2.close()

        page.goto(f"{BASE}/users")
        shot(page, "08_users_list")

        # авторизований користувач на /register -> редірект на account
        page.goto(f"{BASE}/register")
        shot(page, "09_register_redirects_to_account")

        page.goto(f"{BASE}/logout")
        shot(page, "10_after_logout")
        browser.close()
finally:
    server.terminate()
