"""
Sistema de sincronização automática de numero_compras.
Calcula e atualiza o contador de compras sempre que o app inicia.
"""

import sqlite3
import os


def sync_numero_compras(db_path):
    """
    Sincroniza o campo numero_compras para todos os clientes.
    - Adiciona a coluna se não existir
    - Recalcula valores baseado nos pedidos ativos (não soft-deleted)
    - Funciona com qualquer banco de dados
    
    Args:
        db_path: Caminho completo para o arquivo do banco de dados
    """
    if not os.path.exists(db_path):
        print(f"⚠️ Banco não encontrado: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar/Adicionar coluna numero_compras
        cursor.execute("PRAGMA table_info(clientes)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'numero_compras' not in colunas:
            cursor.execute("ALTER TABLE clientes ADD COLUMN numero_compras INTEGER DEFAULT 0")
            conn.commit()
            print("➕ Coluna numero_compras adicionada")
        
        # 2. Verificar se deleted_at existe em ordem_servico
        cursor.execute("PRAGMA table_info(ordem_servico)")
        colunas_os = [col[1] for col in cursor.fetchall()]
        has_deleted_at = 'deleted_at' in colunas_os
        
        # 3. Resetar contadores
        cursor.execute("UPDATE clientes SET numero_compras = 0")
        
        # 4. Recalcular por CPF (normalizado)
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
        
        # 5. Recalcular por CNPJ (normalizado)
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
        
        # Relatório
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE numero_compras > 0")
        clientes_com_compras = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(numero_compras) FROM clientes")
        total_compras = cursor.fetchone()[0] or 0
        
        print(f"✅ Compras sincronizadas: {clientes_com_compras} clientes, {total_compras} compras")
        
    except Exception as e:
        print(f"❌ Erro na sincronização: {e}")
        conn.rollback()
    finally:
        conn.close()
