"""
Modal de Pedidos Simplificado
Design moderno em tons de cinza, sem camadas desnecessárias
"""
import json

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QWidget, QMessageBox, QCompleter, QFrame, QFormLayout,
                            QScrollArea, QAbstractScrollArea)
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
                    # 6=email, 7=rua, 8=numero, 9=bairro, 10=cidade, 11=estado, 12=referencia
                    cpf = row[2] or ''
                    cnpj = row[3] or ''
                    telefone = row[5] or ''
                    
                    # Construir endereço completo
                    endereco_partes = []
                    if row[7]:  # rua
                        endereco_partes.append(row[7])
                    if row[8]:  # numero
                        endereco_partes.append(row[8])
                    if row[9]:  # bairro
                        endereco_partes.append(row[9])
                    if row[10]:  # cidade
                        endereco_partes.append(row[10])
                    if row[11]:  # estado
                        endereco_partes.append(row[11])
                    
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
        if self.clientes_dict and hasattr(self, 'input_cliente'):
            nomes_clientes = list(self.clientes_dict.keys())
            completer = QCompleter(nomes_clientes)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.input_cliente.setCompleter(completer)
            
            # Conectar seleção do completer
            completer.activated.connect(self._on_cliente_selecionado_completer)
    
    def _on_cliente_selecionado_completer(self, nome_cliente):
        """Preenche automaticamente os dados quando um cliente é selecionado do autocomplete"""
        if nome_cliente in self.clientes_dict:
            cliente_data = self.clientes_dict[nome_cliente]
            
            # Preencher os campos automaticamente
            if hasattr(self, 'input_cnpj'):
                # Priorizar CPF se existir, senão CNPJ
                cpf = cliente_data.get('cpf', '').strip()
                cnpj = cliente_data.get('cnpj', '').strip()
                cpf_cnpj_valor = cpf if cpf else cnpj
                self.input_cnpj.setText(cpf_cnpj_valor)
            
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
        """Cria a seção de dados do cliente"""
        group = QGroupBox("Cliente")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(20)  # Mais espaço entre elementos
        group_layout.setContentsMargins(30, 30, 30, 30)  # Mais padding interno
        
        # Linha 1: Nome e CNPJ
        row1 = QHBoxLayout()
        row1.setSpacing(15)  # Espaçamento reduzido entre campos
        
        # Nome
        nome_layout = QVBoxLayout()
        nome_layout.addWidget(QLabel("Nome:"))
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Digite o nome do cliente...")
        self.input_cliente.setMinimumHeight(50)
        self.input_cliente.setFixedHeight(55)
        nome_layout.addWidget(self.input_cliente)
        row1.addLayout(nome_layout, 2)
        
        # CPF/CNPJ
        cnpj_layout = QVBoxLayout()
        cnpj_layout.addWidget(QLabel("CPF/CNPJ:"))
        self.input_cnpj = QLineEdit()
        self.input_cnpj.setPlaceholderText("CPF: 000.000.000-00 ou CNPJ: 00.000.000/0000-00")
        self.input_cnpj.setMinimumHeight(50)
        self.input_cnpj.setFixedHeight(55)
        cnpj_layout.addWidget(self.input_cnpj)
        row1.addLayout(cnpj_layout, 1)
        
        group_layout.addLayout(row1)
        
        # Linha 2: Telefone e Endereço
        row2 = QHBoxLayout()
        row2.setSpacing(15)  # Espaçamento reduzido entre campos
        
        # Telefone
        tel_layout = QVBoxLayout()
        tel_layout.addWidget(QLabel("Telefone:"))
        self.input_telefone = QLineEdit()
        self.input_telefone.setPlaceholderText("(11) 99999-9999")
        self.input_telefone.setMinimumHeight(50)
        self.input_telefone.setFixedHeight(55)
        tel_layout.addWidget(self.input_telefone)
        row2.addLayout(tel_layout, 1)
        
        # Endereço
        end_layout = QVBoxLayout()
        end_layout.addWidget(QLabel("Endereço:"))
        self.input_endereco = QLineEdit()
        self.input_endereco.setPlaceholderText("Endereço completo...")
        self.input_endereco.setMinimumHeight(50)
        self.input_endereco.setFixedHeight(55)
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
        group_layout.setSpacing(12)  # Espaçamento reduzido entre elementos
        group_layout.setContentsMargins(15, 15, 15, 15)  # Padding interno reduzido
        
        # Formulário de adição
        form_layout = QHBoxLayout()
        form_layout.setSpacing(15)  # Espaçamento reduzido entre campos
        
        # Produto
        produto_layout = QVBoxLayout()
        produto_layout.addWidget(QLabel("Produto:"))
        self.input_produto = QLineEdit()
        self.input_produto.setPlaceholderText("Digite o nome do produto...")
        self.input_produto.setMinimumHeight(50)
        self.input_produto.setFixedHeight(55)
        produto_layout.addWidget(self.input_produto)
        form_layout.addLayout(produto_layout, 2)
        
        # Valor
        valor_layout = QVBoxLayout()
        valor_layout.addWidget(QLabel("Valor (R$):"))
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("0,00")
        self.input_valor.setMinimumHeight(50)
        self.input_valor.setFixedHeight(55)
        valor_layout.addWidget(self.input_valor)
        form_layout.addLayout(valor_layout, 1)
        
        # Cor
        cor_layout = QVBoxLayout()
        cor_layout.addWidget(QLabel("Cor:"))
        self.combo_cor = QComboBox()
        self.combo_cor.addItems(['', 'Branco', 'Preto', 'Azul', 'Verde', 'Vermelho', 'Amarelo', 'Personalizado'])
        self.combo_cor.setMinimumHeight(50)
        self.combo_cor.setFixedHeight(55)
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
        self.table_produtos.setColumnWidth(4, 120)  # Ações - ajustado para o botão
        
        # Altura das linhas
        self.table_produtos.verticalHeader().setDefaultSectionSize(50)
        self.table_produtos.verticalHeader().setVisible(False)
        
        # Definir altura inicial para a tabela
        self.table_produtos.setFixedHeight(200)  # Altura inicial quando vazia
        
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
                border: 2px solid #cccccc;
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
                color: #cccccc;
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
            color: #cccccc; 
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
        self.entrada_input.setMinimumHeight(50)
        self.entrada_input.setFixedHeight(55)
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
        self.frete_input.setMinimumHeight(50)
        self.frete_input.setFixedHeight(55)
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
        self.desconto_input.setMinimumHeight(50)
        self.desconto_input.setFixedHeight(55)
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
            color: #cccccc; 
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
        self.metodo_pagamento.setMinimumHeight(50)
        self.metodo_pagamento.setFixedHeight(55)
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
        self.prazo_entrega.setMinimumHeight(50)
        self.prazo_entrega.setFixedHeight(55)
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
        self.status_pedido.setMinimumHeight(50)
        self.status_pedido.setFixedHeight(55)
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
            color: #cccccc; 
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
            color: #cccccc; 
            font-weight: bold; 
            font-size: 18px; 
            background-color: #1a1a1a;
            border: 2px solid #cccccc;
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
            color: #ffffff; 
            font-weight: bold; 
            font-size: 18px; 
            background-color: #1a1a1a;
            border: 2px solid #ffffff;
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
        
        # Buscar por nome exato primeiro
        if texto in self.produtos_dict:
            produto = self.produtos_dict[texto]
            preco = produto.get('preco', 0.0)
            self.input_valor.setText(f"{preco:.2f}")
            return
        
        # Buscar por nome lowercase
        texto_lower = texto.lower()
        if texto_lower in self.produtos_dict:
            produto = self.produtos_dict[texto_lower]
            preco = produto.get('preco', 0.0)
            self.input_valor.setText(f"{preco:.2f}")
            return
            
        print(f"DEBUG: Produto não encontrado no dicionário")
    
    def _on_produto_selecionado(self, texto):
        """Evento quando um produto é selecionado no completer"""
        
        # Buscar por nome exato primeiro
        if texto in self.produtos_dict:
            produto = self.produtos_dict[texto]
            preco = produto.get('preco', 0.0)
            self.input_valor.setText(f"{preco:.2f}")
            return
        
        # Buscar por nome lowercase
        texto_lower = texto.lower()
        if texto_lower in self.produtos_dict:
            produto = self.produtos_dict[texto_lower]
            preco = produto.get('preco', 0.0)
            self.input_valor.setText(f"{preco:.2f}")
            return
            
        print(f"DEBUG: Produto selecionado não encontrado no dicionário")
    
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
            # Nome (pode ser 'nome' ou 'descricao' dependendo da origem)
            nome = produto.get('nome', produto.get('descricao', ''))
            self.table_produtos.setItem(row, 0, QTableWidgetItem(nome))
            
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
            btn_layout.setContentsMargins(2, 2, 2, 2)
            btn_layout.setSpacing(2)
            
            btn_remover = QPushButton("Remover")
            btn_remover.setObjectName("btnRemover")
            btn_remover.setMaximumWidth(100)  # Largura máxima para não cortar
            btn_remover.setMinimumHeight(30)  # Altura mínima
            btn_remover.clicked.connect(lambda checked, idx=row: self._remover_produto(idx))
            btn_layout.addWidget(btn_remover)
            btn_layout.addStretch()  # Espaço extra para centralizar
            
            self.table_produtos.setCellWidget(row, 4, btn_widget)
            
            # Altura da linha
            self.table_produtos.setRowHeight(row, 50)
        
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
        
        if num_produtos == 0:
            # Altura mínima quando vazia (mostra pelo menos 3 linhas vazias)
            altura_ideal = 200
        else:
            # Calcular altura com base no conteúdo
            altura_header = 40  # Altura do header
            altura_linha = 50   # Altura de cada linha
            padding = 20        # Padding interno
            
            altura_ideal = altura_header + (num_produtos * altura_linha) + padding
            
            # Limitar entre 200 e 400 pixels
            altura_ideal = max(200, min(400, altura_ideal))
        
        self.table_produtos.setFixedHeight(altura_ideal)
    
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
                    cor = produto.get('cor', '')
                    if cor and cor != '':
                        detalhes_produtos.append(f"• {nome}  —  Cor: {cor} - R$ {valor:.2f}")
                    else:
                        detalhes_produtos.append(f"• {nome} - R$ {valor:.2f}")
                
                detalhes_texto = '\n'.join(detalhes_produtos)
                
                print(f"DEBUG: Detalhes gerados: {detalhes_texto}")
                
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
            print(f"DEBUG: is_editing={self.is_editing}, pedido_id_editando={self.pedido_id_editando}")
            
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
                print(f"DEBUG: Definindo pedido_id_editando = {self.pedido_id_editando}")
            if 'numero_os' in pedido_data:
                self.numero_os_original = pedido_data['numero_os']
                print(f"DEBUG: Definindo numero_os_original = {self.numero_os_original}")
                
                # Atualizar o título se já foi criado
                if self.titulo_label:
                    self.titulo_label.setText(f"Ordem de Serviço Nº {self.numero_os_original:05d}")
            
            print(f"DEBUG: is_editing={self.is_editing}, pedido_id_editando={self.pedido_id_editando}")
            
            # Preencher dados do cliente - mapeando os campos do banco
            # Mapear nome_cliente para cliente
            if 'nome_cliente' in pedido_data:
                self.input_cliente.setText(pedido_data['nome_cliente'])
            elif 'cliente' in pedido_data:
                self.input_cliente.setText(pedido_data['cliente'])
                
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
                
            # Mapear cpf_cliente para cnpj
            if 'cpf_cliente' in pedido_data:
                self.input_cnpj.setText(pedido_data['cpf_cliente'])
            elif 'cnpj' in pedido_data:
                self.input_cnpj.setText(pedido_data['cnpj'])
                
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
                self.input_cliente.setText(dados['nome_cliente'])
            if 'cpf_cliente' in dados:
                self.input_cnpj.setText(dados['cpf_cliente'])
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