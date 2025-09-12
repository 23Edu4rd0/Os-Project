from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QGroupBox, QFormLayout, QScrollArea
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt

"""
Cria os widgets e layouts para a seção de produtos.
Export: criar_produtos_ui(self, parent_layout, pedido_data)
Retorna: dict com widgets criados (input_desc, input_valor, campos, container_widget)
"""

def criar_produtos_ui(self, parent_layout, pedido_data):
    # Group box com título
    produtos_group = QGroupBox("📦 Produtos do Pedido")
    produtos_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    produtos_layout = QFormLayout(produtos_group)
    produtos_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
    produtos_layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)

    # Produto: campo grande + botões à direita
    row_top = QHBoxLayout()
    input_desc = QLineEdit()
    input_desc.setPlaceholderText('Digite o nome do produto...')
    input_desc.setClearButtonEnabled(True)
    input_desc.setMinimumWidth(300)
    row_top.addWidget(input_desc, 1)

    tools = QHBoxLayout()
    tools.setSpacing(6)
    btn_limpar = QPushButton('Limpar')
    btn_limpar.setFixedHeight(28)
    btn_limpar.setMinimumWidth(70)
    btn_limpar.setToolTip('Limpar produto')
    # Destaque visual: style e cursor (compatibilidade com diferentes versões do PyQt6)
    try:
        cursor_shape = Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else getattr(Qt, 'PointingHandCursor')
    except Exception:
        cursor_shape = getattr(Qt, 'PointingHandCursor', 0)
    btn_limpar.setCursor(QCursor(cursor_shape))
    btn_limpar.setStyleSheet('''
        QPushButton {
            background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffcf9a, stop:1 #ffb86c);
            color: #1b1b1b;
            border: 1px solid #d98b3a;
            border-radius: 6px;
            font-weight: 600;
            padding: 4px 8px;
        }
        QPushButton:hover { background-color: #ffc78a; }
    ''')
    tools.addWidget(btn_limpar)
    btn_add = QPushButton('+ Adicionar')
    btn_add.setFixedHeight(28)
    btn_add.setMinimumWidth(90)
    btn_add.setToolTip('Adicionar produto')
    # Destaque visual: style e cursor (verde de ação)
    try:
        cursor_shape = Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else getattr(Qt, 'PointingHandCursor')
    except Exception:
        cursor_shape = getattr(Qt, 'PointingHandCursor', 0)
    btn_add.setCursor(QCursor(cursor_shape))
    btn_add.setStyleSheet('''
        QPushButton {
            background-color: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #7ef99a, stop:1 #2fb86a);
            color: #0b0b0b;
            border: 1px solid #27a85a;
            border-radius: 6px;
            font-weight: 700;
            padding: 4px 10px;
        }
        QPushButton:hover { background-color: #58e081; }
    ''')
    tools.addWidget(btn_add)
    row_top.addLayout(tools)
    produtos_layout.addRow('Produto:', row_top)

    # Valor (sem categoria)
    input_valor = QLineEdit()
    input_valor.setPlaceholderText('Valor (R$)')
    input_valor.setFixedWidth(140)
    produtos_layout.addRow('Valor:', input_valor)

    # Cor e Reforço
    campos_cor = QComboBox(); campos_cor.addItems(['', 'Branco', 'Amarelo', 'Azul', 'Verde', 'Personalizado'])
    campos_cor.setFixedWidth(220)
    # Divisórias (SpinBox)
    from PyQt6.QtWidgets import QSpinBox, QLabel
    campos_div = QSpinBox()
    campos_div.setMinimum(0)
    campos_div.setMaximum(99)
    campos_div.setValue(0)
    campos_div.setFixedSize(80, 30)
    # Estilo do SpinBox
    try:
        campos_div.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    except Exception:
        try:
            campos_div.setCursor(QCursor(getattr(Qt, 'PointingHandCursor', 0)))
        except Exception:
            pass
    
    campos_div.setStyleSheet('''
        QSpinBox {
            background-color: #404040;
            border: 1px solid #606060;
            border-radius: 4px;
            color: #ffffff;
            font-size: 12px;
            padding: 4px;
        }
        QSpinBox:focus {
            border: 2px solid #0d7377;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background-color: #505050;
            border: none;
            width: 16px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background-color: #0d7377;
        }
    ''')
    
    # Label para divisórias
    div_label = QLabel('Divisórias:')
    div_label.setStyleSheet('color: #ffffff; font-size: 12px;')
    
    # Layout para divisórias
    div_layout = QHBoxLayout()
    div_layout.addWidget(div_label)
    div_layout.addWidget(campos_div)
    div_layout.addWidget(campos_cor)
    div_layout.addStretch()
    
    produtos_layout.addRow('Cor / Divisórias:', div_layout)

    # Lista de produtos adicionados em tabela
    lista_label = QLabel('Produtos adicionados:')
    lista_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
    lista_label.setStyleSheet('color: #ffffff; margin-bottom: 5px;')
    
    from PyQt6.QtWidgets import QTableWidget, QHeaderView
    lista_table = QTableWidget(0, 5)  # 5 colunas: Nome, Quantidade, Cor, Divisórias, Ações
    lista_table.setHorizontalHeaderLabels(['Nome', 'Valor (R$)', 'Cor', 'Divisórias', 'Ações'])
    
    # Configurar redimensionamento das colunas
    header = lista_table.horizontalHeader()
    header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Nome - ocupa espaço restante
    header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Valor - largura fixa
    header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Cor - largura fixa  
    header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Divisórias - largura fixa
    header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Ações - largura fixa
    
    # Definir larguras específicas
    lista_table.setColumnWidth(1, 100)  # Valor (R$)
    lista_table.setColumnWidth(2, 120)  # Cor
    lista_table.setColumnWidth(3, 80)   # Divisórias
    lista_table.setColumnWidth(4, 180)  # Ações (espaço aumentado para 2 botões)
    
    # Estilo moderno para a tabela
    lista_table.setStyleSheet('''
        QTableWidget {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 6px;
            color: #ffffff;
            gridline-color: #404040;
            selection-background-color: #0d7377;
            alternate-background-color: #323232;
        }
        QTableWidget::item {
            background-color: #2d2d2d;
            padding: 8px;
            border-bottom: 1px solid #404040;
            border-right: 1px solid #404040;
            color: #ffffff;
        }
        QTableWidget::item:alternate {
            background-color: #323232;
        }
        QTableWidget::item:selected {
            background-color: #0d7377;
            color: #ffffff;
        }
        QTableWidget::item:hover {
            background-color: #3d3d3d;
        }
        QHeaderView::section {
            background-color: #404040;
            color: #ffffff;
            padding: 8px;
            border: none;
            border-right: 1px solid #505050;
            font-weight: bold;
        }
        QHeaderView::section:first {
            border-left: none;
        }
        QHeaderView::section:hover {
            background-color: #505050;
        }
    ''')
    
    # Configurar altura e comportamento
    lista_table.setMinimumHeight(150)
    lista_table.setMaximumHeight(300)
    lista_table.setAlternatingRowColors(True)
    lista_table.verticalHeader().setVisible(False)  # Esconder números das linhas
    lista_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    
    # Definir altura das linhas para acomodar os botões
    lista_table.verticalHeader().setDefaultSectionSize(40)
    
    produtos_layout.addRow(lista_label, lista_table)

    # Valor total
    valor_total = QLineEdit(); valor_total.setReadOnly(True); valor_total.setPlaceholderText('0.00'); valor_total.setFixedWidth(140)
    produtos_layout.addRow('Valor Total (R$):', valor_total)

    # Aplica um estilo leve para consistência
    produtos_group.setStyleSheet('''
        QGroupBox { margin-top: 8px; border: 1px solid #505050; border-radius: 6px; padding: 10px; }
        QLineEdit { padding: 6px; }
        QPushButton { padding: 4px; }
    ''')

    # Adicionar ao parent layout
    parent_layout.addWidget(produtos_group)

    widgets = {
        'produtos_group': produtos_group,
        'input_desc': input_desc,
        'btn_limpar': btn_limpar,
        'btn_add': btn_add,
        'input_valor': input_valor,
        'campos_cor': campos_cor,
        'campos_div': campos_div,
        'lista_table': lista_table,
        'lista_layout': None,
        'valor_total': valor_total,
    }
    return widgets
