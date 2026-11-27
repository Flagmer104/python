# Лабораторна робота 6 — ORM, SQLAlchemy 2.0, CRUD (Flask)

> Лаба 6 побудована **на основі лаби 5** (так сказано в завданні): уся лаба 5 (контактна форма Flask-WTF, блюпринт `products` з TinyDB, сторінки `/hi`, `/homepage`, `/admin`, кукі, логін) перенесена в цей застосунок, а блюпринт `posts` з SQLAlchemy додано поверх. Чиста лаба 5 — у гілці `lab5`.

Блог із постами: application factory, Flask-SQLAlchemy 2.0, Flask-Migrate, Flask-WTF, Bootstrap 5, unittest.

## Запуск

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\flask db upgrade     # створює instance/data.sqlite
.venv\Scripts\flask run            # http://127.0.0.1:5000/post
.venv\Scripts\python -m pytest -q            # 53 тести (лаба 5 + лаба 6)
```

Конфігурація береться з `.env` (`FLASK_APP`, `FLASK_CONFIG`, `SECRET_KEY`, `DATABASE_URL`).
`FLASK_CONFIG` = `development` | `testing` | `production`.

## Маршрути

| Метод | Шлях | Шаблон |
|---|---|---|
| GET/POST | `/post/create` | `add_post.html` |
| GET | `/post` | `all_posts.html` |
| GET | `/post/<id>` | `detail_post.html` |
| GET/POST | `/post/<id>/update` | `add_post.html` |
| GET/POST | `/post/<id>/delete` | `delete_confirm.html` |
| — | 404 | `404.html` |

### Перенесено з лаби 5

| Метод | Шлях | Опис |
|---|---|---|
| GET/POST | `/contact` | контактна форма (Flask-WTF, лог у `logs/contacts.log`, PRG) |
| GET | `/product`, `/product/<id>` | товари (TinyDB, `data/products.json`) |
| GET/POST | `/product/add`, `/product/<id>/edit`, POST `/product/<id>/delete` | CRUD товарів |
| GET | `/homepage`, `/hi/`, `/hi/<name>`, `/admin` | прості сторінки |
| GET | `/set_cookie`, `/get_cookie`, `/delete_cookie` | кукі |

Блюпринти: `main` (`app/views.py`), `product` (`app/products`), `posts` (`app/posts`, префікс `/post`). Тести лаби 5 (pytest) і лаби 6 (unittest) запускаються разом: `python -m pytest`.

Автор поста береться з `session["username"]` (сторінка `/login`), інакше `Anonymous`.

## Скріншоти

Папка `screenshots/`: частини 2–3 (`01`–`03`), інтерфейс частини 6 (`04`–`14`), модульні тести (`15`).
Термінальні скріни: `scripts/term.py` + `scripts/render.py`. UI-скріни зняті до перенесення лаби 5 (у навбарі тоді не було Homepage/Contact/Products).

## Контрольні запитання (коротко)

1. **Application factory** — функція `create_app(config_name)`, що створює екземпляр застосунку; дає різні конфігурації (dev/test/prod), ізольовані тести та відсутність циклічних імпортів.
2. **Вибір конфігурації** — за назвою (`config[config_name]` + `app.config.from_object`), назва береться з аргументу чи змінної `FLASK_CONFIG`.
3. **`.env` і python-dotenv** — зберігають налаштування й секрети поза кодом; `load_dotenv()` завантажує їх у `os.environ`.
4. **Dev / Testing / Production** — Dev: `DEBUG`, локальна БД; Testing: in-memory SQLite, без CSRF; Production: без `DEBUG`, секрет і БД лише зі змінних середовища.
5. **Реєстрація блюпринта** — `app.register_blueprint(post_bp, url_prefix="/post")`.
6. **ORM** — відображає Python-класи на таблиці, дає писати запити об'єктами без сирого SQL.
7. **БД через CLI** — `flask db init` → `flask db migrate -m "..."` → `flask db upgrade`.
8. **`flask shell`** — інтерактивна консоль з контекстом застосунку: перевірка моделей і запитів вручну.
9. **Модель — форма — шаблон** — view валідує `FlaskForm`, переносить дані в модель/з моделі, шаблон малює форму макросом `render_field`.
10. **Зміна схеми без втрати даних** — змінити модель → `flask db migrate` → `flask db upgrade` (для NOT NULL колонок — `server_default`).
