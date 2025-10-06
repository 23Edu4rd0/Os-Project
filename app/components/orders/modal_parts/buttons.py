from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt


def criar_botoes(modal, layout, numero_os, pedido_data):
    # Container principal dos botões
    frame = QFrame()
    frame.setStyleSheet("""
        QFrame {
            background: #23272e;
            border-top: 2px solid #444;
            border-radius: 10px;
            padding: 5px;
        }
        QPushButton {
            background: #444;
            color: #f5f5f5;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background: #555;
        }
        QPushButton:pressed {
            background: #333;
        }
    """)
    
    h = QHBoxLayout(frame)
    h.setContentsMargins(20, 15, 20, 15)
    h.setSpacing(15)

    # Botão Cancelar
    btn_cancelar = QPushButton("✕ Cancelar")
    btn_cancelar.setObjectName("btn_cancelar")  # Para estilo específico
    btn_cancelar.setMinimumWidth(130)
    btn_cancelar.setMinimumHeight(45)
    btn_cancelar.setStyleSheet("""
        QPushButton {
            background-color: #444444;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #555555;
        }
        QPushButton:pressed {
            background-color: #333333;
        }
    """)
    btn_cancelar.clicked.connect(modal.reject)
    h.addWidget(btn_cancelar)

    h.addStretch()

    # Botão PDF (se estiver editando)
    if pedido_data:
        btn_pdf = QPushButton("� Gerar PDF")
        btn_pdf.setMinimumWidth(130)
        btn_pdf.setMinimumHeight(45)
        btn_pdf.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #777777;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
        """)
        btn_pdf.clicked.connect(lambda: modal._gerar_pdf(pedido_data))
        h.addWidget(btn_pdf)

    # Botão Salvar
    btn_salvar = QPushButton("💾 Salvar Pedido")
    btn_salvar.setMinimumWidth(150)
    btn_salvar.setMinimumHeight(45)
    btn_salvar.setStyleSheet("""
        QPushButton {
            background-color: #666666;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 700;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #777777;
        }
        QPushButton:pressed {
            background-color: #555555;
        }
    """)
    btn_salvar.clicked.connect(lambda: modal._salvar_pedido(numero_os, pedido_data))
    h.addWidget(btn_salvar)

    layout.addWidget(frame)
