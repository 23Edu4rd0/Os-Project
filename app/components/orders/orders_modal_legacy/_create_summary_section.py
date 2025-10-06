
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont

from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel
from PyQt6.QtGui import QFont
from .__init__ import PedidosModal, _criar_secao_resumo_part

def _criar_secao_resumo(self, layout):
    if _criar_secao_resumo_part:
        _criar_secao_resumo_part(self, layout)
        return
    # ...existing code for resumo section...
