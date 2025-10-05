"""
Automatic synchronization system for numero_compras.
Calculates and updates the purchase counter every time the app starts.
All user-facing messages are in Portuguese. All comments, docstrings, and logs are in English.
"""

import sqlite3
import os


def sync_numero_compras(db_path):
    """
    Synchronize the numero_compras field for all clients.
    - Adds the column if it does not exist
    - Recalculates values based on active orders (not soft-deleted)
    - Works with any database
    Args:
        db_path: Full path to the database file
    """
    if not os.path.exists(db_path):
        print(f"⚠️ Banco não encontrado: {db_path}")  # User-facing message in Portuguese
        print(f"Database not found: {db_path}")  # Log in English
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Check/Add numero_compras column
        cursor.execute("PRAGMA table_info(clientes)")
        colunas = [col[1] for col in cursor.fetchall()]
        if 'numero_compras' not in colunas:
            cursor.execute("ALTER TABLE clientes ADD COLUMN numero_compras INTEGER DEFAULT 0")
            conn.commit()
            print("➕ Coluna numero_compras adicionada")  # User-facing message in Portuguese
            print("numero_compras column added")  # Log in English

        # 2. Check if deleted_at exists in ordem_servico
        cursor.execute("PRAGMA table_info(ordem_servico)")
        colunas_os = [col[1] for col in cursor.fetchall()]
        has_deleted_at = 'deleted_at' in colunas_os

        # 3. Reset counters
        cursor.execute("UPDATE clientes SET numero_compras = 0")

        # 4. Recalculate by CPF (normalized)
        filtro_deleted = "AND ordem_servico.deleted_at IS NULL" if has_deleted_at else ""
        cursor.execute(f"""
            UPDATE clientes 
            SET numero_compras = (
                SELECT COUNT(*) 
                FROM ordem_servico 
                WHERE replace(replace(replace(ordem_servico.cpf_cliente, '.', ''), '-', ''), ' ', '') = 
                      replace(replace(replace(clientes.cpf, '.', ''), '-', ''), ' ', '')
                {filtro_deleted}
            )
            WHERE clientes.cpf IS NOT NULL AND clientes.cpf != ''
        """)

        # 5. Recalculate by CNPJ (normalized)
        cursor.execute(f"""
            UPDATE clientes 
            SET numero_compras = (
                SELECT COUNT(*) 
                FROM ordem_servico 
                WHERE replace(replace(replace(replace(ordem_servico.cpf_cliente, '.', ''), '/', ''), '-', ''), ' ', '') = 
                      replace(replace(replace(replace(clientes.cnpj, '.', ''), '/', ''), '-', ''), ' ', '')
                {filtro_deleted}
            )
            WHERE clientes.cnpj IS NOT NULL AND clientes.cnpj != ''
        """)

        conn.commit()

        # Report
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE numero_compras > 0")
        clientes_com_compras = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(numero_compras) FROM clientes")
        total_compras = cursor.fetchone()[0] or 0
        print(f"✅ Compras sincronizadas: {clientes_com_compras} clientes, {total_compras} compras")  # User-facing message in Portuguese
        print(f"Purchases synchronized: {clientes_com_compras} clients, {total_compras} purchases")  # Log in English
    except Exception as e:
        print(f"❌ Erro na sincronização: {e}")  # User-facing message in Portuguese
        print(f"Error during synchronization: {e}")  # Log in English
        conn.rollback()
    finally:
        conn.close()
