
# Nenhum widget PyQt6 usado diretamente, mas garantir import se necessário
from .__init__ import PedidosModal
from database import db_manager

def _carregar_produtos(self):
    try:
        rows = db_manager.listar_produtos()
        self._produtos_rows = rows
        self._produtos_categorias = set([r[4] for r in rows if r[4]])
        self.produtos_dict = {}
        for r in rows:
            nome = (r[1] or '').strip()
            preco = float(r[2] or 0)
            display = f"{nome} | R$ {preco:.2f}"
            self.produtos_dict[display] = {"id": r[0], "nome": nome, "preco": preco, "categoria": (r[4] or '')}
    except Exception as e:
        print(f"Erro ao carregar produtos: {e}")
        self.produtos_dict = {}
