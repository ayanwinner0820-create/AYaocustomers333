import sqlite3
from typing import Optional
from config import DB_FILE

def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        language TEXT DEFAULT '中文'
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id TEXT PRIMARY KEY,
        name TEXT,
        whatsapp TEXT,
        line TEXT,
        telegram TEXT,
        country TEXT,
        city TEXT,
        age INTEGER,
        job TEXT,
        income TEXT,
        marital_status TEXT,
        deal_amount REAL,
        level TEXT,
        progress TEXT,
        main_owner TEXT,
        assistant TEXT,
        notes TEXT,
        created_at TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS followups (
        id TEXT PRIMARY KEY,
        customer_id TEXT,
        author TEXT,
        note TEXT,
        next_action TEXT,
        created_at TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS action_logs (
        id TEXT PRIMARY KEY,
        username TEXT,
        action TEXT,
        target_table TEXT,
        target_id TEXT,
        details TEXT,
        created_at TEXT
    )""")

    # default admin
    cur.execute("SELECT 1 FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users(username,password,role,language) VALUES(?,?,?,?)",
            ("admin", "admin123", "admin", "中文")
        )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
