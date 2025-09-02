import shutil
import os
from datetime import datetime
from pathlib import Path

from database.db_setup import DatabaseSetup


def criar_backup(dest_dir=None, nome_prefixo='backup'):
    """Cria uma cópia do arquivo de banco de dados num diretório de destino.

    - dest_dir: diretório onde salvar o backup (se None, usa um subdiretório 'backups' ao lado do DB)
    - nome_prefixo: prefixo para o arquivo de backup

    Retorna o caminho absoluto do arquivo criado.
    """
    db_path = DatabaseSetup.get_database_path()
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")

    if dest_dir is None:
        dest_dir = os.path.join(os.path.dirname(db_path), 'backups')
    os.makedirs(dest_dir, exist_ok=True)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = f"{nome_prefixo}_{ts}.db"
    dest_path = os.path.join(dest_dir, base_name)

    shutil.copy2(db_path, dest_path)
    return os.path.abspath(dest_path)
