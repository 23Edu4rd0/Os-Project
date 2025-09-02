from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QGroupBox, QFormLayout, QScrollArea
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt

"""
Cria os widgets e layouts para a seção de produtos.
Export: criar_produtos_ui(self, parent_layout, pedido_data)
Retorna: dict com widgets criados (input_desc, input_valor, input_categoria, campos, container_widget)
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

    # Valor e Categoria em uma linha (label + control)
    input_valor = QLineEdit()
    input_valor.setPlaceholderText('Valor (R$)')
    input_valor.setFixedWidth(140)
    input_categoria = QComboBox(); input_categoria.addItem('')
    try:
        from app.utils.categories import load_categories
        cats = load_categories()
        for c in cats:
            input_categoria.addItem(c)
    except Exception:
        # fallback
        input_categoria.addItems(['Agro', 'Normal', 'Outros'])
    input_categoria.setFixedWidth(220)
    val_cat_layout = QHBoxLayout()
    val_cat_layout.addWidget(input_valor)
    val_cat_layout.addSpacing(12)
    val_cat_layout.addWidget(input_categoria)
    produtos_layout.addRow('Valor / Categoria:', val_cat_layout)

    # Cor e Reforço
    campos_cor = QComboBox(); campos_cor.addItems(['', 'Branco', 'Amarelo', 'Azul', 'Verde', 'Personalizado'])
    campos_cor.setFixedWidth(220)
    campos_ref = QCheckBox('Reforço (+R$15)')
    # Visual aprimorado: indicador maior, cantos arredondados e cor quando marcado
    try:
        campos_ref.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    except Exception:
        try:
            campos_ref.setCursor(QCursor(getattr(Qt, 'PointingHandCursor', 0)))
        except Exception:
            pass
    campos_ref.setStyleSheet('''
        QCheckBox { color: #e6e6e6; font-weight: 600; }
        QCheckBox::indicator {
            width: 18px; height: 18px;
            border-radius: 6px;
            border: 1px solid #6b6b6b;
            background: #2f2f2f;
        }
        QCheckBox::indicator:checked {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #7ef99a, stop:1 #2fb86a);
            border: 1px solid #27a85a;
        }
        QCheckBox::indicator:unchecked:hover {
            border: 1px solid #9a9a9a;
        }
    ''')
    ref_layout = QHBoxLayout()
    ref_layout.addWidget(campos_cor)
    ref_layout.addStretch()
    ref_layout.addWidget(campos_ref)
    produtos_layout.addRow('Cor / Reforço:', ref_layout)

    # Lista de produtos adicionados em tabela
    lista_label = QLabel('Produtos adicionados:')
    lista_label.setFont(QFont('Segoe UI', 9))
    from PyQt6.QtWidgets import QTableWidget, QHeaderView
    lista_table = QTableWidget(0, 5)
    lista_table.setHorizontalHeaderLabels(['Descrição', 'Valor (R$)', 'Cor', 'Reforço', 'Ações'])
    lista_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
    lista_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
    lista_table.setMinimumHeight(140)
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
        'input_categoria': input_categoria,
        'campos_cor': campos_cor,
        'campos_ref': campos_ref,
        'lista_table': lista_table,
        'lista_layout': None,
        'valor_total': valor_total,
    }
    return widgets
