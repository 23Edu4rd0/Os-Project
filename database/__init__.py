"""
Módulo de inicialização do banco de dados.
"""

from .db_manager import DatabaseManager

# Criar instância singleton
db_manager = DatabaseManager()
