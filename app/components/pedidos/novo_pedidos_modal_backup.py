"""
Modal de Pedidos Simplificado
Design moderno em tons de cinza, sem camadas desnecessárias
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QWidget, QMessageBox, QCompleter, QFrame, QFormLayout,
                            QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt6.QtGui import QFont

from database import db_manager
from app.numero_os import Contador


class NovoPedidosModal(QDialog):
    pedido_salvo = pyqtSignal()
    
    def __init__(self, parent=None, dados_cliente=None, pedido_id=None):
        super().__init__(parent)
        self.produtos_dict = {}
        self.produtos_list = []
        self.cliente_selecionado = None
        self.dados_cliente_inicial = dados_cliente
        self.pedido_id = pedido_id
        
        if pedido_id:
            self.setWindowTitle(f"Editar Ordem de Serviço Nº {pedido_id:05d}")
        else:
            self.setWindowTitle("Nova Ordem de Serviço")
        
        # Configurar tamanho - meia tela por padrão
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        screen = QApplication.primaryScreen().geometry()
        width = int(screen.width() * 0.7)  # 70% da largura da tela
        height = int(screen.height() * 0.8)  # 80% da altura da tela
        
        self.setMinimumSize(1000, 800)  # Tamanho mínimo
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
            clientes_lista = []
            
            for row in rows:
                nome = (row[1] or '').strip()
                if nome:
                    cliente_data = {
                        "id": row[0],
                        "nome": nome,
                        "cnpj": row[2] or '',
                        "telefone": row[3] or '',
                        "endereco": row[4] or ''
                    }
                    self.clientes_dict[nome] = cliente_data
                    clientes_lista.append(nome)
            
            # Configurar completer para cliente
            if hasattr(self, 'input_cliente'):
                completer = QCompleter(clientes_lista)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                self.input_cliente.setCompleter(completer)
                
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            self.clientes_dict = {}
    
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
                background-color: #0d7377;
            }
        """)
        
        # Widget principal dentro do scroll
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
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
        
        # Configurar scroll area
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
    
    def _criar_header(self, layout):
        """Cria o cabeçalho com número da OS"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Número da OS
        numero_os = Contador().get_proximo_numero()
        titulo = QLabel(f"Ordem de Serviço Nº {numero_os:05d}")
        titulo.setObjectName("titulo")
        
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
    
    def _criar_secao_cliente(self, layout):
        """Cria a seção de dados do cliente"""
        group = QGroupBox("Cliente")
        group_layout = QVBoxLayout(group)
        
        # Linha 1: Nome e CNPJ
        row1 = QHBoxLayout()
        
        # Nome
        nome_layout = QVBoxLayout()
        nome_layout.addWidget(QLabel("Nome:"))
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Digite o nome do cliente...")
        nome_layout.addWidget(self.input_cliente)
        row1.addLayout(nome_layout, 2)
        
        # CNPJ
        cnpj_layout = QVBoxLayout()
        cnpj_layout.addWidget(QLabel("CNPJ:"))
        self.input_cnpj = QLineEdit()
        self.input_cnpj.setPlaceholderText("00.000.000/0000-00")
        cnpj_layout.addWidget(self.input_cnpj)
        row1.addLayout(cnpj_layout, 1)
        
        group_layout.addLayout(row1)
        
        # Linha 2: Telefone e Endereço
        row2 = QHBoxLayout()
        
        # Telefone
        tel_layout = QVBoxLayout()
        tel_layout.addWidget(QLabel("Telefone:"))
        self.input_telefone = QLineEdit()
        self.input_telefone.setPlaceholderText("(11) 99999-9999")
        tel_layout.addWidget(self.input_telefone)
        row2.addLayout(tel_layout, 1)
        
        # Endereço
        end_layout = QVBoxLayout()
        end_layout.addWidget(QLabel("Endereço:"))
        self.input_endereco = QLineEdit()
        self.input_endereco.setPlaceholderText("Endereço completo...")
        end_layout.addWidget(self.input_endereco)
        row2.addLayout(end_layout, 2)
        
        group_layout.addLayout(row2)
        
        # Conectar evento do cliente
        self.input_cliente.textChanged.connect(self._on_cliente_changed)
        
        layout.addWidget(group)
    
    def _criar_secao_produtos(self, layout):
        """Cria a seção de produtos"""
        group = QGroupBox("Produtos")
        group_layout = QVBoxLayout(group)
        
        # Formulário de adição
        form_layout = QHBoxLayout()
        
        # Produto
        produto_layout = QVBoxLayout()
        produto_layout.addWidget(QLabel("Produto:"))
        self.input_produto = QLineEdit()
        self.input_produto.setPlaceholderText("Digite o nome do produto...")
        produto_layout.addWidget(self.input_produto)
        form_layout.addLayout(produto_layout, 2)
        
        # Valor
        valor_layout = QVBoxLayout()
        valor_layout.addWidget(QLabel("Valor (R$):"))
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("0,00")
        valor_layout.addWidget(self.input_valor)
        form_layout.addLayout(valor_layout, 1)
        
        # Cor
        cor_layout = QVBoxLayout()
        cor_layout.addWidget(QLabel("Cor:"))
        self.combo_cor = QComboBox()
        self.combo_cor.addItems(['', 'Branco', 'Preto', 'Azul', 'Verde', 'Vermelho', 'Amarelo', 'Personalizado'])
        cor_layout.addWidget(self.combo_cor)
        form_layout.addLayout(cor_layout, 1)
        
        # Botão adicionar
        btn_add = QPushButton("+ Adicionar")
        btn_add.setFixedHeight(35)
        btn_add.setObjectName("btnAdd")
        btn_add.clicked.connect(self._adicionar_produto)
        form_layout.addWidget(btn_add)
        
        group_layout.addLayout(form_layout)
        
        # Tabela de produtos
        self.table_produtos = QTableWidget(0, 5)
        self.table_produtos.setHorizontalHeaderLabels(['Nome', 'Código', 'Valor (R$)', 'Cor', 'Ações'])
        
        # Aplicar estilo específico da tabela
        self.table_produtos.setStyleSheet("""
            QTableWidget {
                border: 2px solid #555555;
                border-radius: 8px;
                background-color: #3a3a3a;
                gridline-color: #555555;
                font-size: 13px;
                color: #ffffff;
                selection-background-color: #555555;
            }
            
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #555555;
                border-right: 1px solid #555555;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            
            QTableWidget::item:selected {
                background-color: #555555;
                color: #ffffff;
            }
            
            QTableWidget::item:hover {
                background-color: #404040;
            }
            
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 12px 8px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #555555;
                border-bottom: 2px solid #555555;
                font-size: 13px;
            }
            
            QHeaderView::section:first {
                border-left: none;
            }
            
            QHeaderView::section:last {
                border-right: none;
            }
            
            QTableWidget::horizontalHeader {
                background-color: #2d2d2d;
            }
            
            QTableWidget QScrollBar:vertical {
                background-color: #3a3a3a;
                width: 12px;
                border-radius: 6px;
            }
            
            QTableWidget QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QTableWidget QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
        """)
        
        # Configurar colunas
        header = self.table_produtos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Nome
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Código
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Valor
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Cor
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Ações
        
        # Larguras das colunas
        self.table_produtos.setColumnWidth(1, 100)  # Código
        self.table_produtos.setColumnWidth(2, 120)  # Valor
        self.table_produtos.setColumnWidth(3, 100)  # Cor
        self.table_produtos.setColumnWidth(4, 200)  # Ações
        
        # Altura das linhas
        self.table_produtos.verticalHeader().setDefaultSectionSize(50)
        self.table_produtos.verticalHeader().setVisible(False)
        
        group_layout.addWidget(self.table_produtos)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("Valor Total (R$):"))
        self.label_total = QLabel("R$ 0,00")
        self.label_total.setObjectName("total")
        total_layout.addWidget(self.label_total)
        
        group_layout.addLayout(total_layout)
        
        # Configurar completer para produtos
        self._configurar_completer_produtos()
        
        # Conectar eventos
        self.input_produto.textChanged.connect(self._on_produto_changed)
        self.input_valor.returnPressed.connect(self._adicionar_produto)
        self.input_produto.returnPressed.connect(self._adicionar_produto)
        
        layout.addWidget(group)
    
    def _configurar_completer_produtos(self):
        """Configura autocomplete para produtos"""
        produtos_nomes = [produto['nome'] for produto in self.produtos_dict.values() if 'nome' in produto]
        # Remove duplicatas mantendo ordem
        produtos_unicos = list(dict.fromkeys(produtos_nomes))
        
        completer = QCompleter(produtos_unicos)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.activated.connect(self._on_produto_selecionado)
        self.input_produto.setCompleter(completer)
    
    def _criar_secao_pagamento(self, layout):
        """Cria a seção de informações de pagamento"""
        
        pagamento_group = QGroupBox("Informações de Pagamento")
        pagamento_group.setObjectName("pagamentoGroup")
        pagamento_group.setStyleSheet("""
            QGroupBox {
                background-color: #3a3a3a;
                border: 2px solid #0d7377;
                border-radius: 10px;
                margin: 10px 0;
                padding-top: 20px;
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px 0 5px;
                color: #0d7377;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        
        group_layout = QVBoxLayout(pagamento_group)
        group_layout.setSpacing(25)
        group_layout.setContentsMargins(20, 30, 20, 20)
        
        # === VALORES FINANCEIROS ===
        valores_section = QFrame()
        valores_section.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
            }
        """)
        valores_section_layout = QVBoxLayout(valores_section)
        valores_section_layout.setSpacing(20)
        
        # Título da seção
        valores_title = QLabel("💰 Valores Financeiros")
        valores_title.setStyleSheet("""
            color: #0d7377; 
            font-weight: bold; 
            font-size: 16px; 
            margin-bottom: 15px;
            padding: 8px 0;
        """)
        valores_section_layout.addWidget(valores_title)
        
        # Entrada
        entrada_layout = QHBoxLayout()
        entrada_layout.setSpacing(20)
        entrada_label = QLabel("Entrada:")
        entrada_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 140px; font-size: 14px;")
        self.entrada_input = QLineEdit()
        self.entrada_input.setPlaceholderText("R$ 0,00")
        self.entrada_input.setObjectName("entradaInput")
        self.entrada_input.setMinimumHeight(45)
        entrada_layout.addWidget(entrada_label)
        entrada_layout.addWidget(self.entrada_input)
        valores_section_layout.addLayout(entrada_layout)
        
        # Frete
        frete_layout = QHBoxLayout()
        frete_layout.setSpacing(20)
        frete_label = QLabel("Frete:")
        frete_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 140px; font-size: 14px;")
        self.frete_input = QLineEdit()
        self.frete_input.setPlaceholderText("R$ 0,00")
        self.frete_input.setObjectName("freteInput")
        self.frete_input.setMinimumHeight(45)
        frete_layout.addWidget(frete_label)
        frete_layout.addWidget(self.frete_input)
        valores_section_layout.addLayout(frete_layout)
        
        # Desconto
        desconto_layout = QHBoxLayout()
        desconto_layout.setSpacing(20)
        desconto_label = QLabel("Desconto:")
        desconto_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 140px; font-size: 14px;")
        self.desconto_input = QLineEdit()
        self.desconto_input.setPlaceholderText("R$ 0,00")
        self.desconto_input.setObjectName("descontoInput")
        self.desconto_input.setMinimumHeight(45)
        desconto_layout.addWidget(desconto_label)
        desconto_layout.addWidget(self.desconto_input)
        valores_section_layout.addLayout(desconto_layout)
        
        group_layout.addWidget(valores_section)
        
        # === MÉTODOS E PRAZOS ===
        metodos_section = QFrame()
        metodos_section.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
            }
        """)
        metodos_section_layout = QVBoxLayout(metodos_section)
        metodos_section_layout.setSpacing(20)
        
        # Título da seção
        metodos_title = QLabel("💳 Métodos e Prazos")
        metodos_title.setStyleSheet("""
            color: #0d7377; 
            font-weight: bold; 
            font-size: 16px; 
            margin-bottom: 15px;
            padding: 8px 0;
        """)
        metodos_section_layout.addWidget(metodos_title)
        
        # Método de Pagamento
        metodo_layout = QHBoxLayout()
        metodo_layout.setSpacing(20)
        metodo_label = QLabel("Método Pagamento:")
        metodo_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 140px; font-size: 14px;")
        self.metodo_pagamento = QComboBox()
        self.metodo_pagamento.setObjectName("metodoPagamento")
        self.metodo_pagamento.setMinimumHeight(45)
        self.metodo_pagamento.addItems([
            "PIX",
            "Cartão de Crédito", 
            "Cartão de Débito",
            "Dinheiro",
            "Transferência Bancária",
            "Boleto",
            "Cheque",
            "Crediário"
        ])
        metodo_layout.addWidget(metodo_label)
        metodo_layout.addWidget(self.metodo_pagamento)
        metodos_section_layout.addLayout(metodo_layout)
        
        # Prazo de Entrega
        prazo_layout = QHBoxLayout()
        prazo_layout.setSpacing(20)
        prazo_label = QLabel("Prazo Entrega:")
        prazo_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 140px; font-size: 14px;")
        self.prazo_entrega = QLineEdit()
        self.prazo_entrega.setPlaceholderText("Ex: 30 dias")
        self.prazo_entrega.setObjectName("prazoEntrega")
        self.prazo_entrega.setMinimumHeight(45)
        prazo_layout.addWidget(prazo_label)
        prazo_layout.addWidget(self.prazo_entrega)
        metodos_section_layout.addLayout(prazo_layout)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.setSpacing(20)
        status_label = QLabel("Status Pedido:")
        status_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 140px; font-size: 14px;")
        self.status_pedido = QComboBox()
        self.status_pedido.setObjectName("statusPedido")
        self.status_pedido.setMinimumHeight(45)
        try:
            from app.utils.statuses import load_statuses
            self.status_pedido.addItems(load_statuses())
        except Exception:
            self.status_pedido.addItems([
                "Em Produção",
                "Aguardando Material", 
                "Pronto",
                "Enviado",
                "Entregue",
                "Cancelado"
            ])
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_pedido)
        metodos_section_layout.addLayout(status_layout)
        
        group_layout.addWidget(metodos_section)
        
        # === TOTAIS ===
        totais_section = QFrame()
        totais_section.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
            }
        """)
        totais_section_layout = QVBoxLayout(totais_section)
        totais_section_layout.setSpacing(20)
        
        # Título da seção
        totais_title = QLabel("🧮 Totais")
        totais_title.setStyleSheet("""
            color: #0d7377; 
            font-weight: bold; 
            font-size: 16px; 
            margin-bottom: 15px;
            padding: 8px 0;
        """)
        totais_section_layout.addWidget(totais_title)
        
        # Total Geral
        total_layout = QHBoxLayout()
        total_layout.setSpacing(20)
        total_label_text = QLabel("Total Geral:")
        total_label_text.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 140px; font-size: 14px;")
        self.total_label = QLabel("R$ 0,00")
        self.total_label.setStyleSheet("""
            color: #0d7377; 
            font-weight: bold; 
            font-size: 18px; 
            background-color: #1a1a1a;
            border: 2px solid #0d7377;
            border-radius: 8px;
            padding: 12px;
        """)
        total_layout.addWidget(total_label_text)
        total_layout.addWidget(self.total_label)
        totais_section_layout.addLayout(total_layout)
        
        # Valor a Receber
        receber_layout = QHBoxLayout()
        receber_layout.setSpacing(20)
        receber_label_text = QLabel("Valor a Receber:")
        receber_label_text.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 140px; font-size: 14px;")
        self.valor_receber_label = QLabel("R$ 0,00")
        self.valor_receber_label.setStyleSheet("""
            color: #00ff00; 
            font-weight: bold; 
            font-size: 18px; 
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 8px;
            padding: 12px;
        """)
        receber_layout.addWidget(receber_label_text)
        receber_layout.addWidget(self.valor_receber_label)
        totais_section_layout.addLayout(receber_layout)
        
        group_layout.addWidget(totais_section)
        
        # Conectar cálculos
        self.entrada_input.textChanged.connect(self._calcular_total)
        self.frete_input.textChanged.connect(self._calcular_total)
        self.desconto_input.textChanged.connect(self._calcular_total)
        
        layout.addWidget(pagamento_group)
        entrada_label = QLabel("Entrada (R$):")
        entrada_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px; font-size: 13px;")
        self.entrada_input = QLineEdit()
        self.entrada_input.setPlaceholderText("0,00")
        self.entrada_input.setObjectName("entradaInput")
        self.entrada_input.setMinimumHeight(40)
        entrada_layout.addWidget(entrada_label)
        entrada_layout.addWidget(self.entrada_input)
        valores_section_layout.addLayout(entrada_layout)
        
        # Frete
        frete_layout = QHBoxLayout()
        frete_layout.setSpacing(15)
        frete_label = QLabel("Frete (R$):")
        frete_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px; font-size: 13px;")
        self.frete_input = QLineEdit()
        self.frete_input.setPlaceholderText("0,00")
        self.frete_input.setObjectName("freteInput")
        self.frete_input.setMinimumHeight(40)
        frete_layout.addWidget(frete_label)
        frete_layout.addWidget(self.frete_input)
        valores_section_layout.addLayout(frete_layout)
        
        # Desconto
        desconto_layout = QHBoxLayout()
        desconto_layout.setSpacing(15)
        desconto_label = QLabel("Desconto (R$):")
        desconto_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px; font-size: 13px;")
        self.desconto_input = QLineEdit()
        self.desconto_input.setPlaceholderText("0,00")
        self.desconto_input.setObjectName("descontoInput")
        self.desconto_input.setMinimumHeight(40)
        desconto_layout.addWidget(desconto_label)
        desconto_layout.addWidget(self.desconto_input)
        valores_section_layout.addLayout(desconto_layout)
        
        group_layout.addWidget(valores_section)
        
        # === MÉTODO DE PAGAMENTO E PRAZOS ===
        metodos_section = QFrame()
        metodos_section.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 10px;
                padding: 18px;
                margin-bottom: 15px;
            }
        """)
        metodos_section_layout = QVBoxLayout(metodos_section)
        metodos_section_layout.setSpacing(15)
        
        # Título da seção
        metodos_title = QLabel("💳 Métodos e Prazos")
        metodos_title.setStyleSheet("""
            color: #ffffff; 
            font-weight: bold; 
            font-size: 15px; 
            margin-bottom: 10px;
            padding: 5px 0;
        """)
        metodos_section_layout.addWidget(metodos_title)
        
        # Método de Pagamento
        metodo_layout = QHBoxLayout()
        metodo_layout.setSpacing(15)
        metodo_label = QLabel("Método Pagamento:")
        metodo_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px; font-size: 13px;")
        self.metodo_pagamento = QComboBox()
        self.metodo_pagamento.setObjectName("metodoPagamento")
        self.metodo_pagamento.setMinimumHeight(40)
        self.metodo_pagamento.addItems([
            "PIX",
            "Cartão de Crédito", 
            "Cartão de Débito",
            "Dinheiro",
            "Transferência Bancária",
            "Boleto",
            "Cheque",
            "Crediário"
        ])
        metodo_layout.addWidget(metodo_label)
        metodo_layout.addWidget(self.metodo_pagamento)
        metodos_section_layout.addLayout(metodo_layout)
        
        # Prazo de Entrega
        prazo_layout = QHBoxLayout()
        prazo_layout.setSpacing(15)
        prazo_label = QLabel("Prazo Entrega:")
        prazo_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px; font-size: 13px;")
        self.prazo_entrega = QLineEdit()
        self.prazo_entrega.setPlaceholderText("Ex: 30 dias")
        self.prazo_entrega.setObjectName("prazoEntrega")
        self.prazo_entrega.setMinimumHeight(40)
        prazo_layout.addWidget(prazo_label)
        prazo_layout.addWidget(self.prazo_entrega)
        metodos_section_layout.addLayout(prazo_layout)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.setSpacing(15)
        status_label = QLabel("Status Pedido:")
        status_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px; font-size: 13px;")
        self.status_pedido = QComboBox()
        self.status_pedido.setObjectName("statusPedido")
        self.status_pedido.setMinimumHeight(40)
        try:
            from app.utils.statuses import load_statuses
            self.status_pedido.addItems(load_statuses())
        except Exception:
            self.status_pedido.addItems([
                "Em Produção",
                "Aguardando Material", 
                "Pronto",
                "Enviado",
                "Entregue",
                "Cancelado"
            ])
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_pedido)
        metodos_section_layout.addLayout(status_layout)
        
        group_layout.addWidget(metodos_section)
        
                # === TOTAIS ===
        totais_section = QFrame()
        totais_section.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 10px;
                padding: 18px;
                margin-bottom: 15px;
            }
        """)
        totais_section_layout = QVBoxLayout(totais_section)
        totais_section_layout.setSpacing(15)
        
        # Título da seção
        totais_title = QLabel("🧮 Totais")
        totais_title.setStyleSheet("""
            color: #ffffff; 
            font-weight: bold; 
            font-size: 15px; 
            margin-bottom: 10px;
            padding: 5px 0;
        """)
        totais_section_layout.addWidget(totais_title)
        
        # Total Geral
        total_layout = QHBoxLayout()
        total_layout.setSpacing(15)
        total_label_text = QLabel("Total Geral:")
        total_label_text.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px; font-size: 13px;")
        self.total_label = QLabel("R$ 0,00")
        self.total_label.setStyleSheet("""
            color: #0d7377; 
            font-weight: bold; 
            font-size: 16px; 
            background-color: #2d2d2d;
            border: 1px solid #0d7377;
            border-radius: 5px;
            padding: 10px;
        """)
        total_layout.addWidget(total_label_text)
        total_layout.addWidget(self.total_label)
        totais_section_layout.addLayout(total_layout)
        
        # Valor a Receber
        receber_layout = QHBoxLayout()
        receber_layout.setSpacing(15)
        receber_label_text = QLabel("Valor a Receber:")
        receber_label_text.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px; font-size: 13px;")
        self.valor_receber_label = QLabel("R$ 0,00")
        self.valor_receber_label.setStyleSheet("""
            color: #00ff00; 
            font-weight: bold; 
            font-size: 16px; 
            background-color: #2d2d2d;
            border: 1px solid #00ff00;
            border-radius: 5px;
            padding: 10px;
        """)
        receber_layout.addWidget(receber_label_text)
        receber_layout.addWidget(self.valor_receber_label)
        totais_section_layout.addLayout(receber_layout)
        
        group_layout.addWidget(totais_section)
        
        # Conectar cálculos
        self.entrada_input.textChanged.connect(self._calcular_total)
        self.frete_input.textChanged.connect(self._calcular_total)
        self.desconto_input.textChanged.connect(self._calcular_total)
        
        # === SEÇÃO 2: MÉTODO E PRAZO ===
        metodo_frame = QFrame()
        metodo_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)
        metodo_layout = QVBoxLayout(metodo_frame)
        metodo_layout.setSpacing(12)
        
        # Status do Pedido
        status_layout = QHBoxLayout()
        status_icon = QLabel("�")
        status_icon.setFixedWidth(30)
        status_icon.setStyleSheet("font-size: 16px;")
        status_label = QLabel("Status:")
        status_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px;")
        self.status_pedido = QComboBox()
        self.status_pedido.setObjectName("statusPedido")
        try:
            from app.utils.statuses import load_statuses
            self.status_pedido.addItems(load_statuses())
        except Exception:
            self.status_pedido.addItems([
                "Em Produção",
                "Aguardando Material", 
                "Pronto",
                "Enviado",
                "Entregue",
                "Cancelado"
            ])
        status_layout.addWidget(status_icon)
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_pedido)
        metodo_layout.addLayout(status_layout)
        
        # Método de Pagamento
        metodo_pagamento_layout = QHBoxLayout()
        metodo_icon = QLabel("💳")
        metodo_icon.setFixedWidth(30)
        metodo_icon.setStyleSheet("font-size: 16px;")
        metodo_label = QLabel("Forma de Pagamento:")
        metodo_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px;")
        self.metodo_pagamento = QComboBox()
        self.metodo_pagamento.setObjectName("metodoPagamento")
        self.metodo_pagamento.addItems([
            "PIX",
            "Cartão de Crédito", 
            "Cartão de Débito",
            "Dinheiro",
            "Transferência Bancária",
            "Boleto",
            "Cheque",
            "Crediário"
        ])
        metodo_pagamento_layout.addWidget(metodo_icon)
        metodo_pagamento_layout.addWidget(metodo_label)
        metodo_pagamento_layout.addWidget(self.metodo_pagamento)
        metodo_layout.addLayout(metodo_pagamento_layout)
        
        # Prazo para Entrega (em dias)
        prazo_layout = QHBoxLayout()
        prazo_icon = QLabel("📅")
        prazo_icon.setFixedWidth(30)
        prazo_icon.setStyleSheet("font-size: 16px;")
        prazo_label = QLabel("Prazo de Entrega:")
        prazo_label.setStyleSheet("color: #ffffff; font-weight: bold; min-width: 120px;")
        self.prazo_entrega = QLineEdit()
        self.prazo_entrega.setPlaceholderText("Ex: 30 dias")
        self.prazo_entrega.setObjectName("prazoEntrega")
        prazo_layout.addWidget(prazo_icon)
        prazo_layout.addWidget(prazo_label)
        prazo_layout.addWidget(self.prazo_entrega)
        metodo_layout.addLayout(prazo_layout)
        
        group_layout.addWidget(metodo_frame)
        
                # === SEÇÃO 3: TOTAIS ===
        totais_frame = QFrame()
        totais_frame.setStyleSheet("""
            QFrame {
                background-color: #1a4a4c;
                border: 2px solid #0d7377;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        totais_layout = QVBoxLayout(totais_frame)
        totais_layout.setSpacing(10)
        
        # Total Geral
        total_layout = QHBoxLayout()
        total_icon = QLabel("💰")
        total_icon.setFixedWidth(30)
        total_icon.setStyleSheet("font-size: 16px;")
        total_titulo = QLabel("Total Geral:")
        total_titulo.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px; min-width: 120px;")
        self.total_label = QLabel("R$ 0,00")
        self.total_label.setObjectName("totalLabel")
        self.total_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 12px;
                background-color: #1a5a5c;
                border: 2px solid #0d7377;
                border-radius: 6px;
                min-height: 25px;
            }
        """)
        total_layout.addWidget(total_icon)
        total_layout.addWidget(total_titulo)
        total_layout.addWidget(self.total_label)
        totais_layout.addLayout(total_layout)
        
        # Valor a Receber
        receber_layout = QHBoxLayout()
        receber_icon = QLabel("💵")
        receber_icon.setFixedWidth(30)
        receber_icon.setStyleSheet("font-size: 16px;")
        receber_titulo = QLabel("Valor a Receber:")
        receber_titulo.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px; min-width: 120px;")
        self.valor_receber_label = QLabel("R$ 0,00")
        self.valor_receber_label.setObjectName("valorReceberLabel")
        self.valor_receber_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 8px 12px;
                background-color: #1a5a5c;
                border: 2px solid #0d7377;
                border-radius: 6px;
                min-height: 25px;
            }
        """)
        receber_layout.addWidget(receber_icon)
        receber_layout.addWidget(receber_titulo)
        receber_layout.addWidget(self.valor_receber_label)
        totais_section_layout.addLayout(receber_layout)
        
        group_layout.addWidget(totais_section)
        
        # Conectar cálculos
        self.entrada_input.textChanged.connect(self._calcular_total)
        self.frete_input.textChanged.connect(self._calcular_total)
        self.desconto_input.textChanged.connect(self._calcular_total)
        
        layout.addWidget(pagamento_group)
    
    def _calcular_total(self):
        """Calcula o total com entrada, frete e desconto"""
        try:
            # Soma dos produtos
            total_produtos = 0.0
            for row in range(self.table_produtos.rowCount()):
                try:
                    valor_item = self.table_produtos.item(row, 2)  # Coluna "Valor"
                    if valor_item:
                        valor_text = valor_item.text().replace('R$ ', '').replace(',', '.')
                        total_produtos += float(valor_text)
                except:
                    continue
            
            # Valores de entrada, frete e desconto
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
            
            # Total final = produtos + frete - desconto
            total_final = total_produtos + frete - desconto
            
            # Valor a receber = total final - entrada
            valor_a_receber = total_final - entrada
            
            # Atualizar labels
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
    
    def _on_cliente_changed(self, texto):
        """Evento quando o texto do cliente muda"""
        if texto in self.clientes_dict:
            cliente = self.clientes_dict[texto]
            self.input_cnpj.setText(cliente['cnpj'])
            self.input_telefone.setText(cliente['telefone'])
            self.input_endereco.setText(cliente['endereco'])
            self.cliente_selecionado = cliente
        else:
            self.cliente_selecionado = None
    
    def _on_produto_changed(self, texto):
        """Evento quando o texto do produto muda"""
        if texto in self.produtos_dict:
            produto = self.produtos_dict[texto]
            self.input_valor.setText(f"{produto['preco']:.2f}")
    
    def _on_produto_selecionado(self, texto):
        """Evento quando um produto é selecionado no completer"""
        if texto in self.produtos_dict:
            produto = self.produtos_dict[texto]
            self.input_valor.setText(f"{produto['preco']:.2f}")
    
    def _adicionar_produto(self):
        """Adiciona um produto à lista"""
        nome = self.input_produto.text().strip()
        valor_texto = self.input_valor.text().strip()
        cor = self.combo_cor.currentText()
        
        # Validações
        if not nome:
            QMessageBox.warning(self, "Aviso", "Digite o nome do produto!")
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
        
        # Buscar código no catálogo
        codigo = ''
        if nome in self.produtos_dict:
            produto_cat = self.produtos_dict[nome]
            codigo = produto_cat.get('codigo', '')
            # Usar preço do catálogo se disponível
            if produto_cat.get('preco', 0) > 0:
                valor = produto_cat['preco']
        
        # Adicionar à lista
        produto = {
            'nome': nome,
            'codigo': codigo,
            'valor': valor,
            'cor': cor
        }
        self.produtos_list.append(produto)
        
        # Atualizar tabela
        self._atualizar_tabela_produtos()
        
        # Limpar campos
        self.input_produto.clear()
        self.input_valor.clear()
        self.combo_cor.setCurrentIndex(0)
        
        # Focar no campo produto
        self.input_produto.setFocus()
    
    def _atualizar_tabela_produtos(self):
        """Atualiza a tabela de produtos"""
        self.table_produtos.setRowCount(len(self.produtos_list))
        total = 0
        
        for row, produto in enumerate(self.produtos_list):
            # Nome
            self.table_produtos.setItem(row, 0, QTableWidgetItem(produto['nome']))
            
            # Código
            codigo = produto.get('codigo', '')
            self.table_produtos.setItem(row, 1, QTableWidgetItem(codigo if codigo else '-'))
            
            # Valor
            valor = produto['valor']
            self.table_produtos.setItem(row, 2, QTableWidgetItem(f"R$ {valor:.2f}"))
            total += valor
            
            # Cor
            cor = produto.get('cor', '')
            self.table_produtos.setItem(row, 3, QTableWidgetItem(cor if cor else '-'))
            
            # Ações
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            
            btn_remover = QPushButton("Remover")
            btn_remover.setObjectName("btnRemover")
            btn_remover.clicked.connect(lambda checked, idx=row: self._remover_produto(idx))
            btn_layout.addWidget(btn_remover)
            
            self.table_produtos.setCellWidget(row, 4, btn_widget)
            
            # Altura da linha
            self.table_produtos.setRowHeight(row, 50)
        
        # Recalcular totais
        self._calcular_total()
    
    def _remover_produto(self, index):
        """Remove um produto da lista"""
        if 0 <= index < len(self.produtos_list):
            self.produtos_list.pop(index)
            self._atualizar_tabela_produtos()
    
    def _salvar_pedido(self):
        """Salva o pedido no banco de dados"""
        # Validações
        if not self.input_cliente.text().strip():
            QMessageBox.warning(self, "Aviso", "Digite o nome do cliente!")
            return
        
        if not self.produtos_list:
            QMessageBox.warning(self, "Aviso", "Adicione pelo menos um produto!")
            return
        
        try:
            # Dados do cliente
            cliente_data = {
                'nome': self.input_cliente.text().strip(),
                'cnpj': self.input_cnpj.text().strip(),
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
            
            # Dados do pedido
            numero_os = Contador().get_proximo_numero()
            pedido_data = {
                'numero_os': numero_os,
                'cliente_id': cliente_id,
                'cliente_nome': cliente_data['nome'],
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
            
            # Salvar pedido
            pedido_id = db_manager.salvar_pedido(pedido_data)
            
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
                font-size: 14px;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #3a3a3a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #ffffff;
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
                padding: 8px 12px;
                font-size: 13px;
                background-color: #3a3a3a;
                color: #ffffff;
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
                background-color: #0d7377;
                color: #ffffff;
                padding: 8px 16px;
                font-size: 12px;
                min-height: 15px;
                margin-left: 10px;
            }
            
            #btnFullscreen:hover {
                background-color: #0f8a8f;
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
                min-height: 36px;
                font-size: 14px;
                color: #ffffff;
                background-color: #3a3a3a;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 8px 12px;
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


def abrir_novo_pedido(parent=None):
    """Função para abrir o modal de novo pedido"""
    modal = NovoPedidosModal(parent)
    return modal.exec()