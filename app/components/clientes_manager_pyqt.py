"""
Módulo de clientes em PyQt6 - Versão Completa
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDialog, QFormLayout, QGroupBox, QScrollArea,
                             QFrame, QSplitter, QApplication, QMenu)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from database import db_manager
from app.ui.theme import apply_app_theme
from app.utils.formatters import formatar_cpf


class ClienteDetailDialog(QDialog):
    """Mostra os dados do cliente no topo, lista de pedidos e um formulário para adicionar ordens."""

    def __init__(self, parent, cliente):
        super().__init__(parent)
        self.setWindowTitle(f"Detalhes do Cliente: {cliente.get('nome', '')}")
        self.cliente = cliente
        self.resize(900, 600)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        # Top: client info (cartão)
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame { background: #23272e; border-radius: 12px; padding: 18px; }
            QLabel { color: #e6e6e6; font-size: 15px; }
        """)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(32)
        left = QVBoxLayout()
        left.addWidget(QLabel(f"<b>Nome:</b> {cliente.get('nome', '')}"))
        left.addWidget(QLabel(f"<b>CPF:</b> {formatar_cpf(cliente.get('cpf', ''))}"))
        left.addWidget(QLabel(f"<b>Telefone:</b> {cliente.get('telefone', '')}"))

        right = QVBoxLayout()
        endereco = f"{cliente.get('rua','')} {cliente.get('numero','')} - {cliente.get('bairro','')} - {cliente.get('cidade','')} / {cliente.get('estado','')}"
        right.addWidget(QLabel(f"<b>Endereço:</b> {endereco}"))
        right.addWidget(QLabel(f"<b>Email:</b> {cliente.get('email', '')}"))

        info_layout.addLayout(left)
        info_layout.addLayout(right)
        main_layout.addWidget(info_frame)

        # Middle: orders table
        table_label = QLabel("Pedidos deste cliente:")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #b0e0ff; margin-bottom: 6px;")
        main_layout.addWidget(table_label)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels(["ID","Nº OS","Produto","Valor","Prazo","Status"])
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.orders_table.setStyleSheet("""
            QTableWidget { background: #1f232b; color: #e6e6e6; font-size: 14px; border-radius: 8px; }
            QHeaderView::section { background: #23272e; color: #b0e0ff; font-weight: bold; font-size: 15px; border: none; }
            QTableWidget::item:selected { background: #2d8cff; color: #fff; }
        """)
        self.orders_table.verticalHeader().setVisible(False)
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setShowGrid(True)
        self.orders_table.setMinimumHeight(220)
        self.orders_table.cellClicked.connect(self._on_order_table_click)
        self.orders_table.cellDoubleClicked.connect(self._on_order_table_double_click)
        main_layout.addWidget(self.orders_table)

        # Rodapé: botões de ação
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(18)
        self.btn_add = QPushButton("Adicionar Pedido")
        self.btn_add.setMinimumWidth(180)
        self.btn_add.setStyleSheet("font-size: 15px; padding: 10px 24px; background: #2d8cff; color: #fff; border-radius: 8px;")
        self.btn_edit = QPushButton("Editar Pedido")
        self.btn_edit.setMinimumWidth(180)
        self.btn_edit.setStyleSheet("font-size: 15px; padding: 10px 24px; background: #23272e; color: #b0e0ff; border-radius: 8px;")
        self.btn_edit.setEnabled(False)
        self.btn_close = QPushButton("Fechar")
        self.btn_close.setMinimumWidth(120)
        self.btn_close.setStyleSheet("font-size: 15px; padding: 10px 24px; background: #393939; color: #fff; border-radius: 8px;")
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_close)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        self.btn_add.setToolTip("Adicionar um novo pedido para este cliente")
        self.btn_edit.setToolTip("Editar o pedido selecionado")
        self.btn_close.setToolTip("Fechar esta janela")

        self.btn_add.clicked.connect(self.abrir_ordem_completa)
        self.btn_edit.clicked.connect(self.editar_pedido_selecionado)
        self.btn_close.clicked.connect(self.accept)

        self.orders_table.itemSelectionChanged.connect(self._on_table_selection_changed)

        app = QApplication.instance()
        if app:
            try:
                apply_app_theme(app)
            except Exception:
                pass

        self.carregar_pedidos()

    def _on_table_selection_changed(self):
        selected = self.orders_table.selectedItems()
        self.btn_edit.setEnabled(bool(selected))

    def editar_pedido_selecionado(self):
        selected = self.orders_table.selectedItems()
        if not selected:
            QMessageBox.information(self, "Selecione um pedido", "Selecione um pedido na tabela para editar.")
            return
        row = self.orders_table.currentRow()
        pedido_id_item = self.orders_table.item(row, 0)
        if not pedido_id_item:
            QMessageBox.warning(self, "Erro", "Não foi possível identificar o pedido selecionado.")
            return
        try:
            pedido_id = int(pedido_id_item.text())
            from app.components.pedidos.pedidos_modal import PedidosModal
            pm = PedidosModal(self)
            pm.abrir_modal_edicao(pedido_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir pedido: {e}")

    def carregar_pedidos(self):
        import json
        nome = self.cliente.get('nome', '')
        cpf = self.cliente.get('cpf', '')
        # Busca por CPF normalizado (apenas dígitos)
        cpf_digits = ''.join(ch for ch in str(cpf) if ch.isdigit())
        # Choose query
        if cpf_digits:
            rows = db_manager.buscar_pedidos_por_cpf(cpf_digits)
        else:
            rows = db_manager.buscar_pedidos_por_cliente(nome)

        # Debug: report what was requested and how many rows returned
        try:
            print(f"carregar_pedidos: buscando nome='{nome}' cpf_digits='{cpf_digits}' -> {len(rows)} rows fetched")
        except Exception:
            print("carregar_pedidos: fetched rows (unable to compute length)")

        self.orders_table.setRowCount(0)
        for idx, r in enumerate(rows):
            # Tenta mapear campos: id, numero_os, detalhes_produto, valor_produto, prazo, status (de dados_json)
            try:
                pedido_id = r[0]
                numero_os = r[1] if len(r) > 1 else ''
                detalhes = r[6] if len(r) > 6 else ''
                valor = r[7] if len(r) > 7 else ''
                prazo = r[11] if len(r) > 11 else ''
                status = ''
                # Tenta pegar status do último campo (dados_json)
                if len(r) > 12:
                    dados_json = r[-1]
                    if dados_json:
                        try:
                            parsed = json.loads(dados_json)
                            status = parsed.get('status', '')
                        except Exception:
                            status = ''
            except Exception:
                # Fallback conservative mapping
                try:
                    pedido_id = r[0]
                except Exception:
                    pedido_id = ''
                numero_os = r[1] if len(r) > 1 else ''
                detalhes = ''
                valor = ''
                prazo = ''
                status = ''

            # Print a concise row summary for debugging
            try:
                print(f"  row[{idx}] id={pedido_id} numero_os={numero_os} detalhes='{str(detalhes)[:40]}' valor={valor} prazo={prazo} status={status}")
            except Exception:
                pass

            row = self.orders_table.rowCount()
            self.orders_table.insertRow(row)

            # Create items and ensure visibility and non-editable flags
            it_id = QTableWidgetItem(str(pedido_id))
            it_id.setFlags(it_id.flags() & ~Qt.ItemFlag.ItemIsEditable)
            it_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_id.setForeground(QColor('#e6e6e6'))

            it_num = QTableWidgetItem(str(numero_os))
            it_num.setFlags(it_num.flags() & ~Qt.ItemFlag.ItemIsEditable)
            it_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_num.setForeground(QColor('#e6e6e6'))

            it_det = QTableWidgetItem(str(detalhes))
            it_det.setFlags(it_det.flags() & ~Qt.ItemFlag.ItemIsEditable)
            it_det.setForeground(QColor('#e6e6e6'))

            it_val = QTableWidgetItem(str(valor))
            it_val.setFlags(it_val.flags() & ~Qt.ItemFlag.ItemIsEditable)
            it_val.setForeground(QColor('#e6e6e6'))

            it_prazo = QTableWidgetItem(str(prazo))
            it_prazo.setFlags(it_prazo.flags() & ~Qt.ItemFlag.ItemIsEditable)
            it_prazo.setForeground(QColor('#e6e6e6'))

            it_status = QTableWidgetItem(str(status))
            it_status.setFlags(it_status.flags() & ~Qt.ItemFlag.ItemIsEditable)
            it_status.setForeground(QColor('#e6e6e6'))

            self.orders_table.setItem(row, 0, it_id)
            self.orders_table.setItem(row, 1, it_num)
            self.orders_table.setItem(row, 2, it_det)
            self.orders_table.setItem(row, 3, it_val)
            self.orders_table.setItem(row, 4, it_prazo)
            self.orders_table.setItem(row, 5, it_status)

    def _on_order_table_double_click(self, row, column):
        """Open full PedidosModal for the clicked order unless the status column was double-clicked."""
        try:
            # status column index = 5
            pedido_item = self.orders_table.item(row, 0)
            if not pedido_item:
                return
            pedido_id = int(pedido_item.text())
            if column == 5:
                # If status column, open the status menu (double-click to change status)
                try:
                    from app.components.pedidos.status_editor import show_status_menu
                    show_status_menu(self, pedido_id)
                    return
                except Exception:
                    # fallback to opening full modal if status menu not available
                    pass
            # open full modal edit for other columns (or fallback)
            from app.components.pedidos.pedidos_modal import PedidosModal
            pm = PedidosModal(self)
            pm.abrir_modal_edicao(pedido_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir pedido: {e}")

    def _on_order_table_click(self, row, column):
        """Handle single click on order table cells (used to open status menu)."""
        try:
            if column != 5:
                return
            # get pedido id
            item = self.orders_table.item(row, 0)
            if not item:
                return
            pedido_id = int(item.text())
            # delegate to standalone helper to avoid position/indentation issues
            from app.components.pedidos.status_editor import show_status_menu
            show_status_menu(self, pedido_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir menu de status: {e}")

    def salvar_ordem(self):
        # Constrói o dicionário esperado por OrderCRUD.criar_ordem via db_manager.salvar_ordem
        dados = {
            'numero_os': self.input_numero.text() or None,
            'nome_cliente': self.cliente.get('nome', ''),
            'cpf_cliente': self.cliente.get('cpf', ''),
            'telefone_cliente': self.cliente.get('telefone', ''),
            'detalhes_produto': self.input_produto.text(),
            'valor_produto': self._try_parse_float(self.input_valor.text()),
            'valor_entrada': 0,
            'frete': 0,
            'forma_pagamento': self.input_forma.text(),
            'prazo': self.input_prazo.text(),
        }

        ok = db_manager.salvar_ordem(dados)
        if ok:
            QMessageBox.information(self, "Sucesso", "Ordem salva com sucesso")
            # limpar campos
            self.input_numero.clear()
            self.input_produto.clear()
            self.input_valor.clear()
            self.input_prazo.clear()
            self.input_forma.clear()
            self.carregar_pedidos()
            # Também solicitar refresh da aba Pedidos (se disponível na janela principal)
            try:
                main_win = self.window()
                if main_win and hasattr(main_win, 'pedidos_manager'):
                    try:
                        main_win.pedidos_manager.carregar_dados(force_refresh=True)
                    except Exception:
                        # fallback: procurar top-level widgets que tenham pedidos_manager
                        from PyQt6.QtWidgets import QApplication
                        for w in QApplication.topLevelWidgets():
                            if hasattr(w, 'pedidos_manager'):
                                try:
                                    w.pedidos_manager.carregar_dados(force_refresh=True)
                                    break
                                except Exception:
                                    pass
            except Exception:
                pass
        else:
            QMessageBox.critical(self, "Erro", "Falha ao salvar ordem")

    def _try_parse_float(self, v):
        try:
            return float(v.replace(',', '.'))
        except Exception:
            return 0

    def abrir_ordem_completa(self):
        """Abre o modal de novo pedido já preenchendo e travando os dados do cliente."""
        try:
            from app.components.pedidos.pedidos_modal import PedidosModal
            pedidos_modal = PedidosModal(self)
            cli = {
                'nome': self.cliente.get('nome',''),
                'cpf': self.cliente.get('cpf',''),
                'telefone': self.cliente.get('telefone',''),
                'email': self.cliente.get('email',''),
                'rua': self.cliente.get('rua',''),
                'numero': self.cliente.get('numero',''),
                'cidade': self.cliente.get('cidade','')
            }
            # Preenche o modelo com os dados do cliente
            try:
                pedidos_modal.model.preencher({
                    'nome_cliente': cli.get('nome',''),
                    'cpf_cliente': cli.get('cpf',''),
                    'telefone_cliente': cli.get('telefone',''),
                    'endereco_cliente': f"{cli.get('rua','')} {cli.get('numero','')}"
                })
                try:
                    pedidos_modal._preencher_dados_cliente(cli)
                except Exception:
                    pass
            except Exception:
                pass
            try:
                pedidos_modal.setWindowState(pedidos_modal.windowState() | Qt.WindowState.WindowMaximized)
            except Exception:
                pass
            # Chama o modal com cliente_fixo=True, passando rótulo com CPF e cidade para exibição no cabeçalho
            from app.utils.formatters import formatar_cpf
            cpf_fmt = formatar_cpf(cli.get('cpf',''))
            cidade = cli.get('cidade','')
            nome_label = cli.get('nome','')
            extra = []
            if cpf_fmt:
                extra.append(f"CPF: {cpf_fmt}")
            if cidade:
                extra.append(cidade)
            if extra:
                nome_label = f"{nome_label} — { ' | '.join(extra) }"
            pedidos_modal._criar_modal_completo(None, cliente_fixo=True, nome_cliente_label=nome_label)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir modal completo: {e}")


class ClientesManager(QWidget):
    """Gerenciamento de clientes em PyQt6"""
    
    def __init__(self, parent):
        super().__init__()  # Não passar parent aqui
        self.parent = parent
        self._search_timer = None
        self._setup_interface()
    # Clientes will use the Produtos visual style applied in _aplicar_estilo
        self.carregar_dados()
    
    def _setup_interface(self):
        """Configura a interface de clientes"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header (match Produtos)
        header = QLabel('Clientes')
        header.setObjectName('header')
        main_layout.addWidget(header)

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

        # Botões de ação (visually same as Produtos)
        self.btn_novo = QPushButton("➕ Novo")
        self.btn_novo.setMinimumWidth(100)
        self.btn_novo.setMinimumHeight(36)
        self.btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_novo.clicked.connect(self.novo_cliente)
        top_layout.addWidget(self.btn_novo)

        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.setMinimumWidth(100)
        self.btn_editar.setMinimumHeight(36)
        self.btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_editar.clicked.connect(self.editar_cliente)
        top_layout.addWidget(self.btn_editar)

        self.btn_excluir = QPushButton("🗑️ Excluir")
        self.btn_excluir.setMinimumWidth(100)
        self.btn_excluir.setMinimumHeight(36)
        self.btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_excluir.clicked.connect(self.excluir_cliente)
        top_layout.addWidget(self.btn_excluir)

        self.btn_recarregar = QPushButton("🔄 Recarregar")
        self.btn_recarregar.setMinimumWidth(100)
        self.btn_recarregar.setMinimumHeight(36)
        self.btn_recarregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recarregar.clicked.connect(self.carregar_dados)
        top_layout.addWidget(self.btn_recarregar)

        # Spacer before search so buttons stay left
        top_layout.addStretch()

        # Search entry (Produtos-like: large input on the right)
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Nome, CPF ou telefone...")
        self.search_entry.textChanged.connect(self._on_search)
        # Match Produtos input style
        self.search_entry.setStyleSheet('''
            QLineEdit { background-color: #1f1f1f; color: #e6e6e6; border: 1px solid #393939; border-radius: 6px; padding: 8px 12px; font-size: 14px; }
            QLineEdit:focus { border: 1px solid #5a5a5a; }
        ''')
        top_layout.addWidget(self.search_entry, 1)

        self.btn_pesquisar = QPushButton("🔍")
        self.btn_pesquisar.setMaximumWidth(40)
        self.btn_pesquisar.setMinimumHeight(36)
        self.btn_pesquisar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pesquisar.clicked.connect(self.pesquisar_clientes)
        top_layout.addWidget(self.btn_pesquisar)

        self.btn_limpar = QPushButton("✖")
        self.btn_limpar.setMaximumWidth(40)
        self.btn_limpar.setMinimumHeight(36)
        self.btn_limpar.setCursor(Qt.CursorShape.PointingHandCursor)
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

        # Conectar double click para abrir diálogo de detalhes (ver pedidos)
        self.table.doubleClicked.connect(self.abrir_detalhes_cliente)

        # Configurar scroll suave
        self._setup_smooth_table_scroll()

        # Apply Produtos-like palette to table for identical appearance
        try:
            from PyQt6.QtGui import QPalette, QColor
            palette = self.table.palette()
            palette.setColor(QPalette.ColorRole.Base, QColor("#1f1f1f"))
            palette.setColor(QPalette.ColorRole.Window, QColor("#1f1f1f"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#232323"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#e6e6e6"))
            self.table.setPalette(palette)
            header = self.table.horizontalHeader()
            header.setStyleSheet("QHeaderView::section { background-color: #1f1f1f; color: #e6e6e6; font-weight: bold; font-size: 14px; }")
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        except Exception:
            pass

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
                    raw_cpf = str(cliente[2] or '')
                    dados = [
                        str(cliente[0] or ''),   # id
                        str(cliente[1] or ''),   # nome
                        formatar_cpf(raw_cpf),    # cpf (formatado para exibição)
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

    def abrir_detalhes_cliente(self):
        """Abre o diálogo com detalhes do cliente e seus pedidos"""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Info", "Selecione um cliente.")
            return

        # Extrair dados do cliente da linha
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

        dialog = ClienteDetailDialog(self, dados)
        dialog.exec()
    
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
                    cpf = str(cliente[2] or '')
                    telefone = str(cliente[3] or '').lower()

                    # Normalize search term for CPF comparison (strip non-digits)
                    termo_digits = ''.join(ch for ch in termo_pesquisa if ch.isdigit())
                    cpf_digits = ''.join(ch for ch in cpf if ch.isdigit())

                    # Pesquisar nos campos: nome, telefone ou CPF (permitir digitar sem pontos)
                    if (termo_lower in nome or 
                        termo_lower in telefone or 
                        (termo_digits and termo_digits == cpf_digits) or
                        termo_lower in cpf.lower()):
                        clientes_filtrados.append(cliente)
            
            # Configurar número de linhas
            self.table.setRowCount(len(clientes_filtrados))
            
            # Preencher dados filtrados
            for row, cliente in enumerate(clientes_filtrados):
                raw_cpf = str(cliente[2] or '')
                dados = [
                    str(cliente[0] or ''),   # id
                    str(cliente[1] or ''),   # nome
                    formatar_cpf(raw_cpf),    # cpf (formatado)
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
        # Produtos-like QSS (teal accents were added in Produtos dialog, here we keep neutral table + highlighted selection style)
        self.setStyleSheet('''
            QWidget { background-color: #23272e; color: #f8f8f2; }
            QLabel#header { color: #50fa7b; font-size: 22px; font-weight: bold; }
            QPushButton { background-color: #323232; color: #eaeaea; border-radius: 6px; padding: 8px 14px; font-weight: 600; }
            QPushButton:hover { background-color: #3a3a3a; }
            QLineEdit { background-color: #1f1f1f; color: #e6e6e6; border: 1px solid #393939; border-radius: 6px; padding: 8px 12px; font-size: 14px; }
            QLineEdit:focus { border: 1px solid #5a5a5a; }
            QTableWidget { background-color: #1f1f1f; color: #e6e6e6; border: 1px solid #393939; border-radius: 6px; font-size: 13px; gridline-color: #333333; selection-background-color: #2d2d2d; alternate-background-color: #232323; }
            QHeaderView::section { background-color: #1f1f1f; color: #e6e6e6; font-weight: bold; font-size: 14px; }
        ''')
    
    def apply_produtos_style(self):
        """Apply Produtos-like visual style (teal accents, rounded buttons, highlighted search)."""
        style = """
        QPushButton { background-color: #0d7377; color: #ffffff; border-radius: 8px; padding: 8px 14px; font-weight: 600; }
        QPushButton:hover { background-color: #0b6a6c; }
        QPushButton:pressed { background-color: #095c5d; }

        QLineEdit { background-color: #23272e; color: #f8f8f2; border: 1.5px solid #50fa7b; border-radius: 8px; padding: 8px 12px; }
        QLineEdit:focus { border: 2px solid #8be9fd; }

        QTableWidget { background-color: #23272e; color: #f8f8f2; border-radius: 10px; gridline-color: #44475a; alternate-background-color: #282a36; }
        QHeaderView::section { background-color: #000; color: #fff; font-weight: bold; font-size: 16px; }
        QTableWidget::item:selected { background-color: #50fa7b; color: #23272e; }
        QTableWidget::item { padding: 8px; }

        QLabel { color: #e6e6e6; }

        QGroupBox { background-color: #23272e; border: 1px solid #3a3a3a; border-radius: 8px; }
        QGroupBox::title { color: #e6e6e6; }
        """

        # apply to widget
        self.setStyleSheet((self.styleSheet() or "") + "\n" + style)
        # set some object names for per-widget fine tuning if needed
        try:
            self.search_entry.setObjectName('clientes_search')
        except Exception:
            pass
        try:
            for btn in (self.btn_novo, self.btn_editar, self.btn_excluir, self.btn_recarregar, self.btn_pesquisar, self.btn_limpar):
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setMinimumHeight(36)
        except Exception:
            pass


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
            QDialog { background-color: #262626; color: #e6e6e6; }
            QGroupBox { font-weight: bold; border: 1px solid #393939; border-radius: 6px; margin-top: 10px; padding-top: 12px; background-color: #1f1f1f; }
            QGroupBox::title { left: 10px; padding: 0 10px 0 10px; color: #e6e6e6; }
            QLabel { color: #e6e6e6; }
            QLineEdit { background-color: #1f1f1f; color: #e6e6e6; border: 1px solid #393939; border-radius: 6px; padding: 8px; }
            QLineEdit:focus { border: 1px solid #5a5a5a; }
            QPushButton { background-color: #323232; color: #eaeaea; border-radius: 6px; padding: 10px 14px; font-weight: 600; }
            QPushButton:hover { background-color: #3a3a3a; }
            QScrollBar:vertical { background-color: #262626; width: 12px; border-radius: 6px; }
            QScrollBar::handle:vertical { background-color: #606060; border-radius: 6px; min-height: 20px; }
        """)
        self.setStyleSheet("""
            QDialog { background-color: #262626; color: #e6e6e6; }
            QGroupBox { font-weight: bold; border: 1px solid #393939; border-radius: 6px; margin-top: 10px; padding-top: 12px; background-color: #1f1f1f; }
            QGroupBox::title { left: 10px; padding: 0 10px 0 10px; color: #e6e6e6; }
            QLabel { color: #e6e6e6; }
            QLineEdit { background-color: #1f1f1f; color: #e6e6e6; border: 1px solid #393939; border-radius: 6px; padding: 8px; }
            QLineEdit:focus { border: 1px solid #5a5a5a; }
            QPushButton { background-color: #0078d4; color: #ffffff; border-radius: 8px; padding: 10px 14px; font-weight: 600; }
            QPushButton:hover { background-color: #106ebe; }
            QScrollBar:vertical { background-color: #262626; width: 12px; border-radius: 6px; }
            QScrollBar::handle:vertical { background-color: #606060; border-radius: 6px; min-height: 20px; }
        """)
