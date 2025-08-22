"""
CRUD para produtos cadastráveis
"""
from typing import List, Tuple, Optional


class ProductsCRUD:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn

    def inserir_produto(self, nome: str, preco: float, descricao: str = "", categoria: str = "") -> Optional[int]:
        try:
            self.cursor.execute(
                """
                INSERT INTO produtos (nome, preco, descricao, categoria)
                VALUES (?, ?, ?, ?)
                """,
                (nome, float(preco or 0), descricao, categoria),
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Erro ao inserir produto: {e}")
            return None

    def listar_produtos(self, busca: str = "", limite: int = 200) -> List[Tuple]:
        try:
            if busca:
                self.cursor.execute(
                    """
                    SELECT id, nome, preco, descricao, categoria, criado_em
                    FROM produtos
                    WHERE nome LIKE ? OR categoria LIKE ?
                    ORDER BY nome ASC
                    LIMIT ?
                    """,
                    (f"%{busca}%", f"%{busca}%", limite),
                )
            else:
                self.cursor.execute(
                    """
                    SELECT id, nome, preco, descricao, categoria, criado_em
                    FROM produtos
                    ORDER BY nome ASC
                    LIMIT ?
                    """,
                    (limite,),
                )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar produtos: {e}")
            return []

    def atualizar_produto(self, produto_id: int, nome: str, preco: float, descricao: str = "", categoria: str = "") -> bool:
        try:
            self.cursor.execute(
                """
                UPDATE produtos
                SET nome = ?, preco = ?, descricao = ?, categoria = ?
                WHERE id = ?
                """,
                (nome, float(preco or 0), descricao, categoria, produto_id),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar produto: {e}")
            return False

    def deletar_produto(self, produto_id: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao deletar produto: {e}")
            return False
