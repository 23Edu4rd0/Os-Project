"""
CRUD for registerable products.
All user-facing messages are in Portuguese. All comments, docstrings, and logs are in English.
"""
from typing import List, Tuple, Optional


class ProductsCRUD:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def inserir_produto(self, nome: str, preco: float, descricao: str = "", categoria: str = "", codigo: str = None) -> Optional[int]:
        """Insert a new product."""
        try:
            self.cursor.execute(
                """
                INSERT INTO produtos (nome, codigo, preco, descricao, categoria)
                VALUES (?, ?, ?, ?, ?)
                """,
                (nome, codigo, float(preco or 0), descricao, categoria),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Erro ao inserir produto: {e}")  # User-facing message in Portuguese
            print(f"Error inserting product: {e}")  # Log in English
            return None

    def listar_produtos(self, busca: str = "", limite: int = 200) -> List[Tuple]:
        """List non-deleted products (deleted_at IS NULL)."""
        try:
            if busca:
                self.cursor.execute(
                    """
                    SELECT id, nome, codigo, preco, descricao, categoria, criado_em
                    FROM produtos
                    WHERE (nome LIKE ? OR categoria LIKE ? OR codigo LIKE ?)
                      AND deleted_at IS NULL
                    ORDER BY nome ASC
                    LIMIT ?
                    """,
                    (f"%{busca}%", f"%{busca}%", f"%{busca}%", limite),
                )
            else:
                self.cursor.execute(
                    """
                    SELECT id, nome, codigo, preco, descricao, categoria, criado_em
                    FROM produtos
                    WHERE deleted_at IS NULL
                    ORDER BY nome ASC
                    LIMIT ?
                    """,
                    (limite,),
                )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")  # User-facing message in Portuguese
            print(f"Error listing products: {e}")  # Log in English
            return []

    def atualizar_produto(self, produto_id: int, nome: str, preco: float, descricao: str = "", categoria: str = "", codigo: str = None) -> bool:
        """Update a product."""
        try:
            self.cursor.execute(
                """
                UPDATE produtos
                SET nome = ?, codigo = ?, preco = ?, descricao = ?, categoria = ?
                WHERE id = ?
                """,
                (nome, codigo, float(preco or 0), descricao, categoria, produto_id),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar produto: {e}")  # User-facing message in Portuguese
            print(f"Error updating product: {e}")  # Log in English
            return False

    def deletar_produto(self, produto_id: int) -> bool:
        """Soft delete product - marks as deleted instead of removing."""
        try:
            from app.utils.soft_delete import SoftDeleteManager
            success, msg = SoftDeleteManager.soft_delete_produto(produto_id)
            if success:
                print(f"✅ Produto {produto_id} marcado como deletado")  # User-facing message in Portuguese
                print(f"Product {produto_id} marked as deleted")  # Log in English
            else:
                print(f"❌ Erro ao deletar produto: {msg}")  # User-facing message in Portuguese
                print(f"Error deleting product: {msg}")  # Log in English
            return success
        except Exception as e:
            print(f"❌ Erro ao deletar produto: {e}")  # User-facing message in Portuguese
            print(f"Error deleting product: {e}")  # Log in English
            return False
