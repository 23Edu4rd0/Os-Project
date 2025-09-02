"""
Gerador de números de OS
"""
import sqlite3
from database.db_manager import DatabaseManager

class Contador:
    """Classe para gerar números sequenciais de OS"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def get_proximo_numero(self):
        """Gera o próximo número de OS"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Buscar o maior número de OS existente (tabela ordem_servico)
            cursor.execute("SELECT MAX(numero_os) FROM ordem_servico")
            resultado = cursor.fetchone()
            max_num = resultado[0] if resultado and resultado[0] is not None else 0
            proximo_numero = int(max_num) + 1
            
            conn.close()
            return proximo_numero
            
        except Exception as e:
            print(f"Erro ao gerar número de OS: {e}")
            return 1
