"""Сховище товарів на TinyDB (JSON-файл data/products.json)."""
import os
import threading
from datetime import datetime

from tinydb import TinyDB, Query


class ProductRepository:
    def __init__(self, path=None):
        self._lock = threading.Lock()
        self.db = None
        self.table = None
        if path:
            self.init(path)

    def init(self, path):
        """Ініціалізація сховища та таблиці products."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if self.db is not None:
            self.db.close()
        self.db = TinyDB(path, indent=2, ensure_ascii=False, encoding="utf-8")
        self.table = self.db.table("products")

    # --- CRUD ---
    def get_all(self):
        return sorted(self.table.all(), key=lambda p: p["id"])

    def get_by_id(self, product_id):
        return self.table.get(Query().id == product_id)

    def create(self, data):
        with self._lock:
            ids = [p["id"] for p in self.table.all()]
            data = dict(data)
            data["id"] = max(ids) + 1 if ids else 1
            data["created_at"] = datetime.now().isoformat(timespec="seconds")
            self.table.insert(data)
            return data

    def update(self, product_id, data):
        """Оновлює поля, не змінюючи id та created_at."""
        data = {k: v for k, v in data.items() if k not in ("id", "created_at")}
        updated = self.table.update(data, Query().id == product_id)
        return bool(updated)

    def delete(self, product_id):
        return bool(self.table.remove(Query().id == product_id))


product_repo = ProductRepository()
