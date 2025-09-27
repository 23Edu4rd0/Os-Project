"""
Módulo de clientes em PyQt6 - Versão Completa
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDialog, QFormLayout, QGroupBox, QScrollArea,
                             QFrame, QSplitter, QApplication, QMenu, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from database import db_manager
from app.ui.theme import apply_app_theme
from app.utils.formatters import formatar_cpf
from app.utils.cep_api import CepAPI


class ClienteDetailDialog(QDialog):
    """Mostra os dados do cliente no topo, lista de pedidos e um formulário para adicionar ordens."""

    def __init__(self, parent, cliente):
        super().__init__(parent)
        self.setWindowTitle(f"Detalhes do Cliente: {cliente.get('nome', '')}")
        self.cliente = cliente
        
        # Tamanho responsivo baseado na tela
        screen = QApplication.primaryScreen().geometry()
        # 80% da largura da tela, máximo 1200px, mínimo 800px
        width = min(max(int(screen.width() * 0.8), 800), 1200)
        # 70% da altura da tela, máximo 800px, mínimo 500px  
        height = min(max(int(screen.height() * 0.7), 500), 800)
        self.resize(width, height)

        main_layout = QVBoxLayout(self)
        # Margens menores para aproveitamento do espaço
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Top: client info (cartão compacto e responsivo)
        info_frame = QFrame()
        # Altura responsiva baseada no tamanho da tela
        min_height = min(max(int(height * 0.15), 140), 180)
        info_frame.setMinimumHeight(min_height)
        info_frame.setMaximumHeight(200)
        info_frame.setStyleSheet("""
            QFrame { 
                background: #23272e; 
                border-radius: 12px; 
                padding: 12px;
                border: 1px solid #393939;
            }
            QLabel { 
                color: #e6e6e6; 
                font-size: 12px; 
                margin: 1px 0;
                line-height: 1.3;
            }
        """)
        
        # Layout principal responsivo com três colunas
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(16, 12, 16, 12)
        info_layout.setSpacing(24)
        
        # Coluna 1: Dados pessoais (35%)
        left = QVBoxLayout()
        left.setSpacing(3)
        
        nome_label = QLabel(f"<b>Nome:</b> {self.cliente.get('nome', '')}")
        nome_label.setWordWrap(True)
        left.addWidget(nome_label)
        
        if self.cliente.get('cpf'):
            left.addWidget(QLabel(f"<b>CPF:</b> {formatar_cpf(self.cliente.get('cpf', ''))}"))
        
        if self.cliente.get('cnpj'):
            left.addWidget(QLabel(f"<b>CNPJ:</b> {self.cliente.get('cnpj', '')}"))
        
        if self.cliente.get('inscricao_estadual'):
            left.addWidget(QLabel(f"<b>I.E.:</b> {self.cliente.get('inscricao_estadual', '')}"))
        
        left.addStretch()

        # Coluna 2: Contato (30%)
        center = QVBoxLayout()
        center.setSpacing(3)
        
        if self.cliente.get('telefone'):
            center.addWidget(QLabel(f"<b>Telefone:</b> {self.cliente.get('telefone', '')}"))
        
        if self.cliente.get('email'):
            email_label = QLabel(f"<b>Email:</b> {self.cliente.get('email', '')}")
            email_label.setWordWrap(True)
            center.addWidget(email_label)
        
        # Sempre mostrar CEP
        cep_value = self.cliente.get('cep', '')
        if cep_value:
            cep_formatado = CepAPI.format_cep_display(cep_value)
        else:
            cep_formatado = "Não informado"
        center.addWidget(QLabel(f"<b>CEP:</b> {cep_formatado}"))
        
        center.addStretch()

        # Coluna 3: Endereço (35%)
        right = QVBoxLayout()
        right.setSpacing(3)
        
        # Construir endereço de forma mais compacta
        endereco_parts = []
        if self.cliente.get('rua'):
            rua_numero = self.cliente.get('rua', '')
            if self.cliente.get('numero'):
                rua_numero += f", {self.cliente.get('numero', '')}"
            endereco_parts.append(rua_numero)
        
        if self.cliente.get('bairro'):
            endereco_parts.append(self.cliente.get('bairro', ''))
        
        if self.cliente.get('cidade') or self.cliente.get('estado'):
            cidade_estado = ""
            if self.cliente.get('cidade'):
                cidade_estado = self.cliente.get('cidade', '')
            if self.cliente.get('estado'):
                if cidade_estado:
                    cidade_estado += f" - {self.cliente.get('estado', '')}"
                else:
                    cidade_estado = self.cliente.get('estado', '')
            endereco_parts.append(cidade_estado)
        
        if endereco_parts:
            endereco_text = "<br>".join(endereco_parts)
            endereco_label = QLabel(f"<b>Endereço:</b><br>{endereco_text}")
        else:
            endereco_label = QLabel("<b>Endereço:</b><br>Não informado")
        
        endereco_label.setWordWrap(True)
        endereco_label.setStyleSheet("font-size: 12px; line-height: 1.4;")
        right.addWidget(endereco_label)
        
        if self.cliente.get('referencia'):
            ref_label = QLabel(f"<b>Ref.:</b> {self.cliente.get('referencia', '')}")
            ref_label.setWordWrap(True)
            ref_label.setStyleSheet("font-size: 11px; color: #c0c0c0; margin-top: 4px;")
            right.addWidget(ref_label)
        
        right.addStretch()

        # Proporções das colunas: 35%, 30%, 35%
        info_layout.addLayout(left, 35)
        info_layout.addLayout(center, 30)
        info_layout.addLayout(right, 35)
        main_layout.addWidget(info_frame)

        # Middle: orders table
        table_label = QLabel("Pedidos deste cliente:")
        table_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #b0e0ff; margin-bottom: 6px;")
        main_layout.addWidget(table_label)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(3)
        self.orders_table.setHorizontalHeaderLabels(["OS", "Status", "Ações"])
        # Centralizar cabeçalhos
        for i in range(3):
            item = self.orders_table.horizontalHeaderItem(i)
            if item:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.orders_table.setStyleSheet("""
            QTableWidget { background: #1f232b; color: #e6e6e6; font-size: 14px; border-radius: 8px; }
            QHeaderView::section { background: #23272e; color: #b0e0ff; font-weight: bold; font-size: 15px; border: none; }
            QTableWidget::item:selected { background: #2d8cff; color: #fff; }
        """)
        self.orders_table.verticalHeader().setVisible(False)
        
        # Configurar larguras das colunas de forma responsiva
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # OS - ajusta ao conteúdo
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Status - expande
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Ações - largura fixa
        
        # Definir larguras mínimas
        self.orders_table.setColumnWidth(0, 100)  # OS mínimo
        self.orders_table.setColumnWidth(2, 220)  # Largura fixa para coluna de ações
        self.orders_table.setColumnWidth(2, 300)  # Ações mínimo
        
        self.orders_table.setAlternatingRowColors(True)
        self.orders_table.setShowGrid(True)
        self.orders_table.setMinimumHeight(350)  # Aumentado de 220 para 350
        self.orders_table.cellDoubleClicked.connect(self._on_status_double_click)
        main_layout.addWidget(self.orders_table)

        # Rodapé: botões de ação responsivos
        # Layout de botões responsivo
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 16, 0, 0)
        btn_layout.setSpacing(12)
        
        # Botão Adicionar
        self.btn_add = QPushButton("Adicionar Pedido")
        self.btn_add.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_add.setMinimumHeight(45)
        self.btn_add.setMinimumWidth(140)
        self.btn_add.setStyleSheet("""
            QPushButton {
                font-size: 14px; 
                font-weight: 600;
                padding: 12px 20px; 
                background-color: #2196F3; 
                color: white; 
                border: none;
                border-radius: 8px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        
        # Botão Editar
        self.btn_edit = QPushButton("Editar Pedido")
        self.btn_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_edit.setMinimumHeight(45)
        self.btn_edit.setMinimumWidth(140)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                font-size: 14px; 
                font-weight: 600;
                padding: 12px 20px; 
                background-color: #6c757d; 
                color: white; 
                border: none;
                border-radius: 8px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #888;
            }
        """)
        self.btn_edit.setEnabled(False)
        
        # Botão Fechar
        self.btn_close = QPushButton("Fechar")
        self.btn_close.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_close.setMinimumHeight(45)
        self.btn_close.setMinimumWidth(120)
        self.btn_close.setMaximumWidth(140)
        self.btn_close.setStyleSheet("""
            QPushButton {
                font-size: 14px; 
                font-weight: 600;
                padding: 12px 20px; 
                background-color: #f44336; 
                color: white; 
                border: none;
                border-radius: 8px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        """)
        
        # Layout responsivo dos botões
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addStretch()  # Empurra o botão Fechar para a direita
        btn_layout.addWidget(self.btn_close)
        
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
            # Obter o ID real armazenado no UserRole, não o texto da célula
            pedido_id = pedido_id_item.data(Qt.ItemDataRole.UserRole)
            if pedido_id is None:
                # Fallback: tentar extrair do texto se necessário
                texto = pedido_id_item.text()
                if texto.startswith("OS "):
                    pedido_id = int(texto.replace("OS ", ""))
                else:
                    pedido_id = int(texto)
            
            from app.components.pedidos.novo_pedidos_modal import NovoPedidosModal
            pm = NovoPedidosModal(self)
            # Conectar sinal para atualizar a interface após salvar
            pm.pedido_salvo.connect(lambda: self.carregar_pedidos())
            pm.abrir_modal_edicao(pedido_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir pedido: {e}")

    def carregar_pedidos(self):
        print(f"=== CARREGAR_PEDIDOS INICIO para cliente: {self.cliente.get('nome', 'SEM_NOME')} ===")
        nome = self.cliente.get('nome', '')
        cpf = self.cliente.get('cpf', '')
        # Busca por CPF normalizado (apenas dígitos)
        cpf_digits = ''.join(ch for ch in str(cpf) if ch.isdigit())
        print(f"Nome: '{nome}', CPF: '{cpf}', CPF digits: '{cpf_digits}'")
        
        # Choose query
        if cpf_digits:
            print("Buscando por CPF...")
            rows = db_manager.buscar_pedidos_por_cpf(cpf_digits)
        else:
            print("Buscando por nome...")
            rows = db_manager.buscar_pedidos_por_cliente(nome)

        print(f"carregar_pedidos: buscando nome='{nome}' cpf_digits='{cpf_digits}' -> {len(rows) if rows else 0} rows fetched")

        self.orders_table.setRowCount(0)
        self.orders_table.verticalHeader().setDefaultSectionSize(48)  # Altura padrão das linhas
        print(f"Processando {len(rows) if rows else 0} pedidos...")
        
        for idx, r in enumerate(rows):
            print(f"=== PROCESSANDO PEDIDO {idx} ===")
            try:
                # Parse dados básicos
                pedido_id = r[0] if r and len(r) > 0 else 0
                numero_os = r[1] if r and len(r) > 1 else 0
                
                # Tenta extrair status do JSON
                status = 'Em Andamento'  # default
                if r and len(r) > 13:
                    try:
                        import json
                        dados_json = r[13] if r[13] else '{}'
                        parsed = json.loads(dados_json)
                        status = parsed.get('status', 'Em Andamento')
                    except Exception:
                        pass
                
                print(f"  Dados: id={pedido_id}, numero_os={numero_os}, status={status}")
                
                # Adicionar linha simplificada
                row = self.orders_table.rowCount()
                self.orders_table.insertRow(row)
                
                # Coluna 1: "OS X"
                os_text = f"OS {numero_os:03d}"
                os_item = QTableWidgetItem(os_text)
                os_item.setData(Qt.ItemDataRole.UserRole, pedido_id)  # Guardar ID
                os_item.setFlags(os_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                os_item.setForeground(QColor('#e6e6e6'))
                self.orders_table.setItem(row, 0, os_item)
                
                # Coluna 2: Status (editável)
                status_item = QTableWidgetItem(status)
                status_item.setData(Qt.ItemDataRole.UserRole, pedido_id)  # Guardar ID também aqui
                status_item.setForeground(QColor('#b0e0ff'))  # Cor diferente para indicar que é editável
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.orders_table.setItem(row, 1, status_item)
                
                # Coluna 3: Container com botões "Visualizar" e "Deletar"
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)  # Sem margens
                actions_layout.setSpacing(12)  # Manter espaçamento entre botões
                actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centralizar horizontalmente
                actions_widget.setFixedHeight(36)  # Altura ainda menor
                actions_widget.setStyleSheet("background: transparent;")  # Remover qualquer background
                
                # Botão Visualizar
                btn_visualizar = QPushButton("Visualizar")
                btn_visualizar.setFixedHeight(32)  # Altura fixa para não ficar amassado
                btn_visualizar.setStyleSheet("""
                    QPushButton {
                        background-color: #2d8cff;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 14px;
                        font-weight: 600;
                        font-size: 13px;
                        min-width: 90px;
                    }
                    QPushButton:hover {
                        background-color: #1e7ae6;
                    }
                """)
                btn_visualizar.clicked.connect(lambda checked, pid=pedido_id: self._visualizar_pedido(pid))
                
                # Botão Deletar
                btn_deletar = QPushButton("Deletar")
                btn_deletar.setFixedHeight(32)  # Altura fixa para não ficar amassado
                btn_deletar.setStyleSheet("""
                    QPushButton {
                        background-color: #ff4757;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px 14px;
                        font-weight: 600;
                        font-size: 13px;
                        min-width: 90px;
                    }
                    QPushButton:hover {
                        background-color: #e74c3c;
                    }
                """)
                btn_deletar.clicked.connect(lambda checked, pid=pedido_id: self._deletar_pedido(pid))
                
                actions_layout.addWidget(btn_visualizar)
                actions_layout.addWidget(btn_deletar)
                self.orders_table.setCellWidget(row, 2, actions_widget)
                
                print(f"  Linha {idx} criada com sucesso")
                
            except Exception as e:
                print(f"=== ERRO ao processar pedido {idx}: {e} ===")
                import traceback
                traceback.print_exc()
        
        print(f"=== CARREGAR_PEDIDOS FIM: {self.orders_table.rowCount()} linhas adicionadas ===")
    

    def _on_status_double_click(self, row, column):
        """Trata duplo clique na coluna de status para editá-lo."""
        if column != 1:  # Só permite editar a coluna de status (índice 1)
            return
            
        try:
            # Obter dados do pedido
            status_item = self.orders_table.item(row, 1)
            
            if not status_item:
                return
                
            pedido_id = status_item.data(Qt.ItemDataRole.UserRole)
            
            print(f"Editando status do pedido {pedido_id}")
            
            # Usar o menu de status existente
            from app.components.pedidos.status_editor import show_status_menu
            show_status_menu(self, pedido_id)
            
            # Recarregar os pedidos para atualizar a interface
            QTimer.singleShot(100, self.carregar_pedidos)
                        
        except Exception as e:
            print(f"Erro ao editar status: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao editar status: {e}")

    def _visualizar_pedido(self, pedido_id):
        """Abre o dialog de resumo do pedido."""
        try:
            print(f"Visualizando pedido ID: {pedido_id}")
            from app.components.dialogs.pedido_resumo_dialog import PedidoResumoDialog
            dialog = PedidoResumoDialog(pedido_id, self)
            dialog.exec()
        except Exception as e:
            print(f"Erro ao visualizar pedido: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao abrir resumo do pedido: {e}")

    def _deletar_pedido(self, pedido_id):
        """Deleta um pedido após confirmação."""
        try:
            # Confirmação de exclusão
            reply = QMessageBox.question(
                self, 
                "Confirmar Exclusão", 
                f"Tem certeza que deseja deletar a OS {pedido_id}?\n\nEsta ação não pode ser desfeita.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                print(f"Deletando pedido ID: {pedido_id}")
                
                # Chama função de deletar do banco de dados
                from database.db_manager import db_manager
                sucesso = db_manager.deletar_pedido(pedido_id)
                
                if sucesso:
                    QMessageBox.information(self, "Sucesso", "Pedido deletado com sucesso!")
                    # Recarrega a tabela para atualizar a interface
                    self.carregar_pedidos()
                else:
                    QMessageBox.warning(self, "Erro", "Não foi possível deletar o pedido.")
                    
        except Exception as e:
            print(f"Erro ao deletar pedido: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao deletar pedido: {e}")
    

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
                        main_win.pedidos_manager.carregar_dados()
                    except Exception:
                        # fallback: procurar top-level widgets que tenham pedidos_manager
                        from PyQt6.QtWidgets import QApplication
                        for w in QApplication.topLevelWidgets():
                            if hasattr(w, 'pedidos_manager'):
                                try:
                                    w.pedidos_manager.carregar_dados()
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
            from app.components.pedidos.novo_pedidos_modal import NovoPedidosModal
            pedidos_modal = NovoPedidosModal(self)
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
            # Conectar o sinal para atualizar este dialog quando o pedido for salvo
            try:
                pedidos_modal.pedido_salvo.connect(lambda: self.carregar_pedidos())
            except Exception:
                pass
            # Também conectar para atualizar a aba principal de Pedidos
            try:
                main_win = self.window()
                if main_win and hasattr(main_win, 'pedidos_manager'):
                    pedidos_modal.pedido_salvo.connect(lambda: main_win.pedidos_manager.carregar_dados())
                else:
                    # fallback: procurar top-level widgets que tenham pedidos_manager
                    from PyQt6.QtWidgets import QApplication
                    for w in QApplication.topLevelWidgets():
                        if hasattr(w, 'pedidos_manager'):
                            try:
                                pedidos_modal.pedido_salvo.connect(lambda: w.pedidos_manager.carregar_dados())
                                break
                            except Exception:
                                continue
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
        self._conectar_sinais()
        self._setup_interface()
        self.carregar_dados()
    
    def _conectar_sinais(self):
        """Conecta os sinais globais para atualização em tempo real"""
        try:
            from app.signals import get_signals
            signals = get_signals()
            signals.cliente_criado.connect(self._on_cliente_atualizado)
            signals.cliente_editado.connect(self._on_cliente_atualizado)
            signals.cliente_excluido.connect(self._on_cliente_atualizado)
            signals.clientes_atualizados.connect(self._on_clientes_atualizados)
        except Exception as e:
            print(f"Erro ao conectar sinais de clientes: {e}")
    
    def _on_cliente_atualizado(self, cliente_id: int = None):
        """Atualiza a lista quando um cliente é modificado"""
        self.carregar_dados()
    
    def _on_clientes_atualizados(self):
        """Atualiza a lista quando há mudança geral nos clientes"""
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
        self.search_entry.setPlaceholderText("Nome, CPF, CNPJ, Insc. Estadual ou telefone...")
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
        columns = ["ID", "Nome", "CPF", "CNPJ", "Insc. Estadual", "Telefone", "Email", "Rua", "Nº", "Bairro", "Cidade", "UF", "Referência"]
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        
        # Configurar larguras das colunas (mais compacto)
        header = self.table.horizontalHeader()
        column_widths = [50, 160, 90, 100, 80, 100, 140, 120, 40, 90, 90, 40, 110]
        
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
                # cliente é uma tupla: (id, nome, cpf, cnpj, inscricao_estadual, telefone, email, rua, numero, bairro, cidade, estado, referencia)
                if len(cliente) >= 13:
                    raw_cpf = str(cliente[2] or '')
                    # Formatação de CNPJ
                    raw_cnpj = str(cliente[3] or '')
                    if raw_cnpj and len(raw_cnpj.strip()) > 0:
                        try:
                            from app.utils.formatters import formatar_cnpj
                            cnpj_fmt = formatar_cnpj(raw_cnpj)
                        except Exception:
                            cnpj_fmt = raw_cnpj
                    else:
                        cnpj_fmt = ''
                    
                    dados = [
                        str(cliente[0] or ''),   # id
                        str(cliente[1] or ''),   # nome
                        formatar_cpf(raw_cpf),   # cpf (formatado para exibição)
                        cnpj_fmt,                # cnpj (formatado)
                        str(cliente[4] or ''),   # inscricao_estadual
                        str(cliente[5] or ''),   # telefone
                        str(cliente[6] or ''),   # email
                        str(cliente[7] or ''),   # rua
                        str(cliente[8] or ''),   # numero
                        str(cliente[9] or ''),   # bairro
                        str(cliente[10] or ''),  # cidade
                        str(cliente[11] or ''),  # estado
                        str(cliente[12] or '')   # referencia
                    ]
                    
                    for col, valor in enumerate(dados):
                        item = QTableWidgetItem(valor)
                        # Centralizar todas as colunas
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
            # Emitir sinal de cliente criado
            from app.signals import get_signals
            signals = get_signals()
            signals.clientes_atualizados.emit()
    
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
                dados['cnpj'] = valor
            elif col == 4:
                dados['inscricao_estadual'] = valor
            elif col == 5:
                dados['telefone'] = valor
            elif col == 6:
                dados['email'] = valor
            elif col == 7:
                dados['rua'] = valor
            elif col == 8:
                dados['numero'] = valor
            elif col == 9:
                dados['bairro'] = valor
            elif col == 10:
                dados['cidade'] = valor
            elif col == 11:
                dados['estado'] = valor
            elif col == 12:
                dados['referencia'] = valor
        
        modal = ClienteModal(self, dados)
        if modal.exec() == QDialog.DialogCode.Accepted:
            # Emitir sinal de cliente editado
            from app.signals import get_signals
            signals = get_signals()
            signals.cliente_editado.emit(int(dados.get('id', 0)))

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
                dados['cnpj'] = valor
            elif col == 4:
                dados['inscricao_estadual'] = valor
            elif col == 5:
                dados['telefone'] = valor
            elif col == 6:
                dados['email'] = valor
            elif col == 7:
                dados['rua'] = valor
            elif col == 8:
                dados['numero'] = valor
            elif col == 9:
                dados['bairro'] = valor
            elif col == 10:
                dados['cidade'] = valor
            elif col == 11:
                dados['estado'] = valor
            elif col == 12:
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
                # Emitir sinal de cliente excluído
                from app.signals import get_signals
                signals = get_signals()
                signals.cliente_excluido.emit(int(cliente_id))
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
        """Pesquisa clientes por nome, CPF, CNPJ ou telefone"""
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
                if len(cliente) >= 13:
                    nome = str(cliente[1] or '').lower()
                    cpf = str(cliente[2] or '')
                    cnpj = str(cliente[3] or '')
                    inscricao_estadual = str(cliente[4] or '').lower()
                    telefone = str(cliente[5] or '').lower()

                    # Normalize search term for CPF/CNPJ comparison (strip non-digits)
                    termo_digits = ''.join(ch for ch in termo_pesquisa if ch.isdigit())
                    cpf_digits = ''.join(ch for ch in cpf if ch.isdigit())
                    cnpj_digits = ''.join(ch for ch in cnpj if ch.isdigit())

                    # Pesquisar nos campos: nome, telefone, CPF, CNPJ, Inscr. Estadual (permitir digitar sem pontos)
                    if (termo_lower in nome or 
                        termo_lower in telefone or 
                        (termo_digits and (termo_digits == cpf_digits or termo_digits == cnpj_digits)) or
                        termo_lower in cpf.lower() or
                        termo_lower in cnpj.lower() or
                        termo_lower in inscricao_estadual):
                        clientes_filtrados.append(cliente)
            
            # Configurar número de linhas
            self.table.setRowCount(len(clientes_filtrados))
            
            # Preencher dados filtrados
            for row, cliente in enumerate(clientes_filtrados):
                raw_cpf = str(cliente[2] or '')
                # Formatação de CNPJ
                raw_cnpj = str(cliente[3] or '')
                if raw_cnpj and len(raw_cnpj.strip()) > 0:
                    try:
                        from app.utils.formatters import formatar_cnpj
                        cnpj_fmt = formatar_cnpj(raw_cnpj)
                    except Exception:
                        cnpj_fmt = raw_cnpj
                else:
                    cnpj_fmt = ''
                
                dados = [
                    str(cliente[0] or ''),   # id
                    str(cliente[1] or ''),   # nome
                    formatar_cpf(raw_cpf),   # cpf (formatado para exibição)
                    cnpj_fmt,                # cnpj (formatado)
                    str(cliente[4] or ''),   # inscricao_estadual
                    str(cliente[5] or ''),   # telefone
                    str(cliente[6] or ''),   # email
                    str(cliente[7] or ''),   # rua
                    str(cliente[8] or ''),   # numero
                    str(cliente[9] or ''),   # bairro
                    str(cliente[10] or ''),  # cidade
                    str(cliente[11] or ''),  # estado
                    str(cliente[12] or '')   # referencia
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
        
        self.campos['cnpj'] = QLineEdit()
        self.campos['cnpj'].setPlaceholderText("00.000.000/0000-00")
        form_layout.addRow("CNPJ:", self.campos['cnpj'])
        
        self.campos['inscricao_estadual'] = QLineEdit()
        self.campos['inscricao_estadual'].setPlaceholderText("Inscrição Estadual")
        form_layout.addRow("Inscrição Estadual:", self.campos['inscricao_estadual'])
        
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
        
        # Campo CEP com busca automática
        cep_layout = QHBoxLayout()
        self.campos['cep'] = QLineEdit()
        self.campos['cep'].setPlaceholderText("00000-000")
        self.campos['cep'].setMaxLength(9)
        self.campos['cep'].textChanged.connect(self._on_cep_changed)
        
        self.btn_buscar_cep = QPushButton("🔍 Buscar")
        self.btn_buscar_cep.setMaximumWidth(80)
        self.btn_buscar_cep.clicked.connect(self._buscar_cep)
        
        cep_layout.addWidget(self.campos['cep'])
        cep_layout.addWidget(self.btn_buscar_cep)
        form_layout.addRow("CEP:", cep_layout)
        
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
        self.campos['cnpj'].setText(self.dados.get('cnpj', ''))
        self.campos['inscricao_estadual'].setText(self.dados.get('inscricao_estadual', ''))
        self.campos['telefone'].setText(self.dados.get('telefone', ''))
        self.campos['email'].setText(self.dados.get('email', ''))
        self.campos['cep'].setText(CepAPI.format_cep_display(self.dados.get('cep', '')))
        self.campos['rua'].setText(self.dados.get('rua', ''))
        self.campos['numero'].setText(self.dados.get('numero', ''))
        self.campos['bairro'].setText(self.dados.get('bairro', ''))
        self.campos['cidade'].setText(self.dados.get('cidade', ''))
        self.campos['estado'].setText(self.dados.get('estado', ''))
        self.campos['referencia'].setText(self.dados.get('referencia', ''))
    
    def _salvar_cliente(self):
        """Salva o cliente no banco de dados"""
        from app.validation.cliente_validator import validar_dados_cliente
        from app.components.dialogs.cliente_confirm_dialog import ClienteConfirmDialog
        
        # Coletar dados
        dados = {
            'nome': self.campos['nome'].text().strip(),
            'cpf': self.campos['cpf'].text().strip() or None,
            'cnpj': self.campos['cnpj'].text().strip() or None,
            'inscricao_estadual': self.campos['inscricao_estadual'].text().strip() or None,
            'telefone': self.campos['telefone'].text().strip() or None,
            'email': self.campos['email'].text().strip() or None,
            'cep': CepAPI.format_cep(self.campos['cep'].text().strip()) or None,
            'rua': self.campos['rua'].text().strip() or None,
            'numero': self.campos['numero'].text().strip() or None,
            'bairro': self.campos['bairro'].text().strip() or None,
            'cidade': self.campos['cidade'].text().strip() or None,
            'estado': self.campos['estado'].text().strip() or None,
            'referencia': self.campos['referencia'].text().strip() or None
        }
        
        # Validar dados
        is_valid, message = validar_dados_cliente(dados)
        if not is_valid:
            QMessageBox.warning(self, "Erro de Validação", message)
            return
        
        # Mostrar diálogo de confirmação
        confirm_dialog = ClienteConfirmDialog(dados, self)
        if confirm_dialog.exec() == QDialog.DialogCode.Accepted:
            resultado = confirm_dialog.get_resultado()
            
            if resultado == 'copiar':
                QMessageBox.information(self, "Copiado", "Dados copiados para a área de transferência!")
                return  # Não salva, apenas copia
            
            elif resultado == 'confirmar':
                # Salvar no banco de dados
                try:
                    if self.is_edit and self.dados and self.dados.get('id'):
                        # Atualizar cliente existente
                        db_manager.atualizar_cliente_completo(
                            int(self.dados['id']),
                            dados['nome'],
                            dados['cpf'],
                            dados['cnpj'],
                            dados['inscricao_estadual'],
                            dados['telefone'],
                            dados['email'],
                            dados['cep'],
                            dados['rua'],
                            dados['numero'],
                            dados['bairro'],
                            dados['cidade'],
                            dados['estado'],
                            dados['referencia']
                        )
                        QMessageBox.information(self, "Sucesso", "Cliente atualizado com sucesso!")
                    else:
                        # Criar novo cliente
                        db_manager.criar_cliente_completo(
                            dados['nome'],
                            dados['cpf'],
                            dados['cnpj'],
                            dados['inscricao_estadual'],
                            dados['telefone'],
                            dados['email'],
                            dados['cep'],
                            dados['rua'],
                            dados['numero'],
                            dados['bairro'],
                            dados['cidade'],
                            dados['estado'],
                            dados['referencia']
                        )
                        QMessageBox.information(self, "Sucesso", "Cliente criado com sucesso!")
                    
                    self.accept()  # Fecha o modal
                    
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao salvar cliente: {e}")
    
    def _on_cep_changed(self, text):
        """Formatar CEP enquanto digita"""
        # Remove caracteres não numéricos
        cep_limpo = ''.join(filter(str.isdigit, text))
        
        # Formatar CEP (XXXXX-XXX)
        if len(cep_limpo) > 5:
            cep_formatado = f"{cep_limpo[:5]}-{cep_limpo[5:8]}"
        else:
            cep_formatado = cep_limpo
        
        # Atualizar campo se diferente
        if cep_formatado != text:
            cursor_pos = self.campos['cep'].cursorPosition()
            self.campos['cep'].setText(cep_formatado)
            # Ajustar posição do cursor
            if len(cep_formatado) > len(text):
                cursor_pos += 1
            self.campos['cep'].setCursorPosition(cursor_pos)
    
    def _buscar_cep(self):
        """Busca endereço pelo CEP"""
        cep = self.campos['cep'].text().strip()
        
        if not cep:
            QMessageBox.warning(self, "CEP Vazio", "Por favor, digite um CEP.")
            return
        
        if not CepAPI.is_valid_cep(cep):
            QMessageBox.warning(self, "CEP Inválido", "Por favor, digite um CEP válido (8 dígitos).")
            return
        
        try:
            # Desabilitar botão durante busca
            self.btn_buscar_cep.setEnabled(False)
            self.btn_buscar_cep.setText("🔄 Buscando...")
            QApplication.processEvents()  # Atualizar interface
            
            # Buscar endereço
            endereco = CepAPI.buscar_endereco(cep)
            
            if endereco:
                # Preencher campos com os dados encontrados
                self.campos['rua'].setText(endereco.get('rua', ''))
                self.campos['bairro'].setText(endereco.get('bairro', ''))
                self.campos['cidade'].setText(endereco.get('cidade', ''))
                self.campos['estado'].setText(endereco.get('estado', ''))
                
                QMessageBox.information(self, "CEP Encontrado", "Endereço preenchido automaticamente!")
            else:
                QMessageBox.warning(self, "CEP Não Encontrado", "CEP não encontrado ou inválido.")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao buscar CEP: {e}")
        
        finally:
            # Reabilitar botão
            self.btn_buscar_cep.setEnabled(True)
            self.btn_buscar_cep.setText("🔍 Buscar")
    
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
