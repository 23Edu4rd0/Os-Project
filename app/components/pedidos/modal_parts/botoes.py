from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt


def criar_botoes(modal, layout, numero_os, pedido_data):
    # Container principal dos botões
    frame = QFrame()
    frame.setStyleSheet("""
        QFrame {
            background: rgba(45, 45, 45, 0.8);
            border-top: 2px solid #0d7377;
            border-radius: 10px;
            padding: 5px;
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
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6a4c93, stop:1 #553c7b);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7a5ca3, stop:1 #634c8b);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a3c83, stop:1 #4a2c6b);
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
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0d7377, stop:1 #0a5d61);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 700;
            font-size: 14px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0e8a8f, stop:1 #0c6b70);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #094e52, stop:1 #073d41);
        }
    """)
    btn_salvar.clicked.connect(lambda: modal._salvar_pedido(numero_os, pedido_data))
    h.addWidget(btn_salvar)

    layout.addWidget(frame)
