"""
Diálogo de confirmação de cliente com opção de cópia
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pyperclip


class ClienteConfirmDialog(QDialog):
    def __init__(self, cliente_data, parent=None):
        super().__init__(parent)
        self.cliente_data = cliente_data
        self.resultado = None  # 'confirmar', 'copiar' ou None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Confirmar Dados do Cliente")
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        # Aplicar tema escuro
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0a5d61;
            }
            QPushButton#btnNao {
                background-color: #dc3545;
            }
            QPushButton#btnNao:hover {
                background-color: #c82333;
            }
            QPushButton#btnCopiar {
                background-color: #28a745;
            }
            QPushButton#btnCopiar:hover {
                background-color: #218838;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel("Confirmar dados do cliente:")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        
        # Área de texto com os dados
        self.texto_dados = QTextEdit()
        self.texto_dados.setReadOnly(True)
        self.texto_dados.setPlainText(self._formatar_dados())
        layout.addWidget(self.texto_dados)
        
        # Botões
        layout_botoes = QHBoxLayout()
        
        btn_nao = QPushButton("❌ Não")
        btn_nao.setObjectName("btnNao")
        btn_nao.clicked.connect(self.reject)
        
        btn_copiar = QPushButton("📋 Copiar")
        btn_copiar.setObjectName("btnCopiar")
        btn_copiar.clicked.connect(self.copiar_dados)
        
        btn_confirmar = QPushButton("✅ Confirmar")
        btn_confirmar.clicked.connect(self.confirmar_dados)
        
        layout_botoes.addWidget(btn_nao)
        layout_botoes.addWidget(btn_copiar)
        layout_botoes.addWidget(btn_confirmar)
        
        layout.addLayout(layout_botoes)
        
    def _formatar_dados(self):
        """Formata os dados do cliente para exibição"""
        dados = []
        dados.append("=== DADOS DO CLIENTE ===")
        dados.append("")
        
        if self.cliente_data.get('nome'):
            dados.append(f"Nome: {self.cliente_data['nome']}")
        
        if self.cliente_data.get('cpf'):
            dados.append(f"CPF: {self.cliente_data['cpf']}")
        
        if self.cliente_data.get('cnpj'):
            dados.append(f"CNPJ: {self.cliente_data['cnpj']}")
        
        if self.cliente_data.get('inscricao_estadual'):
            dados.append(f"Inscrição Estadual: {self.cliente_data['inscricao_estadual']}")
        
        if self.cliente_data.get('telefone'):
            dados.append(f"Telefone: {self.cliente_data['telefone']}")
        
        if self.cliente_data.get('email'):
            dados.append(f"Email: {self.cliente_data['email']}")
        
        # Endereço
        endereco_partes = []
        if self.cliente_data.get('rua'):
            endereco_partes.append(self.cliente_data['rua'])
        if self.cliente_data.get('numero'):
            endereco_partes.append(f"nº {self.cliente_data['numero']}")
        if self.cliente_data.get('bairro'):
            endereco_partes.append(self.cliente_data['bairro'])
        if self.cliente_data.get('cidade'):
            endereco_partes.append(self.cliente_data['cidade'])
        if self.cliente_data.get('estado'):
            endereco_partes.append(self.cliente_data['estado'])
        
        if endereco_partes:
            dados.append(f"Endereço: {' - '.join(endereco_partes)}")
        
        if self.cliente_data.get('referencia'):
            dados.append(f"Referência: {self.cliente_data['referencia']}")
        
        dados.append("")
        dados.append("======================")
        
        return "\n".join(dados)
    
    def copiar_dados(self):
        """Copia os dados para a área de transferência"""
        try:
            pyperclip.copy(self.texto_dados.toPlainText())
            self.resultado = 'copiar'
            self.accept()
        except Exception:
            # Fallback se pyperclip não funcionar
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(self.texto_dados.toPlainText())
            self.resultado = 'copiar'
            self.accept()
    
    def confirmar_dados(self):
        """Confirma e salva os dados"""
        self.resultado = 'confirmar'
        self.accept()
    
    def get_resultado(self):
        """Retorna o resultado da ação do usuário"""
        return self.resultado
