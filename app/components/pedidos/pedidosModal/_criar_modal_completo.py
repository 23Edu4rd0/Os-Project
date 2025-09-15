
from PyQt6.QtWidgets import QVBoxLayout, QScrollArea, QWidget, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

def _criar_modal_completo(self, pedido_data=None, cliente_fixo=False, nome_cliente_label=None):
    """Cria modal completo para pedido"""
    is_edit = pedido_data is not None
    # Preserve any pre-filled model data when opening modal from a client (cliente_fixo=True).
    # If editing, reset then preencher with pedido_data. If creating new, only reset when
    # we are not in cliente_fixo mode (so ClientesManager can prefill via model.preencher).
    if is_edit:
        self.model.reset()
        self.model.preencher(pedido_data)
    else:
        if not cliente_fixo:
            # fresh new modal without client context: reset model
            self.model.reset()
    numero_os = pedido_data.get('numero_os') if pedido_data else None
    titulo = f"Editar OS #{numero_os}" if is_edit else "Nova Ordem de Serviço"
    self.setWindowTitle(titulo)
    self.setFixedSize(900, 700)
    
    # Aplicar estilo global consistente ao modal
    self.setStyleSheet("""
        QDialog {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        
        QScrollArea {
            border: none;
            background: transparent;
        }
        
        QScrollBar:vertical {
            background: #333333;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background: #666666;
            min-height: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #777777;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
    """)
    
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

    # Remember mode: if cliente_fixo, we want to preserve model.dados and force client info on save
    try:
        self._cliente_fixo = bool(cliente_fixo)
    except Exception:
        self._cliente_fixo = False

    # Se cliente_fixo, mostra um label de contexto; senão, mostra a seção de cliente
    if cliente_fixo:
        nome = nome_cliente_label or ''
        label = QLabel()
        label.setText(f"<span style='font-size:15px;font-weight:600;color:#ffffff;padding:2px 8px 2px 0;'>Pedido para:</span> "
                      f"<span style='font-size:15px;font-weight:700;color:#ffffff;background:#333333;border-radius:6px;padding:6px 12px;'>{nome}</span>")
        label.setContentsMargins(0, 0, 0, 0)
        label.setStyleSheet("margin-bottom: 12px; padding: 8px; background-color: #2a2a2a; border-radius: 8px; border: 1px solid #666666;")
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
