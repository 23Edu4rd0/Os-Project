"""
Módulo para implementar Soft Delete no banco de dados.

Soft Delete: Em vez de deletar registros permanentemente, marca-os como deletados
com timestamp. Permite recuperação posterior.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional
from pathlib import Path
import os


class SoftDeleteManager:
    """Gerenciador de Soft Delete para todas as tabelas"""
    
    @staticmethod
    def get_database_path() -> str:
        """Retorna o caminho do banco de dados"""
        base_path = os.path.expanduser("~/Documents")
        db_dir = os.path.join(base_path, "OrdemServico")
        return os.path.join(db_dir, "ordem_servico.db")
    
    @staticmethod
    def migrate_add_deleted_at_columns():
        """
        Adiciona coluna deleted_at em todas as tabelas principais.
        Executa migração segura (ignora se coluna já existe).
        
        Returns:
            Tupla (sucesso: bool, mensagem: str)
        """
        db_path = SoftDeleteManager.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Lista de tabelas para adicionar soft delete
            tabelas = ['ordem_servico', 'clientes', 'produtos', 'gastos']
            
            for tabela in tabelas:
                try:
                    cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN deleted_at TEXT")
                    print(f"✅ Coluna deleted_at adicionada em {tabela}")
                except sqlite3.OperationalError as e:
                    if "duplicate column" in str(e).lower():
                        print(f"ℹ️ Coluna deleted_at já existe em {tabela}")
                    else:
                        print(f"⚠️ Erro ao adicionar coluna em {tabela}: {e}")
            
            # Criar índices para melhorar performance de filtros
            indices = [
                ("idx_ordem_servico_deleted", "ordem_servico", "deleted_at"),
                ("idx_clientes_deleted", "clientes", "deleted_at"),
                ("idx_produtos_deleted", "produtos", "deleted_at"),
                ("idx_gastos_deleted", "gastos", "deleted_at"),
            ]
            
            for idx_name, tabela, coluna in indices:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {tabela}({coluna})")
                    print(f"✅ Índice {idx_name} criado")
                except Exception as e:
                    print(f"⚠️ Erro ao criar índice {idx_name}: {e}")
            
            conn.commit()
            conn.close()
            
            return True, "Migração de Soft Delete concluída com sucesso!"
            
        except Exception as e:
            return False, f"Erro na migração: {str(e)}"
    
    # ===== SOFT DELETE FUNCTIONS =====
    
    @staticmethod
    def soft_delete_pedido(pedido_id: int) -> Tuple[bool, str]:
        """Marca um pedido como deletado"""
        return SoftDeleteManager._soft_delete('ordem_servico', 'id', pedido_id)
    
    @staticmethod
    def soft_delete_cliente(cliente_id: int) -> Tuple[bool, str]:
        """Marca um cliente como deletado"""
        return SoftDeleteManager._soft_delete('clientes', 'id', cliente_id)
    
    @staticmethod
    def soft_delete_produto(produto_id: int) -> Tuple[bool, str]:
        """Marca um produto como deletado"""
        return SoftDeleteManager._soft_delete('produtos', 'id', produto_id)
    
    @staticmethod
    def soft_delete_gasto(gasto_id: int) -> Tuple[bool, str]:
        """Marca um gasto como deletado"""
        return SoftDeleteManager._soft_delete('gastos', 'id', gasto_id)
    
    @staticmethod
    def _soft_delete(tabela: str, id_column: str, record_id: int) -> Tuple[bool, str]:
        """Implementação genérica de soft delete"""
        db_path = SoftDeleteManager.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar se registro existe e não está deletado
            cursor.execute(f"SELECT deleted_at FROM {tabela} WHERE {id_column} = ?", (record_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, f"Registro {record_id} não encontrado em {tabela}"
            
            if result[0]:  # Já está deletado
                conn.close()
                return False, f"Registro {record_id} já está deletado"
            
            # Marcar como deletado
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(f"UPDATE {tabela} SET deleted_at = ? WHERE {id_column} = ?", 
                         (now, record_id))
            
            conn.commit()
            conn.close()
            
            return True, f"Registro {record_id} marcado como deletado"
            
        except Exception as e:
            return False, f"Erro ao deletar: {str(e)}"
    
    # ===== RESTORE FUNCTIONS =====
    
    @staticmethod
    def restore_pedido(pedido_id: int) -> Tuple[bool, str]:
        """Restaura um pedido deletado"""
        return SoftDeleteManager._restore('ordem_servico', 'id', pedido_id)
    
    @staticmethod
    def restore_cliente(cliente_id: int) -> Tuple[bool, str]:
        """Restaura um cliente deletado"""
        return SoftDeleteManager._restore('clientes', 'id', cliente_id)
    
    @staticmethod
    def restore_produto(produto_id: int) -> Tuple[bool, str]:
        """Restaura um produto deletado"""
        return SoftDeleteManager._restore('produtos', 'id', produto_id)
    
    @staticmethod
    def restore_gasto(gasto_id: int) -> Tuple[bool, str]:
        """Restaura um gasto deletado"""
        return SoftDeleteManager._restore('gastos', 'id', gasto_id)
    
    @staticmethod
    def _restore(tabela: str, id_column: str, record_id: int) -> Tuple[bool, str]:
        """Implementação genérica de restore"""
        db_path = SoftDeleteManager.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Verificar se registro existe e está deletado
            cursor.execute(f"SELECT deleted_at FROM {tabela} WHERE {id_column} = ?", (record_id,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, f"Registro {record_id} não encontrado em {tabela}"
            
            if not result[0]:  # Não está deletado
                conn.close()
                return False, f"Registro {record_id} não está deletado"
            
            # Restaurar (remover deleted_at)
            cursor.execute(f"UPDATE {tabela} SET deleted_at = NULL WHERE {id_column} = ?", 
                         (record_id,))
            
            conn.commit()
            conn.close()
            
            return True, f"Registro {record_id} restaurado com sucesso"
            
        except Exception as e:
            return False, f"Erro ao restaurar: {str(e)}"
    
    # ===== LIST DELETED FUNCTIONS =====
    
    @staticmethod
    def list_deleted_pedidos() -> List[Tuple]:
        """Lista todos os pedidos deletados"""
        return SoftDeleteManager._list_deleted('ordem_servico')
    
    @staticmethod
    def list_deleted_clientes() -> List[Tuple]:
        """Lista todos os clientes deletados"""
        return SoftDeleteManager._list_deleted('clientes')
    
    @staticmethod
    def list_deleted_produtos() -> List[Tuple]:
        """Lista todos os produtos deletados"""
        return SoftDeleteManager._list_deleted('produtos')
    
    @staticmethod
    def list_deleted_gastos() -> List[Tuple]:
        """Lista todos os gastos deletados"""
        return SoftDeleteManager._list_deleted('gastos')
    
    @staticmethod
    def _list_deleted(tabela: str) -> List[Tuple]:
        """Implementação genérica de listagem de deletados"""
        db_path = SoftDeleteManager.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {tabela} WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC")
            results = cursor.fetchall()
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Erro ao listar deletados de {tabela}: {e}")
            return []
    
    # ===== PERMANENT DELETE FUNCTIONS =====
    
    @staticmethod
    def permanent_delete_old_records(days: int = 30):
        """
        Deleta permanentemente registros deletados há mais de X dias.
        
        Args:
            days: Número de dias (padrão: 30)
            
        Returns:
            Tupla (total_deletado: int, mensagem: str)
        """
        db_path = SoftDeleteManager.get_database_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Data limite
            from datetime import datetime, timedelta
            limite = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            
            total = 0
            tabelas = ['ordem_servico', 'clientes', 'produtos', 'gastos']
            
            for tabela in tabelas:
                cursor.execute(f"DELETE FROM {tabela} WHERE deleted_at IS NOT NULL AND deleted_at < ?", 
                             (limite,))
                total += cursor.rowcount
            
            conn.commit()
            conn.close()
            
            return total, f"{total} registros deletados permanentemente (mais de {days} dias)"
            
        except Exception as e:
            return 0, f"Erro ao deletar permanentemente: {str(e)}"
