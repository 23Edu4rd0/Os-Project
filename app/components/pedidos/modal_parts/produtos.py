
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel, QWidget, QListWidgetItem, QListWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import db_manager
from app.utils.produtos_busca import buscar_produtos_por_nome
from database import db_manager


def criar_secao_produtos(modal, layout, pedido_data):
    # Criar GroupBox para manter consistência com outras seções
    produtos_group = QGroupBox("🛍️ Produtos do Pedido")
    produtos_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
    produtos_group.setStyleSheet("""
        QGroupBox {
            font-weight: 600;
            font-size: 16px;
            border: 2px solid #666666;
            border-radius: 8px;
            margin-top: 20px;
            margin-bottom: 18px;
            padding: 50px 18px 22px 18px;
            background-color: #2a2a2a;
            color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            top: 25px;
            padding: 0 15px 0 15px;
            color: #ffffff;
            font-weight: bold;
            background: transparent;
            font-size: 18px;
        }
        QLabel {
            color: #ffffff;
            font-size: 14px;
            font-weight: 500;
            padding: 4px 0 4px 0;
            background: transparent;
        }
        QLineEdit, QComboBox {
            min-height: 36px;
            font-size: 14px;
            color: #ffffff;
            background-color: #404040;
            border: 2px solid #666666;
            border-radius: 6px;
            padding: 8px 12px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #999999;
            background-color: #505050;
        }
        QLineEdit:hover, QComboBox:hover {
            border: 2px solid #888888;
        }
        QPushButton {
            background-color: #666666;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: bold;
            font-size: 12px;
            padding: 8px 16px;
            min-height: 36px;
        }
        QPushButton:hover {
            background-color: #777777;
        }
        QPushButton:pressed {
            background-color: #555555;
        }
    """)
    
    main_layout = QVBoxLayout(produtos_group)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(15)
    layout.addWidget(produtos_group)

    # Container para entrada de produtos - agora dentro do GroupBox
    entrada_frame = QWidget()
    entrada_frame.setStyleSheet("""
        QWidget {
            background-color: #404040;
            border: 1px solid #666666;
            border-radius: 8px;
            padding: 10px;
        }
    """)
    entrada_layout = QVBoxLayout(entrada_frame)
    main_layout.addWidget(entrada_frame)
    entrada_layout.setContentsMargins(15, 15, 15, 15)
    entrada_layout.setSpacing(12)

    # Linha 1: Categoria e Produto
    linha1 = QHBoxLayout()
    linha1.setSpacing(15)
    
    # Categoria
    cat_container = QWidget()
    cat_container.setStyleSheet("background: transparent;")
    cat_layout = QVBoxLayout(cat_container)
    cat_layout.setContentsMargins(0, 0, 0, 0)
    cat_layout.setSpacing(5)
    
    cat_label = QLabel("Categoria:")
    cat_label.setStyleSheet("color: #ffffff; font-weight: 600; font-size: 12px;")
    cat_layout.addWidget(cat_label)
    
    modal.input_categoria = QComboBox()
    modal.input_categoria.setMinimumWidth(150)
    modal.input_categoria.addItem("Todas")
    
    def _load_categories_modal():
        """Carrega categorias no combo"""
        current_text = modal.input_categoria.currentText()
        modal.input_categoria.clear()
        modal.input_categoria.addItem("Todas")
        try:
            from app.utils.categories import load_categories
            cats = load_categories()
            for c in cats:
                if modal.input_categoria.findText(c) < 0:
                    modal.input_categoria.addItem(c)
        except Exception:
            for c in ('Agro','Normal','Outros'):
                if modal.input_categoria.findText(c) < 0:
                    modal.input_categoria.addItem(c)
        # Restaura seleção anterior se ainda existir
        index = modal.input_categoria.findText(current_text)
        if index >= 0:
            modal.input_categoria.setCurrentIndex(index)
    
    # Carrega categorias iniciais
    _load_categories_modal()
    
    # Conecta ao sinal de atualização de categorias
    try:
        from app.signals import get_signals
        signals = get_signals()
        signals.categorias_atualizadas.connect(_load_categories_modal)
    except Exception as e:
        print(f"Erro ao conectar sinal de categorias no modal: {e}")
    cat_layout.addWidget(modal.input_categoria)
    linha1.addWidget(cat_container)
    
    # Produto
    prod_container = QWidget()
    prod_container.setStyleSheet("background: transparent;")
    prod_layout = QVBoxLayout(prod_container)
    prod_layout.setContentsMargins(0, 0, 0, 0)
    prod_layout.setSpacing(5)
    
    prod_label = QLabel("Produto:")
    prod_label.setStyleSheet("color: #ffffff; font-weight: 600; font-size: 12px;")
    prod_layout.addWidget(prod_label)
    
    modal.input_desc = QLineEdit()
    modal.input_desc.setPlaceholderText("Digite o nome do produto...")
    modal.input_desc.setClearButtonEnabled(True)
    prod_layout.addWidget(modal.input_desc)
    linha1.addWidget(prod_container, 2)  # Mais espaço para o produto
    
    entrada_layout.addLayout(linha1)

    # Linha 2: Valor e Botão
    linha2 = QHBoxLayout()
    linha2.setSpacing(15)
    
    # Valor
    valor_container = QWidget()
    valor_container.setStyleSheet("background: transparent;")
    valor_layout = QVBoxLayout(valor_container)
    valor_layout.setContentsMargins(0, 0, 0, 0)
    valor_layout.setSpacing(5)
    
    valor_label = QLabel("Valor (R$):")
    valor_label.setStyleSheet("color: #ffffff; font-weight: 600; font-size: 12px;")
    valor_layout.addWidget(valor_label)
    
    modal.input_valor = QLineEdit()
    modal.input_valor.setPlaceholderText("0,00")
    modal.input_valor.setMaximumWidth(130)
    valor_layout.addWidget(modal.input_valor)
    linha2.addWidget(valor_container)
    
    linha2.addStretch()  # Espaço flexível
    
    # Botão Adicionar
    btn_add = QPushButton("+ Adicionar Produto")
    btn_add.setMinimumHeight(40)
    btn_add.setStyleSheet("""
        QPushButton {
            background-color: #666666;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 13px;
        }
        QPushButton:hover {
            background-color: #777777;
        }
        QPushButton:pressed {
            background-color: #555555;
        }
    """)
    btn_add.clicked.connect(modal._add_produto)
    linha2.addWidget(btn_add)
    
    entrada_layout.addLayout(linha2)
    # Removido: vbox.addWidget(entrada_frame)
    modal.sugestoes_produtos.setStyleSheet('''
        QListWidget { 
            background-color: #404040; 
            color: #ffffff; 
            border: 2px solid #666666; 
            font-size: 14px;
            border-radius: 6px;
            padding: 4px;
        }
        QListWidget::item:selected { 
            background-color: #666666; 
            color: #ffffff; 
        }
        QListWidget::item:hover { 
            background-color: #555555; 
        }
    ''')
    modal.sugestoes_produtos.hide()
    def buscar_sugestoes_produtos(texto):
        texto = texto.strip()
        if not texto:
            modal.sugestoes_produtos.hide()
            return
        produtos = buscar_produtos_por_nome(texto, limite=8)
        modal.sugestoes_produtos.clear()
        for prod in produtos:
            nome = prod['nome']
            valor = prod['preco']
            categoria = prod['categoria']
            item = QListWidgetItem(f"{nome} | R$ {valor:.2f} | {categoria}")
            item.setData(Qt.ItemDataRole.UserRole, prod)
            modal.sugestoes_produtos.addItem(item)
        if modal.sugestoes_produtos.count() > 0:
            modal.sugestoes_produtos.setMinimumWidth(modal.input_desc.width())
            modal.sugestoes_produtos.move(modal.input_desc.mapToGlobal(modal.input_desc.rect().bottomLeft()))
            modal.sugestoes_produtos.show()
        else:
            modal.sugestoes_produtos.hide()

        setup_produtos_sugestoes(modal)

    try:
        modal.input_valor.returnPressed.connect(modal._add_produto)
        modal.input_desc.returnPressed.connect(modal._add_produto)
    except Exception:
        pass

    # Autocomplete e catálogo
    try:
        modal._carregar_produtos()
        if hasattr(modal, '_produtos_categorias'):
            modal.input_categoria.addItems(sorted(modal._produtos_categorias))
            modal.input_categoria.currentTextChanged.connect(modal._filtrar_produtos_por_categoria)
        modal._montar_produtos_completer()
    except Exception:
        pass
    # Evita conflito: só conecta se não estiver usando sugestões
    if not hasattr(modal, 'sugestoes_produtos'):
        try:
            modal.input_desc.textChanged.connect(modal._on_produto_text_changed)
        except Exception:
            pass

    linha.addWidget(modal.input_categoria)
    linha.addWidget(modal.input_desc, stretch=1)
    linha.addWidget(modal.input_valor)
    linha.addWidget(btn_add)
    layout.addLayout(linha)

    # Opções gerais do pedido
    opcoes = QHBoxLayout()
    lbl_cor = QLabel("Cor:"); modal.campos['cor'] = QComboBox(); modal.campos['cor'].addItems(["", "Preto","Branco","Azul","Vermelho","Verde","Amarelo","Cinza","Marrom","Rosa","Roxo"])
    lbl_ref = QLabel("Reforço:"); modal.campos['reforco'] = QComboBox(); modal.campos['reforco'].addItems(["não", "sim"])
    opcoes.addWidget(lbl_cor); opcoes.addWidget(modal.campos['cor']); opcoes.addSpacing(16); opcoes.addWidget(lbl_ref); opcoes.addWidget(modal.campos['reforco']); opcoes.addStretch()
    layout.addLayout(opcoes)

    modal.lista_produtos_container = QVBoxLayout(); modal.lista_produtos_container.setSpacing(6)
    layout.addLayout(modal.lista_produtos_container)

    # Valor total (somado automaticamente)
    modal.campos['valor_total'] = QLineEdit(); modal.campos['valor_total'].setReadOnly(True); modal.campos['valor_total'].setPlaceholderText("0.00")
    total_row = QHBoxLayout(); total_row.addWidget(QLabel("Valor Total (R$):")); total_row.addWidget(modal.campos['valor_total'])
    layout.addLayout(total_row)

    # Prefill lista e opções
    if pedido_data:
        detalhes = pedido_data.get('detalhes_produto', '') or ''
        for linha in [l.strip() for l in detalhes.replace('\\n', '\n').split('\n') if l.strip() and not l.strip().startswith('-')]:
            if ' - R$ ' in linha:
                try:
                    desc, valtxt = linha.rsplit(' - R$ ', 1)
                    valor = float(valtxt.replace('.', '').replace(',', '.')) if valtxt else 0.0
                    modal.produtos_list.append({"descricao": desc.strip('• ').strip(), "valor": valor})
                except Exception:
                    modal.produtos_list.append({"descricao": linha.strip('• ').strip(), "valor": 0.0})
            else:
                modal.produtos_list.append({"descricao": linha.strip('• ').strip(), "valor": 0.0})
        modal._refresh_produtos_ui()
        valor = pedido_data.get('valor_total', pedido_data.get('valor_produto', 0))
        try:
            modal.campos['valor_total'].setText(f"{float(valor or 0):.2f}")
        except Exception:
            modal.campos['valor_total'].setText("0.00")
        try:
            cor = pedido_data.get('cor', '') or ''
            if cor:
                idx = modal.campos['cor'].findText(cor)
                if idx >= 0:
                    modal.campos['cor'].setCurrentIndex(idx)
        except Exception:
            pass
        try:
            reforco_val = pedido_data.get('reforco', False)
            reforco_txt = 'sim' if (str(reforco_val).lower() in ('1','true','sim','yes')) else 'não'
            idx = modal.campos['reforco'].findText(reforco_txt)
            if idx >= 0:
                modal.campos['reforco'].setCurrentIndex(idx)
        except Exception:
            pass

    # Removido: layout.addWidget(grupo)
