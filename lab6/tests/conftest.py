import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.utils.repo import product_repo

# мінімальний валідний PNG 1x1
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c6360000002000001e221bc330000000049454e44ae426082"
)


@pytest.fixture
def client(tmp_path):
    flask_app = create_app("testing")
    flask_app.config.update(
        UPLOAD_FOLDER=str(tmp_path / "app" / "static" / "uploads"),
        CONTACT_LOG=str(tmp_path / "contacts.log"),
    )
    # тимчасове сховище, щоб тести не чіпали data/products.json
    product_repo.init(str(tmp_path / "products.json"))
    yield flask_app.test_client()
    product_repo.db.close()


def valid_data(**over):
    data = {
        "name": "Laptop",
        "content": "Потужний ноутбук",
        "price": "1200.50",
        "category": "electronics",
        "quantity": "5",
    }
    data.update(over)
    return data
