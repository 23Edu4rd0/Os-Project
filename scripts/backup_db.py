"""
Script simples para backup do arquivo SQLite usado pelo projeto.
Uso:
    python scripts/backup_db.py --out backups/db_backup_YYYYmmdd_HHMMSS.db

Ele usa DatabaseManager para descobrir o caminho do DB e copia o arquivo.
"""
import os
import shutil
import argparse
from datetime import datetime
from database.db_manager import DatabaseManager


def backup(out_path: str = None):
    db = DatabaseManager()
    src = db.db_path
    if not os.path.exists(src):
        print(f"Arquivo DB não encontrado: {src}")
        return False

    if not out_path:
        base = os.path.join('backups', f'db_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        out_path = base
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    shutil.copy2(src, out_path)
    print(f'Backup criado: {out_path}')
    return True

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=str, default=None, help='Caminho do arquivo de backup')
    args = p.parse_args()
    backup(args.out)
