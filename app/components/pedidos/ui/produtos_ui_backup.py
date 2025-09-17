from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QComboBox, QCompleter, QFrame)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

"""
Formulário de produtos - Design Limpo e Simples
Export: criar_produtos_ui(self, parent_layout, pedido_data)
Retorna: dict com widgets criados
"""

def criar_produtos_ui(self, parent_layout, pedido_data):
    # Container principal - design simples e clean
    produtos_container = QFrame()
    produtos_container.setStyleSheet("""
        QFrame {
            background-color: #2b2b2b;
            border: 1px solid #555555;
            border-radius: 8px;
            padding: 20px;
        }
    """)
    
    # Layout principal
    main_layout = QVBoxLayout(produtos_container)
    main_layout.setSpacing(20)
    main_layout.setContentsMargins(0, 0, 0, 0)
    
    # Título simples
    titulo = QLabel("Produtos do Pedido")
    titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
    titulo.setStyleSheet("color: #ffffff; margin-bottom: 10px;")
    main_layout.addWidget(titulo)
    
    # Formulário de entrada - uma linha só
    form_layout = QHBoxLayout()
    form_layout.setSpacing(15)
    
    # Campo Produto
    input_produto = QLineEdit()
    input_produto.setPlaceholderText("Nome do produto...")
    input_produto.setStyleSheet("""
        QLineEdit {
            background-color: #404040;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 8px;
            color: #ffffff;
            font-size: 13px;
            min-width: 200px;
        }
        QLineEdit:focus {
            border-color: #4CAF50;
        }
    """)
    
    # Autocomplete
    try:
        from database import db_manager
        produtos_existentes = db_manager.listar_produtos()
        nomes_produtos = [produto[1] for produto in produtos_existentes if produto[1]]
        completer = QCompleter(nomes_produtos)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        input_produto.setCompleter(completer)
    except:
        pass
    
    # Campo Valor
    input_valor = QLineEdit()
    input_valor.setPlaceholderText("Valor")
    input_valor.setStyleSheet("""
        QLineEdit {
            background-color: #404040;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 8px;
            color: #ffffff;
            font-size: 13px;
            max-width: 100px;
        }
        QLineEdit:focus {
            border-color: #4CAF50;
        }
    """)
    
    # Campo Cor
    campos_cor = QComboBox()
    campos_cor.addItems(["Selecione", "Preto", "Branco", "Azul", "Vermelho", "Verde", "Amarelo", "Cinza", "Marrom", "Rosa", "Roxo"])
    campos_cor.setStyleSheet("""
        QComboBox {
            background-color: #404040;
            border: 1px solid #666666;
            border-radius: 4px;
            padding: 8px;
            color: #ffffff;
            font-size: 13px;
            min-width: 120px;
        }
        QComboBox:focus {
            border-color: #4CAF50;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border: 2px solid transparent;
            border-top: 4px solid #ffffff;
            margin-right: 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #404040;
            color: #ffffff;
            selection-background-color: #4CAF50;
            border: 1px solid #666666;
        }
    """)
    
    # Botão Adicionar
    btn_add = QPushButton("Adicionar")
    btn_add.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 20px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """)
    
    # Adicionar campos ao layout horizontal
    form_layout.addWidget(input_produto)
    form_layout.addWidget(input_valor)
    form_layout.addWidget(campos_cor)
    form_layout.addWidget(btn_add)
    form_layout.addStretch()
    
    main_layout.addLayout(form_layout)
    
    # Lista de produtos adicionados
    lista_produtos_container = QVBoxLayout()
    lista_produtos_container.setSpacing(5)
    main_layout.addLayout(lista_produtos_container)
    
    # Valor total
    total_layout = QHBoxLayout()
    total_layout.addStretch()
    
    total_label = QLabel("Total: R$")
    total_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px;")
    
    valor_total = QLineEdit()
    valor_total.setReadOnly(True)
    valor_total.setText("0,00")
    valor_total.setStyleSheet("""
        QLineEdit {
            background-color: #404040;
            border: 1px solid #4CAF50;
            border-radius: 4px;
            padding: 8px;
            color: #4CAF50;
            font-size: 14px;
            font-weight: bold;
            max-width: 100px;
        }
    """)
    
    total_layout.addWidget(total_label)
    total_layout.addWidget(valor_total)
    
    main_layout.addLayout(total_layout)
    
    # Adicionar ao layout pai
    parent_layout.addWidget(produtos_container)
    
    # Conectar eventos
    try:
        input_valor.returnPressed.connect(lambda: btn_add.click())
        input_produto.returnPressed.connect(lambda: btn_add.click())
    except:
        pass
    
    # Retornar widgets
    widgets = {
        'input_desc': input_produto,
        'input_produto': input_produto,
        'btn_add': btn_add,
        'input_valor': input_valor,
        'campos_cor': campos_cor,
        'valor_total': valor_total,
        'lista_produtos_container': lista_produtos_container,
        'container_widget': produtos_container
    }
    return widgets