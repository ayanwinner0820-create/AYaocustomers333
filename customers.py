from db import get_conn
from utils import gen_id, now_iso, log_action
import pandas as pd

def insert_customer(rec: dict) -> str:
    conn = get_conn()
    cur = conn.cursor()
    cid = gen_id()
    now = now_iso()
    cur.execute(
        "INSERT INTO customers(id,name,whatsapp,line,telegram,country,city,age,job,income,marital_status,deal_amount,level,progress,main_owner,assistant,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (cid, rec.get('name'), rec.get('whatsapp'), rec.get('line'), rec.get('telegram'),
         rec.get('country'), rec.get('city'), rec.get('age'), rec.get('job'), rec.get('income'),
         rec.get('marital_status'), rec.get('deal_amount'), rec.get('level'), rec.get('progress'),
         rec.get('main_owner'), rec.get('assistant'), rec.get('notes'), now)
    )
    conn.commit()
    conn.close()
    log_action(rec.get('operator','system'), 'add_customer', 'customers', cid, rec)
    return cid

def update_customer(cid: str, updates: dict, operator: str='system'):
    conn = get_conn()
    cur = conn.cursor()
    keys = ','.join([f"{k}=?" for k in updates.keys()])
    params = list(updates.values()) + [cid]
    cur.execute(f"UPDATE customers SET {keys} WHERE id=?", params)
    conn.commit()
    conn.close()
    log_action(operator, 'update_customer', 'customers', cid, updates)

def delete_customer(cid: str, operator: str='system'):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM customers WHERE id=?", (cid,))
    r = cur.fetchone()
    name = r['name'] if r else ''
    cur.execute("DELETE FROM customers WHERE id=?", (cid,))
    conn.commit()
    conn.close()
    log_action(operator, 'delete_customer', 'customers', cid, {'name': name})

def list_customers_df() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM customers ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_customer(cid: str) -> dict:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers WHERE id=?", (cid,))
    r = cur.fetchone()
    conn.close()
    return dict(r) if r else None

def add_followup(customer_id: str, author: str, note: str, next_action: str=''):
    conn = get_conn()
    cur = conn.cursor()
    fid = gen_id()
    cur.execute("INSERT INTO followups(id,customer_id,author,note,next_action,created_at) VALUES(?,?,?,?,?,?)",
                (fid, customer_id, author, note, next_action, now_iso()))
    conn.commit()
    conn.close()
    log_action(author, 'add_followup', 'followups', fid, {'customer_id': customer_id, 'note': note})

def list_followups_df(customer_id: str):
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM followups WHERE customer_id=? ORDER BY created_at DESC",
                           conn, params=(customer_id,))
    conn.close()
    return df
