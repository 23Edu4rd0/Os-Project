
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from .__init__ import PedidosModal, _criar_botoes_part

def _criar_botoes(self, layout, numero_os, pedido_data):
    if '_criar_botoes_part' in globals() and _criar_botoes_part:
        _criar_botoes_part(self, layout, numero_os, pedido_data)
        return
    # ...existing code for botoes section...
