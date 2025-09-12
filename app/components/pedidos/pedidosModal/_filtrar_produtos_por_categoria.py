
# Nenhum widget PyQt6 usado diretamente, mas garantir import se necessário
from .__init__ import PedidosModal

def _filtrar_produtos_por_categoria(self, cat: str):
    self._montar_produtos_completer(cat)
