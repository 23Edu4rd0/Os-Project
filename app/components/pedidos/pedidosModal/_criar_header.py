
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .__init__ import PedidosModal

def _criar_header(self, layout, numero_os, is_edit):
    header_frame = QFrame()
    header_layout = QVBoxLayout(header_frame)
    header_layout.setContentsMargins(0, 0, 0, 10)
    if is_edit and numero_os is not None:
        titulo = f"Editar Ordem de Serviço #{numero_os:05d}"
    elif is_edit:
        titulo = "Editar Ordem de Serviço"
    else:
        titulo = f"Nova Ordem de Serviço" if numero_os is None else f"Nova Ordem de Serviço #{numero_os:05d}"
    titulo_label = QLabel(titulo)
    titulo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    titulo_label.setStyleSheet("color: #ffffff; padding: 10px;")
    header_layout.addWidget(titulo_label)
    layout.addWidget(header_frame)
