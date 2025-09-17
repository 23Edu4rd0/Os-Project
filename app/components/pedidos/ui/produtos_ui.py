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
    
    # --- FORMULÁRIO VERTICAL: produto / valor / cor ---
    form_col = QVBoxLayout()
    form_col.setSpacing(8)

    # Produto
    produto_label = QLabel('Produto')
    produto_label.setStyleSheet('color: #ffffff; font-weight: 600;')
    input_produto = QLineEdit()
    input_produto.setPlaceholderText('Insira o produto...')
    input_produto.setClearButtonEnabled(True)
    input_produto.setMinimumWidth(360)
    form_col.addWidget(produto_label)
    form_col.addWidget(input_produto)

    # Valor
    valor_label = QLabel('Valor (R$)')
    valor_label.setStyleSheet('color: #ffffff; font-weight: 600;')
    input_valor = QLineEdit()
    input_valor.setPlaceholderText('0,00')
    input_valor.setFixedWidth(160)
    form_col.addWidget(valor_label)
    form_col.addWidget(input_valor)

    # Cor
    cor_label = QLabel('Cor')
    cor_label.setStyleSheet('color: #ffffff; font-weight: 600;')
    campos_cor = QComboBox()
    campos_cor.addItems(['', 'Branco', 'Amarelo', 'Azul', 'Verde', 'Vermelho', 'Preto', 'Personalizado'])
    campos_cor.setFixedWidth(220)
    form_col.addWidget(cor_label)
    form_col.addWidget(campos_cor)

    # Botão adicionar alinhado à direita
    btn_row = QHBoxLayout()
    btn_row.addStretch()
    btn_add = QPushButton('+ Adicionar')
    btn_add.setFixedHeight(32)
    btn_add.setMinimumWidth(120)
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
        QPushButton:hover { background-color: #45a049; }
        QPushButton:pressed { background-color: #3d8b40; }
    ''')
    btn_row.addWidget(btn_add)
    form_col.addLayout(btn_row)

    produtos_layout.addLayout(form_col)
    
    # Lista de produtos adicionados em tabela
    lista_label = QLabel('Produtos adicionados:')
    lista_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
    lista_label.setStyleSheet('color: #ffffff; margin: 15px 0 5px 0; background: transparent;')
    produtos_layout.addWidget(lista_label)
    
    from PyQt6.QtWidgets import QTableWidget, QHeaderView

    # Tabela de produtos: colunas -> Nome, Código, Valor, Cor, Ações
    lista_table = QTableWidget(0, 5)
    lista_table.setHorizontalHeaderLabels(['Nome', 'Código', 'Valor (R$)', 'Cor', 'Ações'])

    # Configurar redimensionamento das colunas
    header = lista_table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Nome - ocupa espaço restante
    # Código, Valor, Cor, Ações terão largura fixa
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
    header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

    # Definir larguras específicas para colunas fixas
    lista_table.setColumnWidth(1, 80)   # Código - pequeno
    lista_table.setColumnWidth(2, 120)  # Valor
    lista_table.setColumnWidth(3, 120)  # Cor
    lista_table.setColumnWidth(4, 260)  # Ações - aumentado para caber botões

    # Ajustes de aparência e altura das linhas
    lista_table.verticalHeader().setVisible(False)
    lista_table.setShowGrid(False)
    lista_table.setAlternatingRowColors(False)
    lista_table.verticalHeader().setDefaultSectionSize(44)  # altura padrão das linhas
    lista_table.setWordWrap(False)

    # Estilo da tabela
    lista_table.setStyleSheet('''
        QTableWidget {
            background-color: #404040;
            color: #ffffff;
            border: none;
            gridline-color: #555555;
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
            padding: 10px 12px;
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
        'lista_table': lista_table,
        'valor_total': valor_total,
        'container_widget': produtos_group
    }
    return widgets
