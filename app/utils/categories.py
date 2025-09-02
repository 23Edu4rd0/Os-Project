import json
import os
from pathlib import Path

CATEGORIES_FILE = Path(__file__).resolve().parents[1] / 'data' / 'categories.json'
DEFAULT_CATEGORIES = ["Agro", "Normal", "Outros"]


def _ensure_file():
    CATEGORIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CATEGORIES_FILE.exists():
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CATEGORIES, f, ensure_ascii=False, indent=2)


def load_categories():
    try:
        _ensure_file()
        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                return [str(x) for x in data]
    except Exception:
        pass
    return DEFAULT_CATEGORIES.copy()


def save_categories(cats):
    try:
        _ensure_file()
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(cats), f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
