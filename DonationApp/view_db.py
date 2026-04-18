import sqlite3
import os
import sys

def main():
    # Allow optional DB path via command-line, prefer instance/donations.db if present
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        base = os.path.dirname(__file__)
        inst = os.path.join(base, 'instance', 'donations.db')
        default = os.path.join(base, 'donations.db')
        if os.path.exists(inst):
            db_path = inst
        else:
            db_path = default
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [r[0] for r in cur.fetchall()]
    print("Tables:", tables)

    for t in tables:
        print(f"\n--- {t} ---")
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})")]
        print("Columns:", cols)
        cur.execute(f"SELECT * FROM {t} LIMIT 100")
        rows = cur.fetchall()
        if not rows:
            print("(no rows)")
            continue
        for row in rows:
            # Print row as dict for clarity
            print(dict(zip(cols, row)))

    conn.close()

if __name__ == '__main__':
    main()
