# Лабораторна робота 9 — Реєстрація та вхід (Flask-Bcrypt, Flask-Login)

Продовжує лабу 8 (модель `User` з лаби 8; а та — 7 → 6 → 5): у застосунку лишається все попереднє
(контактна форма, товари TinyDB, пости з авторами й тегами, міграції). Додано реєстрацію, вхід із bcrypt-хешами,
Flask-Login та тести.

## Запуск

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\flask db upgrade
.venv\Scripts\flask run                 # http://127.0.0.1:5000/register
.venv\Scripts\python -m pytest -q       # 73 тести (лаби 5–9)
```

## Що зроблено

**Частина 1 — реєстрація**

| Пункт | Реалізація |
|---|---|
| Flask-Bcrypt | `bcrypt = Bcrypt()` у `app/__init__.py`; `User.set_password()` / `check_password()` (`app/posts/models.py`) зберігають лише bcrypt-хеш (`$2b$…`) |
| Форма реєстрації | `RegistrationForm` (`app/forms.py`): `Email()`, довжина, `EqualTo`, унікальність `username` та `email` перевіряється в БД (`validate_username`, `validate_email`) |
| Маршрут | `GET/POST /register` → збереження користувача → flash → редірект на `/login` |
| Вхід | `GET/POST /login`: пошук за email, порівняння хешів; `session['username'] = user.username`; редірект на `/account` |
| Профіль | `/account` (`account.html`): дані з сесії та БД |
| Список користувачів | `/users` (`users.html`): таблиця й кількість, повідомлення, якщо список порожній |

**Частина 2 — Flask-Login**

`login_manager` (`login_view = "main.login"`), `user_loader` за id з БД, `User(UserMixin, db.Model)`, `login_user`,
`logout_user`, `@login_required` на `/account` і `/users`. Авторизовані користувачі з `/register` та `/login`
перенаправляються на `/account`; у меню замість «Реєстрація / Вхід» з'являються «Профіль» та «Вихід»
(`includes/nav.html`, `current_user.is_authenticated`). Перенаправлення після входу на `?next=` обмежене локальними шляхами.

**Частина 3 — тести** (`tests/test_auth.py`, 11 тестів): завантаження сторінок реєстрації та входу; збереження
користувача й хешування пароля; унікальність username/email; валідація; вхід і вихід; неправильний пароль; захищені
сторінки; список користувачів; зміна меню; редірект авторизованих.

Зміна `User`: пароль тепер bcrypt (раніше werkzeug). Схема таблиці та міграції не змінювались (поле `password` — `String(255)`).

## Скріншоти (`screenshots/`)

| Файл | Що показує |
|---|---|
| `01_register_form` | форма реєстрації |
| `02_register_success` | успішна реєстрація (flash + сторінка входу) |
| `03_register_user_exists` | користувач уже існує (username та email) |
| `04_register_validation_errors` | помилки валідації (email, довжина пароля, паролі не збігаються) |
| `05_login_required_redirect` | `/users` без входу → `/login?next=…` |
| `06_login_wrong_password` | невірний пароль |
| `07_account_after_login` | `/account` після входу, меню «Профіль / Вихід» |
| `08_users_list` | список користувачів і кількість |
| `09_register_redirects_to_account` | авторизований на `/register` потрапляє на `/account` |
| `10_after_logout` | після виходу меню знову «Реєстрація / Вхід» |

Відтворити: `python scripts/make_screenshots.py` (Playwright + Edge, тимчасова БД, сервер на :5059).

Скріншот пункту 2 завдання (хеш пароля у `flask shell`) не знімався окремо; хеш перевіряється в `tests/test_auth.py`.
