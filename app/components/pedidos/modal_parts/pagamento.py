from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QComboBox


def criar_secao_pagamento(modal, layout, pedido_data):
    """Cria seção de pagamento moderna no modal"""
    pagamento_group = QGroupBox("💳 Informações de Pagamento e Entrega")
    pagamento_group.setStyleSheet("""
        QGroupBox {
            font-weight: 600;
            font-size: 16px;
            border: 2px solid #666666;
            border-radius: 8px;
            margin-top: 20px;
            margin-bottom: 18px;
            padding: 50px 18px 22px 18px;
            background-color: #2a2a2a;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            top: 25px;
            padding: 0 15px 0 15px;
            color: #ffffff;
            font-weight: bold;
            background: transparent;
            font-size: 18px;
        }
        QLabel {
            color: #ffffff;
            font-size: 14px;
            font-weight: 500;
            padding: 8px 0 4px 0;
            background: transparent;
        }
        QLineEdit, QComboBox {
            min-height: 36px;
            font-size: 14px;
            color: #ffffff;
            background-color: #404040;
            border: 2px solid #666666;
            border-radius: 6px;
            padding: 8px 12px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #999999;
            background-color: #505050;
        }
        QLineEdit:hover, QComboBox:hover {
            border: 2px solid #888888;
        }
        QFormLayout {
            background: transparent;
            spacing: 12px;
        }
    """)
    pagamento_layout = QFormLayout(pagamento_group)
    pagamento_layout.setSpacing(15)
    pagamento_layout.setContentsMargins(20, 20, 20, 20)

    # Entrada (R$)
    modal.campos['entrada'] = QLineEdit()
    modal.campos['entrada'].setPlaceholderText("0,00")
    modal.campos['entrada'].setMaximumWidth(180)
    modal.campos['entrada'].setMinimumHeight(35)
    pagamento_layout.addRow("💰 Entrada (R$):", modal.campos['entrada'])

    # Frete (R$)
    modal.campos['frete'] = QLineEdit()
    modal.campos['frete'].setPlaceholderText("0,00")
    modal.campos['frete'].setMaximumWidth(180)
    modal.campos['frete'].setMinimumHeight(35)
    pagamento_layout.addRow("🚚 Frete (R$):", modal.campos['frete'])

    # Desconto (R$)
    modal.campos['desconto'] = QLineEdit()
    modal.campos['desconto'].setPlaceholderText("0,00")
    modal.campos['desconto'].setMaximumWidth(180)
    modal.campos['desconto'].setMinimumHeight(35)
    pagamento_layout.addRow("🏷️ Desconto (R$):", modal.campos['desconto'])

    # Status
    modal.campos['status'] = QComboBox()
    modal.campos['status'].setMinimumHeight(35)
    try:
        from app.utils.statuses import load_statuses
        modal.campos['status'].addItems(load_statuses())
    except Exception:
        modal.campos['status'].addItems(["em produção", "enviado", "entregue", "cancelado"])
    pagamento_layout.addRow("📊 Status:", modal.campos['status'])

    # Forma de pagamento
    modal.campos['forma_pagamento'] = QComboBox()
    modal.campos['forma_pagamento'].setMinimumHeight(35)
    modal.campos['forma_pagamento'].addItems([
        "PIX", 
        "Cartão de Crédito", 
        "Cartão de Débito", 
        "Dinheiro", 
        "Transferência", 
        "Boleto"
    ])
    pagamento_layout.addRow("💳 Forma de Pagamento:", modal.campos['forma_pagamento'])

    # Prazo (dias)
    modal.campos['prazo_entrega'] = QLineEdit()
    modal.campos['prazo_entrega'].setPlaceholderText("Ex: 30 dias")
    modal.campos['prazo_entrega'].setMaximumWidth(180)
    modal.campos['prazo_entrega'].setMinimumHeight(35)
    pagamento_layout.addRow("📅 Prazo de Entrega:", modal.campos['prazo_entrega'])

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
