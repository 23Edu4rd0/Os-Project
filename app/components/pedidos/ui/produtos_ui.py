from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
                             QLineEdit, QComboBox, QCheckBox, QGroupBox, QFormLayout, 
                             QScrollArea, QSpinBox, QCompleter)
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt, QStringListModel

"""
Cria os widgets e layouts para a seção de produtos - Layout Compacto.
Export: criar_produtos_ui(self, parent_layout, pedido_data)
Retorna: dict com widgets criados (input_produto, input_valor, campos_div, campos_cor, container_widget)
"""

def criar_produtos_ui(self, parent_layout, pedido_data):
    # Group box com título
    produtos_group = QGroupBox("📦 Produtos do Pedido")
    produtos_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    produtos_layout = QVBoxLayout(produtos_group)
    
    # Layout compacto principal - tudo em uma linha
    linha_principal = QHBoxLayout()
    linha_principal.setSpacing(15)
    
    # 1. Campo de produto com autocomplete (maior parte do espaço)
    input_produto = QLineEdit()
    input_produto.setPlaceholderText('Insira o produto...')
    input_produto.setClearButtonEnabled(True)
    input_produto.setMinimumWidth(250)
    
    # Configurar autocomplete para produtos
    try:
        from database.db_manager import db_manager
        produtos_existentes = db_manager.listar_produtos()
        nomes_produtos = [produto[1] for produto in produtos_existentes if produto[1]]  # índice 1 = nome
        
        completer = QCompleter(nomes_produtos)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        input_produto.setCompleter(completer)
    except Exception as e:
        print(f"Erro ao configurar autocomplete: {e}")
    
    linha_principal.addWidget(QLabel("Produto:"))
    linha_principal.addWidget(input_produto, 1)  # Flex grow
    
    # 2. Campo de valor na mesma linha
    input_valor = QLineEdit()
    input_valor.setPlaceholderText('Valor (R$)')
    input_valor.setFixedWidth(120)
    linha_principal.addWidget(QLabel("Valor:"))
    linha_principal.addWidget(input_valor)
    
    # 3. Botão adicionar na mesma linha
    btn_add = QPushButton('+ Adicionar')
    btn_add.setFixedHeight(32)
    btn_add.setMinimumWidth(100)
    btn_add.setStyleSheet('''
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
            padding: 6px 12px;
        }
        QPushButton:hover { 
            background-color: #45a049; 
        }
        QPushButton:pressed { 
            background-color: #3d8b40; 
        }
    ''')
    try:
        btn_add.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    except:
        pass
    linha_principal.addWidget(btn_add)
    
    produtos_layout.addLayout(linha_principal)
    
    # Segunda linha - Divisórias e Cor
    linha_secundaria = QHBoxLayout()
    linha_secundaria.setSpacing(20)
    
    # Divisórias
    linha_secundaria.addWidget(QLabel("Divisórias:"))
    campos_div = QSpinBox()
    campos_div.setMinimum(0)
    campos_div.setMaximum(99)
    campos_div.setValue(0)
    campos_div.setFixedSize(80, 32)
    campos_div.setStyleSheet('''
        QSpinBox {
            background-color: #404040;
            border: 2px solid #666666;
            border-radius: 6px;
            color: #ffffff;
            font-size: 13px;
            padding: 4px 8px;
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
    ''')
    linha_secundaria.addWidget(campos_div)
    
    linha_secundaria.addStretch()
    
    # Cor
    linha_secundaria.addWidget(QLabel("Cor:"))
    campos_cor = QComboBox()
    campos_cor.addItems(['', 'Branco', 'Amarelo', 'Azul', 'Verde', 'Vermelho', 'Preto', 'Personalizado'])
    campos_cor.setFixedWidth(150)
    campos_cor.setStyleSheet('''
        QComboBox {
            background-color: #404040;
            border: 2px solid #666666;
            border-radius: 6px;
            color: #ffffff;
            font-size: 13px;
            padding: 4px 8px;
            min-height: 20px;
        }
        QComboBox:focus {
            border-color: #999999;
            background-color: #505050;
        }
        QComboBox:hover {
            border-color: #888888;
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
    ''')
    linha_secundaria.addWidget(campos_cor)
    
    linha_secundaria.addStretch()
    
    produtos_layout.addLayout(linha_secundaria)
    
    # Lista de produtos adicionados em tabela
    lista_label = QLabel('Produtos adicionados:')
    lista_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
    lista_label.setStyleSheet('color: #ffffff; margin: 15px 0 5px 0; background: transparent;')
    produtos_layout.addWidget(lista_label)
    
    from PyQt6.QtWidgets import QTableWidget, QHeaderView
    lista_table = QTableWidget(0, 5)  # 5 colunas: Nome, Valor, Cor, Divisórias, Ações
    lista_table.setHorizontalHeaderLabels(['Nome', 'Valor (R$)', 'Cor', 'Divisórias', 'Ações'])
    
    # Configurar redimensionamento das colunas
    header = lista_table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Nome - ocupa espaço restante
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Valor - largura fixa
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Cor - largura fixa  
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Divisórias - largura fixa
    header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Ações - largura fixa
    
    # Definir larguras específicas
    lista_table.setColumnWidth(1, 100)  # Valor
    lista_table.setColumnWidth(2, 100)  # Cor
    lista_table.setColumnWidth(3, 80)   # Divisórias
    lista_table.setColumnWidth(4, 80)   # Ações
    
    # Estilo da tabela - tema simplificado
    lista_table.setStyleSheet('''
        QTableWidget {
            background-color: #404040;
            border: 2px solid #666666;
            border-radius: 6px;
            color: #ffffff;
            gridline-color: #666666;
            font-size: 13px;
        }
        QHeaderView::section {
            background-color: #666666;
            color: #ffffff;
            padding: 8px;
            font-weight: 600;
            border: none;
            border-right: 1px solid #888888;
        }
        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #666666;
            background: transparent;
        }
        QTableWidget::item:selected {
            background-color: #666666;
        }
        QTableWidget::item:hover {
            background-color: #555555;
        }
    ''')
    
    lista_table.setMaximumHeight(200)
    produtos_layout.addWidget(lista_table)
    
    
    # Valor total na parte inferior
    linha_total = QHBoxLayout()
    linha_total.addStretch()
    linha_total.addWidget(QLabel("Valor Total (R$):"))
    valor_total = QLineEdit()
    valor_total.setReadOnly(True)
    valor_total.setPlaceholderText('0,00')
    valor_total.setFixedWidth(140)
    valor_total.setStyleSheet('''
        QLineEdit {
            background-color: #404040;
            border: 2px solid #666666;
            border-radius: 6px;
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            padding: 6px 8px;
            text-align: right;
        }
    ''')
    linha_total.addWidget(valor_total)
    produtos_layout.addLayout(linha_total)

    # Aplicar estilo geral ao grupo
    produtos_group.setStyleSheet('''
        QGroupBox {
            background-color: #1a1a1a;
            border: 2px solid #404040;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            font-size: 14px;
            color: #e0e0e0;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: #ffffff;
            font-weight: bold;
        }
        QLabel {
            color: #e0e0e0;
            font-size: 13px;
        }
    ''')

    # Adicionar ao parent layout
    parent_layout.addWidget(produtos_group)

    # Retornar widgets atualizados para compatibilidade
    widgets = {
        'produtos_group': produtos_group,
        'input_desc': input_produto,  # Mapeamento para compatibilidade
        'input_produto': input_produto,  # Nome novo
        'btn_add': btn_add,
        'input_valor': input_valor,
        'campos_cor': campos_cor,
        'campos_div': campos_div,
        'lista_table': lista_table,
        'valor_total': valor_total,
        'container_widget': produtos_group
    }
    return widgets
