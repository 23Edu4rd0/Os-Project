import json
from pathlib import Path

STATUSES_FILE = Path(__file__).resolve().parents[1] / 'data' / 'statuses.json'
DEFAULT_STATUSES = ["em produção", "pronto", "enviado", "entregue", "cancelado"]


def _ensure_file():
    STATUSES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not STATUSES_FILE.exists():
        with open(STATUSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_STATUSES, f, ensure_ascii=False, indent=2)


def load_statuses():
    try:
        _ensure_file()
        with open(STATUSES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                return [str(x) for x in data]
    except Exception:
        pass
    return DEFAULT_STATUSES.copy()


def save_statuses(statuses):
    try:
        _ensure_file()
        with open(STATUSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(statuses), f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
