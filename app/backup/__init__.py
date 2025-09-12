"""Área de backup modular.

Fornece utilitários para:
- criar backup do arquivo de banco de dados
- restaurar um backup (substituir o DB atual por um arquivo enviado)
- substituir o DB por um arquivo externo (import)
- excluir todos os dados do banco (cautela)
- excluir registros anteriores a X dias/anos (por tabela)

Design:
Cada função é pequena e testável; operações destrutivas exigem confirmação no nível da UI.
"""

from .backup_file import criar_backup
from .restore_file import restaurar_backup, substituir_por_arquivo
from .cleanup import apagar_tudo, apagar_anteriores

__all__ = [
    'criar_backup', 'restaurar_backup', 'substituir_por_arquivo', 'apagar_tudo', 'apagar_anteriores'
]
