import json
from config import LANG_OPTIONS

TRANS_FILE = "translations.json"

DEFAULT = {
"中文": {"app_title":"氯雷他定用户统计"},
"English": {"app_title":"Loratadine Customer Dashboard"}
}

def load_translations():
    try:
        with open(TRANS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT

def save_translations(data: dict):
    with open(TRANS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
