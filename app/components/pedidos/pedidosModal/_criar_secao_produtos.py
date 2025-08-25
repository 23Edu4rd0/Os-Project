
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .__init__ import PedidosModal, _criar_secao_produtos_part

def _criar_secao_produtos(self, layout, pedido_data):
    from ._criar_secao_produtos_pedidos import _criar_secao_produtos_pedidos
    _criar_secao_produtos_pedidos(self, layout, pedido_data)
