"""
Módulo de clientes em PyQt6 - Versão Completa
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDialog, QFormLayout, QGroupBox, QScrollArea,
                             QFrame, QSplitter)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from database import db_manager


class ClientesManager(QWidget):
    """Gerenciamento de clientes em PyQt6"""
    
    def __init__(self, parent):
        super().__init__()  # Não passar parent aqui
        self.parent = parent
        self._search_timer = None
        self._setup_interface()
        self.carregar_dados()
    
    def _setup_interface(self):
        """Configura a interface de clientes"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Barra superior com botões e pesquisa
        self._criar_barra_superior(main_layout)
        
        # Tabela de clientes
        self._criar_tabela(main_layout)
        
        # Aplicar estilo
        self._aplicar_estilo()
    
    def _criar_barra_superior(self, layout):
        """Cria barra superior com botões e pesquisa"""
        top_frame = QFrame()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(5, 5, 5, 5)
        
        # Botões de ação
        self.btn_novo = QPushButton("➕ Novo")
        self.btn_novo.setMinimumWidth(100)
        self.btn_novo.clicked.connect(self.novo_cliente)
        top_layout.addWidget(self.btn_novo)
        
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.setMinimumWidth(100)
        self.btn_editar.clicked.connect(self.editar_cliente)
        top_layout.addWidget(self.btn_editar)
        
        self.btn_excluir = QPushButton("🗑️ Excluir")
        self.btn_excluir.setMinimumWidth(100)
        self.btn_excluir.clicked.connect(self.excluir_cliente)
        top_layout.addWidget(self.btn_excluir)
        
        self.btn_recarregar = QPushButton("🔄 Recarregar")
        self.btn_recarregar.setMinimumWidth(100)
        self.btn_recarregar.clicked.connect(self.carregar_dados)
        top_layout.addWidget(self.btn_recarregar)
        
        # Spacer
        top_layout.addStretch()
        
        # Pesquisa
        search_label = QLabel("Pesquisar:")
        search_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        top_layout.addWidget(search_label)
        
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Nome, CPF ou telefone...")
        self.search_entry.setMinimumWidth(250)
        self.search_entry.textChanged.connect(self._on_search)
        top_layout.addWidget(self.search_entry)
        
        self.btn_pesquisar = QPushButton("🔍")
        self.btn_pesquisar.setMaximumWidth(40)
        self.btn_pesquisar.clicked.connect(self.pesquisar_clientes)
        top_layout.addWidget(self.btn_pesquisar)
        
        self.btn_limpar = QPushButton("✖")
        self.btn_limpar.setMaximumWidth(40)
        self.btn_limpar.clicked.connect(self.limpar_pesquisa)
        top_layout.addWidget(self.btn_limpar)
        
        layout.addWidget(top_frame)
    
    def _criar_tabela(self, layout):
        """Cria tabela de clientes com scroll suave"""
        self.table = QTableWidget()
        
        # Configurar colunas
        columns = ["ID", "Nome", "CPF", "Telefone", "Email", "Rua", "Nº", "Bairro", "Cidade", "UF", "Referência"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Configurar larguras das colunas
        header = self.table.horizontalHeader()
        column_widths = [60, 200, 120, 120, 180, 180, 60, 120, 120, 60, 150]
        
        for i, width in enumerate(column_widths):
            self.table.setColumnWidth(i, width)
        
        # Esticar última coluna
        header.setStretchLastSection(True)
        
        # Configurar seleção
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # REMOVER indicadores visuais de seleção desnecessários
        self.table.verticalHeader().setVisible(False)  # Remove números de linha à esquerda
        self.table.setShowGrid(True)  # Manter grid das células
        self.table.setAlternatingRowColors(True)  # Cores alternadas para melhor legibilidade
        
        # Conectar double click para editar
        self.table.doubleClicked.connect(self.editar_cliente)
        
        # Configurar scroll suave
        self._setup_smooth_table_scroll()
        
        layout.addWidget(self.table)
    
    def _setup_smooth_table_scroll(self):
        """Configura scroll suave para a tabela"""
        from PyQt6.QtCore import QTimer
        from PyQt6.QtGui import QWheelEvent
        
        # Configurar parâmetros de scroll
        v_scrollbar = self.table.verticalScrollBar()
        v_scrollbar.setSingleStep(3)   # Passos bem pequenos
        v_scrollbar.setPageStep(15)    # Página pequena
        
        h_scrollbar = self.table.horizontalScrollBar()
        h_scrollbar.setSingleStep(10)
        h_scrollbar.setPageStep(50)
        
        # Sistema de animação suave
        self.table_scroll_timer = QTimer()
        self.table_scroll_timer.timeout.connect(self._animate_table_scroll)
        self.table_target_scroll = 0
        self.table_current_scroll = 0
        self.table_scroll_speed = 0.2
        
        # Sobrescrever wheel event
        original_wheel = self.table.wheelEvent
        
        def smooth_table_wheel(event: QWheelEvent):
            delta = event.angleDelta().y()
            scroll_amount = -delta // 6  # Menos sensível
            
            current_value = v_scrollbar.value()
            self.table_target_scroll = current_value + scroll_amount
            
            # Limitar
            self.table_target_scroll = max(v_scrollbar.minimum(), 
                                         min(v_scrollbar.maximum(), self.table_target_scroll))
            
            # Iniciar animação
            if not self.table_scroll_timer.isActive():
                self.table_current_scroll = current_value
                self.table_scroll_timer.start(16)
            
            event.accept()
        
        self.table.wheelEvent = smooth_table_wheel
    
    def _animate_table_scroll(self):
        """Anima scroll da tabela"""
        diff = self.table_target_scroll - self.table_current_scroll
        
        if abs(diff) < 0.5:
            self.table_current_scroll = self.table_target_scroll
            self.table.verticalScrollBar().setValue(int(self.table_current_scroll))
            self.table_scroll_timer.stop()
            return
        
        self.table_current_scroll += diff * self.table_scroll_speed
        self.table.verticalScrollBar().setValue(int(self.table_current_scroll))
    
    def carregar_dados(self):
        """Carrega dados dos clientes"""
        try:
            clientes = db_manager.listar_clientes(500)
            
            # Configurar número de linhas
            self.table.setRowCount(len(clientes))
            
            # Preencher dados
            for row, cliente in enumerate(clientes):
                # cliente é uma tupla: (id, nome, cpf, telefone, email, rua, numero, bairro, cidade, estado, referencia)
                if len(cliente) >= 11:
                    dados = [
                        str(cliente[0] or ''),   # id
                        str(cliente[1] or ''),   # nome
                        str(cliente[2] or ''),   # cpf
                        str(cliente[3] or ''),   # telefone
                        str(cliente[4] or ''),   # email
                        str(cliente[5] or ''),   # rua
                        str(cliente[6] or ''),   # numero
                        str(cliente[7] or ''),   # bairro
                        str(cliente[8] or ''),   # cidade
                        str(cliente[9] or ''),   # estado
                        str(cliente[10] or '')   # referencia
                    ]
                    
                    for col, valor in enumerate(dados):
                        item = QTableWidgetItem(valor)
                        if col == 0:  # ID - centralizado
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        # Tornar item não editável
                        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.table.setItem(row, col, item)
            
            # Ajustar altura das linhas
            self.table.resizeRowsToContents()
            
            print(f"Carregados {len(clientes)} clientes na tabela")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar clientes: {e}")
            print(f"Erro detalhado: {e}")
            import traceback
            traceback.print_exc()
    
    def novo_cliente(self):
        """Abre modal para novo cliente"""
        modal = ClienteModal(self)
        if modal.exec() == QDialog.DialogCode.Accepted:
            self.carregar_dados()
    
    def editar_cliente(self):
        """Edita cliente selecionado"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Selecione um cliente para editar.")
            return
        
        # Obter dados da linha selecionada
        dados = {}
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            valor = item.text() if item else ''
            
            if col == 0:
                dados['id'] = valor
            elif col == 1:
                dados['nome'] = valor
            elif col == 2:
                dados['cpf'] = valor
            elif col == 3:
                dados['telefone'] = valor
            elif col == 4:
                dados['email'] = valor
            elif col == 5:
                dados['rua'] = valor
            elif col == 6:
                dados['numero'] = valor
            elif col == 7:
                dados['bairro'] = valor
            elif col == 8:
                dados['cidade'] = valor
            elif col == 9:
                dados['estado'] = valor
            elif col == 10:
                dados['referencia'] = valor
        
        modal = ClienteModal(self, dados)
        if modal.exec() == QDialog.DialogCode.Accepted:
            self.carregar_dados()
    
    def excluir_cliente(self):
        """Exclui cliente selecionado"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Selecione um cliente para excluir.")
            return
        
        # Obter dados do cliente
        id_item = self.table.item(row, 0)
        nome_item = self.table.item(row, 1)
        
        if not id_item or not nome_item:
            QMessageBox.warning(self, "Erro", "Dados inválidos do cliente.")
            return
        
        cliente_id = id_item.text()
        nome_cliente = nome_item.text()
        
        # Confirmar exclusão
        reply = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Excluir cliente '{nome_cliente}'?\n\nEsta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                db_manager.deletar_cliente(int(cliente_id))
                self.carregar_dados()
                QMessageBox.information(self, "Sucesso", "Cliente excluído com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir cliente: {e}")
    
    def _on_search(self):
        """Pesquisa automaticamente enquanto digita (com debounce)"""
        if self._search_timer:
            self._search_timer.stop()
        
        self._search_timer = QTimer()
        self._search_timer.timeout.connect(self.pesquisar_clientes)
        self._search_timer.setSingleShot(True)
        self._search_timer.start(500)  # 500ms de delay
    
    def pesquisar_clientes(self):
        """Pesquisa clientes por nome, CPF ou telefone"""
        termo_pesquisa = self.search_entry.text().strip()
        
        if not termo_pesquisa:
            self.carregar_dados()
            return
        
        try:
            # Buscar todos os clientes do banco
            clientes = db_manager.listar_clientes(1000)
            
            # Filtrar clientes
            clientes_filtrados = []
            termo_lower = termo_pesquisa.lower()
            
            for cliente in clientes:
                if len(cliente) >= 11:
                    nome = str(cliente[1] or '').lower()
                    cpf = str(cliente[2] or '').lower()
                    telefone = str(cliente[3] or '').lower()
                    
                    # Pesquisar nos campos
                    if (termo_lower in nome or 
                        termo_lower in cpf or 
                        termo_lower in telefone):
                        clientes_filtrados.append(cliente)
            
            # Configurar número de linhas
            self.table.setRowCount(len(clientes_filtrados))
            
            # Preencher dados filtrados
            for row, cliente in enumerate(clientes_filtrados):
                dados = [
                    str(cliente[0] or ''),   # id
                    str(cliente[1] or ''),   # nome
                    str(cliente[2] or ''),   # cpf
                    str(cliente[3] or ''),   # telefone
                    str(cliente[4] or ''),   # email
                    str(cliente[5] or ''),   # rua
                    str(cliente[6] or ''),   # numero
                    str(cliente[7] or ''),   # bairro
                    str(cliente[8] or ''),   # cidade
                    str(cliente[9] or ''),   # estado
                    str(cliente[10] or '')   # referencia
                ]
                
                for col, valor in enumerate(dados):
                    item = QTableWidgetItem(valor)
                    if col == 0:  # ID - centralizado
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(row, col, item)
            
            print(f"Encontrados {len(clientes_filtrados)} clientes")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao pesquisar: {e}")
    
    def limpar_pesquisa(self):
        """Limpa a pesquisa e recarrega todos os dados"""
        self.search_entry.clear()
        self.carregar_dados()
    
    def _aplicar_estilo(self):
        """Aplica estilo moderno ao módulo"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 5px;
            }
            
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: 500;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #0a5d61;
            }
            
            QPushButton:pressed {
                background-color: #084a4d;
            }
            
            QLineEdit {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            
            QLineEdit:focus {
                border: 2px solid #0d7377;
            }
            
            QTableWidget {
                background-color: #3a3a3a;
                alternate-background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 8px;
                gridline-color: #606060;
                selection-background-color: #0d7377;
                selection-color: #ffffff;
                outline: none;
            }
            
            QTableWidget::item {
                padding: 8px;
                border: none;
                background-color: transparent;
            }
            
            QTableWidget::item:selected {
                background-color: #0d7377;
                color: #ffffff;
            }
            
            QTableWidget::item:alternate {
                background-color: #404040;
            }
            
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #606060;
                padding: 8px;
                font-weight: bold;
            }
            
            QTableWidget QTableCornerButton::section {
                background-color: #2d2d2d;
                border: 1px solid #606060;
            }
            
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #0d7377;
                color: #ffffff;
            }
            
            QTableWidget::item:hover {
                background-color: #4a4a4a;
            }
            
            QTableWidget QTableCornerButton::section {
                background-color: #404040;
                border: none;
            }
            
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                padding: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QHeaderView::section:hover {
                background-color: #505050;
            }
            
            QScrollBar:vertical {
                background-color: #404040;
                width: 14px;
                border-radius: 7px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 7px;
                min-height: 30px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #707070;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #808080;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)


class ClienteModal(QDialog):
    """Modal para criar/editar cliente"""
    
    def __init__(self, parent, dados=None):
        super().__init__(parent)
        self.dados = dados
        self.is_edit = dados is not None
        self._setup_modal()
    
    def _setup_modal(self):
        """Configura o modal"""
        # Configurar janela
        titulo = "Editar Cliente" if self.is_edit else "Novo Cliente"
        self.setWindowTitle(titulo)
        self.setFixedSize(600, 600)
        
        # Layout principal com scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Configurar scroll suave para modal
        scroll_area.verticalScrollBar().setSingleStep(10)
        scroll_area.verticalScrollBar().setPageStep(50)
        
        # Widget de conteúdo
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Criar seções
        self.campos = {}
        self._criar_secao_pessoal(content_layout)
        self._criar_secao_endereco(content_layout)
        self._criar_secao_outros(content_layout)
        
        # Botões
        self._criar_botoes(content_layout)
        
        # Preencher dados se for edição
        if self.is_edit and self.dados:
            self._preencher_dados()
        
        # Configurar scroll
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # Aplicar estilo
        self._aplicar_estilo()
    
    def _criar_secao_pessoal(self, layout):
        """Cria seção de dados pessoais"""
        group = QGroupBox("👤 Dados Pessoais")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        form_layout = QFormLayout(group)
        
        # Campos pessoais
        self.campos['nome'] = QLineEdit()
        self.campos['nome'].setPlaceholderText("Nome completo do cliente")
        form_layout.addRow("Nome:", self.campos['nome'])
        
        self.campos['cpf'] = QLineEdit()
        self.campos['cpf'].setPlaceholderText("000.000.000-00")
        form_layout.addRow("CPF:", self.campos['cpf'])
        
        self.campos['telefone'] = QLineEdit()
        self.campos['telefone'].setPlaceholderText("(11) 99999-9999")
        form_layout.addRow("Telefone:", self.campos['telefone'])
        
        self.campos['email'] = QLineEdit()
        self.campos['email'].setPlaceholderText("cliente@email.com")
        form_layout.addRow("Email:", self.campos['email'])
        
        layout.addWidget(group)
    
    def _criar_secao_endereco(self, layout):
        """Cria seção de endereço"""
        group = QGroupBox("🏠 Endereço")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        form_layout = QFormLayout(group)
        
        # Campos de endereço
        self.campos['rua'] = QLineEdit()
        self.campos['rua'].setPlaceholderText("Nome da rua")
        form_layout.addRow("Rua:", self.campos['rua'])
        
        self.campos['numero'] = QLineEdit()
        self.campos['numero'].setPlaceholderText("123")
        form_layout.addRow("Número:", self.campos['numero'])
        
        self.campos['bairro'] = QLineEdit()
        self.campos['bairro'].setPlaceholderText("Nome do bairro")
        form_layout.addRow("Bairro:", self.campos['bairro'])
        
        self.campos['cidade'] = QLineEdit()
        self.campos['cidade'].setPlaceholderText("Nome da cidade")
        form_layout.addRow("Cidade:", self.campos['cidade'])
        
        self.campos['estado'] = QLineEdit()
        self.campos['estado'].setPlaceholderText("SP")
        form_layout.addRow("Estado:", self.campos['estado'])
        
        layout.addWidget(group)
    
    def _criar_secao_outros(self, layout):
        """Cria seção de outros dados"""
        group = QGroupBox("📝 Outros")
        group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        form_layout = QFormLayout(group)
        
        self.campos['referencia'] = QLineEdit()
        self.campos['referencia'].setPlaceholderText("Ponto de referência ou observações")
        form_layout.addRow("Referência:", self.campos['referencia'])
        
        layout.addWidget(group)
    
    def _criar_botoes(self, layout):
        """Cria botões do modal"""
        botoes_frame = QFrame()
        botoes_layout = QHBoxLayout(botoes_frame)
        botoes_layout.setContentsMargins(0, 10, 0, 0)
        
        # Botão Cancelar
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.setMinimumWidth(120)
        btn_cancelar.clicked.connect(self.reject)
        botoes_layout.addWidget(btn_cancelar)
        
        botoes_layout.addStretch()
        
        # Botão Salvar
        btn_salvar = QPushButton("💾 Salvar")
        btn_salvar.setMinimumWidth(120)
        btn_salvar.clicked.connect(self._salvar_cliente)
        botoes_layout.addWidget(btn_salvar)
        
        layout.addWidget(botoes_frame)
    
    def _preencher_dados(self):
        """Preenche campos com dados existentes"""
        if not self.dados:
            return
        
        self.campos['nome'].setText(self.dados.get('nome', ''))
        self.campos['cpf'].setText(self.dados.get('cpf', ''))
        self.campos['telefone'].setText(self.dados.get('telefone', ''))
        self.campos['email'].setText(self.dados.get('email', ''))
        self.campos['rua'].setText(self.dados.get('rua', ''))
        self.campos['numero'].setText(self.dados.get('numero', ''))
        self.campos['bairro'].setText(self.dados.get('bairro', ''))
        self.campos['cidade'].setText(self.dados.get('cidade', ''))
        self.campos['estado'].setText(self.dados.get('estado', ''))
        self.campos['referencia'].setText(self.dados.get('referencia', ''))
    
    def _salvar_cliente(self):
        """Salva o cliente no banco de dados"""
        # Validações
        nome = self.campos['nome'].text().strip()
        if not nome:
            QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
            return
        
        # Coletar dados
        dados = {
            'nome': nome,
            'cpf': self.campos['cpf'].text().strip() or None,
            'telefone': self.campos['telefone'].text().strip() or None,
            'email': self.campos['email'].text().strip() or None,
            'rua': self.campos['rua'].text().strip() or None,
            'numero': self.campos['numero'].text().strip() or None,
            'bairro': self.campos['bairro'].text().strip() or None,
            'cidade': self.campos['cidade'].text().strip() or None,
            'estado': self.campos['estado'].text().strip() or None,
            'referencia': self.campos['referencia'].text().strip() or None
        }
        
        try:
            if self.is_edit and self.dados and self.dados.get('id'):
                # Atualizar cliente existente
                db_manager.atualizar_cliente(
                    int(self.dados['id']),
                    dados['nome'],
                    dados['cpf'],
                    dados['telefone'],
                    dados['email'],
                    None,  # endereco antigo = None
                    dados['referencia'],
                    dados['rua'],
                    dados['numero'],
                    dados['bairro'],
                    dados['cidade'],
                    dados['estado']
                )
                QMessageBox.information(self, "Sucesso", "Cliente atualizado com sucesso!")
            else:
                # Criar novo cliente
                db_manager.upsert_cliente_completo(
                    dados['nome'],
                    dados['cpf'],
                    dados['telefone'],
                    dados['email'],
                    None,  # endereco antigo = None
                    dados['referencia'],
                    dados['rua'],
                    dados['numero'],
                    dados['bairro'],
                    dados['cidade'],
                    dados['estado']
                )
                QMessageBox.information(self, "Sucesso", "Cliente criado com sucesso!")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar cliente: {e}")
    
    def _aplicar_estilo(self):
        """Aplica estilo moderno ao modal"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #353535;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #ffffff;
                background-color: #353535;
            }
            
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            
            QLineEdit {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            
            QLineEdit:focus {
                border: 2px solid #0d7377;
            }
            
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: 500;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #0a5d61;
            }
            
            QPushButton:pressed {
                background-color: #084a4d;
            }
            
            QScrollBar:vertical {
                background-color: #404040;
                width: 14px;
                border-radius: 7px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 7px;
                min-height: 30px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #707070;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #808080;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
