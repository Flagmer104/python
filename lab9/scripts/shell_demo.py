"""Транскрипт сесії `flask shell` для п. 2 лаби 9: користувач із bcrypt-хешем пароля.

Виконує команди в контексті застосунку (тимчасова БД в пам'яті) і друкує їх разом з виводом,
як у інтерактивній консолі. Далі: python scripts/render.py transcript.txt screenshots/00_shell_hashed_password.png
"""
import code
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import bcrypt, create_app, db  # noqa: E402
from app.posts.models import User  # noqa: E402

app = create_app("testing")
bcrypt._log_rounds = 12  # як у dev/prod (у testing раунди зменшені для швидкості)
COMMANDS = [
    "from app import db, bcrypt",
    "from app.posts.models import User",
    "u = User(username='vlad', email='vlad@example.com')",
    "u.set_password('secret12')",
    "db.session.add(u); db.session.commit()",
    "u.password",
    "u.password == 'secret12'",
    "bcrypt.check_password_hash(u.password, 'secret12')",
    "bcrypt.check_password_hash(u.password, 'wrong')",
    "u.check_password('secret12')",
]

out = io.StringIO()
with app.app_context():
    db.create_all()
    console = code.InteractiveConsole({"db": db, "bcrypt": bcrypt, "User": User})
    out.write("(.venv) PS C:\\Python\\lab9> flask shell\n")
    for cmd in COMMANDS:
        out.write(f">>> {cmd}\n")
        buf = io.StringIO()
        with redirect_stdout(buf):
            console.push(cmd)
        out.write(buf.getvalue())
    # InteractiveConsole друкує значення виразів у sys.stdout через displayhook
    db.session.remove()
    db.drop_all()
print(out.getvalue())
