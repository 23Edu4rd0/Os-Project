import shutil
import os
from pathlib import Path
from database.db_setup import DatabaseSetup


def restaurar_backup(backup_file_path):
    """Restaura o banco de dados atual a partir de um arquivo de backup.

    - backup_file_path: caminho para o arquivo .db de backup.
    - Faz `copy2` para substituir o arquivo de DB atual.

    Retorna True em sucesso.
    """
    db_path = DatabaseSetup.get_database_path()
    if not os.path.exists(backup_file_path):
        raise FileNotFoundError(f"Backup file not found: {backup_file_path}")

    # realizar cópia de segurança do DB atual antes de sobrescrever
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    safe_copy = os.path.join(backup_dir, 'pre_restore_' + Path(db_path).name)
    shutil.copy2(db_path, safe_copy)

    shutil.copy2(backup_file_path, db_path)
    return True


def substituir_por_arquivo(source_db_path):
    """Substitui o DB atual por outro arquivo de banco (por exemplo upload de outro dispositivo).

    - Faz cópia do arquivo source_db_path sobre o arquivo de DB atual, após criar uma cópia de segurança.
    - Retorna True em sucesso.
    """
    return restaurar_backup(source_db_path)
