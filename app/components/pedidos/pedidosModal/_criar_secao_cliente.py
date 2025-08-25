
from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QWidget, QCompleter
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QHBoxLayout, QPushButton, QWidget, QCompleter
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .__init__ import PedidosModal, _criar_secao_cliente_part

def _criar_secao_cliente(self, layout, pedido_data):
    if _criar_secao_cliente_part:
        _criar_secao_cliente_part(self, layout, pedido_data)
        return
    from PyQt6.QtWidgets import QLineEdit
    cliente_group = QGroupBox("👤 Dados do Cliente")
    cliente_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    cliente_layout = QFormLayout(cliente_group)
    self.campos['nome_cliente'] = QLineEdit()
    self.campos['nome_cliente'].setPlaceholderText("Digite o nome do cliente...")
    if self.clientes_dict:
        self.clientes_completer = QCompleter(list(self.clientes_dict.keys()))
        self.clientes_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.clientes_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.campos['nome_cliente'].setCompleter(self.clientes_completer)
        try:
            self.clientes_completer.activated[str].connect(self._on_cliente_completer_activated)
        except Exception:
            pass
        self.campos['nome_cliente'].textChanged.connect(self._on_cliente_selecionado)
        try:
            self.campos['nome_cliente'].editingFinished.connect(lambda: self._on_cliente_selecionado(self.campos['nome_cliente'].text()))
        except Exception:
            pass
    nome_row = QHBoxLayout()
    nome_row.addWidget(self.campos['nome_cliente'])
    btn_limpar_cli = QPushButton("🧹 Limpar")
    btn_limpar_cli.setMaximumWidth(90)
    btn_limpar_cli.setToolTip("Limpar dados do cliente")
    btn_limpar_cli.clicked.connect(self._limpar_campos_cliente)
    nome_row.addWidget(btn_limpar_cli)
    nome_row_w = QWidget()
    nome_row_w.setLayout(nome_row)
    cliente_layout.addRow("Nome do Cliente:", nome_row_w)
    self.campos['telefone_cliente'] = QLineEdit()
    self.campos['telefone_cliente'].setPlaceholderText("(11) 99999-9999")
    try:
        self.campos['telefone_cliente'].setInputMask("(00) 00000-0000;_")
    except Exception:
        pass
    cliente_layout.addRow("Telefone:", self.campos['telefone_cliente'])
    self.campos['cpf_cliente'] = QLineEdit()
    self.campos['cpf_cliente'].setPlaceholderText("000.000.000-00")
    try:
        self.campos['cpf_cliente'].setInputMask("000.000.000-00;_")
    except Exception:
        pass
    cliente_layout.addRow("CPF:", self.campos['cpf_cliente'])
    self.campos['endereco_cliente'] = QLineEdit()
    self.campos['endereco_cliente'].setPlaceholderText("Rua, número, bairro, cidade")
    cliente_layout.addRow("Endereço:", self.campos['endereco_cliente'])
    layout.addWidget(cliente_group)
