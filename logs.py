from db import get_conn
import pandas as pd

def recent_actions(limit: int=500) -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM action_logs ORDER BY created_at DESC LIMIT ?",
                           conn, params=(limit,))
    conn.close()
    return df
