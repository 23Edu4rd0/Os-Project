from .__init__ import PedidosModal

def abrir_modal_novo(self):
    """Abre modal para novo pedido"""
    self._carregar_clientes()
    self._criar_modal_completo()
