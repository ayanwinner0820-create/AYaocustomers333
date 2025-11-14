from db import get_conn
from utils import gen_id, log_action
import pandas as pd

def authenticate(username: str, password: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT username,role,language FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def list_users():
    conn = get_conn()
    df = pd.read_sql_query("SELECT username, role, language FROM users", conn)
    conn.close()
    return df

def add_user(username: str, password: str, role: str='user', language: str='中文'):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO users(username,password,role,language) VALUES(?,?,?,?)",
    (username, password, role, language))
    conn.commit()
    conn.close()
    log_action('system', 'add_user', 'users', username, {'role': role})

def reset_password(username: str, new_password: str):
    conn = get_conn()
    conn.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()
    log_action('system', 'reset_password', 'users', username, '')

def delete_user(username: str):
    conn = get_conn()
    conn.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    conn.close()
    log_action('system', 'delete_user', 'users', username, '')
