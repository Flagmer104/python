"""Допоміжний інструмент для звіту: дописує до транскрипту термінала.

  term.py OUT.txt cmd flask db upgrade     -> виконує команду, дописує "PS> cmd" та вивід
  term.py OUT.txt shell "stmt1" "stmt2"    -> сесія як у `flask shell` (>>> рядки та результат)
  term.py OUT.txt schema users post        -> CREATE TABLE та PRAGMA table_info з instance/data.sqlite
  term.py OUT.txt sqlite "SELECT ..."      -> запит до instance/data.sqlite у вигляді таблиці
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
PROMPT = r"(.venv) PS C:\Python\lab8> "
DB = ROOT / "instance" / "data.sqlite"
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def append(out, text):
    with open(out, "a", encoding="utf-8") as f:
        f.write(text)


def run_cmd(out, args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", NO_COLOR="1")
    shown = " ".join(f'"{a}"' if " " in a else a for a in args)
    if args[0] == "flask":
        exe = [sys.executable, "-m", "flask"] + args[1:]
    elif args[0] == "python":
        exe = [sys.executable] + args[1:]
    else:
        exe = args
    r = subprocess.run(exe, capture_output=True, text=True, encoding="utf-8", env=env, cwd=ROOT)
    append(out, f"{PROMPT}{shown}\n{r.stdout}{r.stderr}")
    return r.returncode


def run_shell(out, stmts):
    """Еквівалент `flask shell`: app context + InteractiveConsole. Багаторядковий блок завершується порожнім рядком."""
    from app import create_app

    app = create_app("development")
    append(out, f"{PROMPT}flask shell\n")
    with app.app_context():
        console = code.InteractiveConsole({"app": app})
        for stmt in stmts:
            lines = stmt.split("\n")
            for i, line in enumerate(lines):
                append(out, (">>> " if i == 0 else "... ") + line + "\n")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    console.push(line)
                append(out, buf.getvalue())
            if len(lines) > 1:
                append(out, "... \n")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    console.push("")
                append(out, buf.getvalue())
        append(out, ">>> exit()\n")


def run_schema(out, tables):
    con = sqlite3.connect(DB)
    for table in tables:
        sql = con.execute("SELECT sql FROM sqlite_master WHERE name = ?", (table,)).fetchone()[0]
        append(out, f"{PROMPT}sqlite3 instance/data.sqlite \".schema {table}\"\n{sql};\n\n")
    for table in tables:
        append(out, f"{PROMPT}sqlite3 instance/data.sqlite \"PRAGMA table_info({table});\"\n")
        for cid, name, ctype, notnull, dflt, pk in con.execute(f"PRAGMA table_info({table})"):
            append(out, f"{cid}|{name}|{ctype}|{notnull}|{dflt if dflt is not None else ''}|{pk}\n")
        append(out, "\n")
    con.close()


def run_sqlite(out, query):
    append(out, f"{PROMPT}sqlite3 -header -column instance/data.sqlite \"{query}\"\n")
    con = sqlite3.connect(DB)
    cur = con.execute(query)
    header = [d[0] for d in cur.description]
    rows = [[("" if c is None else str(c)) for c in row] for row in cur.fetchall()]
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h) for i, h in enumerate(header)]
    append(out, "  ".join(h.ljust(w) for h, w in zip(header, widths)) + "\n")
    append(out, "  ".join("-" * w for w in widths) + "\n")
    for r in rows:
        append(out, "  ".join(c.ljust(w) for c, w in zip(r, widths)) + "\n")
    append(out, "\n")
    con.close()


if __name__ == "__main__":
    out, mode, *rest = sys.argv[1:]
    if mode == "cmd":
        sys.exit(run_cmd(out, rest))
    elif mode == "shell":
        run_shell(out, rest)
    elif mode == "schema":
        run_schema(out, rest)
    elif mode == "sqlite":
        run_sqlite(out, rest[0])
