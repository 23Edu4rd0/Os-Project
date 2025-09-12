
from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QComboBox
from PyQt6.QtGui import QFont

from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QComboBox
from PyQt6.QtGui import QFont
from .__init__ import PedidosModal, _criar_secao_pagamento_part

def _criar_secao_pagamento(self, layout, pedido_data):
    if _criar_secao_pagamento_part:
        _criar_secao_pagamento_part(self, layout, pedido_data)
        return
    # ...existing code for pagamento section...
