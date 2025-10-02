"""
Modal de Pedidos Simplificado
Design moderno em tons de cinza, sem camadas desnecessárias
"""
import json

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QWidget, QMessageBox, QCompleter, QFrame, QFormLayout,
                            QScrollArea, QAbstractScrollArea, QSpinBox, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel, QEvent
from PyQt6.QtGui import QFont

from database import db_manager
from app.numero_os import Contador


class ClickableComboBox(QComboBox):
    """ComboBox que abre dropdown ao clicar em qualquer parte e ignora scroll do mouse"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().installEventFilter(self)
        self.installEventFilter(self)  # Instalar event filter no próprio combobox também
        
    def eventFilter(self, obj, event):
        # Bloquear scroll do mouse
        if event.type() == QEvent.Type.Wheel:
            event.ignore()
            return True
            
        # Fazer combobox abrir ao clicar em qualquer parte
        if obj == self.lineEdit():
            if event.type() == QEvent.Type.MouseButtonPress:
                self.showPopup()
                return True
        return super().eventFilter(obj, event)
    
    def wheelEvent(self, event):
        """Bloquear completamente eventos de roda do mouse"""
        event.ignore()


class NoScrollSpinBox(QSpinBox):
    """QSpinBox que ignora eventos de scroll do mouse"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.installEventFilter(self)
        
    def eventFilter(self, obj, event):
        # Bloquear scroll do mouse
        if event.type() == QEvent.Type.Wheel:
            event.ignore()
            return True
        return super().eventFilter(obj, event)
    
    def wheelEvent(self, event):
        """Bloquear completamente eventos de roda do mouse"""
        event.ignore()


class NovoPedidosModal(QDialog):
    pedido_salvo = pyqtSignal()
    
    def __init__(self, parent=None, dados_cliente=None, pedido_id=None):
        super().__init__(parent)
        self.produtos_dict = {}
        self.produtos_list = []
        self.cliente_selecionado = None
        self.dados_cliente_inicial = dados_cliente
        self.pedido_id = pedido_id
        
        # Variáveis para controle de edição
        self.is_editing = False
        self.numero_os_original = None
        self.pedido_id_editando = None  # ID do pedido sendo editado
        self.titulo_label = None  # Referência para atualizar o título
        
        # Compatibilidade com modal antigo - criar objeto model fake
        self.model = type('Model', (), {
            'preencher': self._preencher_compatibilidade
        })()
        
        if pedido_id:
            self.setWindowTitle(f"Editar Ordem de Serviço Nº {pedido_id:05d}")
        else:
            self.setWindowTitle("Nova Ordem de Serviço")
        
        # Configurar tamanho - mais compacto
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.7)   # 70% da largura da tela
        height = int(screen.height() * 0.8)  # 80% da altura da tela
        
        self.setMinimumSize(800, 600)  # Tamanho mínimo reduzido
        self.resize(width, height)
        self.setModal(True)
        
        # Centralizar na tela
        x = (screen.width() - width) // 2
        y = (screen.height() - height) // 2
        self.move(x, y)
        
        # Carregar dados
        self._carregar_produtos()
        self._carregar_clientes()
        
        # Criar interface
        self._criar_interface()
        self._aplicar_estilo()
        
        # Preencher dados se fornecidos
        if dados_cliente:
            self._preencher_dados_cliente(dados_cliente)
        
    def _carregar_produtos(self):
        """Carrega produtos do banco de dados"""
        try:
            rows = db_manager.listar_produtos()
            self.produtos_dict = {}
            
            for row in rows:
                # (id, nome, codigo, preco, descricao, categoria, criado_em)
                nome = (row[1] or '').strip()
                codigo = (row[2] or '').strip()
                preco = float(row[3]) if row[3] is not None else 0.0
                categoria = (row[5] or '').strip()
                
                if nome:
                    produto_data = {
                        "id": row[0],
                        "nome": nome,
                        "codigo": codigo,
                        "preco": preco,
                        "categoria": categoria
                    }
                    # Indexar por nome
                    self.produtos_dict[nome] = produto_data
                    # Indexar por nome lowercase
                    self.produtos_dict[nome.lower()] = produto_data
                    
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
            self.produtos_dict = {}
    
    def _carregar_clientes(self):
        """Carrega clientes do banco de dados"""
        try:
            rows = db_manager.listar_clientes()
            self.clientes_dict = {}
            
            for row in rows:
                nome = (row[1] or '').strip()
                if nome:
                    # Estrutura da tabela clientes:
                    # 0=id, 1=nome, 2=cpf, 3=cnpj, 4=inscricao_estadual, 5=telefone, 
                    # 6=email, 7=cep, 8=rua, 9=numero, 10=bairro, 11=cidade, 12=estado, 13=referencia
                    cpf = row[2] or ''
                    cnpj = row[3] or ''
                    telefone = row[5] or ''
                    
                    # Construir endereço completo
                    endereco_partes = []
                    if row[8]:  # rua (corrigido de 7 para 8)
                        endereco_partes.append(row[8])
                    if row[9]:  # numero (corrigido de 8 para 9)
                        endereco_partes.append(row[9])
                    if row[10]:  # bairro (corrigido de 9 para 10)
                        endereco_partes.append(row[10])
                    if row[11]:  # cidade (corrigido de 10 para 11)
                        endereco_partes.append(row[11])
                    if row[12]:  # estado (corrigido de 11 para 12)
                        endereco_partes.append(row[12])
                    
                    endereco = ', '.join(endereco_partes)
                    
                    cliente_data = {
                        "id": row[0],
                        "nome": nome,
                        "cpf": cpf,
                        "cnpj": cnpj,
                        "telefone": telefone,
                        "endereco": endereco
                    }
                    self.clientes_dict[nome] = cliente_data
                
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            self.clientes_dict = {}
    
    def _configurar_autocomplete_clientes(self):
        """Configura o autocomplete para clientes após criação do campo"""
        if self.clientes_dict and hasattr(self, 'input_nome_cliente'):
            nomes_clientes = list(self.clientes_dict.keys())
            completer = QCompleter(nomes_clientes)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.input_nome_cliente.setCompleter(completer)
            
            # Conectar seleção do completer
            completer.activated.connect(self._on_cliente_selecionado_completer)
    
    def _on_cliente_selecionado_completer(self, nome_cliente):
        """Preenche automaticamente os dados quando um cliente é selecionado do autocomplete"""
        if nome_cliente in self.clientes_dict:
            cliente_data = self.clientes_dict[nome_cliente]
            
            # Preencher os campos automaticamente
            if hasattr(self, 'input_cpf'):
                # Priorizar CPF se existir, senão CNPJ
                cpf = cliente_data.get('cpf', '').strip()
                cnpj = cliente_data.get('cnpj', '').strip()
                cpf_cnpj_valor = cpf if cpf else cnpj
                self.input_cpf.setText(cpf_cnpj_valor)
            
            if hasattr(self, 'input_telefone'):
                self.input_telefone.setText(cliente_data.get('telefone', ''))
            
            if hasattr(self, 'input_endereco'):
                self.input_endereco.setText(cliente_data.get('endereco', ''))
    

    def _criar_interface(self):
        """Cria a interface do modal com scroll geral"""
        # Layout principal do modal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)
        
        # === SCROLL AREA GERAL ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #3a3a3a;
                width: 14px;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 7px;
                min-height: 25px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #cccccc;
            }
        """)
        
        # Widget principal dentro do scroll
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(15)  # Espaçamento reduzido entre seções
        layout.setContentsMargins(20, 20, 20, 30)  # Margem inferior maior para scroll
        
        # Header
        self._criar_header(layout)
        
        # Seção Cliente
        self._criar_secao_cliente(layout)
        
        # Seção Produtos
        self._criar_secao_produtos(layout)
        
        # Seção Pagamento
        self._criar_secao_pagamento(layout)
        
        # Botões
        self._criar_botoes(layout)
        
        # Espaçamento final para permitir scroll completo
        layout.addStretch()
        
        # Configurar scroll area
        scroll_area.setWidget(scroll_widget)
        scroll_area.verticalScrollBar().setSingleStep(20)
        scroll_area.verticalScrollBar().setPageStep(100)
        main_layout.addWidget(scroll_area)
        
        # Configurar autocomplete após criar todos os campos
        self._configurar_autocomplete_clientes()
    
    def _criar_header(self, layout):
        """Cria o cabeçalho com número da OS"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Número da OS - será atualizado dinamicamente
        if self.is_editing and self.numero_os_original:
            numero_os = self.numero_os_original
        else:
            numero_os = Contador().get_proximo_numero()
            
        self.titulo_label = QLabel(f"Ordem de Serviço Nº {numero_os:05d}")
        self.titulo_label.setObjectName("titulo")
        
        header_layout.addWidget(self.titulo_label)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
    
    def _criar_secao_cliente(self, layout):
        """Cria a seção de dados do cliente - design minimalista"""
        group = QGroupBox("📋 Cliente")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 6px;
                margin-top: 8px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(15, 20, 15, 15)
        
        # Estilo minimalista para campos
        field_style = """
            QLineEdit, QComboBox {
                background: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #666;
            }
        """
        
        # Grade para campos do cliente
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        
        # Nome do cliente
        form_layout.addWidget(QLabel("Nome:"), 0, 0)
        self.input_nome_cliente = QLineEdit()
        self.input_nome_cliente.setPlaceholderText("Nome completo")
        self.input_nome_cliente.setStyleSheet(field_style)
        form_layout.addWidget(self.input_nome_cliente, 0, 1, 1, 3)
        
        # CPF/CNPJ e Telefone
        form_layout.addWidget(QLabel("CPF/CNPJ:"), 1, 0)
        self.input_cpf = QLineEdit()
        self.input_cpf.setPlaceholderText("000.000.000-00")
        self.input_cpf.setStyleSheet(field_style)
        form_layout.addWidget(self.input_cpf, 1, 1)
        
        form_layout.addWidget(QLabel("Telefone:"), 1, 2)
        self.input_telefone = QLineEdit()
        self.input_telefone.setPlaceholderText("(00) 00000-0000")
        self.input_telefone.setStyleSheet(field_style)
        form_layout.addWidget(self.input_telefone, 1, 3)
        
        # Endereço completo
        form_layout.addWidget(QLabel("Endereço:"), 2, 0)
        self.input_endereco = QLineEdit()
        self.input_endereco.setPlaceholderText("Rua, número, bairro, cidade")
        self.input_endereco.setStyleSheet(field_style)
        form_layout.addWidget(self.input_endereco, 2, 1, 1, 3)
        
        group_layout.addLayout(form_layout)
        
        # Configurar autocomplete de clientes após criar os campos
        self._configurar_autocomplete_clientes()
        
        # Conectar evento de mudança de texto (para compatibilidade)
        self.input_nome_cliente.textChanged.connect(self._on_cliente_changed)
        
        layout.addWidget(group)
    
    def _criar_secao_produtos(self, layout):
        """Cria a seção de produtos - design minimalista"""
        group = QGroupBox("📦 Produtos")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 6px;
                margin-top: 8px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(15, 20, 15, 15)
        
        # Estilo minimalista para campos
        field_style = """
            QLineEdit, QSpinBox, QComboBox {
                background: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #666;
            }
        """
        
        # Formulário para adicionar produtos
        form_grid = QGridLayout()
        form_grid.setSpacing(10)
        
        # Produto - ComboBox clicável em toda área
        form_grid.addWidget(QLabel("Produto:"), 0, 0)
        self.input_produto = ClickableComboBox()
        self._preencher_combo_produtos()
        self.input_produto.setStyleSheet(field_style + """
            QComboBox {
                padding-right: 20px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #999;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background: #2a2a2a;
                border: 1px solid #555;
                selection-background-color: #007acc;
                selection-color: #fff;
                padding: 4px;
            }
        """)
        form_grid.addWidget(self.input_produto, 0, 1, 1, 2)
        
        # Quantidade e Valor
        form_grid.addWidget(QLabel("Qtd:"), 1, 0)
        self.input_quantidade = NoScrollSpinBox()
        self.input_quantidade.setMinimum(1)
        self.input_quantidade.setMaximum(9999)
        self.input_quantidade.setValue(1)
        self.input_quantidade.setStyleSheet(field_style)
        form_grid.addWidget(self.input_quantidade, 1, 1)
        
        form_grid.addWidget(QLabel("Valor (R$):"), 1, 2)
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("0,00")
        self.input_valor.setStyleSheet(field_style)
        form_grid.addWidget(self.input_valor, 1, 3)
        
        # Cores - 2 cores por padrão (Tampa e Corpo)
        from app.ui.color_manager import load_colors
        from PyQt6.QtWidgets import QCheckBox
        
        cores_disponiveis = [''] + load_colors()
        
        # 2 cores por padrão (Tampa e Corpo) - armazenar labels como atributos
        self.label_tampa = QLabel("Tampa:")
        form_grid.addWidget(self.label_tampa, 2, 0)
        self.combo_cor_tampa = ClickableComboBox()
        self.combo_cor_tampa.addItems(cores_disponiveis)
        self.combo_cor_tampa.setStyleSheet(field_style)
        form_grid.addWidget(self.combo_cor_tampa, 2, 1)
        
        self.label_corpo = QLabel("Corpo:")
        form_grid.addWidget(self.label_corpo, 2, 2)
        self.combo_cor_corpo = ClickableComboBox()
        self.combo_cor_corpo.addItems(cores_disponiveis)
        self.combo_cor_corpo.setStyleSheet(field_style)
        form_grid.addWidget(self.combo_cor_corpo, 2, 3)
        
        # Checkbox estilizado para alternar para 1 cor apenas
        self.checkbox_uma_cor = QCheckBox("✓ Usar apenas 1 cor")
        self.checkbox_uma_cor.setStyleSheet("""
            QCheckBox {
                color: #999;
                font-size: 11px;
                padding: 4px;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #555;
                border-radius: 3px;
                background: #2a2a2a;
            }
            QCheckBox::indicator:checked {
                background: #007acc;
                border-color: #007acc;
            }
            QCheckBox::indicator:hover {
                border-color: #666;
            }
        """)
        self.checkbox_uma_cor.stateChanged.connect(self._toggle_uma_cor)
        form_grid.addWidget(self.checkbox_uma_cor, 3, 0, 1, 2)
        
        # Cor única (inicialmente oculto)
        self.label_cor_unica = QLabel("Cor:")
        self.label_cor_unica.setVisible(False)
        form_grid.addWidget(self.label_cor_unica, 2, 0)
        
        self.combo_cor = ClickableComboBox()
        self.combo_cor.addItems(cores_disponiveis)
        self.combo_cor.setStyleSheet(field_style)
        self.combo_cor.setVisible(False)
        form_grid.addWidget(self.combo_cor, 2, 1, 1, 3)
        
        # Botão adicionar
        btn_add = QPushButton("+ Adicionar Produto")
        btn_add.clicked.connect(self._adicionar_produto)
        btn_add.setStyleSheet("""
            QPushButton {
                background: #007acc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #005a9e;
            }
        """)
        form_grid.addWidget(btn_add, 4, 0, 1, 4)
        
        group_layout.addLayout(form_grid)
        
        # Tabela de produtos
        from PyQt6.QtWidgets import QAbstractItemView
        self.table_produtos = QTableWidget(0, 6)
        self.table_produtos.setHorizontalHeaderLabels(['Produto', 'Qtd', 'Código', 'Valor', 'Cor', 'Ações'])
        self.table_produtos.setStyleSheet("""
            QTableWidget {
                border: 1px solid #444;
                border-radius: 4px;
                background: #2a2a2a;
                gridline-color: #444;
            }
            QHeaderView::section {
                background: #222;
                color: #ccc;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
                color: #e0e0e0;
            }
        """)
        self.table_produtos.verticalHeader().setVisible(False)
        self.table_produtos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        # Configurar larguras
        header = self.table_produtos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in [1, 2, 3, 4]:
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table_produtos.setColumnWidth(5, 80)
        
        group_layout.addWidget(self.table_produtos)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("Total:"))
        self.label_total = QLabel("R$ 0,00")
        self.label_total.setStyleSheet("font-weight: bold; font-size: 14px;")
        total_layout.addWidget(self.label_total)
        group_layout.addLayout(total_layout)
        
        # Conectar eventos do ComboBox de produtos
        self.input_produto.currentTextChanged.connect(self._on_produto_changed)
        self.input_produto.activated.connect(self._on_produto_selecionado_combo)
        self.input_valor.returnPressed.connect(self._adicionar_produto)
        
        layout.addWidget(group)
    
    def _preencher_combo_produtos(self):
        """Preenche o combo de produtos com formatação: Nome - R$ Preço - Código: XXX"""
        self.input_produto.clear()
        self.input_produto.addItem("")  # Item vazio no topo
        
        # Criar lista única de produtos (evitar duplicatas por lowercase)
        produtos_unicos = {}
        for produto in self.produtos_dict.values():
            if 'nome' in produto and 'id' in produto:
                prod_id = produto['id']
                if prod_id not in produtos_unicos:
                    produtos_unicos[prod_id] = produto
        
        # Ordenar por nome
        produtos_ordenados = sorted(produtos_unicos.values(), key=lambda p: p['nome'].lower())
        
        # Adicionar ao combo formatado
        for produto in produtos_ordenados:
            nome = produto['nome']
            preco = produto.get('preco', 0.0)
            codigo = produto.get('codigo', '')
            
            # Formatar: "Nome - R$ Preço - Código: XXX"
            preco_formatado = f"{preco:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            texto_display = f"{nome} - R$ {preco_formatado}"
            if codigo:
                texto_display += f" - Código: {codigo}"
            
            self.input_produto.addItem(texto_display)
            # Guardar dados do produto no item (via UserRole)
            self.input_produto.setItemData(self.input_produto.count() - 1, produto, Qt.ItemDataRole.UserRole)
    
    def _criar_secao_pagamento(self, layout):
        """Cria a seção de pagamento - design minimalista"""
        group = QGroupBox("💳 Pagamento")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 6px;
                margin-top: 8px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(15, 20, 15, 15)
        
        # Estilo minimalista para campos
        field_style = """
            QLineEdit, QComboBox {
                background: #2a2a2a;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #666;
            }
        """
        
        # Grade para campos de pagamento
        form_grid = QGridLayout()
        form_grid.setSpacing(10)
        
        # Valores financeiros
        form_grid.addWidget(QLabel("Entrada (R$):"), 0, 0)
        self.entrada_input = QLineEdit()
        self.entrada_input.setPlaceholderText("0,00")
        self.entrada_input.setStyleSheet(field_style)
        form_grid.addWidget(self.entrada_input, 0, 1)
        
        form_grid.addWidget(QLabel("Frete (R$):"), 0, 2)
        self.frete_input = QLineEdit()
        self.frete_input.setPlaceholderText("0,00")
        self.frete_input.setStyleSheet(field_style)
        form_grid.addWidget(self.frete_input, 0, 3)
        
        form_grid.addWidget(QLabel("Desconto (R$):"), 1, 0)
        self.desconto_input = QLineEdit()
        self.desconto_input.setPlaceholderText("0,00")
        self.desconto_input.setStyleSheet(field_style)
        form_grid.addWidget(self.desconto_input, 1, 1)
        
        # Prazo ao lado do desconto
        form_grid.addWidget(QLabel("Prazo:"), 1, 2)
        self.prazo_entrega = QLineEdit()
        self.prazo_entrega.setPlaceholderText("Ex: 30 dias")
        self.prazo_entrega.setStyleSheet(field_style)
        form_grid.addWidget(self.prazo_entrega, 1, 3)
        
        # Método de pagamento
        form_grid.addWidget(QLabel("Método:"), 2, 0)
        self.metodo_pagamento = ClickableComboBox()
        self.metodo_pagamento.addItems([
            "PIX", "Cartão de Crédito", "Cartão de Débito",
            "Dinheiro", "Transferência Bancária", "Boleto", "Cheque", "Crediário"
        ])
        self.metodo_pagamento.setStyleSheet(field_style)
        form_grid.addWidget(self.metodo_pagamento, 2, 1, 1, 3)
        
        # Status
        form_grid.addWidget(QLabel("Status:"), 3, 0)
        self.status_pedido = ClickableComboBox()
        try:
            from app.utils.statuses import load_statuses
            self.status_pedido.addItems(load_statuses())
        except Exception:
            self.status_pedido.addItems([
                "Em Produção", "Aguardando Material", "Pronto",
                "Enviado", "Entregue", "Cancelado"
            ])
        self.status_pedido.setStyleSheet(field_style)
        form_grid.addWidget(self.status_pedido, 3, 1, 1, 3)
        
        group_layout.addLayout(form_grid)
        
        # Totais
        totais_layout = QVBoxLayout()
        totais_layout.setSpacing(8)
        
        # Total geral
        total_h = QHBoxLayout()
        total_h.addStretch()
        total_h.addWidget(QLabel("Total Geral:"))
        self.total_label = QLabel("R$ 0,00")
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        total_h.addWidget(self.total_label)
        totais_layout.addLayout(total_h)
        
        # Valor a receber
        receber_h = QHBoxLayout()
        receber_h.addStretch()
        receber_h.addWidget(QLabel("A Receber:"))
        self.valor_receber_label = QLabel("R$ 0,00")
        self.valor_receber_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #4CAF50;")
        receber_h.addWidget(self.valor_receber_label)
        totais_layout.addLayout(receber_h)
        
        group_layout.addLayout(totais_layout)
        
        # Conectar cálculos
        self.entrada_input.textChanged.connect(self._calcular_total)
        self.frete_input.textChanged.connect(self._calcular_total)
        self.desconto_input.textChanged.connect(self._calcular_total)
        
        layout.addWidget(group)

    def _calcular_total(self):
        """Calcula o total do pedido"""
        try:
            # Total dos produtos
            total_produtos = sum(p['valor'] for p in self.produtos_list)
            
            # Valores financeiros (entrada, frete, desconto)
            try:
                entrada_text = self.entrada_input.text().replace('R$', '').replace(',', '.').strip()
                entrada = float(entrada_text) if entrada_text else 0.0
            except ValueError:
                entrada = 0.0
            
            try:
                frete_text = self.frete_input.text().replace('R$', '').replace(',', '.').strip()
                frete = float(frete_text) if frete_text else 0.0
            except ValueError:
                frete = 0.0
            
            try:
                desconto_text = self.desconto_input.text().replace('R$', '').replace(',', '.').strip()
                desconto = float(desconto_text) if desconto_text else 0.0
            except ValueError:
                desconto = 0.0
            
            # Calcular total final
            total_final = total_produtos + frete - desconto
            valor_a_receber = total_final - entrada
            
            # Atualizar os labels
            if hasattr(self, 'total_label'):
                self.total_label.setText(f"R$ {total_final:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            if hasattr(self, 'valor_receber_label'):
                self.valor_receber_label.setText(f"R$ {valor_a_receber:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                
        except Exception as e:
            print(f"Erro ao calcular total: {e}")
    
    def _criar_botoes(self, layout):
        """Cria os botões do modal"""
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # Cancelar
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        # Salvar
        btn_salvar = QPushButton("Salvar Pedido")
        btn_salvar.setObjectName("btnSalvar")
        btn_salvar.clicked.connect(self._salvar_pedido)
        btn_layout.addWidget(btn_salvar)
        
        layout.addLayout(btn_layout)
    
    def _toggle_uma_cor(self, state):
        """Alterna entre modo de 2 cores (padrão) ou 1 cor apenas"""
        usar_uma_cor = state == 2  # Qt.CheckState.Checked
        
        # Mostrar/ocultar campos de 1 cor
        self.combo_cor.setVisible(usar_uma_cor)
        self.label_cor_unica.setVisible(usar_uma_cor)
        
        # Mostrar/ocultar campos de 2 cores
        self.combo_cor_tampa.setVisible(not usar_uma_cor)
        self.combo_cor_corpo.setVisible(not usar_uma_cor)
        self.label_tampa.setVisible(not usar_uma_cor)
        self.label_corpo.setVisible(not usar_uma_cor)
    
    def _on_cliente_changed(self, texto):
        """Evento quando o texto do cliente muda"""
        if texto in self.clientes_dict:
            cliente = self.clientes_dict[texto]
            self.input_cpf.setText(cliente.get('cpf', cliente.get('cnpj', '')))
            self.input_telefone.setText(cliente['telefone'])
            self.input_endereco.setText(cliente['endereco'])
            self.cliente_selecionado = cliente
        else:
            self.cliente_selecionado = None
    
    def _on_produto_changed(self, texto):
        """Evento quando o texto do combo produto muda (digitação)"""
        if not texto or texto.strip() == "":
            return
        
        # Se o texto for exatamente um item do combo (seleção via mouse/teclado)
        index = self.input_produto.findText(texto, Qt.MatchFlag.MatchExactly)
        if index >= 0:
            produto = self.input_produto.itemData(index, Qt.ItemDataRole.UserRole)
            if produto:
                preco = produto.get('preco', 0.0)
                self.input_valor.setText(f"{preco:.2f}")
                return
        
        # Buscar por nome digitado (sem formatação)
        # Extrair apenas o nome antes do " - R$"
        nome_busca = texto.split(" - R$")[0].strip()
        
        # Buscar no dicionário
        if nome_busca in self.produtos_dict:
            produto = self.produtos_dict[nome_busca]
            preco = produto.get('preco', 0.0)
            self.input_valor.setText(f"{preco:.2f}")
            return
        
        # Buscar por nome lowercase
        if nome_busca.lower() in self.produtos_dict:
            produto = self.produtos_dict[nome_busca.lower()]
            preco = produto.get('preco', 0.0)
            self.input_valor.setText(f"{preco:.2f}")
            return
            
    
    def _on_produto_selecionado_combo(self, index):
        """Evento quando um produto é selecionado no combo"""
        if index <= 0:  # Item vazio ou inválido
            return
        
        # Obter dados do produto armazenados no item
        produto = self.input_produto.itemData(index, Qt.ItemDataRole.UserRole)
        if produto:
            preco = produto.get('preco', 0.0)
            self.input_valor.setText(f"{preco:.2f}")
            
    
    def _adicionar_produto(self):
        """Adiciona um produto à lista"""
        texto_combo = self.input_produto.currentText().strip()
        valor_texto = self.input_valor.text().strip()
        quantidade = self.input_quantidade.value()
        
        # Validações
        if not texto_combo:
            QMessageBox.warning(self, "Aviso", "Selecione um produto!")
            return
        
        if not valor_texto or valor_texto in ['0', '0,00', '0.00']:
            QMessageBox.warning(self, "Aviso", "Digite um valor válido!")
            return
        
        # Converter valor
        try:
            valor = float(valor_texto.replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Valor inválido!")
            return
        
        # Extrair nome do produto (antes do " - R$")
        nome = texto_combo.split(" - R$")[0].strip()
        
        # Buscar código no catálogo
        codigo = ''
        if nome in self.produtos_dict:
            produto_cat = self.produtos_dict[nome]
            codigo = produto_cat.get('codigo', '')
            # Usar preço do catálogo se disponível
            if produto_cat.get('preco', 0) > 0:
                valor = produto_cat['preco']
        elif nome.lower() in self.produtos_dict:
            produto_cat = self.produtos_dict[nome.lower()]
            codigo = produto_cat.get('codigo', '')
            nome = produto_cat.get('nome', nome)  # Nome correto do catálogo
            if produto_cat.get('preco', 0) > 0:
                valor = produto_cat['preco']
        
        # Obter cor(es) - lógica invertida: 2 cores é o padrão
        if self.checkbox_uma_cor.isChecked():
            # Usar apenas 1 cor
            cor = self.combo_cor.currentText() or '-'
        else:
            # 2 cores (padrão): tampa e corpo
            cor_tampa = self.combo_cor_tampa.currentText()
            cor_corpo = self.combo_cor_corpo.currentText()
            cor = f"T:{cor_tampa}/C:{cor_corpo}" if (cor_tampa or cor_corpo) else '-'
        
        # Adicionar à lista
        produto = {
            'nome': nome,
            'codigo': codigo,
            'valor': valor,
            'cor': cor,
            'quantidade': quantidade
        }
        self.produtos_list.append(produto)
        
        # Atualizar tabela
        self._atualizar_tabela_produtos()
        
        # Limpar campos
        self.input_produto.setCurrentIndex(0)  # Voltar para item vazio
        self.input_valor.clear()
        self.combo_cor.setCurrentIndex(0)
        self.combo_cor_tampa.setCurrentIndex(0)
        self.combo_cor_corpo.setCurrentIndex(0)
        self.input_quantidade.setValue(1)
        
        # Focar no campo produto
        self.input_produto.setFocus()
    
    def _atualizar_tabela_produtos(self):
        """Atualiza a tabela de produtos"""
        self.table_produtos.setRowCount(len(self.produtos_list))
        total = 0
        
        for row, produto in enumerate(self.produtos_list):
            # Nome (pode ser 'nome' ou 'descricao' dependendo da origem)
            nome = produto.get('nome', produto.get('descricao', ''))
            self.table_produtos.setItem(row, 0, QTableWidgetItem(nome))
            
            # Quantidade
            quantidade = produto.get('quantidade', 1)
            self.table_produtos.setItem(row, 1, QTableWidgetItem(str(quantidade)))
            
            # Código
            codigo = produto.get('codigo', '')
            self.table_produtos.setItem(row, 2, QTableWidgetItem(codigo if codigo else '-'))
            
            # Valor (multiplicado pela quantidade)
            valor_unitario = produto['valor']
            valor_total = valor_unitario * quantidade
            self.table_produtos.setItem(row, 3, QTableWidgetItem(f"R$ {valor_total:.2f}"))
            total += valor_total
            
            # Cor - design simplificado
            cor = produto.get('cor', '-')
            self.table_produtos.setItem(row, 4, QTableWidgetItem(cor))
            
            # Ações - Botão mais compacto e bem posicionado
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(3, 3, 3, 3)
            btn_layout.setSpacing(0)
            
            # ícone estilo circular pequeno
            btn_remover = QPushButton("")
            btn_remover.setObjectName("btnRemover")
            btn_remover.setFixedSize(28, 28)
            btn_remover.setToolTip("Remover produto")
            btn_remover.setStyleSheet("""
                QPushButton#btnRemover {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 14px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton#btnRemover::after {
                    content: '×';
                }
                QPushButton#btnRemover:hover {
                    background-color: #c82333;
                }
                QPushButton#btnRemover:pressed {
                    background-color: #bd2130;
                }
            """)
            # usar um label pequeno dentro do botão para exibir o × (fallback se CSS content não funcionar)
            btn_remover.setText('×')
            btn_remover.clicked.connect(lambda checked, idx=row: self._remover_produto(idx))
            btn_layout.addStretch()
            btn_layout.addWidget(btn_remover)
            btn_layout.addStretch()
            
            self.table_produtos.setCellWidget(row, 5, btn_widget)
            
            # Altura da linha
            self.table_produtos.setRowHeight(row, 40)
        
        # Ajustar altura da tabela dinamicamente
        self._ajustar_altura_tabela()
        
        # Atualizar label total dos produtos
        if hasattr(self, 'label_total'):
            self.label_total.setText(f"R$ {total:.2f}")
        
        # Recalcular totais gerais
        self._calcular_total()
    
    def _ajustar_altura_tabela(self):
        """Ajusta a altura da tabela com base no número de produtos"""
        num_produtos = len(self.produtos_list)
        # obter alturas reais do header/linhas para cálculo mais preciso
        header_height = self.table_produtos.horizontalHeader().height() or 32
        # altura da linha configurada (caso tenha sido alterada)
        default_row_height = self.table_produtos.verticalHeader().defaultSectionSize() or 34

        if num_produtos <= 0:
            # Mostrar 2 linhas vazias quando não houver produtos, manter compacto
            visible_rows = 2
        else:
            # Mostrar até 6 linhas antes de ativar scroll interno
            visible_rows = min(max(1, num_produtos), 6)

        padding = 8  # padding extra
        altura_ideal = header_height + (visible_rows * default_row_height) + padding

        # Limitar entre 120 e 360 pixels para evitar espaços mortos
        altura_ideal = max(120, min(360, altura_ideal))

        # usar setFixedHeight para manter layout consistente dentro do modal
        self.table_produtos.setFixedHeight(altura_ideal)
    
    def _remover_produto(self, index):
        """Remove um produto da lista"""
        if 0 <= index < len(self.produtos_list):
            self.produtos_list.pop(index)
            self._atualizar_tabela_produtos()
    
    def _salvar_pedido(self):
        """Salva o pedido no banco de dados"""
        # Validações
        if not self.input_nome_cliente.text().strip():
            QMessageBox.warning(self, "Aviso", "Digite o nome do cliente!")
            return
        
        if not self.produtos_list:
            QMessageBox.warning(self, "Aviso", "Adicione pelo menos um produto!")
            return
        
        try:
            # Dados do cliente
            cliente_data = {
                'nome': self.input_nome_cliente.text().strip(),
                'cnpj': self.input_cpf.text().strip(),
                'telefone': self.input_telefone.text().strip(),
                'endereco': self.input_endereco.text().strip()
            }
            
            # Salvar cliente se não existir
            if self.cliente_selecionado:
                cliente_id = self.cliente_selecionado['id']
            else:
                cliente_id = db_manager.salvar_cliente(
                    cliente_data['nome'],
                    cliente_data['cnpj'],
                    cliente_data['telefone'],
                    cliente_data['endereco']
                )
            
            # Calcular total
            valor_total = sum(p['valor'] for p in self.produtos_list)
            
            # Obter dados de pagamento
            try:
                entrada = float(self.entrada_input.text().replace(',', '.')) if self.entrada_input.text() else 0.0
            except:
                entrada = 0.0
                
            try:
                frete = float(self.frete_input.text().replace(',', '.')) if self.frete_input.text() else 0.0
            except:
                frete = 0.0
                
            try:
                desconto = float(self.desconto_input.text().replace(',', '.')) if self.desconto_input.text() else 0.0
            except:
                desconto = 0.0
            
            try:
                prazo = int(self.prazo_entrega.text()) if self.prazo_entrega.text() else 0
            except:
                prazo = 0
            
            # Total final considerando frete e desconto
            valor_final = valor_total + frete - desconto
            valor_a_receber = valor_final - entrada
            
            # Número da OS - usar original se for edição, caso contrário gerar novo
            if self.is_editing and self.numero_os_original:
                numero_os = self.numero_os_original
                print(f"Usando número OS original: {numero_os}")
            else:
                numero_os = Contador().get_proximo_numero()
                print(f"Gerando novo número OS: {numero_os}")
            
            # Dados do pedido
            if self.is_editing and self.pedido_id_editando:
                # Gerar detalhes dos produtos para exibição na interface
                detalhes_produtos = []
                for produto in self.produtos_list:
                    nome = produto.get('nome', produto.get('descricao', ''))
                    valor = produto.get('valor', 0)
                    quantidade = produto.get('quantidade', 1)
                    cor = produto.get('cor', '-')
                    
                    # Montar linha do produto
                    linha_produto = f"• {nome}"
                    if quantidade > 1:
                        linha_produto += f" (Qtd: {quantidade})"
                    if cor and cor != '-':
                        linha_produto += f" — Cor: {cor}"
                    linha_produto += f" - R$ {valor * quantidade:.2f}"
                    
                    detalhes_produtos.append(linha_produto)
                
                detalhes_texto = '\n'.join(detalhes_produtos)
                
                
                # Para atualização, usar apenas campos que existem na tabela ordem_servico
                pedido_data = {
                    'numero_os': numero_os,
                    'nome_cliente': cliente_data['nome'],
                    'cpf_cliente': cliente_data['cnpj'],  # CPF/CNPJ vai para cpf_cliente
                    'telefone_cliente': cliente_data['telefone'],
                    'detalhes_produto': detalhes_texto,  # Campo que aparece na interface
                    'valor_produto': valor_total,
                    'valor_entrada': entrada,
                    'frete': frete,
                    'forma_pagamento': self.metodo_pagamento.currentText(),
                    'prazo': prazo,
                    'status': self.status_pedido.currentText(),
                    # dados_json pode conter info adicional como produtos, desconto, etc.
                    'dados_json': json.dumps({
                        'produtos': self.produtos_list,
                        'desconto': desconto,
                        'valor_total': valor_final,
                        'valor_a_receber': valor_a_receber
                    }, ensure_ascii=False)
                }
            else:
                # Para criação, usar estrutura completa
                pedido_data = {
                    'numero_os': numero_os,
                    'nome_cliente': cliente_data['nome'],  # Corrigido: nome_cliente em vez de cliente_nome
                    'cpf_cliente': cliente_data['cnpj'],   # Adicionado campo obrigatório
                    'telefone_cliente': cliente_data['telefone'],  # Adicionado campo obrigatório
                    'valor_total': valor_final,
                    'valor_entrada': entrada,
                    'valor_a_receber': valor_a_receber,
                    'frete': frete,
                    'desconto': desconto,
                    'forma_pagamento': self.metodo_pagamento.currentText(),
                    'prazo': prazo,
                    'status': self.status_pedido.currentText(),
                    'produtos': self.produtos_list
                }
            
            # Salvar ou atualizar pedido
            
            if self.is_editing and self.pedido_id_editando:
                # Atualizar pedido existente
                print(f"Atualizando pedido ID: {self.pedido_id_editando}")
                resultado = db_manager.atualizar_pedido(self.pedido_id_editando, pedido_data)
                pedido_id = self.pedido_id_editando
                QMessageBox.information(self, "Sucesso", f"Pedido #{numero_os:05d} atualizado com sucesso!")
            else:
                # Criar novo pedido
                print(f"Criando novo pedido")
                pedido_id = db_manager.salvar_ordem(pedido_data)
                QMessageBox.information(self, "Sucesso", f"Pedido #{numero_os:05d} salvo com sucesso!")
            
            # Emitir sinal e fechar
            self.pedido_salvo.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar pedido:\n{e}")
    
    def _aplicar_estilo(self):
        """Aplica o estilo moderno em tema escuro com cinza e branco"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #555555;
                border-radius: 12px;
                margin: 20px 0px;
                padding: 30px 20px 20px 20px;
                background-color: #3a3a3a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
                color: #ffffff;
                font-size: 18px;
            }
            
            QLabel {
                color: #ffffff;
                font-weight: 500;
                font-size: 12px;
            }
            
            #titulo {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px 0;
            }
            
            #total {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QLineEdit, QComboBox {
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 15px 20px;
                font-size: 16px;
                background-color: #3a3a3a;
                color: #ffffff;
                min-height: 45px;
                height: 50px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #888888;
            }
            
            QTableWidget {
                border: 1px solid #555555;
                border-radius: 6px;
                background-color: #3a3a3a;
                gridline-color: #555555;
                font-size: 12px;
                color: #ffffff;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            
            QHeaderView::section {
                background-color: #555555;
                color: #ffffff;
                padding: 10px 8px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #2b2b2b;
            }
            
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                min-height: 20px;
            }
            
            #btnAdd {
                background-color: #555555;
                color: #ffffff;
            }
            
            #btnAdd:hover {
                background-color: #666666;
            }
            
            #btnSalvar {
                background-color: #555555;
                color: #ffffff;
            }
            
            #btnSalvar:hover {
                background-color: #666666;
            }
            
            #btnCancelar {
                background-color: #555555;
                color: #ffffff;
            }
            
            #btnCancelar:hover {
                background-color: #666666;
            }
            
            #btnRemover {
                background-color: #555555;
                color: #ffffff;
                padding: 5px 10px;
                font-size: 11px;
            }
            
            #btnRemover:hover {
                background-color: #666666;
            }
            
            #btnFullscreen {
                background-color: #cccccc;
                color: #000000;
                padding: 8px 16px;
                font-size: 12px;
                min-height: 15px;
                margin-left: 10px;
            }
            
            #btnFullscreen:hover {
                background-color: #dddddd;
            }
            
            /* Estilos específicos para seção de pagamento */
            #pagamentoGroup {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #666666;
                border-radius: 8px;
                margin-top: 20px;
                margin-bottom: 18px;
                padding: 20px 18px 22px 18px;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            
            #pagamentoGroup::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
                color: #ffffff;
                font-weight: bold;
                background: transparent;
                font-size: 18px;
            }
            
            #entradaInput, #freteInput, #descontoInput, #prazoEntrega,
            #metodoPagamento, #statusPedido {
                min-height: 50px;
                height: 55px;
                font-size: 16px;
                color: #ffffff;
                background-color: #3a3a3a;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 15px 20px;
            }
            
            #entradaInput:focus, #freteInput:focus, #descontoInput:focus, 
            #prazoEntrega:focus, #metodoPagamento:focus, #statusPedido:focus {
                border: 2px solid #888888;
                background-color: #404040;
            }
            
            #entradaInput:hover, #freteInput:hover, #descontoInput:hover,
            #prazoEntrega:hover, #metodoPagamento:hover, #statusPedido:hover {
                border: 2px solid #777777;
            }
        """)
    
    def _preencher_dados_cliente(self, dados):
        """Preenche os campos do cliente com os dados fornecidos"""
        try:
            if 'nome' in dados and dados['nome']:
                self.nome_input.setText(dados['nome'])
            if 'cpf' in dados and dados['cpf']:
                self.cpf_input.setText(dados['cpf'])
            if 'telefone' in dados and dados['telefone']:
                self.telefone_input.setText(dados['telefone'])
            if 'email' in dados and dados['email']:
                self.email_input.setText(dados['email'])
            
            # Endereço combinado
            endereco_parts = []
            if 'rua' in dados and dados['rua']:
                endereco_parts.append(dados['rua'])
            if 'numero' in dados and dados['numero']:
                endereco_parts.append(dados['numero'])
            if 'cidade' in dados and dados['cidade']:
                endereco_parts.append(dados['cidade'])
            
            if endereco_parts:
                self.endereco_input.setText(', '.join(endereco_parts))
                
        except Exception as e:
            print(f"Erro ao preencher dados do cliente: {e}")

    def abrir_modal_edicao(self, pedido_id):
        """Abre modal para editar pedido - compatibilidade com gerenciador de clientes"""
        try:
            print(f"=== ABRIR_MODAL_EDICAO: pedido_id={pedido_id} ===")
            pedidos = db_manager.listar_pedidos_ordenados_por_prazo()
            print(f"Pedidos carregados: {len(pedidos) if pedidos else 0}")
            
            pedido_data = None
            for i, pedido in enumerate(pedidos):
                print(f"  Pedido {i}: {type(pedido)} - ID: {pedido.get('id', 'SEM_ID')}")
                if isinstance(pedido, dict):
                    print(f"    Chaves: {list(pedido.keys())}")
                if pedido.get('id') == pedido_id:
                    pedido_data = pedido
                    print(f"  ENCONTRADO! Pedido {i}")
                    break
                    
            if pedido_data:
                print(f"Carregando dados do pedido: {type(pedido_data)}")
                self._carregar_dados_pedido(pedido_data)
                print("Mostrando modal...")
                self.show()
                print("Modal mostrado com sucesso")
            else:
                print("ERRO: Pedido não encontrado na lista!")
                QMessageBox.warning(self, "Erro", "Pedido não encontrado!")
                
        except Exception as e:
            print(f"=== ERRO em abrir_modal_edicao: {e} ===")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Erro ao carregar pedido: {e}")

    def _carregar_dados_pedido(self, pedido_data):
        """Carrega dados do pedido para edição"""
        try:
            # Marcar como edição e salvar número da OS original
            self.is_editing = True
            if 'id' in pedido_data:
                self.pedido_id_editando = pedido_data['id']
            if 'numero_os' in pedido_data:
                self.numero_os_original = pedido_data['numero_os']
                
                # Atualizar o título se já foi criado
                if self.titulo_label:
                    self.titulo_label.setText(f"Ordem de Serviço Nº {self.numero_os_original:05d}")
            
            
            # Preencher dados do cliente - mapeando os campos do banco
            # Mapear nome_cliente para cliente
            if 'nome_cliente' in pedido_data:
                self.input_nome_cliente.setText(pedido_data['nome_cliente'])
            elif 'cliente' in pedido_data:
                self.input_nome_cliente.setText(pedido_data['cliente'])
                
            # Mapear telefone_cliente para telefone
            if 'telefone_cliente' in pedido_data:
                self.input_telefone.setText(pedido_data['telefone_cliente'])
            elif 'telefone' in pedido_data:
                self.input_telefone.setText(pedido_data['telefone'])
                
            # Mapear endereco_cliente para endereco
            if 'endereco_cliente' in pedido_data:
                self.input_endereco.setText(pedido_data['endereco_cliente'])
            elif 'endereco' in pedido_data:
                self.input_endereco.setText(pedido_data['endereco'])
                
            # Mapear cpf_cliente para cpf
            if 'cpf_cliente' in pedido_data:
                self.input_cpf.setText(pedido_data['cpf_cliente'])
            elif 'cnpj' in pedido_data:
                self.input_cpf.setText(pedido_data['cnpj'])
                
            # Carregar produtos se houver
            if 'produtos' in pedido_data and pedido_data['produtos']:
                for produto in pedido_data['produtos']:
                    self.produtos_list.append(produto)
                self._atualizar_tabela_produtos()
                
            # Preencher dados de pagamento - mapeando os campos do banco
            # Mapear valor_entrada para entrada_input
            if 'valor_entrada' in pedido_data:
                self.entrada_input.setText(str(pedido_data['valor_entrada']))
            elif 'entrada' in pedido_data:
                self.entrada_input.setText(str(pedido_data['entrada']))
                
            if 'frete' in pedido_data:
                self.frete_input.setText(str(pedido_data['frete']))
            if 'desconto' in pedido_data:
                self.desconto_input.setText(str(pedido_data['desconto']))
                
            # Mapear forma_pagamento para metodo_pagamento
            if 'forma_pagamento' in pedido_data:
                index = self.metodo_pagamento.findText(pedido_data['forma_pagamento'])
                if index >= 0:
                    self.metodo_pagamento.setCurrentIndex(index)
            elif 'metodo_pagamento' in pedido_data:
                index = self.metodo_pagamento.findText(pedido_data['metodo_pagamento'])
                if index >= 0:
                    self.metodo_pagamento.setCurrentIndex(index)
                    
            if 'prazo' in pedido_data:
                self.prazo_entrega.setText(str(pedido_data['prazo']))
            if 'status' in pedido_data:
                index = self.status_pedido.findText(pedido_data['status'])
                if index >= 0:
                    self.status_pedido.setCurrentIndex(index)
                    
        except Exception as e:
            print(f"Erro ao carregar dados do pedido: {e}")
            import traceback
            traceback.print_exc()

    def _preencher_compatibilidade(self, dados):
        """Método de compatibilidade com modal antigo"""
        try:
            if 'nome_cliente' in dados:
                self.input_nome_cliente.setText(dados['nome_cliente'])
            if 'cpf_cliente' in dados:
                self.input_cpf.setText(dados['cpf_cliente'])
            if 'telefone_cliente' in dados:
                self.input_telefone.setText(dados['telefone_cliente'])
            if 'endereco_cliente' in dados:
                self.input_endereco.setText(dados['endereco_cliente'])
        except Exception as e:
            print(f"Erro na compatibilidade: {e}")

    def _criar_modal_completo(self, pedido_data=None, cliente_fixo=False, nome_cliente_label=None):
        """Método de compatibilidade com modal antigo"""
        try:
            if pedido_data:
                self._carregar_dados_pedido(pedido_data)
            
            # Se há nome do cliente no label, usar no título
            if nome_cliente_label:
                self.setWindowTitle(f"Pedido para: {nome_cliente_label}")
            
            self.show()
        except Exception as e:
            print(f"Erro ao criar modal completo: {e}")


def abrir_novo_pedido(parent=None):
    """Função para abrir o modal de novo pedido"""
    modal = NovoPedidosModal(parent)
    return modal.exec()