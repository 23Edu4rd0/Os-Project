
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from .__init__ import PedidosModal

def _criar_header(self, layout, numero_os, is_edit):
    # Container principal do header
    header_container = QFrame()
    header_container.setStyleSheet("""
        QFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0d7377, stop:0.5 #14a085, stop:1 #0d7377);
            border-radius: 15px;
            padding: 10px;
            margin-bottom: 20px;
        }
    """)
    
    header_layout = QVBoxLayout(header_container)
    header_layout.setContentsMargins(25, 20, 25, 20)
    header_layout.setSpacing(8)
    
    # Ícone e título principal
    titulo_container = QFrame()
    titulo_container.setStyleSheet("background: transparent;")
    titulo_layout = QVBoxLayout(titulo_container)
    titulo_layout.setContentsMargins(0, 0, 0, 0)
    titulo_layout.setSpacing(5)
    
    # Ícone
    icone_label = QLabel("📋")
    icone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icone_label.setStyleSheet("""
        font-size: 28px;
        background: rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 8px;
        margin-bottom: 5px;
    """)
    icone_label.setFixedSize(50, 50)
    titulo_layout.addWidget(icone_label, alignment=Qt.AlignmentFlag.AlignCenter)
    
    # Título principal
    if is_edit and numero_os is not None:
        titulo = f"Editar Ordem de Serviço"
        numero_texto = f"OS #{numero_os:05d}"
    elif is_edit:
        titulo = "Editar Ordem de Serviço"
        numero_texto = ""
    else:
        titulo = "Nova Ordem de Serviço"
        numero_texto = f"OS #{numero_os:05d}" if numero_os else ""
    
    titulo_label = QLabel(titulo)
    titulo_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
    titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    titulo_label.setStyleSheet("""
        color: white;
        background: transparent;
        font-weight: 700;
        margin: 0px;
    """)
    titulo_layout.addWidget(titulo_label)
    
    # Número da OS (se houver)
    if numero_texto:
        numero_label = QLabel(numero_texto)
        numero_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Medium))
        numero_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        numero_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 6px 16px;
            margin: 5px 50px;
        """)
        titulo_layout.addWidget(numero_label)
    
    header_layout.addWidget(titulo_container)
    
    # Informações adicionais do cliente (se disponível)
    try:
        dados = getattr(self, 'model', None)
        if dados and getattr(dados, 'dados', None):
            md = dados.dados
            nome_cliente = md.get('nome_cliente') or md.get('nome') or ''
            cpf = md.get('cpf_cliente') or md.get('cpf') or ''
            
            if nome_cliente or cpf:
                info_container = QFrame()
                info_container.setStyleSheet("""
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 5px;
                """)
                info_layout = QVBoxLayout(info_container)
                info_layout.setContentsMargins(15, 10, 15, 10)
                info_layout.setSpacing(3)
                
                if nome_cliente:
                    cliente_label = QLabel(f"Cliente: {nome_cliente}")
                    cliente_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
                    cliente_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cliente_label.setStyleSheet("color: rgba(255, 255, 255, 0.95); background: transparent;")
                    info_layout.addWidget(cliente_label)
                
                if cpf:
                    cpf_label = QLabel(f"CPF: {cpf}")
                    cpf_label.setFont(QFont("Segoe UI", 10))
                    cpf_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cpf_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); background: transparent;")
                    info_layout.addWidget(cpf_label)
                
                header_layout.addWidget(info_container)
    except Exception:
        pass
    
    layout.addWidget(header_container)
