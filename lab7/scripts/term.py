"""Допоміжний інструмент для звіту: дописує до транскрипту термінала.

  term.py OUT.txt cmd flask db init        -> виконує команду, дописує "PS> cmd" та вивід
  term.py OUT.txt shell "stmt1" "stmt2"    -> сесія як у `flask shell` (>>> рядки та результат)
  term.py OUT.txt sqlite "SELECT ..."      -> запит до instance/data.sqlite
"""
import code
import contextlib
import io
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT = r"(.venv) PS C:\Python\lab6> "
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def append(out, text):
    with open(out, "a", encoding="utf-8") as f:
        f.write(text)


def run_cmd(out, args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", NO_COLOR="1")
    shown = " ".join(f'"{a}"' if " " in a else a for a in args)
    exe = [sys.executable, "-m", "flask"] + args[1:] if args[0] == "flask" else args
    r = subprocess.run(exe, capture_output=True, text=True, encoding="utf-8", env=env, cwd=ROOT)
    append(out, f"{PROMPT}{shown}\n{r.stdout}{r.stderr}")
    return r.returncode


def run_shell(out, stmts):
    from app import create_app

    app = create_app("development")
    append(out, f"{PROMPT}flask shell\n")
    with app.app_context():
        console = code.InteractiveConsole({"app": app})
        for stmt in stmts:
            append(out, f">>> {stmt}\n")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                console.push(stmt)
            append(out, buf.getvalue())
        append(out, ">>> exit()\n")


def run_sqlite(out, query):
    append(out, f"{PROMPT}sqlite3 instance/data.sqlite \"{query}\"\n")
    con = sqlite3.connect(ROOT / "instance" / "data.sqlite")
    cur = con.execute(query)
    for row in cur.fetchall():
        append(out, "|".join(str(c) for c in row) + "\n")
    con.close()


if __name__ == "__main__":
    out, mode, *rest = sys.argv[1:]
    if mode == "cmd":
        sys.exit(run_cmd(out, rest))
    elif mode == "shell":
        run_shell(out, rest)
    elif mode == "sqlite":
        run_sqlite(out, rest[0])
