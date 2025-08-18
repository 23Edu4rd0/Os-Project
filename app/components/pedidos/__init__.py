"""
Módulo de gerenciamento de pedidos
"""

from .pedidos_interface import PedidosInterface
from .pedidos_modal import PedidosModal
from .pedidos_card import PedidosCard
from .pedidos_actions import PedidosActions

__all__ = ['PedidosInterface', 'PedidosModal', 'PedidosCard', 'PedidosActions']

# Classe principal que substitui o PedidosManager
class PedidosManager:
    """Classe principal que coordena todos os módulos de pedidos"""
    
    def __init__(self, parent):
        self.parent = parent
        self.interface = PedidosInterface(parent)
    
    # Métodos proxy para manter compatibilidade
    def carregar_dados(self):
        return self.interface.carregar_dados()
    
    def novo_pedido(self):
        return self.interface.novo_pedido()
    
    def editar_pedido(self, pedido):
        return self.interface.editar_pedido(pedido)
    
    def alterar_status(self, pedido):
        return self.interface.alterar_status(pedido)
    
    def excluir_pedido(self, pedido):
        return self.interface.excluir_pedido(pedido)
    
    def enviar_whatsapp_card(self, pedido):
        return self.interface.enviar_whatsapp_card(pedido)
