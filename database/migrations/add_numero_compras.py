"""
Migração para adicionar campo numero_compras na tabela clientes
"""

import sqlite3
import os


def migrate_add_numero_compras(db_connection):
    """
    Adiciona coluna numero_compras na tabela clientes e calcula o valor inicial
    baseado nos pedidos existentes.
    
    Args:
        db_connection: Conexão SQLite já aberta (sqlite3.Connection)
    
    Returns:
        bool: True se sucesso, False se erro
    """
    if db_connection is None:
        print("❌ Conexão com banco de dados inválida")
        return False
    
    try:
        cursor = db_connection.cursor()
        
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(clientes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'numero_compras' not in columns:
            # Adicionar coluna numero_compras com valor padrão 0
            print("📝 Adicionando coluna numero_compras...")
            cursor.execute("ALTER TABLE clientes ADD COLUMN numero_compras INTEGER DEFAULT 0")
        else:
            print("ℹ️ Coluna numero_compras já existe, recalculando valores...")
        
        # Calcular número de compras para cada cliente baseado nos pedidos existentes
        print("🔢 Calculando número de compras por cliente...")
        
        # Verificar se a coluna deleted_at existe em ordem_servico
        cursor.execute("PRAGMA table_info(ordem_servico)")
        ordem_columns = [col[1] for col in cursor.fetchall()]
        has_deleted_at = 'deleted_at' in ordem_columns
        
        # Considerar apenas pedidos do último ano, não cancelados nem deletados
        from datetime import datetime, timedelta
        hoje = datetime.now()
        um_ano_atras = (hoje - timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
        hoje_str = hoje.strftime('%Y-%m-%d %H:%M:%S')
        # Detectar coluna de data válida
        data_col = None
        for candidate in ['data_criacao', 'data_emissao', 'created_at', 'data']:
            if candidate in ordem_columns:
                data_col = candidate
                break
        if not data_col:
            raise Exception('Nenhuma coluna de data encontrada em ordem_servico')
        # Só filtrar por status se a coluna existir
        has_status = 'status' in ordem_columns
        if has_deleted_at and has_status:
            deleted_filter = "AND ordem_servico.deleted_at IS NULL AND (ordem_servico.status IS NULL OR ordem_servico.status NOT IN ('cancelado', 'cancelada'))"
        elif has_deleted_at:
            deleted_filter = "AND ordem_servico.deleted_at IS NULL"
        elif has_status:
            deleted_filter = "AND (ordem_servico.status IS NULL OR ordem_servico.status NOT IN ('cancelado', 'cancelada'))"
        else:
            deleted_filter = ""

        # Atualizar baseado em CPF (normalizado - sem pontuação)
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

        # Atualizar baseado em CNPJ (normalizado - sem pontuação)
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
        
        # Mostrar estatísticas
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE numero_compras > 0")
        count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(numero_compras) FROM clientes")
        total = cursor.fetchone()[0] or 0
        
        print(f"✅ Migração numero_compras concluída!")
        print(f"   📊 {count} clientes com compras registradas")
        print(f"   🛒 {total} compras totais contabilizadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False


if __name__ == "__main__":
    # Script standalone para testar (usa banco padrão)
    import sys
    base_path = os.path.expanduser("~/Documents")
    db_dir = os.path.join(base_path, "OrdemServico")
    db_path = os.path.join(db_dir, "ordem_servico.db")
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        sys.exit(1)
    
    print("🔄 Iniciando migração: adicionar numero_compras")
    print("=" * 60)
    
    conn = sqlite3.connect(db_path)
    try:
        migrate_add_numero_compras(conn)
    finally:
        conn.close()
