"""
Compat: módulo de atalho para o gerenciador de Pedidos.

Este arquivo existe apenas para manter importações como
`from app.components.pedidos import PedidosManager` funcionando mesmo
quando há também o pacote `app.components.pedidos` (pasta).
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout

# Importa a interface real do pacote
try:
    from .pedidos.pedidos_interface import PedidosInterface
except Exception:  # fallback caso caminho relativo falhe
    from app.components.pedidos.pedidos_interface import PedidosInterface


class PedidosManager(QWidget):
    """Wrapper simples que hospeda a PedidosInterface"""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.interface = PedidosInterface(self)
        layout.addWidget(self.interface)

    # Proxies para compatibilidade
    def carregar_dados(self):
        return self.interface.carregar_dados()

    def novo_pedido(self):
        return self.interface.novo_pedido()

    def editar_pedido(self, pedido_id):
        return self.interface.editar_pedido(pedido_id)

    def excluir_pedido(self, pedido_id):
        return self.interface.excluir_pedido(pedido_id)

    def atualizar_status(self, pedido_id, novo_status):
        return self.interface.atualizar_status(pedido_id, novo_status)
        # Atualiza a origem de dados do pedido
        for p in self._lista_pedidos:
            pid = p.get("id") or p.get("numero") or p.get("os_id")
            if pid == pedido_id:
                p["status"] = novo_status
                break

        # Persistência (se houver DAO/DB). Deixe o hook:
        try:
            self._repo.update_status(pedido_id, novo_status)  # opcional se existir
        except Exception:
            pass

        # Reaplica o filtro para respeitar a regra dos concluídos
        self._build_cards()