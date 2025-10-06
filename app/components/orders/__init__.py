"""
Módulo de gerenciamento de pedidos em PyQt6
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from .orders_interface import PedidosInterface
from .orders_modal_legacy import PedidosModal
from .order_card import PedidosCard
from .orders_actions import PedidosActions

__all__ = ['PedidosInterface', 'PedidosModal', 'PedidosCard', 'PedidosActions', 'PedidosManager']

# Classe principal que substitui o PedidosManager
class PedidosManager(QWidget):
    """Classe principal que coordena todos os módulos de pedidos"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Layout para o manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Criar e adicionar interface
        self.interface = PedidosInterface(self)
        layout.addWidget(self.interface)

    # Métodos proxy para manter compatibilidade
    def carregar_dados(self):
        """Carrega os dados dos pedidos"""
        return self.interface.carregar_dados()

    def novo_pedido(self):
        """Abre modal para novo pedido"""
        return self.interface.novo_pedido()

    def editar_pedido(self, pedido_id):
        """Abre modal para editar pedido"""
        return self.interface.editar_pedido(pedido_id)

    def excluir_pedido(self, pedido_id):
        """Exclui um pedido"""
        return self.interface.excluir_pedido(pedido_id)

    def atualizar_status(self, pedido_id, novo_status):
        """Atualiza o status de um pedido"""
        return self.interface.atualizar_status(pedido_id, novo_status)

