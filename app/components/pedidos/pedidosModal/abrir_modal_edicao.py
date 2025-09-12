from .__init__ import PedidosModal
from PyQt6.QtWidgets import QMessageBox
from database import db_manager

def abrir_modal_edicao(self, pedido_id):
    """Abre modal para editar pedido"""
    try:
        pedidos = db_manager.listar_pedidos_ordenados_por_prazo()
        pedido_data = None
        for pedido in pedidos:
            if pedido.get('id') == pedido_id:
                pedido_data = pedido
                break
        if pedido_data:
            self._carregar_clientes()
            self._criar_modal_completo(pedido_data)
        else:
            QMessageBox.warning(self, "Erro", "Pedido não encontrado!")
    except Exception as e:
        QMessageBox.critical(self, "Erro", f"Erro ao carregar pedido: {e}")
