
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .__init__ import PedidosModal

def _criar_header(self, layout, numero_os, is_edit):
    # Container principal do header
    # Linha: OS N - Nome do Cliente - CPF/CNPJ
    dados = getattr(self, 'model', None)
    nome_cliente = ''
    cpf_cnpj = ''
    if dados and getattr(dados, 'dados', None):
        md = dados.dados
        nome_cliente = md.get('nome_cliente') or md.get('nome') or ''
        cpf_cnpj = md.get('cpf_cliente') or md.get('cpf') or md.get('cnpj') or ''
    os_num = f"OS {numero_os}" if numero_os else "OS"
    info = os_num
    if nome_cliente:
        info += f" - {nome_cliente}"
    if cpf_cnpj:
        info += f" - {cpf_cnpj}"
    linha = QLabel(info)
    linha.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
    linha.setAlignment(Qt.AlignmentFlag.AlignLeft)
    linha.setStyleSheet("color: #f5f5f5; background: #23272e; padding: 8px 18px 8px 18px; border-radius: 8px;")
    layout.addWidget(linha)
