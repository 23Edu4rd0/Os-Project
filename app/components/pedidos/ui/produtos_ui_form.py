from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QComboBox, QCompleter, QFrame, QFormLayout, QGroupBox)
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtCore import Qt

"""
Formulário Tradicional de Produtos
Export: criar_produtos_ui(self, parent_layout, pedido_data)
Retorna: dict com widgets criados
"""

def criar_produtos_ui(self, parent_layout, pedido_data):
    # Campo 2: Quantidade
    quantidade_label = QLabel("Quantidade:")
    quantidade_label.setStyleSheet(label_style)
    input_quantidade = QLineEdit()
    input_quantidade.setPlaceholderText("1")
    input_quantidade.setText("1")
    input_quantidade.setStyleSheet(input_style)
    input_quantidade.setValidator(QIntValidator(1, 9999))
    form_layout.addRow(quantidade_label, input_quantidade)
    # Container principal
    produtos_container = QGroupBox("Produtos do Pedido")
    produtos_container.setFont(QFont("Arial", 12, QFont.Weight.Bold))
    produtos_container.setStyleSheet("""
        QGroupBox {
            color: #ffffff;
            border: 2px solid #666666;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #333333;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: #ffffff;
            font-weight: bold;
        }
    """)
    
    # Layout principal do grupo
    main_layout = QVBoxLayout(produtos_container)
    main_layout.setSpacing(15)
    main_layout.setContentsMargins(15, 20, 15, 15)
    
    # Formulário tradicional
    form_widget = QFrame()
    form_widget.setStyleSheet("""
        QFrame {
            background-color: #3a3a3a;
            border: 1px solid #555555;
            border-radius: 6px;
            padding: 15px;
        }
    """)
    
    form_layout = QFormLayout(form_widget)
    form_layout.setSpacing(12)
    form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
    
    # Estilo para labels
    label_style = """
        QLabel {
            color: #ffffff;
            font-weight: bold;
            font-size: 12px;
            min-width: 100px;
        }
    """
    
    # Estilo para campos de entrada
    input_style = """
        QLineEdit, QComboBox {
            background-color: #505050;
            border: 1px solid #777777;
            border-radius: 4px;
            padding: 8px;
            color: #ffffff;
            font-size: 12px;
            min-height: 20px;
        }
        QLineEdit:focus, QComboBox:focus {
            border-color: #4CAF50;
            background-color: #555555;
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
            background-color: #505050;
            color: #ffffff;
            selection-background-color: #4CAF50;
            border: 1px solid #777777;
        }
    """
    
    # Campo 1: Nome do Produto
    produto_label = QLabel("Produto:")
    produto_label.setStyleSheet(label_style)
    
    input_produto = QLineEdit()
    input_produto.setPlaceholderText("Digite o nome do produto")
    input_produto.setStyleSheet(input_style)
    
    # Autocomplete para produtos
    try:
        from database import db_manager
        produtos_existentes = db_manager.listar_produtos()
        nomes_produtos = [produto[1] for produto in produtos_existentes if produto[1]]
        completer = QCompleter(nomes_produtos)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        input_produto.setCompleter(completer)
    except:
        pass
    
    form_layout.addRow(produto_label, input_produto)
    
    # Campo 2: Valor
    valor_label = QLabel("Valor (R$):")
    valor_label.setStyleSheet(label_style)
    
    input_valor = QLineEdit()
    input_valor.setPlaceholderText("0,00")
    input_valor.setStyleSheet(input_style)
    
    form_layout.addRow(valor_label, input_valor)
    
    # Campo 3: Cor
    cor_label = QLabel("Cor:")
    cor_label.setStyleSheet(label_style)
    
    campos_cor = QComboBox()
    campos_cor.addItems(["Selecione uma cor", "Preto", "Branco", "Azul", "Vermelho", "Verde", "Amarelo", "Cinza", "Marrom", "Rosa", "Roxo"])
    campos_cor.setStyleSheet(input_style)
    
    form_layout.addRow(cor_label, campos_cor)
    
    # Botão Adicionar
    btn_add = QPushButton("Adicionar Produto")
    btn_add.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: bold;
            margin-top: 10px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """)
    
    form_layout.addRow("", btn_add)
    
    main_layout.addWidget(form_widget)
    
    # Separador visual
    separador = QFrame()
    separador.setFrameShape(QFrame.Shape.HLine)
    separador.setStyleSheet("color: #666666; margin: 10px 0px;")
    main_layout.addWidget(separador)
    
    # Lista de produtos adicionados
    lista_label = QLabel("Produtos Adicionados:")
    lista_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
    lista_label.setStyleSheet("color: #ffffff; margin-bottom: 5px;")
    main_layout.addWidget(lista_label)
    
    # Container para lista
    lista_produtos_container = QVBoxLayout()
    lista_produtos_container.setSpacing(3)
    main_layout.addLayout(lista_produtos_container)
    
    # Valor total
    total_frame = QFrame()
    total_frame.setStyleSheet("""
        QFrame {
            background-color: #2a5a2a;
            border: 1px solid #4CAF50;
            border-radius: 6px;
            padding: 10px;
            margin-top: 10px;
        }
    """)
    
    total_layout = QHBoxLayout(total_frame)
    total_layout.setContentsMargins(10, 5, 10, 5)
    
    total_label = QLabel("Total Geral:")
    total_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
    total_label.setStyleSheet("color: #ffffff;")
    
    valor_total = QLineEdit()
    valor_total.setReadOnly(True)
    valor_total.setText("R$ 0,00")
    valor_total.setStyleSheet("""
        QLineEdit {
            background-color: #ffffff;
            border: 1px solid #4CAF50;
            border-radius: 4px;
            padding: 8px;
            color: #2a5a2a;
            font-size: 13px;
            font-weight: bold;
            max-width: 120px;
        }
    """)
    
    total_layout.addWidget(total_label)
    total_layout.addStretch()
    total_layout.addWidget(valor_total)
    
    main_layout.addWidget(total_frame)
    
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