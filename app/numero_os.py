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
            
            # Buscar o maior número de OS existente
            cursor.execute("SELECT MAX(numero_os) FROM pedidos")
            resultado = cursor.fetchone()
            
            if resultado[0] is None:
                proximo_numero = 1
            else:
                proximo_numero = resultado[0] + 1
            
            conn.close()
            return proximo_numero
            
        except Exception as e:
            print(f"Erro ao gerar número de OS: {e}")
            return 1
