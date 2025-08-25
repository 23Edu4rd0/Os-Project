from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QWidget
from PyQt6.QtWidgets import QLineEdit  # Corrige escopo para isinstance
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCompleter


def criar_secao_cliente(modal, layout, pedido_data):
    grupo = QGroupBox("👤 Dados do Cliente")
    grupo.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    form = QFormLayout(grupo)

    # Nome + limpar
    modal.campos['nome_cliente'] = QLineEdit()
    modal.campos['nome_cliente'].setPlaceholderText("Digite o nome do cliente...")

    if getattr(modal, 'clientes_dict', None):
        completer = QCompleter(list(modal.clientes_dict.keys()))
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        modal.clientes_completer = completer
        modal.campos['nome_cliente'].setCompleter(completer)
        try:
            completer.activated[str].connect(modal._on_cliente_completer_activated)
        except Exception:
            pass
        modal.campos['nome_cliente'].textChanged.connect(modal._on_cliente_selecionado)
        try:
            modal.campos['nome_cliente'].editingFinished.connect(lambda: modal._on_cliente_selecionado(modal.campos['nome_cliente'].text()))
        except Exception:
            pass

    row = QHBoxLayout()
    row.addWidget(modal.campos['nome_cliente'])
    btn_limpar = QPushButton("🧹 Limpar")
    btn_limpar.setMaximumWidth(90)
    btn_limpar.setToolTip("Limpar dados do cliente")
    btn_limpar.clicked.connect(modal._limpar_campos_cliente)
    row.addWidget(btn_limpar)
    w = QWidget(); w.setLayout(row)
    form.addRow("Nome do Cliente:", w)

    # Telefone
    modal.campos['telefone_cliente'] = QLineEdit()
    modal.campos['telefone_cliente'].setPlaceholderText("(11) 99999-9999")
    try:
        modal.campos['telefone_cliente'].setInputMask("(00) 00000-0000;_")
    except Exception:
        pass
    form.addRow("Telefone:", modal.campos['telefone_cliente'])

    # CPF
    modal.campos['cpf_cliente'] = QLineEdit()
    modal.campos['cpf_cliente'].setPlaceholderText("000.000.000-00")
    try:
        modal.campos['cpf_cliente'].setInputMask("000.000.000-00;_")
    except Exception:
        pass
    form.addRow("CPF:", modal.campos['cpf_cliente'])

    # Endereço
    modal.campos['endereco_cliente'] = QLineEdit()
    modal.campos['endereco_cliente'].setPlaceholderText("Rua, número, bairro, cidade")
    form.addRow("Endereço:", modal.campos['endereco_cliente'])

    # Prefill
    if pedido_data:
        if isinstance(modal.campos.get('nome_cliente'), QLineEdit):
            modal.campos['nome_cliente'].setText(str(pedido_data.get('nome_cliente', '') or ''))
        if isinstance(modal.campos.get('telefone_cliente'), QLineEdit):
            modal.campos['telefone_cliente'].setText(str(pedido_data.get('telefone_cliente', '') or ''))
        if isinstance(modal.campos.get('cpf_cliente'), QLineEdit):
            modal.campos['cpf_cliente'].setText(str(pedido_data.get('cpf_cliente', '') or ''))
        if isinstance(modal.campos.get('endereco_cliente'), QLineEdit):
            modal.campos['endereco_cliente'].setText(str(pedido_data.get('endereco_cliente', '') or ''))

    layout.addWidget(grupo)
