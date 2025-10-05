"""
Migration to add the numero_compras field to the clientes table.
All user-facing messages are in Portuguese. All comments, docstrings, and logs are in English.
"""

import sqlite3
import os
from datetime import datetime, timedelta


def migrate_add_numero_compras(db_connection):
    """
    Adds the numero_compras column to the clientes table and calculates the initial value
    based on existing orders.
    Args:
        db_connection: Open SQLite connection (sqlite3.Connection)
    Returns:
        bool: True if successful, False if error
    """
    if db_connection is None:
        print("❌ Conexão com banco de dados inválida")  # User-facing message in Portuguese
        print("Invalid database connection")  # Log in English
        return False
    
    try:
        cursor = db_connection.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(clientes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'numero_compras' not in columns:
            # Add numero_compras column with default value 0
            print("📝 Adicionando coluna numero_compras...")  # User-facing message in Portuguese
            print("Adding numero_compras column...")  # Log in English
            cursor.execute("ALTER TABLE clientes ADD COLUMN numero_compras INTEGER DEFAULT 0")
        else:
            print("ℹ️ Coluna numero_compras já existe, recalculando valores...")  # User-facing message in Portuguese
            print("numero_compras column already exists, recalculating values...")  # Log in English
        
        # Calculate number of purchases per client based on existing orders
        print("🔢 Calculando número de compras por cliente...")  # User-facing message in Portuguese
        print("Calculating number of purchases per client...")  # Log in English
        
        # Check if ordem_servico table exists before proceeding
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ordem_servico'")
        if not cursor.fetchone():
            raise Exception("Tabela 'ordem_servico' não existe no banco de dados")
        
        # Check if deleted_at column exists in ordem_servico
        cursor.execute("PRAGMA table_info(ordem_servico)")
        ordem_columns = [col[1] for col in cursor.fetchall()]
        has_deleted_at = 'deleted_at' in ordem_columns
        
        # Consider only orders from the last year, not canceled or deleted
        hoje = datetime.now()
        um_ano_atras = (hoje - timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
        hoje_str = hoje.strftime('%Y-%m-%d %H:%M:%S')
        
        # Detect valid date column
        data_col = None
        for candidate in ['data_criacao', 'data_emissao', 'created_at', 'data']:
            if candidate in ordem_columns:
                data_col = candidate
                break
        if not data_col:
            raise Exception('Nenhuma coluna de data encontrada em ordem_servico')
        
        # Only filter by status if column exists
        has_status = 'status' in ordem_columns
        if has_deleted_at and has_status:
            deleted_filter = "AND ordem_servico.deleted_at IS NULL AND (ordem_servico.status IS NULL OR ordem_servico.status NOT IN ('cancelado', 'cancelada'))"
        elif has_deleted_at:
            deleted_filter = "AND ordem_servico.deleted_at IS NULL"
        elif has_status:
            deleted_filter = "AND (ordem_servico.status IS NULL OR ordem_servico.status NOT IN ('cancelado', 'cancelada'))"
        else:
            deleted_filter = ""

        # Update based on CPF (normalized - no punctuation)
        cursor.execute(f"""
            UPDATE clientes 
            SET numero_compras = (
                SELECT COUNT(*) 
                FROM ordem_servico 
                WHERE replace(replace(replace(ordem_servico.cpf_cliente, '.', ''), '-', ''), ' ', '') = 
                      replace(replace(replace(clientes.cpf, '.', ''), '-', ''), ' ', '')
                  AND clientes.cpf IS NOT NULL
                  AND clientes.cpf != ''
                  AND ordem_servico.{data_col} >= ? AND ordem_servico.{data_col} <= ?
                  {deleted_filter}
            )
            WHERE clientes.cpf IS NOT NULL AND clientes.cpf != ''
        """, (um_ano_atras, hoje_str))

        # Update based on CNPJ (normalized - no punctuation)
        cursor.execute(f"""
            UPDATE clientes 
            SET numero_compras = (
                SELECT COUNT(*) 
                FROM ordem_servico 
                WHERE replace(replace(replace(replace(ordem_servico.cpf_cliente, '.', ''), '/', ''), '-', ''), ' ', '') = 
                      replace(replace(replace(replace(clientes.cnpj, '.', ''), '/', ''), '-', ''), ' ', '')
                  AND clientes.cnpj IS NOT NULL
                  AND clientes.cnpj != ''
                  AND ordem_servico.{data_col} >= ? AND ordem_servico.{data_col} <= ?
                  {deleted_filter}
            )
            WHERE clientes.cnpj IS NOT NULL 
              AND clientes.cnpj != ''
              AND numero_compras = 0
        """, (um_ano_atras, hoje_str))
        
        db_connection.commit()
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE numero_compras > 0")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(numero_compras) FROM clientes")
        total = cursor.fetchone()[0] or 0
        
        print(f"✅ Migração numero_compras concluída!")  # User-facing message in Portuguese
        print(f"   📊 {count} clientes com compras registradas")  # User-facing message in Portuguese
        print(f"   🛒 {total} compras totais contabilizadas")  # User-facing message in Portuguese
        print(f"numero_compras migration completed!")  # Log in English
        print(f"   {count} clients with registered purchases")  # Log in English
        print(f"   {total} total purchases counted")  # Log in English
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")  # User-facing message in Portuguese
        print(f"Error in migration: {e}")  # Log in English
        return False


if __name__ == "__main__":
    # Standalone script for testing (uses default database)
    import sys
    base_path = os.path.expanduser("~/Documents")
    db_dir = os.path.join(base_path, "OrdemServico")
    db_path = os.path.join(db_dir, "ordem_servico.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")  # User-facing message in Portuguese
        print(f"Database not found: {db_path}")  # Log in English
        sys.exit(1)
    
    print("🔄 Iniciando migração: adicionar numero_compras")  # User-facing message in Portuguese
    print("=" * 60)
    print("Starting migration: add numero_compras")  # Log in English
    
    conn = sqlite3.connect(db_path)
    try:
        migrate_add_numero_compras(conn)
    finally:
        conn.close()
