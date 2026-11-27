"""UI-скріншоти пп. 8, 11, 12. Потрібен сервер на :5058 з мігрованою БД (користувачі й теги вже є)."""
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5058"
OUT = Path(__file__).resolve().parent.parent / "screenshots"
OUT.mkdir(exist_ok=True)


def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    print("saved", name)


def expand(page, selector, size):
    """Показує варіанти <select> списком (випадаючий список у headless не потрапляє на скріншот)."""
    page.eval_on_selector(selector, f"el => el.setAttribute('size', '{size}')")


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 1100, "height": 800})

    # п. 8: список авторів з БД у формі
    page.goto(f"{BASE}/post/create")
    page.fill("#title", "Test by user 2")
    page.fill("#content", "Автор вибирається зі списку користувачів із БД.")
    page.select_option("#author_id", label="user2")
    expand(page, "#author_id", 2)
    shot(page, "08_ui_author_select")

    # п. 11: вибір кількох тегів та збереження
    page.goto(f"{BASE}/post/create")
    page.fill("#title", "Art of pop culture")
    page.fill("#content", "Допис із кількома тегами, вибраними у формі через SelectMultipleField.")
    page.select_option("#category", "tech")
    page.select_option("#author_id", label="user1")
    page.select_option("#tags", label=["Tech", "Art", "Science"])
    expand(page, "#tags", 3)
    shot(page, "11_ui_tags_select")
    page.click("#submit")
    shot(page, "12_ui_post_detail_tags")

    page.goto(f"{BASE}/post")
    shot(page, "12_ui_posts_list_tags")
    browser.close()
