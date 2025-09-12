from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QWidget
from PyQt6.QtWidgets import QLineEdit  # Corrige escopo para isinstance
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCompleter


def criar_secao_cliente(modal, layout, pedido_data):
    grupo = QGroupBox("👤 Dados do Cliente")
    grupo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    grupo.setStyleSheet("""
        QGroupBox {
            font-weight: 600;
            font-size: 14px;
            border: 2px solid #0d7377;
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 20px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(13, 115, 119, 0.1), stop:1 rgba(13, 115, 119, 0.05));
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 15px 0 15px;
            color: #0d7377;
            background: #2d2d2d;
            border-radius: 6px;
            font-weight: bold;
        }
    """)
    form = QFormLayout(grupo)
    form.setSpacing(15)
    form.setContentsMargins(20, 20, 20, 20)

    # Nome do Cliente + Botão Limpar
    nome_container = QWidget()
    nome_container.setStyleSheet("background: transparent;")
    nome_layout = QHBoxLayout(nome_container)
    nome_layout.setContentsMargins(0, 0, 0, 0)
    nome_layout.setSpacing(10)
    
    modal.campos['nome_cliente'] = QLineEdit()
    modal.campos['nome_cliente'].setPlaceholderText("Digite o nome completo do cliente...")
    modal.campos['nome_cliente'].setMinimumHeight(35)

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

    nome_layout.addWidget(modal.campos['nome_cliente'], 3)
    
    btn_limpar = QPushButton("🧹 Limpar")
    btn_limpar.setObjectName("btn_limpar_cli")  # Para CSS específico
    btn_limpar.setMaximumWidth(100)
    btn_limpar.setMinimumHeight(35)
    btn_limpar.setToolTip("Limpar todos os dados do cliente")
    btn_limpar.clicked.connect(modal._limpar_campos_cliente)
    nome_layout.addWidget(btn_limpar)
    
    form.addRow("Nome:", nome_container)

    # Telefone
    modal.campos['telefone_cliente'] = QLineEdit()
    modal.campos['telefone_cliente'].setPlaceholderText("(11) 99999-9999")
    modal.campos['telefone_cliente'].setMinimumHeight(35)
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
