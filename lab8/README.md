# Лабораторна робота 8 — ORM. Зв'язки (Flask, SQLAlchemy 2.0)

Продовження проєкту лаби 6 (блог із постами). Додано `User` (1:N з `Post`), `Tag` (M:N з `Post`
через `post_tags`), вибір автора й тегів у формі, оптимізацію завантаження зв'язків.

## Запуск

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\flask db upgrade
.venv\Scripts\flask run                       # http://127.0.0.1:5000/post
.venv\Scripts\python -m unittest discover -s tests -t . -v
```

## Модель даних

| Таблиця | Поля / зв'язки |
|---|---|
| `users` | `id`, `username` (unique), `email` (unique), `password` (хеш); `posts` (1:N, `cascade="all, delete-orphan"`) |
| `post` | колишнє `author` замінено на `user_id` (FK → `users.id`, nullable) + `user`; `tags` (M:N) |
| `tags` | `id`, `name` (unique); `posts` (M:N) |
| `post_tags` | асоціативна таблиця: `post_id`, `tag_id` (складений PK) |

`user_id` nullable: пости, створені до появи користувачів, лишаються без автора (крок 6 призначає їм автора).
Назви обмежень задає `naming_convention` у `Base.metadata`, тому міграції з FK у SQLite працюють без правок.

## Міграції

| Ревізія | Що |
|---|---|
| `c6118fd16140` Add User | таблиця `users` |
| `3e2b6abe83dc` Replace Post.author with user_id | `post.user_id` + FK, видалено `post.author` |
| `6fee6f7f60e3` Add Tag and post_tags | `tags`, `post_tags` |

## Пункт 13 — оптимізація завантаження (7 дописів, 2 автори, 3 теги)

Запуск: `python scripts/eager_demo.py lazy` та `python scripts/eager_demo.py eager` (кожен у новому процесі,
SQL-журнал через `SQLALCHEMY_ECHO`, рахуються лише SELECT під час вибірки та циклу).

| Варіант запиту | Кількість дописів | Кількість SELECT |
|---|---|---|
| Без `.options()` | 7 | 10 (1 + 2 автори + 7 запитів тегів) |
| Із `joinedload()` та `selectinload()` | 7 | 2 (1 JOIN з авторами + 1 `IN` по тегах) |

Без `.options()` виникає проблема N+1: автор вантажиться ледачо (кожен унікальний автор — окремий SELECT, повторні
беруться з identity map), теги — окремим SELECT на кожен допис. `joinedload(Post.user)` підтягує автора тим самим
запитом через `LEFT OUTER JOIN`, `selectinload(Post.tags)` — одним `SELECT ... WHERE post_id IN (...)`.
У застосунку така вибірка вже використана у списку постів (`all_posts`).

## Скріншоти (`screenshots/`)

| Файл | Пункт |
|---|---|
| `02_users_table`, `04_post_table` | 2, 4 — таблиці `users` та `post` після міграцій |
| `05_shell_add_users`, `06_shell_assign_posts`, `07_shell_user_posts` | 5, 6, 7 |
| `08_ui_author_select` | 8 — список авторів із БД у формі |
| `09_tags_tables`, `10_shell_tags` | 9, 10 |
| `11_ui_tags_select`, `12_ui_post_detail_tags`, `12_ui_posts_list_tags` | 11, 12 |
| `13a_without_options`, `13b_joinedload_selectinload` | 13 — код, результат, SQL-журнал |
| `14_unit_tests`, `15_db_posts_authors_tags` | тести (35 OK), підсумкові дані |

Скрипти: `scripts/term.py` + `scripts/render.py` (термінал), `scripts/make_screenshots.py` (UI, Playwright + Edge).
