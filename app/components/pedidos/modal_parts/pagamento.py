from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QComboBox


def criar_secao_pagamento(modal, layout, pedido_data):
    """Cria seção de pagamento no modal, com 'Prazo (dias)'.
    Preenche campos em modo edição e conecta sinais para recálculo.
    """
    pagamento_group = QGroupBox("💳 Dados de Pagamento")
    pagamento_layout = QFormLayout(pagamento_group)

    # Entrada (R$)
    modal.campos['entrada'] = QLineEdit()
    modal.campos['entrada'].setPlaceholderText("0.00")
    modal.campos['entrada'].setMaximumWidth(150)
    pagamento_layout.addRow("Entrada (R$):", modal.campos['entrada'])

    # Frete (R$)
    modal.campos['frete'] = QLineEdit()
    modal.campos['frete'].setPlaceholderText("0.00")
    modal.campos['frete'].setMaximumWidth(150)
    pagamento_layout.addRow("Frete (R$):", modal.campos['frete'])

    # Desconto (R$)
    modal.campos['desconto'] = QLineEdit()
    modal.campos['desconto'].setPlaceholderText("0.00")
    modal.campos['desconto'].setMaximumWidth(150)
    pagamento_layout.addRow("Desconto (R$):", modal.campos['desconto'])

    # Status
    modal.campos['status'] = QComboBox()
    try:
        from app.utils.statuses import load_statuses
        modal.campos['status'].addItems(load_statuses())
    except Exception:
        modal.campos['status'].addItems(["em produção", "enviado", "entregue", "cancelado"])
    pagamento_layout.addRow("Status:", modal.campos['status'])

    # Forma de pagamento
    modal.campos['forma_pagamento'] = QComboBox()
    modal.campos['forma_pagamento'].addItems(["pix", "cartão de crédito", "cartão de débito", "dinheiro", "transferência", "boleto"])
    pagamento_layout.addRow("Forma de Pagamento:", modal.campos['forma_pagamento'])

    # Prazo (dias)
    modal.campos['prazo_entrega'] = QLineEdit()
    modal.campos['prazo_entrega'].setPlaceholderText("dias (ex: 30)")
    pagamento_layout.addRow("Prazo (dias):", modal.campos['prazo_entrega'])

    # Preencher dados se for edição
    if pedido_data:
        try:
            modal.campos['entrada'].setText(f"{float(pedido_data.get('valor_entrada', 0) or 0):.2f}")
        except Exception:
            pass
        try:
            modal.campos['frete'].setText(f"{float(pedido_data.get('frete', 0) or 0):.2f}")
        except Exception:
            pass
        try:
            modal.campos['desconto'].setText(f"{float(pedido_data.get('desconto', 0) or 0):.2f}")
        except Exception:
            pass
        try:
            from app.utils.statuses import load_statuses
            _sts = load_statuses()
            default_status = _sts[0] if _sts else 'em produção'
        except Exception:
            default_status = 'em produção'
        status = pedido_data.get('status', default_status)
        idx = modal.campos['status'].findText(status)
        if idx >= 0:
            modal.campos['status'].setCurrentIndex(idx)

        forma_pag = pedido_data.get('forma_pagamento', 'pix')
        idx = modal.campos['forma_pagamento'].findText(forma_pag)
        if idx >= 0:
            modal.campos['forma_pagamento'].setCurrentIndex(idx)

        # Mostrar prazo em dias
        try:
            modal.campos['prazo_entrega'].setText(str(int(pedido_data.get('prazo', 0) or 0)))
        except Exception:
            modal.campos['prazo_entrega'].setText("")

    # Conectar para recalcular total
    try:
        modal.campos['entrada'].textChanged.connect(modal._recalcular_total)
        modal.campos['frete'].textChanged.connect(modal._recalcular_total)
        modal.campos['desconto'].textChanged.connect(modal._recalcular_total)
    except Exception:
        pass

    layout.addWidget(pagamento_group)
