"""
Módulo de contas/financeiro em PyQt6 - Versão Completa
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTabWidget, QFrame, QGridLayout, QGroupBox, QScrollArea,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QDateEdit, QSpinBox, QDoubleSpinBox, QMessageBox,
                             QRadioButton, QButtonGroup, QLineEdit)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
from datetime import datetime, timedelta
import calendar

from database import db_manager

# Import the new DB-driven finance widget (guarded - matplotlib may be missing)
try:
    from app.components.contas.contas_financeiro import ContasFinanceiroWidget
except Exception:
    ContasFinanceiroWidget = None

# Tentar importar matplotlib para gráficos
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ContasManager(QWidget):
    """Gerenciamento de contas/financeiro em PyQt6"""
    
    def __init__(self, parent):
        super().__init__()  # Não passar parent aqui
        self.parent = parent
        self._setup_interface()
        self._carregar_dados_iniciais()
    
    def _setup_interface(self):
        """Configura a interface principal"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        self._criar_header(main_layout)
        
        # Abas principais
        self._criar_abas(main_layout)
        
        # Aplicar estilo
        self._aplicar_estilo()
    
    def _criar_header(self, layout):
        """Cria header do módulo"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        # Título
        titulo_label = QLabel("💼 Gestão Financeira")
        titulo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        titulo_label.setStyleSheet("color: #ffffff; padding: 10px;")
        header_layout.addWidget(titulo_label)
        
        header_layout.addStretch()
        
        # Botão atualizar
        btn_atualizar = QPushButton("🔄 Atualizar Dados")
        btn_atualizar.setMinimumWidth(150)
        btn_atualizar.clicked.connect(self._carregar_dados_iniciais)
        header_layout.addWidget(btn_atualizar)
        
        layout.addWidget(header_frame)
    
    def _criar_abas(self, layout):
        """Cria as abas do módulo financeiro"""
        self.tab_widget = QTabWidget()

        # Aba Dashboard (DB-driven widget when available)
        if ContasFinanceiroWidget is not None:
            try:
                self.dashboard_tab = ContasFinanceiroWidget(self)
            except Exception:
                self.dashboard_tab = FinanceiroDashboard(self)
        else:
            self.dashboard_tab = FinanceiroDashboard(self)
        self.tab_widget.addTab(self.dashboard_tab, "📊 Dashboard")

        # Aba Gastos
        self.gastos_tab = GastosTab(self)
        self.tab_widget.addTab(self.gastos_tab, "💸 Gastos")

        # Aba Margem de Lucro
        self.margem_tab = MargemLucroTab(self)
        self.tab_widget.addTab(self.margem_tab, "📈 Margem de Lucro")

        # Conectar mudança de aba
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tab_widget)
    
    def _on_tab_changed(self, index):
        """Executado quando a aba é alterada"""
        current_widget = self.tab_widget.widget(index)
        if hasattr(current_widget, 'atualizar_dados'):
            current_widget.atualizar_dados()
    
    def _carregar_dados_iniciais(self):
        """Carrega dados iniciais de todas as abas"""
        try:
            # Atualizar aba ativa
            current_widget = self.tab_widget.currentWidget()
            if hasattr(current_widget, 'atualizar_dados'):
                current_widget.atualizar_dados()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados: {e}")
    
    def _aplicar_estilo(self):
        """Aplica estilo moderno ao módulo"""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2d2d2d;
                border-radius: 8px;
            }
            
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                font-size: 12px;
            }
            
            QTabBar::tab:selected {
                background-color: #0d7377;
                color: #ffffff;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #505050;
            }
        """)


class FinanceiroDashboard(QWidget):
    """Dashboard financeiro principal"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._setup_interface()
        
    def _setup_interface(self):
        """Configura interface do dashboard"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Cards de resumo
        self._criar_cards_resumo(layout)
        
        # Gráficos (se matplotlib disponível)
        if MATPLOTLIB_AVAILABLE:
            self._criar_area_graficos(layout)
        else:
            self._criar_placeholder_graficos(layout)
    
    def _criar_cards_resumo(self, layout):
        """Cria cards de resumo financeiro"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(15)
        
        # Cards de métricas
        self.card_vendas = self._criar_card_metrica("💰", "Total Vendas", "R$ 0,00", "#00ff88")
        self.card_produtos = self._criar_card_metrica("📦", "Valor Produtos", "R$ 0,00", "#00aaff")
        self.card_lucro = self._criar_card_metrica("📈", "Lucro Bruto", "R$ 0,00", "#ffaa00")
        self.card_quantidade = self._criar_card_metrica("🛒", "Qtd. Vendas", "0", "#ff6b9d")
        
        # Adicionar cards ao grid
        cards_layout.addWidget(self.card_vendas, 0, 0)
        cards_layout.addWidget(self.card_produtos, 0, 1)
        cards_layout.addWidget(self.card_lucro, 0, 2)
        cards_layout.addWidget(self.card_quantidade, 0, 3)
        
        layout.addWidget(cards_frame)
    
    def _criar_card_metrica(self, icone, titulo, valor, cor):
        """Cria um card de métrica"""
        card = QFrame()
        card.setFixedHeight(120)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #3a3a3a;
                border: 2px solid {cor};
                border-radius: 12px;
                padding: 10px;
            }}
            QFrame:hover {{
                background-color: #404040;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        
        # Ícone e título
        header_layout = QHBoxLayout()
        
        icone_label = QLabel(icone)
        icone_label.setFont(QFont("Segoe UI", 24))
        header_layout.addWidget(icone_label)
        
        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        titulo_label.setStyleSheet("color: #cccccc;")
        header_layout.addWidget(titulo_label)
        
        header_layout.addStretch()
        card_layout.addLayout(header_layout)
        
        # Valor
        valor_label = QLabel(valor)
        valor_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        valor_label.setStyleSheet(f"color: {cor};")
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(valor_label)
        
        # Guardar referência do label de valor
        card.valor_label = valor_label
        
        return card
    
    def _criar_area_graficos(self, layout):
        """Cria área de gráficos com matplotlib"""
        graficos_group = QGroupBox("📊 Análise Visual")
        graficos_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        graficos_layout = QVBoxLayout(graficos_group)
        
        # Placeholder para gráfico
        self.figure = Figure(figsize=(12, 6), facecolor='#2d2d2d')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #2d2d2d;")
        graficos_layout.addWidget(self.canvas)
        
        layout.addWidget(graficos_group)
    
    def _criar_placeholder_graficos(self, layout):
        """Cria placeholder quando matplotlib não está disponível"""
        placeholder_group = QGroupBox("📊 Gráficos")
        placeholder_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        placeholder_layout = QVBoxLayout(placeholder_group)
        
        msg_label = QLabel("""
        📊 Gráficos não disponíveis
        
        Para visualizar gráficos, instale o matplotlib:
        pip install matplotlib
        """)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg_label.setStyleSheet("color: #888888; padding: 50px;")
        placeholder_layout.addWidget(msg_label)
        
        layout.addWidget(placeholder_group)
    
    def atualizar_dados(self):
        """Atualiza dados do dashboard"""
        try:
            # Buscar dados de vendas
            pedidos = db_manager.listar_pedidos_ordenados_por_prazo()
            
            total_vendas = 0.0
            total_produtos = 0.0
            quantidade_vendas = len(pedidos)
            
            for pedido in pedidos:
                valor = pedido.get('valor_total', pedido.get('valor_produto', 0))
                if valor:
                    total_vendas += float(valor)
                    total_produtos += float(valor)  # Simplificado
            
            lucro_bruto = total_vendas * 0.3  # Estimativa de 30% de margem
            
            # Atualizar cards
            self.card_vendas.valor_label.setText(f"R$ {total_vendas:.2f}")
            self.card_produtos.valor_label.setText(f"R$ {total_produtos:.2f}")
            self.card_lucro.valor_label.setText(f"R$ {lucro_bruto:.2f}")
            self.card_quantidade.valor_label.setText(str(quantidade_vendas))
            
            # Atualizar gráfico se disponível
            if MATPLOTLIB_AVAILABLE and hasattr(self, 'canvas'):
                self._atualizar_grafico(pedidos)
                
        except Exception as e:
            print(f"Erro ao atualizar dashboard: {e}")
    
    def _atualizar_grafico(self, pedidos):
        """Atualiza gráfico com dados dos pedidos"""
        try:
            self.figure.clear()
            
            # Gráfico de vendas por mês (exemplo)
            ax = self.figure.add_subplot(111, facecolor='#2d2d2d')
            
            # Dados de exemplo (simplificado)
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
            valores = [1000, 1500, 1200, 1800, 2000, 2200]  # Dados simulados
            
            bars = ax.bar(meses, valores, color='#0d7377', alpha=0.8)
            
            # Configurar aparência
            ax.set_title('Vendas por Mês', color='white', fontsize=14, fontweight='bold')
            ax.set_xlabel('Mês', color='white')
            ax.set_ylabel('Valor (R$)', color='white')
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.3, color='white')
            
            # Cor de fundo
            ax.set_facecolor('#3a3a3a')
            
            self.canvas.draw()
            
        except Exception as e:
            print(f"Erro ao atualizar gráfico: {e}")


class ReceitasTab(QWidget):
    """Aba de receitas"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._setup_interface()
    
    def _setup_interface(self):
        """Configura interface de receitas"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Placeholder
        label = QLabel("💰 Módulo de Receitas\n\nEm desenvolvimento...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Segoe UI", 16))
        label.setStyleSheet("color: #cccccc; padding: 50px;")
        layout.addWidget(label)
    
    def atualizar_dados(self):
        """Atualiza dados de receitas"""
        pass


class GastosTab(QWidget):
    """Aba de gastos"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._setup_interface()
    
    def _setup_interface(self):
        """Configura interface de gastos (form + tabela) com estilo escuro e layout responsivo"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Formulário compacto
        form_frame = QFrame()
        form_layout = QHBoxLayout(form_frame)
        form_layout.setSpacing(8)

        # Inline form removed — use modal dialog to add gastos
        from app.components.contas.gastos_modal import GastosDialog
        btn_add = QPushButton("Adicionar")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setStyleSheet('''
            QPushButton { background: #0d7377; color: white; padding: 6px 10px; border-radius: 6px }
            QPushButton:hover { background: #139a9c }
        ''')
        def _open_modal():
            dlg = GastosDialog(self)
            dlg.gasto_adicionado.connect(self.atualizar_dados)
            dlg.exec()
        btn_add.clicked.connect(_open_modal)
        form_layout.addWidget(btn_add)

        layout.addWidget(form_frame)

        # Search bar + buttons (visual parity com aba Produtos)
        search_row = QHBoxLayout()
        self.input_busca_gastos = QLineEdit()
        self.input_busca_gastos.setPlaceholderText('Buscar gasto...')
        self.input_busca_gastos.setStyleSheet('''
            QLineEdit {
                background-color: #282a2c;
                color: #e6e6e6;
                border: 1.5px solid #00c48c;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
            }
        ''')
        search_row.addWidget(self.input_busca_gastos, stretch=1)

        self.btn_buscar_gastos = QPushButton('Buscar')
        self.btn_buscar_gastos.setStyleSheet('''
            QPushButton { background-color: #00c48c; color: #222; border-radius: 8px; padding: 6px 12px; font-weight: bold }
            QPushButton:hover { background-color: #00b07a }
        ''')
        search_row.addWidget(self.btn_buscar_gastos)

        layout.addLayout(search_row)

        # Tabela de gastos (agora com coluna ID e sem cabeçalho vertical)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Tipo", "Descrição", "Valor", "Data"])
        # esconder cabeçalho vertical (números de linha) para usar coluna ID
        try:
            self.table.verticalHeader().setVisible(False)
            # remover o botão-canto branco (pequeno quadrado no canto superior esquerdo)
            try:
                self.table.setCornerButtonEnabled(False)
            except Exception:
                # fallback via stylesheet
                self.table.setStyleSheet(self.table.styleSheet() + '\nQTableCornerButton::section { background: transparent }')
        except Exception:
            pass
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet('''
            QTableWidget {
                background-color: #232526;
                color: #e6e6e6;
                border-radius: 10px;
                font-size: 16px; /* maior texto */
                gridline-color: #3a3a3a;
                selection-background-color: #3a3a3a;
                alternate-background-color: #2b2b2b;
            }
            QHeaderView::section {
                background-color: #3b3b3b;
                color: #00c48c;
                font-weight: bold;
                font-size: 15px; /* cabeçalho maior */
                border: none;
                padding: 8px 12px;
            }
            QTableWidget::item { padding: 10px; }
        ''')
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        try:
            hdr = self.table.horizontalHeader()
            hdr.setSectionResizeMode(0, hdr.ResizeMode.ResizeToContents)
            hdr.setSectionResizeMode(1, hdr.ResizeMode.Stretch)
            hdr.setSectionResizeMode(2, hdr.ResizeMode.ResizeToContents)
            hdr.setSectionResizeMode(3, hdr.ResizeMode.ResizeToContents)
            # Ajuste inicial de larguras para dar mais espaço ao texto e reduzir descrição
            try:
                # valores iniciais (ajuste fino conforme a janela)
                self.table.setColumnWidth(0, 70)   # ID
                self.table.setColumnWidth(1, 120)  # Tipo
                self.table.setColumnWidth(2, 360)  # Descrição
                self.table.setColumnWidth(3, 140)  # Valor
                self.table.setColumnWidth(4, 120)  # Data
            except Exception:
                pass
            # alignment will be set per-item when filling the table
        except Exception:
            try:
                from PyQt6.QtWidgets import QHeaderView
                self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            except Exception:
                pass

        layout.addWidget(self.table, 1)

        # conexão para editar ao dar duplo clique
        try:
            self.table.cellDoubleClicked.connect(self._on_table_double_click)
        except Exception:
            pass

        # Soma de gastos (rodapé, alinhado à direita)
        footer = QHBoxLayout()
        footer.addStretch()
        self.soma_label = QLabel("Total: R$ 0,00")
        self.soma_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.soma_label.setStyleSheet("color: #00c48c;")
        footer.addWidget(self.soma_label)
        layout.addLayout(footer)
    
    def atualizar_dados(self):
        """Atualiza a tabela e soma de gastos (padrão: últimos 12 meses)"""
        try:
            hoje = datetime.now().date()
            inicio = hoje - timedelta(days=365)
            gastos = db_manager.listar_gastos_periodo(inicio.strftime("%Y-%m-%d"), hoje.strftime("%Y-%m-%d"))
            self._preencher_tabela(gastos)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar gastos: {e}")

    def _preencher_tabela(self, gastos):
        """Preenche a tabela de gastos e atualiza soma"""
        self.table.setRowCount(0)
        total = 0.0
        filtro = None
        try:
            filtro = self.input_busca_gastos.text().strip().lower()
        except Exception:
            filtro = None
        for gasto in gastos:
            row = self.table.rowCount()
            # suportar linhas retornadas pelo DB como tuplas (id, tipo, descricao, valor, data)
            # ou dicionários com chaves 'tipo','descricao','valor','data'
            tipo = ''
            descricao = ''
            valor = 0.0
            data = ''
            if isinstance(gasto, dict):
                tipo = gasto.get('tipo', '')
                descricao = gasto.get('descricao', '')
                try:
                    valor = float(gasto.get('valor', 0) or 0)
                except Exception:
                    valor = 0.0
                data = gasto.get('data', '')
            else:
                try:
                    # suporte para (id, tipo, descricao, valor, data)
                    if len(gasto) == 5:
                        _, tipo, descricao, valor_raw, data = gasto
                    # suporte para (tipo, descricao, valor, data)
                    elif len(gasto) == 4:
                        tipo, descricao, valor_raw, data = gasto
                    else:
                        # fallback por índice quando o formato for diferente
                        tipo = gasto[1] if len(gasto) > 1 else ''
                        descricao = gasto[2] if len(gasto) > 2 else ''
                        valor_raw = gasto[3] if len(gasto) > 3 else 0
                        data = gasto[4] if len(gasto) > 4 else ''
                    try:
                        valor = float(valor_raw or 0)
                    except Exception:
                        valor = 0.0
                except Exception:
                    # se não for indexável, manter valores padrão
                    tipo = descricao = ''
                    valor = 0.0
                    data = ''
            # aplicar filtro de busca local (por tipo ou descricao)
            if filtro:
                texto_comb = f"{tipo} {descricao}".lower()
                if filtro not in texto_comb:
                    continue

            self.table.insertRow(row)
            # formatar valor e alinhar colunas (ID | Tipo | Descrição | Valor | Data)
            from PyQt6.QtCore import Qt
            id_item = QTableWidgetItem(str(gasto[0]) if isinstance(gasto, (list, tuple)) and len(gasto) > 0 else "")
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # tornar ID mais discreto (não editável)
            id_item.setFlags(id_item.flags() & ~ (Qt.ItemFlag.ItemIsEditable))
            tipo_item = QTableWidgetItem(str(tipo))
            descricao_item = QTableWidgetItem(str(descricao))
            valor_item = QTableWidgetItem(f"R$ {valor:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
            data_item = QTableWidgetItem(str(data))

            valor_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            data_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, tipo_item)
            self.table.setItem(row, 2, descricao_item)
            self.table.setItem(row, 3, valor_item)
            self.table.setItem(row, 4, data_item)

            total += valor

        self.soma_label.setText(f"Total: R$ {total:.2f}")

    def _on_table_double_click(self, row, col):
        """Abrir diálogo de edição quando o usuário der duplo-clique numa linha."""
        try:
            item = self.table.item(row, 0)  # ID
            if not item:
                return
            gasto_id = item.text()
            try:
                gasto_id = int(gasto_id)
            except Exception:
                return

            from app.components.contas.gastos_modal import GastosDialog
            dlg = GastosDialog(self)
            if dlg.load_gasto(gasto_id):
                dlg.gasto_adicionado.connect(self.atualizar_dados)
                dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao abrir editor de gasto: {e}')

    def _adicionar_gasto(self):
        """Insere um novo gasto no DB e atualiza a tabela"""
        tipo = self.tipo_combo.currentText()
        descricao = self.descricao_edit.text().strip()
        valor = float(self.valor_spin.value())
        try:
            data_py = self.data_edit.date().toPyDate()
        except Exception:
            data_py = datetime.now().date()

        if not descricao:
            QMessageBox.warning(self, "Validação", "Informe a descrição do gasto.")
            return

        if valor <= 0:
            QMessageBox.warning(self, "Validação", "Informe um valor maior que zero.")
            return

        try:
            db_manager.inserir_gasto(tipo, descricao, valor, data_py.strftime("%Y-%m-%d"))
            QMessageBox.information(self, "Sucesso", "Gasto adicionado com sucesso.")
            # limpar campos
            self.descricao_edit.clear()
            self.valor_spin.setValue(0.0)
            self.data_edit.setDate(QDate.currentDate())
            # Atualizar lista
            self.atualizar_dados()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao inserir gasto: {e}")


class MargemLucroTab(QWidget):
    """Aba de margem de lucro"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._setup_interface()
    
    def _setup_interface(self):
        """Configura interface de margem de lucro: cards e gráfico simples"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Filters row
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Período:"))
        self.combo_period_margem = QComboBox()
        self.combo_period_margem.addItems(["Este Mês", "Últimos 3 Meses", "Este Ano"]) 
        top_row.addWidget(self.combo_period_margem)
        top_row.addStretch()
        btn_refresh = QPushButton("Atualizar Dados")
        btn_refresh.clicked.connect(self.atualizar_dados)
        top_row.addWidget(btn_refresh)
        layout.addLayout(top_row)

        # Cards
        cards = QHBoxLayout()
        self.card_total_vendas = self._make_card_small("Total Vendas", "R$ 0,00", "#00c48c")
        self.card_total_gastos = self._make_card_small("Total Gastos", "R$ 0,00", "#ffaa33")
        self.card_lucro = self._make_card_small("Lucro Líquido", "R$ 0,00", "#66d9ef")
        self.card_margem = self._make_card_small("Margem (%)", "0%", "#ff6b9d")
        cards.addWidget(self.card_total_vendas)
        cards.addWidget(self.card_total_gastos)
        cards.addWidget(self.card_lucro)
        cards.addWidget(self.card_margem)
        layout.addLayout(cards)

        # Chart area (small)
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            self.figure_m = Figure(figsize=(6,2), facecolor='#2d2d2d')
            self.canvas_m = FigureCanvas(self.figure_m)
            chart_g = QGroupBox("Evolução")
            cl = QVBoxLayout(chart_g)
            cl.addWidget(self.canvas_m)
            layout.addWidget(chart_g)
        except Exception:
            # fallback placeholder
            ph = QLabel("Gráfico indisponível (matplotlib não instalado)")
            ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(ph)

        # initial load
        self.combo_period_margem.currentIndexChanged.connect(self.atualizar_dados)
        self.atualizar_dados()

    def _make_card_small(self, title, value, color):
        box = QGroupBox(title)
        box.setStyleSheet(f"QGroupBox {{ background: #333333; border: 1px solid {color}; border-radius: 8px; padding: 8px }}")
        l = QVBoxLayout(box)
        lbl = QLabel(value)
        lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {color}")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(lbl)
        box.value_label = lbl
        return box

    def atualizar_dados(self):
        # determine period
        idx = self.combo_period_margem.currentIndex()
        hoje = datetime.now()
        if idx == 0:
            inicio = hoje.replace(day=1).strftime('%Y-%m-%d')
            fim = hoje.strftime('%Y-%m-%d')
        elif idx == 1:
            inicio = (hoje - timedelta(weeks=12)).strftime('%Y-%m-%d')
            fim = hoje.strftime('%Y-%m-%d')
        else:
            inicio = hoje.replace(month=1, day=1).strftime('%Y-%m-%d')
            fim = hoje.strftime('%Y-%m-%d')

        # fetch values
        try:
            vendas = db_manager.calcular_resumo_vendas(inicio, fim)
            total_vendas = float((vendas[1] or 0) if len(vendas) > 1 else (vendas or 0))
        except Exception:
            total_vendas = 0.0

        try:
            total_gastos = float(db_manager.soma_gastos_periodo(inicio, fim) or 0)
        except Exception:
            total_gastos = 0.0

        lucro = total_vendas - total_gastos
        margem = (lucro / total_vendas * 100) if total_vendas else 0.0

        self.card_total_vendas.value_label.setText(f"R$ {total_vendas:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        self.card_total_gastos.value_label.setText(f"R$ {total_gastos:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        self.card_lucro.value_label.setText(f"R$ {lucro:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        self.card_margem.value_label.setText(f"{margem:.1f}%")

        # plot simple evolution if available
        try:
            ax = self.figure_m.subplots()
            ax.clear()
            # show simple bars: months labels for the period
            ax.bar(['Periodo'], [lucro], color='#00c48c')
            ax.set_facecolor('#2d2d2d')
            ax.tick_params(colors='#e6e6e6')
            self.figure_m.tight_layout()
            self.canvas_m.draw()
        except Exception:
            pass
    
    # Remove this duplicate method, as atualizar_dados is already defined above.
