from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtGui import QFont


def criar_secao_resumo(modal, layout):
    resumo_group = QGroupBox("💰 Resumo Financeiro")
    resumo_group.setStyleSheet("""
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
            font-size: 15px;
            padding: 8px 0 8px 0;
            background: transparent;
        }
    """)
    resumo_layout = QHBoxLayout(resumo_group)

    modal.label_resumo = QLabel("Valor Total: R$ 0,00")
    modal.label_resumo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    modal.label_resumo.setStyleSheet("color: #ffffff; font-weight: bold;")
    resumo_layout.addWidget(modal.label_resumo)

    # Atualizar quando valor_total mudar
    # Garantir que o campo 'valor_total' exista (pode ser criado pela seção de produtos mais tarde)
    if 'valor_total' not in getattr(modal, 'campos', {}):
        modal.campos['valor_total'] = QLineEdit()
        modal.campos['valor_total'].setReadOnly(True)
        modal.campos['valor_total'].setPlaceholderText("0.00")
        # Não adicionar este widget visualmente aqui — a seção de produtos adiciona a exibição.
        modal.campos['valor_total'].setVisible(False)

    try:
        modal.campos['valor_total'].textChanged.connect(lambda: atualizar_resumo(modal))
    except Exception:
        pass

    layout.addWidget(resumo_group)


def atualizar_resumo(modal):
    try:
        valor_texto = modal.campos['valor_total'].text().replace(',', '.')
        valor = float(valor_texto) if valor_texto else 0.0
        modal.label_resumo.setText(f"Valor Total: R$ {valor:.2f}")
    except Exception:
        modal.label_resumo.setText("Valor Total: R$ 0,00")


def recalcular_total(modal):
    def _f(v):
        try:
            return float((v or '').replace(',', '.'))
        except Exception:
            return 0.0

    total_produtos = sum([p.get('valor', 0.0) for p in modal.produtos_list])
    frete = _f(modal.campos.get('frete').text()) if 'frete' in modal.campos else 0.0
    desconto = _f(modal.campos.get('desconto').text()) if 'desconto' in modal.campos else 0.0
    total = max(0.0, total_produtos + frete - desconto)
    try:
        modal.campos['valor_total'].setText(f"{total:.2f}")
    except Exception:
        pass
