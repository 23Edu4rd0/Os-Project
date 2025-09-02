
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QPushButton, QLabel, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database import db_manager
from app.utils.produtos_busca import buscar_produtos_por_nome
from database import db_manager


def criar_secao_produtos(modal, layout, pedido_data):
    grupo = QGroupBox("📦 Produtos")
    grupo.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
    vbox = QVBoxLayout(grupo)

    from app.components.produtos_sugestoes import setup_produtos_sugestoes
    modal.input_categoria = QComboBox(); modal.input_categoria.setMinimumWidth(140); modal.input_categoria.addItem("Todas")
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
    from PyQt6.QtWidgets import QListWidget, QListWidgetItem
    modal.input_desc = QLineEdit(); modal.input_desc.setPlaceholderText("Produto (catálogo)")
    modal.input_desc.setClearButtonEnabled(True)
    linha = QHBoxLayout()
    modal.input_valor = QLineEdit(); modal.input_valor.setPlaceholderText("Valor (R$)"); modal.input_valor.setMaximumWidth(120)
    btn_add = QPushButton("+ Adicionar")
    btn_add.clicked.connect(modal._add_produto)
    # Adicionar widgets ao layout linha apenas uma vez, e nunca reaproveitar o mesmo layout
    # (Widgets já adicionados ao layout linha e vbox acima, não repetir)
    # Sugestão de produtos (editável)
    from PyQt6.QtCore import QEvent
    def esconder_sugestoes():
        modal.sugestoes_produtos.hide()
    modal.input_desc.installEventFilter(modal)
    def eventFilter(self, obj, event):
        if obj == modal.input_desc:
            if event.type() == QEvent.Type.FocusOut:
                modal.sugestoes_produtos.hide()
        return False
    modal.eventFilter = eventFilter.__get__(modal)
    modal.input_desc.focusOutEvent = lambda event: (modal.sugestoes_produtos.hide(), QLineEdit.focusOutEvent(modal.input_desc, event))
    # Sugestão de produtos
    modal.sugestoes_produtos = QListWidget()
    modal.sugestoes_produtos.setWindowFlags(modal.sugestoes_produtos.windowFlags() | Qt.WindowType.Popup)
    modal.sugestoes_produtos.setStyleSheet('''
        QListWidget { background: #23272e; color: #f8f8f2; border: 1.5px solid #50fa7b; font-size: 15px; }
        QListWidget::item:selected { background: #50fa7b; color: #23272e; }
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
    vbox.addLayout(linha)

    # Opções gerais do pedido
    opcoes = QHBoxLayout()
    lbl_cor = QLabel("Cor:"); modal.campos['cor'] = QComboBox(); modal.campos['cor'].addItems(["", "Preto","Branco","Azul","Vermelho","Verde","Amarelo","Cinza","Marrom","Rosa","Roxo"])
    lbl_ref = QLabel("Reforço:"); modal.campos['reforco'] = QComboBox(); modal.campos['reforco'].addItems(["não", "sim"])
    opcoes.addWidget(lbl_cor); opcoes.addWidget(modal.campos['cor']); opcoes.addSpacing(16); opcoes.addWidget(lbl_ref); opcoes.addWidget(modal.campos['reforco']); opcoes.addStretch()
    vbox.addLayout(opcoes)

    modal.lista_produtos_container = QVBoxLayout(); modal.lista_produtos_container.setSpacing(6)
    vbox.addLayout(modal.lista_produtos_container)

    # Valor total (somado automaticamente)
    modal.campos['valor_total'] = QLineEdit(); modal.campos['valor_total'].setReadOnly(True); modal.campos['valor_total'].setPlaceholderText("0.00")
    total_row = QHBoxLayout(); total_row.addWidget(QLabel("Valor Total (R$):")); total_row.addWidget(modal.campos['valor_total'])
    vbox.addLayout(total_row)

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

    layout.addWidget(grupo)
