"""Робить скріншоти лабораторної №5 (потрібен запущений сервер на :5055)."""
import struct
import sys
import zlib
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5055"
OUT = Path(__file__).resolve().parent.parent / "screenshots"
OUT.mkdir(exist_ok=True)
TMP = OUT / "_tmp"
TMP.mkdir(exist_ok=True)


def make_png(path, rgb, size=200):
    row = b"\x00" + bytes(rgb) * size
    raw = row * size

    def chunk(t, d):
        c = struct.pack(">I", len(d)) + t + d
        return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    Path(path).write_bytes(png)


make_png(TMP / "blue.png", (40, 100, 200))
make_png(TMP / "green.png", (40, 160, 90))


def shot(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    print("saved", name)


def fill_product(page, name, price, qty, category, content, image=None):
    page.fill("#name", name)
    page.fill("#content", content)
    page.fill("#price", price)
    page.select_option("#category", category)
    page.fill("#quantity", qty)
    if image:
        page.set_input_files("#image", str(image))


with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge")
    page = browser.new_page(viewport={"width": 1100, "height": 800})
    page.on("dialog", lambda d: d.accept())

    # --- Завдання 1: контактна форма ---
    page.goto(f"{BASE}/contact")
    shot(page, "01_contact_empty")
    page.fill("#name", "В")
    page.fill("#email", "not-an-email")
    page.fill("#phone", "abc")
    page.fill("#message", "коротко")
    page.click("#submit")
    shot(page, "02_contact_errors")
    page.fill("#name", "Владислав Харків")
    page.fill("#email", "vlad@example.com")
    page.fill("#phone", "+380501234567")
    page.select_option("#topic", "question")
    page.fill("#message", "Доброго дня! Це тестове повідомлення з контактної форми.")
    shot(page, "03_contact_filled")
    page.click("#submit")
    shot(page, "04_contact_success_flash")

    # --- Завдання 2: товари ---
    page.goto(f"{BASE}/product")
    shot(page, "05_products_empty")
    page.goto(f"{BASE}/product/add")
    shot(page, "06_product_add_form")
    fill_product(page, "ab", "-5", "-1", "books", "")
    page.click("#submit")
    shot(page, "07_product_add_errors")

    page.goto(f"{BASE}/product/add")
    fill_product(page, "Laptop", "1200.50", "5", "electronics",
                 "Потужний ноутбук: Intel Core i7, 16 ГБ RAM, SSD 512 ГБ.", TMP / "blue.png")
    page.click("#submit")
    shot(page, "08_product_created_detail")

    page.goto(f"{BASE}/product/add")
    fill_product(page, "Book Python", "24.99", "12", "books", "Книга про Python та Flask.")
    page.click("#submit")  # без зображення

    page.goto(f"{BASE}/product/add")
    fill_product(page, "Phone", "800", "3", "electronics", "Смартфон з OLED-дисплеєм.", TMP / "green.png")
    page.click("#submit")
    page.goto(f"{BASE}/product")
    shot(page, "09_products_list")

    page.goto(f"{BASE}/product/2")
    shot(page, "10_product_detail_no_image")

    page.goto(f"{BASE}/product/1/edit")
    shot(page, "11_product_edit_form")
    page.fill("#name", "Laptop Pro")
    page.fill("#price", "1399.99")
    page.click("#submit")
    shot(page, "12_product_edited")

    page.goto(f"{BASE}/product/999")
    shot(page, "13_product_not_found_404")

    page.goto(f"{BASE}/product/3")
    page.click("input[value='Видалити']")  # підтвердження приймає обробник dialog
    shot(page, "14_product_deleted_flash")

    browser.close()
print("done", file=sys.stderr)
