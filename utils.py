import uuid
import json
from datetime import datetime
from db import get_conn

def now_iso():
    return datetime.utcnow().isoformat()

def gen_id():
    return str(uuid.uuid4())

def log_action(username, action, target_table, target_id, details=""):
    if isinstance(details, (dict, list)):
        try:
            details = json.dumps(details, ensure_ascii=False)
        except Exception:
            details = str(details)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO action_logs(id,username,action,target_table,target_id,details,created_at) VALUES (?,?,?,?,?,?,?)",
        (gen_id(), username, action, target_table, target_id, details, now_iso())
    )
    conn.commit()
    conn.close()
