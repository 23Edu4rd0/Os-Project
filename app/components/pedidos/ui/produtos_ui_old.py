from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QComboBox, QCheckBox, QGroupBox, QFormLayout, 
                             QScrollArea, QSpinBox, QCompleter, QFrame, QGridLayout)
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt, QStringListModel

"""
Cria os widgets e layouts para a seção de produtos - Design Moderno com Cards.
Export: criar_produtos_ui(self, parent_layout, pedido_data)
Retorna: dict com widgets criados
"""

def criar_produtos_ui(self, parent_layout, pedido_data):
    # Container principal da seção
    produtos_container = QFrame()
    produtos_container.setFrameStyle(QFrame.Shape.StyledPanel)
    produtos_container.setStyleSheet("""
        QFrame {
            background-color: #1e1e1e;
            border: 2px solid #666666;
            border-radius: 12px;
            margin: 8px 0px;
        }
        QLabel {
            color: #ffffff;
            font-weight: 500;
            background: transparent;
            border: none;
        }
        QLineEdit, QComboBox {
            background-color: #404040;
            border: 2px solid #666666;
            border-radius: 8px;
            padding: 10px 12px;
            font-size: 14px;
            color: #ffffff;
            min-height: 20px;
        }
        QLineEdit:focus, QComboBox:focus {
            border-color: #999999;
            background-color: #505050;
            outline: none;
        }
        QLineEdit:hover, QComboBox:hover {
            border-color: #888888;
            background-color: #505050;
        }
        QPushButton {
            background-color: #27ae60;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            padding: 12px 20px;
            min-height: 40px;
        }
        QPushButton:hover {
            background-color: #229954;
        }
        QPushButton:pressed {
            background-color: #1e8449;
        }
        QSpinBox {
            background-color: #404040;
            border: 2px solid #666666;
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
            color: #ffffff;
        }
        QSpinBox:focus {
            border-color: #999999;
            background-color: #505050;
        }
        QSpinBox:hover {
            border-color: #888888;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #666666;
            border: none;
            width: 20px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #777777;
        }
        QComboBox::drop-down {
            border: none;
            width: 25px;
        }
        QComboBox::down-arrow {
            border: 3px solid transparent;
            border-top: 6px solid #ffffff;
            margin-right: 5px;
        }
        QComboBox QAbstractItemView {
            background-color: #404040;
            color: #ffffff;
            selection-background-color: #666666;
            border: 1px solid #666666;
        }
    """)
    
    container_layout = QVBoxLayout(produtos_container)
    container_layout.setContentsMargins(20, 15, 20, 20)
    container_layout.setSpacing(15)
    
    # Título da seção
    title_label = QLabel("🛍️ Produtos do Pedido")
    title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
    title_label.setStyleSheet("""
        QLabel {
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            padding: 0px 0px 10px 0px;
            border-bottom: 2px solid #666666;
            margin-bottom: 5px;
        }
    """)
    container_layout.addWidget(title_label)
    
    # Card para entrada de produtos
    entrada_card = QFrame()
    entrada_card.setFrameStyle(QFrame.Shape.Box)
    entrada_card.setStyleSheet("""
        QFrame {
            background-color: #2d2d2d;
            border: 1px solid #666666;
            border-radius: 10px;
            padding: 10px;
        }
    """)
    entrada_layout = QVBoxLayout(entrada_card)
    entrada_layout.setContentsMargins(15, 15, 15, 15)
    entrada_layout.setSpacing(12)
    
    # Subtítulo
    subtitle = QLabel("Adicionar Produto")
    subtitle.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
    subtitle.setStyleSheet("color: #ffffff; margin-bottom: 5px; font-weight: 600;")
    entrada_layout.addWidget(subtitle)
    
    # Campo de produto (largura total)
    prod_label = QLabel("Nome do Produto:")
    prod_label.setStyleSheet("font-weight: 600; color: #ffffff;")
    entrada_layout.addWidget(prod_label)
    
    input_produto = QLineEdit()
    input_produto.setPlaceholderText("Digite o nome do produto...")
    input_produto.setClearButtonEnabled(True)
    
    # Configurar autocomplete para produtos
    try:
        from database import db_manager
        produtos_existentes = db_manager.listar_produtos()
        nomes_produtos = [produto[1] for produto in produtos_existentes if produto[1]]
        
        completer = QCompleter(nomes_produtos)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        input_produto.setCompleter(completer)
    except Exception as e:
        print(f"Erro ao configurar autocomplete: {e}")
        
    entrada_layout.addWidget(input_produto)
    
    # Layout horizontal simples: Valor e Cor lado a lado
    linha_horizontal = QHBoxLayout()
    linha_horizontal.setSpacing(15)
    
    # Coluna do Valor
    valor_container = QVBoxLayout()
    valor_label = QLabel("Valor (R$):")
    valor_label.setStyleSheet("font-weight: 600; color: #ffffff;")
    valor_container.addWidget(valor_label)
    
    input_valor = QLineEdit()
    input_valor.setPlaceholderText("0,00")
    input_valor.setMinimumWidth(120)
    valor_container.addWidget(input_valor)
    
    linha_horizontal.addLayout(valor_container)
    
    # Coluna da Cor
    cor_container = QVBoxLayout()
    cor_label = QLabel("Cor:")
    cor_label.setStyleSheet("font-weight: 600; color: #ffffff;")
    cor_container.addWidget(cor_label)
    
    campos_cor = QComboBox()
    campos_cor.addItems(["", "Preto", "Branco", "Azul", "Vermelho", "Verde", "Amarelo", "Cinza", "Marrom", "Rosa", "Roxo"])
    campos_cor.setMinimumWidth(120)
    cor_container.addWidget(campos_cor)
    
    linha_horizontal.addLayout(cor_container)
    
    entrada_layout.addLayout(linha_horizontal)
    
    # Botão adicionar
    btn_add = QPushButton("➕ Adicionar Produto")
    btn_add.setMinimumHeight(45)
    entrada_layout.addWidget(btn_add)
    
    container_layout.addWidget(entrada_card)
    
    # Card para lista de produtos adicionados
    lista_card = QFrame()
    lista_card.setFrameStyle(QFrame.Shape.Box)
    lista_card.setStyleSheet("""
        QFrame {
            background-color: #2d2d2d;
            border: 1px solid #666666;
            border-radius: 10px;
            padding: 10px;
            min-height: 120px;
        }
    """)
    lista_layout = QVBoxLayout(lista_card)
    lista_layout.setContentsMargins(15, 15, 15, 15)
    
    lista_title = QLabel("📋 Produtos Adicionados")
    lista_title.setFont(QFont("Segoe UI", 14, QFont.Weight.DemiBold))
    lista_title.setStyleSheet("color: #ffffff; margin-bottom: 10px; font-weight: 600;")
    lista_layout.addWidget(lista_title)
    
    # Container para lista de produtos (será preenchido dinamicamente)
    lista_produtos_container = QVBoxLayout()
    lista_produtos_container.setSpacing(6)
    lista_layout.addLayout(lista_produtos_container)
    container_layout.addWidget(lista_card)
    
    # Card para valor total
    total_card = QFrame()
    total_card.setFrameStyle(QFrame.Shape.Box)
    total_card.setStyleSheet("""
        QFrame {
            background-color: #2d2d2d;
            border: 2px solid #27ae60;
            border-radius: 10px;
            padding: 10px;
        }
    """)
    total_layout = QHBoxLayout(total_card)
    total_layout.setContentsMargins(15, 12, 15, 12)
    
    total_label = QLabel("💰 Valor Total (R$):")
    total_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
    total_label.setStyleSheet("color: #27ae60; font-weight: bold;")
    total_layout.addWidget(total_label)
    
    valor_total = QLineEdit()
    valor_total.setReadOnly(True)
    valor_total.setPlaceholderText("0.00")
    valor_total.setStyleSheet("""
        QLineEdit {
            background-color: #404040;
            border: 2px solid #27ae60;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 16px;
            font-weight: bold;
            color: #27ae60;
            min-width: 120px;
        }
    """)
    total_layout.addWidget(valor_total)
    total_layout.addStretch()
    
    container_layout.addWidget(total_card)
    
    # Adicionar container principal ao layout pai
    parent_layout.addWidget(produtos_container)
    
    # Conectar eventos de entrada
    try:
        input_valor.returnPressed.connect(lambda: btn_add.click())
        input_produto.returnPressed.connect(lambda: btn_add.click())
    except Exception:
        pass
    
    # Retornar widgets para compatibilidade com o modal
    widgets = {
        'input_desc': input_produto,  # Mapeamento para compatibilidade
        'input_produto': input_produto,
        'btn_add': btn_add,
        'input_valor': input_valor,
        'campos_cor': campos_cor,
        'valor_total': valor_total,
        'lista_produtos_container': lista_produtos_container,
        'container_widget': produtos_container
    }
    return widgets