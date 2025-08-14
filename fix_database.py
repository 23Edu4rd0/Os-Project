"""
Script para recriar/verificar o banco de dados
"""

import os
import sqlite3
from database.db_manager import db_manager

def verificar_e_recriar_banco():
    """Verifica e recria o banco se necessário"""
    
    # Remover arquivo de banco antigo se estiver corrompido
    if os.path.exists("ordens_servico.db"):
        try:
            conn = sqlite3.connect("ordens_servico.db")
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            conn.close()
            print("✅ Banco existente está OK")
        except Exception as e:
            print(f"❌ Banco corrompido: {e}")
            print("🔄 Removendo arquivo corrompido...")
            os.remove("ordens_servico.db")
    
    # Forçar criação do banco através do db_manager
    try:
        print("🔄 Inicializando banco de dados...")
        db_manager._conectar()
        db_manager._criar_tabelas()
        
        # Testar com uma consulta simples
        db_manager.cursor.execute("SELECT COUNT(*) FROM ordem_servico")
        count = db_manager.cursor.fetchone()[0]
        print(f"✅ Banco criado com sucesso! Ordens existentes: {count}")
        
        # Testar clientes
        db_manager.cursor.execute("SELECT COUNT(*) FROM clientes")
        count_clientes = db_manager.cursor.fetchone()[0]
        print(f"✅ Clientes na base: {count_clientes}")
        
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
        return False
        
    return True

if __name__ == "__main__":
    verificar_e_recriar_banco()
