from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton


def criar_botoes(modal, layout, numero_os, pedido_data):
    frame = QFrame()
    h = QHBoxLayout(frame)
    h.setContentsMargins(0, 10, 0, 0)

    btn_cancelar = QPushButton("❌ Cancelar")
    btn_cancelar.setMinimumWidth(120)
    btn_cancelar.clicked.connect(modal.reject)
    h.addWidget(btn_cancelar)

    h.addStretch()

    btn_salvar = QPushButton("💾 Salvar")
    btn_salvar.setMinimumWidth(120)
    btn_salvar.clicked.connect(lambda: modal._salvar_pedido(numero_os, pedido_data))
    h.addWidget(btn_salvar)

    if pedido_data:
        btn_pdf = QPushButton("📄 Gerar PDF")
        btn_pdf.setMinimumWidth(120)
        btn_pdf.clicked.connect(lambda: modal._gerar_pdf(pedido_data))
        h.addWidget(btn_pdf)

    layout.addWidget(frame)
