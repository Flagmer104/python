"""Insert data into products table

Revision ID: 8a6821233e48
Revises: ada51320c115
Create Date: 2026-11-27 13:36:01.310794

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a6821233e48'
down_revision = 'ada51320c115'
branch_labels = None
depends_on = None


CATEGORIES = ["Laptops", "Smartphones", "Accessories"]

# (name, price, active, category)
PRODUCTS = [
    ("MacBook Air M3", 1299.00, True, "Laptops"),
    ("Dell XPS 13", 1099.00, True, "Laptops"),
    ("Samsung Galaxy S24", 899.00, True, "Smartphones"),
    ("Google Pixel 8", 699.00, True, "Smartphones"),
    ("Logitech MX Master 3S", 99.00, True, "Accessories"),
    ("USB-C Hub (discontinued)", 39.00, False, "Accessories"),
]


def upgrade():
    conn = op.get_bind()
    # Нові категорії; існуючі з таким самим name не змінюються
    for name in CATEGORIES:
        conn.execute(
            sa.text("INSERT INTO categories (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
            {"name": name},
        )
    for name, price, active, category in PRODUCTS:
        conn.execute(
            sa.text(
                "INSERT INTO products (name, price, active, category_id) "
                "SELECT :name, :price, :active, id FROM categories WHERE name = :category"
            ),
            {"name": name, "price": price, "active": active, "category": category},
        )


def downgrade():
    conn = op.get_bind()
    for name, _price, _active, _category in PRODUCTS:
        conn.execute(sa.text("DELETE FROM products WHERE name = :name"), {"name": name})
    # Категорію видаляємо лише якщо в ній не лишилось товарів (Laptops має власні)
    for name in CATEGORIES:
        conn.execute(
            sa.text(
                "DELETE FROM categories WHERE name = :name "
                "AND NOT EXISTS (SELECT 1 FROM products WHERE category_id = categories.id)"
            ),
            {"name": name},
        )
