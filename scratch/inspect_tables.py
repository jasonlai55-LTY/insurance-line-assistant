import sqlite3

conn = sqlite3.connect('local_dev.db')
cursor = conn.cursor()
tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

for t in tables:
    cols = [row[1] for row in cursor.execute(f"PRAGMA table_info('{t}')").fetchall()]
    print(f"Table '{t}': {cols}")
