"""Скріншоти Частини 6 (ручне тестування). Потрібен сервер на :5056 з мігрованою БД."""
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5056"
OUT = Path(__file__).resolve().parent.parent / "screenshots"
OUT.mkdir(exist_ok=True)


def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    print("saved", name)


def add_post(page, title, content, category, when, enabled=True):
    page.goto(f"{BASE}/post/create")
    page.fill("#title", title)
    page.fill("#content", content)
    page.select_option("#category", category)
    page.fill("#publish_date", when)
    if not enabled:
        page.uncheck("#enabled")
    page.click("#submit")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 1200, "height": 800})

    page.goto(f"{BASE}/post")
    shot(page, "04_ui_posts_empty")

    # автор з сесії
    page.goto(f"{BASE}/login")
    page.fill("#login", "vlad")
    page.click("button[type=submit]")

    page.goto(f"{BASE}/post/create")
    shot(page, "05_ui_add_post_form")
    page.fill("#title", "")
    page.fill("#content", "")
    page.click("#submit")
    shot(page, "06_ui_add_post_errors")

    add_post(page, "Flask 3.1 вийшов", "Нова версія Flask приносить покращення роботи з конфігурацією та CLI. "
             "Це довгий текст, який буде обрізано на сторінці зі списком постів, "
             "щоб картка лишалась компактною та охайною.", "news", "2025-11-20T09:00")
    shot(page, "07_ui_post_added_flash_detail")

    add_post(page, "SQLAlchemy 2.0 ORM", "Сучасний синтаксис Mapped та mapped_column.", "tech", "2025-11-22T14:30")
    add_post(page, "Мій перший допис", "Короткий текст публікації.", "publication", "2025-11-21T18:15")
    add_post(page, "Прихований пост", "Цей пост вимкнено, у списку його не видно.", "other", "2025-11-23T10:00", enabled=False)

    page.goto(f"{BASE}/post")
    shot(page, "08_ui_posts_list")

    page.goto(f"{BASE}/post/3/update")
    shot(page, "09_ui_edit_post_form")
    page.fill("#title", "Мій перший допис (оновлено)")
    page.fill("#content", "Текст було оновлено через форму редагування.")
    page.select_option("#category", "news")
    page.click("#submit")
    shot(page, "10_ui_post_updated_flash")

    page.goto(f"{BASE}/post/2/delete")
    shot(page, "11_ui_delete_confirm")
    page.click("#submit")
    shot(page, "12_ui_post_deleted_flash_list")

    page.goto(f"{BASE}/post/999")
    shot(page, "13_ui_404")
    browser.close()
