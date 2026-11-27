# Лабораторна робота 7 — Зв'язки. Міграції (Flask, SQLAlchemy 2.0, Flask-Migrate)

Продовжує лабораторну №6 (а та — лабораторну №5): пререквізити завдання (БД, `db`, Flask-Migrate) і блюпринт `products` уже є в проєкті. Моделі `Product` і `Category` додано в `app/products/models.py`; міграції лежать у тому ж `migrations/` після міграцій лаби 6 (`a7d3a4fa7dba`, `6c24b2df3afa`). Решта застосунку (контактна форма, TinyDB-товари, пости) працює як і раніше. Моделі `Category` (1) → `Product` (N), міграції, naming convention,
додавання полів до заповненої таблиці, міграція з даними.

## Запуск

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\flask db upgrade     # створює instance/data.sqlite з усіма даними
.venv\Scripts\flask db history
```

## Історія міграцій

| Міграція | Що робить |
|---|---|
| `a7d3a4fa7dba`, `6c24b2df3afa` | з лаби 6: таблиця `post` |
| `538e9e9b34f3` Add Product | таблиця `products` |
| `9eaf4d496c45` Add Category | таблиця `categories`, FK `products.category_id` (ім'я FK задано вручну, інакше SQLite batch падає з `Constraint must have a name`) |
| `6637e67bf92a` Naming convention | іменовані обмеження (`uq_categories_name`) |
| `8579c00a3399` Add active to Product | `active BOOLEAN NOT NULL` з `server_default=sa.true()` |
| `ada51320c115` Add created_at with server_default | `created_at` з `server_default=func.now()` |
| `8a6821233e48` Insert data into products table | ручна міграція: категорії та товари, `ON CONFLICT (name) DO NOTHING`, відкат у `downgrade()` |

## Скріншоти (`screenshots/`)

- `01_schema.png` — схема таблиць
- `02_data.png` — дані в БД
- `03_history.png` — `flask db current` та `flask db history`
- `04_history_downgrade.png` — `flask db downgrade` + `flask db history` (+ повернення `upgrade`)

Відтворити: `scripts/term.py` (транскрипт) + `scripts/render.py` (PNG, Playwright + Edge).
