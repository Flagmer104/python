"""Допоміжний інструмент для звіту: дописує до транскрипту термінала.

  term.py OUT.txt cmd flask db history      -> виконує команду, дописує "PS> cmd" та вивід
  term.py OUT.txt schema                    -> схема таблиць (CREATE TABLE з instance/data.sqlite)
  term.py OUT.txt sqlite "SELECT ..."       -> запит до instance/data.sqlite
"""
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT = r"(.venv) PS C:\Python\lab7> "
DB = ROOT / "instance" / "data.sqlite"
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


def run_schema(out):
    """Еквівалент `sqlite3 data.sqlite .schema` + PRAGMA table_info для кожної таблиці."""
    con = sqlite3.connect(DB)
    append(out, f"{PROMPT}sqlite3 instance/data.sqlite .schema\n")
    rows = con.execute(
        "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    for (sql,) in rows:
        append(out, sql + ";\n\n")
    for table in ("categories", "products"):
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
    widths = [max(len(h), *(len(r[i]) for r in rows)) for i, h in enumerate(header)]
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
    elif mode == "schema":
        run_schema(out)
    elif mode == "sqlite":
        run_sqlite(out, rest[0])
