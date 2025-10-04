"""
Módulo de migrações de banco de dados
"""

from .add_numero_compras import migrate_add_numero_compras

__all__ = ['migrate_add_numero_compras']
