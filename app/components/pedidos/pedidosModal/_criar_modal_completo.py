
from PyQt6.QtWidgets import QVBoxLayout, QScrollArea, QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

def _criar_modal_completo(self, pedido_data=None, cliente_fixo=False, nome_cliente_label=None):
    """Cria modal completo para pedido"""
    is_edit = pedido_data is not None
    if is_edit:
        self.model.reset()
        self.model.preencher(pedido_data)
    else:
        self.model.reset()
    numero_os = pedido_data.get('numero_os') if pedido_data else None
    titulo = f"Editar OS #{numero_os}" if is_edit else "Nova Ordem de Serviço"
    self.setWindowTitle(titulo)
    self.setFixedSize(900, 700)
    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(10, 10, 10, 10)
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
    scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    scroll_area.verticalScrollBar().setSingleStep(15)
    scroll_area.verticalScrollBar().setPageStep(60)
    content_widget = QWidget()
    content_layout = QVBoxLayout(content_widget)
    content_layout.setContentsMargins(20, 20, 20, 20)
    content_layout.setSpacing(15)
    self._criar_header(content_layout, numero_os, is_edit)
    self.campos = self.model.campos
    self.produtos_list = self.model.produtos_list

    # Se cliente_fixo, mostra um label de contexto; senão, mostra a seção de cliente
    if cliente_fixo:
        nome = nome_cliente_label or ''
        label = QLabel()
        label.setText(f"<span style='font-size:15px;font-weight:600;color:#b0e0ff;padding:2px 8px 2px 0;'>Pedido para:</span> "
                      f"<span style='font-size:15px;font-weight:700;color:#fff;background:#222;border-radius:6px;padding:2px 12px;'>{nome}</span>")
        label.setContentsMargins(0, 0, 0, 0)
        label.setStyleSheet("margin-bottom: 6px;")
        content_layout.addWidget(label)
    else:
        self._criar_secao_cliente(content_layout, pedido_data)

    self._criar_secao_produtos(content_layout, pedido_data)
    self._criar_secao_pagamento(content_layout, pedido_data)
    self._criar_secao_resumo(content_layout)
    self._criar_botoes(content_layout, numero_os, pedido_data)
    try:
        scroll_area.setStyleSheet("QScrollArea{background:#2d2d2d;border:none;} QScrollArea > QWidget > QWidget {background:#2d2d2d;}")
        scroll_area.viewport().setStyleSheet("background:#2d2d2d;")
        content_widget.setStyleSheet("background:#2d2d2d;")
    except Exception:
        pass
    scroll_area.setWidget(content_widget)
    main_layout.addWidget(scroll_area)
    self._aplicar_estilo()
    self.exec()
