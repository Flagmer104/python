"""Рендерить текстовий транскрипт у PNG-скріншот термінала (Playwright + Edge)."""
import html
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text(encoding="utf-8").replace("\r\n", "\n")
page_html = f"""<html><body style="margin:0;background:#0c0c0c">
<div style="padding:14px 18px;color:#cccccc;font:15px/1.35 Consolas,'Cascadia Mono',monospace;
white-space:pre-wrap;word-break:break-all;width:1100px">
<div style="color:#888;margin-bottom:8px">Windows PowerShell</div>{html.escape(text)}</div></body></html>"""
dst.parent.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    pg = b.new_page(viewport={"width": 1140, "height": 200})
    pg.set_content(page_html)
    pg.screenshot(path=str(dst), full_page=True)
    b.close()
print("saved", dst)
