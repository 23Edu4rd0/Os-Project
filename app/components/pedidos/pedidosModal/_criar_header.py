
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
    # If model or pedido_data contains client cpf/city, append them to the header
    extra_parts = []
    try:
        # model.dados may be populated when editing
        dados = getattr(self, 'model', None)
        if dados and getattr(dados, 'dados', None):
            md = dados.dados
            cpf = md.get('cpf_cliente') or md.get('cpf') or ''
            endereco = md.get('endereco_cliente') or ''
            cidade = ''
            # try to extract city from endereco if it contains commas
            if endereco and ',' in endereco:
                parts = [p.strip() for p in endereco.split(',') if p.strip()]
                if len(parts) >= 3:
                    cidade = parts[2]
            if cpf:
                extra_parts.append(f"CPF: {cpf}")
            if cidade:
                extra_parts.append(cidade)
    except Exception:
        pass

    titulo_label = QLabel(titulo + (" — " + " | ".join(extra_parts) if extra_parts else ""))
    titulo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    titulo_label.setStyleSheet("color: #ffffff; padding: 10px;")
    header_layout.addWidget(titulo_label)
    layout.addWidget(header_frame)
