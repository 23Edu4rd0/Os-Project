from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QWidget, QVBoxLayout, QCompleter
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


def criar_secao_cliente(modal, layout, pedido_data):
    grupo = QGroupBox("Dados do Cliente")
    grupo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    grupo.setStyleSheet(
        "QGroupBox {"
        " font-weight: 600;"
        " font-size: 16px;"
        " border: 2px solid #666666;"
        " border-radius: 8px;"
        " margin-top: 15px;"
        " margin-bottom: 12px;"
        " padding: 05px 15px 15px 05px;"
        " background-color: #1e1e1e;"
        " color: #ffffff;"
        " }"
        " QGroupBox::title {"
        " subcontrol-origin: margin;"
        " left: 15px;"
        " top: 40px;"
        " padding: 0 10px 0 10px;"
        " color: #ffffff;"
        " font-weight: bold;"
        " background: transparent;"
        " font-size: 16px;"
        " }"
        " QLabel {"
        " color: #ffffff;"
        " font-size: 14px;"
        " font-weight: 500;"
        " padding: 8px 0 4px 0;"
        " background: transparent;"
        " }"
        " QLineEdit {"
        " min-height: 30px;"
        " font-size: 14px;"
        " color: #ffffff;"
        " background-color: #404040;"
        " border: 2px solid #666666;"
        " border-radius: 6px;"
        " padding: 6px 10px;"
        " }"
        " QLineEdit:focus {"
        " border: 2px solid #999999;"
        " background-color: #505050;"
        " }"
        " QLineEdit:hover {"
        " border: 2px solid #888888;"
        " }"
        " QFormLayout {"
        " background: transparent;"
        " spacing: 12px;"
        " }"
        " QWidget {"
        " background: transparent;"
        " }"
    )

    # Layout principal do grupo
    main_layout = QVBoxLayout(grupo)
    main_layout.setContentsMargins(15, 0, 15, 15)
    
    # Cabeçalho com botão limpar
    header_layout = QHBoxLayout()
    header_layout.setContentsMargins(0, 0, 0, 5)
    
    # Espaçador para empurrar o botão para a direita
    header_layout.addStretch()
    
    # Botão limpar
    btn_limpar = QPushButton("Limpar")
    btn_limpar.setObjectName("btn_limpar_cli")
    btn_limpar.setMaximumWidth(100)
    btn_limpar.setMinimumHeight(30)
    btn_limpar.setToolTip("Limpar todos os dados do cliente")
    btn_limpar.setStyleSheet("""
        QPushButton {
            background-color: #666666;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
            margin-top: 10px;
            padding: 10px 16px;
        }
        QPushButton:hover {
            background-color: #777777;
        }
        QPushButton:pressed {
            background-color: #555555;
        }
    """)
    btn_limpar.clicked.connect(modal._limpar_campos_cliente)
    header_layout.addWidget(btn_limpar)
    
    main_layout.addLayout(header_layout)

    # Form layout para os campos
    form_widget = QWidget()
    form = QFormLayout(form_widget)
    form.setSpacing(8)
    form.setContentsMargins(0, -25, 0, 0)

    # Nome
    modal.campos['nome_cliente'] = QLineEdit()
    modal.campos['nome_cliente'].setPlaceholderText("Digite o nome completo do cliente...")
    modal.campos['nome_cliente'].setMinimumHeight(30)
    form.addRow("Nome:", modal.campos['nome_cliente'])

    # Completer
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

    # Telefone
    modal.campos['telefone_cliente'] = QLineEdit()
    modal.campos['telefone_cliente'].setPlaceholderText("(11) 99999-9999")
    modal.campos['telefone_cliente'].setMinimumHeight(30)
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

    main_layout.addWidget(form_widget)
    layout.addWidget(grupo)
