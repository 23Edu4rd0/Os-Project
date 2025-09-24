"""
Módulo de contas/financeiro em PyQt6
Interface unificada para gestão financeira
"""

from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QGridLayout, QGroupBox, QPushButton,
    QMessageBox, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QHeaderView, QTabWidget
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont

# Configuração do matplotlib (opcional)
MATPLOTLIB_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use('Qt5Agg')  # Usar backend Qt5 que funciona com PyQt6
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    pass  # Matplotlib não disponível

from database import db_manager


class MetricCard(QFrame):
    """Card para exibição de métricas financeiras"""
    
    def __init__(self, title, value, icon, color, trend=None, parent=None):
        super().__init__(parent)
        self.setObjectName("metricCard")
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Header com ícone e título
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 24))
        header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet("color: #b0b0b0;")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)
        
        # Valor principal
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Tendência (opcional)
        if trend:
            trend_label = QLabel(trend)
            trend_label.setFont(QFont("Segoe UI", 10))
            trend_label.setStyleSheet("color: #b0b0b0;")
            trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(trend_label)
        else:
            layout.addStretch()
        
        # Estilo
        self.setStyleSheet(f"""
            #metricCard {{
                background: #2d2d2d;
                border: 1px solid {color};
                border-radius: 12px;
                padding: 15px;
                min-height: 120px;
            }}
        """)


class ContasManager(QWidget):
    """Interface unificada de gestão financeira"""
    
    def __init__(self, parent=None):
        """Inicializa o widget de gestão financeira"""
        super().__init__(parent)
        self._setup_ui()
        self._aplicar_estilo()
        
    def _setup_ui(self):
        """Configura a interface do widget"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Criar header
        self._criar_header(layout)
        
        # Criar e configurar abas
        self._criar_abas(layout)
    
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

        # Aba Dashboard
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
            elif hasattr(current_widget, '_load_data'):
                current_widget._load_data()
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
    
    def __init__(self, parent=None):
        """Inicializa o dashboard financeiro"""
        super().__init__(parent)
        self.parent = parent
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Configura a interface do dashboard"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(15)

        # Header com título e botão de atualizar
        header = QHBoxLayout()
        title = QLabel("Dashboard Financeiro")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()

        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.setFont(QFont("Segoe UI", 11))
        refresh_btn.clicked.connect(self._load_data)
        header.addWidget(refresh_btn)
        self.layout.addLayout(header)

        # Grid de métricas
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(15)

        # Adicionar cards de métricas
        self.total_sales = self._create_metric_card("💰", "Total de Vendas", "R$ 0,00", "#4CAF50")
        self.active_orders = self._create_metric_card("📝", "Pedidos Ativos", "0", "#2196F3")
        self.avg_ticket = self._create_metric_card("📊", "Ticket Médio", "R$ 0,00", "#FF9800")
        self.conversion = self._create_metric_card("📈", "Conversão", "0%", "#9C27B0")

        metrics_grid.addWidget(self.total_sales, 0, 0)
        metrics_grid.addWidget(self.active_orders, 0, 1)
        metrics_grid.addWidget(self.avg_ticket, 1, 0)
        metrics_grid.addWidget(self.conversion, 1, 1)

        metrics_frame = QFrame()
        metrics_frame.setLayout(metrics_grid)
        self.layout.addWidget(metrics_frame)

        # Gráfico ou placeholder
        chart_container = QGroupBox("Vendas por Período")
        chart_container.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        chart_layout = QVBoxLayout(chart_container)

        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(8, 4))
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setMinimumHeight(300)
            chart_layout.addWidget(self.canvas)
        else:
            msg = QLabel("📊 Gráficos indisponíveis\n\nPara visualizar gráficos, instale matplotlib:\npip install matplotlib")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("color: #888; padding: 20px;")
            chart_layout.addWidget(msg)

        self.layout.addWidget(chart_container)
        self.layout.addStretch()

    def _create_metric_card(self, icon, title, value, color):
        """Cria um card de métrica"""
        card = QFrame()
        card.setObjectName("metricCard")
        card.setStyleSheet(f"""
            #metricCard {{
                background: #2d2d2d;
                border: 1px solid {color};
                border-radius: 12px;
                padding: 15px;
                min-height: 120px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(5)

        # Header
        header = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI", 24))
        header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet("color: #b0b0b0;")
        header.addWidget(title_label)
        header.addStretch()
        layout.addLayout(header)

        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        layout.addStretch()

        card.value_label = value_label
        return card

    def _load_data(self):
        """Carrega dados do dashboard"""
        try:
            # Buscar dados de vendas do último mês
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            vendas = db_manager.calcular_resumo_vendas(start_date, end_date)

            # Extrair métricas
            total = float(vendas[0] if vendas else 0)
            pedidos_ativos = len(db_manager.listar_pedidos_ordenados_por_prazo())
            ticket_medio = total / pedidos_ativos if pedidos_ativos > 0 else 0
            conversao = 68  # TODO: Implementar cálculo real

            # Atualizar cards
            self.total_sales.value_label.setText(f"R$ {total:,.2f}".replace(',', '.'))
            self.active_orders.value_label.setText(str(pedidos_ativos))
            self.avg_ticket.value_label.setText(f"R$ {ticket_medio:,.2f}".replace(',', '.'))
            self.conversion.value_label.setText(f"{conversao}%")

            # Atualizar gráfico se disponível
            if MATPLOTLIB_AVAILABLE:
                self._update_chart()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados: {e}")

    def _update_chart(self):
        """Atualiza o gráfico de vendas"""
        if not hasattr(self, 'canvas'):
            return

        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#2d2d2d')
            self.figure.patch.set_facecolor('#2d2d2d')

            # Dados dos últimos 6 meses
            meses = ['Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set']  
            valores = [15000, 18000, 16500, 19000, 22000, 25000]  # Dados exemplo

            bars = ax.bar(meses, valores, color='#00c48c', alpha=0.8)
            ax.set_title('Vendas Mensais', color='white', pad=15)
            ax.set_xlabel('Mês', color='white')
            ax.set_ylabel('Valor (R$)', color='white')
            
            # Estilo
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.2, color='white')
            ax.spines['bottom'].set_color('#404040')
            ax.spines['top'].set_color('#404040') 
            ax.spines['right'].set_color('#404040')
            ax.spines['left'].set_color('#404040')

            # Valores sobre as barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'R${int(height):,}',
                        ha='center', va='bottom', color='white')

            self.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            print(f"Erro ao atualizar gráfico: {e}")

    def atualizar_dados(self):
        """Método público para atualização de dados"""
        self._load_data()


class GastosTab(QWidget):
    """Aba de gastos com gestão de despesas"""
    
    gasto_alterado = pyqtSignal()  # Sinal emitido quando um gasto é alterado
    
    def __init__(self, parent=None):
        """Inicializa a aba de gastos"""
        super().__init__(parent)
        self.parent = parent
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura a interface da aba de gastos"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Header com título e botão de adicionar
        header = QHBoxLayout()
        title = QLabel("Gestão de Gastos")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        
        add_btn = QPushButton("➕ Novo Gasto")
        add_btn.setFont(QFont("Segoe UI", 11))
        add_btn.clicked.connect(self._show_add_dialog)
        header.addWidget(add_btn)
        self.layout.addLayout(header)
        
        # Barra de busca
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(15, 10, 15, 10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar gastos...")
        self.search_input.textChanged.connect(self._filter_expenses)
        search_layout.addWidget(self.search_input)
        
        search_frame.setStyleSheet("""
            #searchFrame {
                background: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
            }
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
        """)
        
        self.layout.addWidget(search_frame)
        
        # Tabela de gastos
        self.table = QTableWidget(0, 5)
        self.table.setObjectName("expensesTable")
        
        # Configurar cabeçalhos
        headers = ["ID", "Tipo", "Descrição", "Valor", "Data"]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Configurar layout da tabela
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        # Estilo da tabela
        self.table.setStyleSheet("""
            QTableWidget {
                background: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                gridline-color: #404040;
            }
            QHeaderView::section {
                background: #404040;
                color: #b0b0b0;
                border: none;
                padding: 10px;
                font-size: 13px;
            }
            QTableWidget::item {
                color: white;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #4a4a4a;
            }
        """)
        
        self.layout.addWidget(self.table)
        
        # Rodapé com total
        footer = QHBoxLayout()
        footer.addStretch()
        
        self.total_label = QLabel("Total: R$ 0,00")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #00c48c;")
        footer.addWidget(self.total_label)
        
        self.layout.addLayout(footer)
        
        # Carregar dados iniciais
        self.load_data()
        
    def load_data(self):
        """Carrega os dados de gastos do banco"""
        try:
            # Calcular período dos últimos 12 meses
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
            
            # Buscar gastos do período
            expenses = db_manager.listar_gastos_periodo(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d")
            )
            
            self._populate_table(expenses)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar gastos: {e}")
    
    def _populate_table(self, expenses):
        """Preenche a tabela com os gastos"""
        self.table.setRowCount(0)
        total = 0.0
        
        # Filtro de busca
        search_text = self.search_input.text().lower()
        
        for expense in expenses:
            # Extrair dados do gasto
            if isinstance(expense, dict):
                expense_id = expense.get('id', '')
                tipo = expense.get('tipo', '')
                descricao = expense.get('descricao', '')
                valor = float(expense.get('valor', 0) or 0)
                data = expense.get('data', '')
            else:
                try:
                    expense_id = expense[0]
                    tipo = expense[1]
                    descricao = expense[2]
                    valor = float(expense[3] or 0)
                    data = expense[4]
                except Exception:
                    continue
            
            # Aplicar filtro
            if search_text and search_text not in f"{tipo} {descricao}".lower():
                continue
            
            # Adicionar linha
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Criar e configurar células
            cells = [
                (str(expense_id), Qt.AlignmentFlag.AlignCenter),
                (tipo, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                (descricao, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                (f"R$ {valor:,.2f}".replace(',', '.'), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter),
                (data, Qt.AlignmentFlag.AlignCenter)
            ]
            
            for col, (text, alignment) in enumerate(cells):
                item = QTableWidgetItem(text)
                item.setTextAlignment(alignment)
                self.table.setItem(row, col, item)
            
            total += valor
        
        # Atualizar total
        self.total_label.setText(f"Total: R$ {total:,.2f}".replace(',', '.'))
    
    def _filter_expenses(self):
        """Filtra a tabela de gastos"""
        self.load_data()  # Recarrega aplicando o filtro
    
    def _show_add_dialog(self):
        """Exibe o diálogo para adicionar gasto"""
        try:
            from app.components.contas.gastos_modal import GastosDialog
            dialog = GastosDialog(self)
            if dialog.exec() == 1:  # Aceito
                self.load_data()
                self.gasto_alterado.emit()
        except ImportError:
            QMessageBox.information(self, "Aviso", "Modal de gastos ainda não implementado.")
    
    def _on_row_double_clicked(self, row, col):
        """Manipula o duplo clique em uma linha para edição"""
        try:
            expense_id = int(self.table.item(row, 0).text())
            from app.components.contas.gastos_modal import GastosDialog
            dialog = GastosDialog(self)
            if dialog.load_gasto(expense_id):
                if dialog.exec() == 1:  # Aceito
                    self.load_data()
                    self.gasto_alterado.emit()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir editor: {e}")

    def atualizar_dados(self):
        """Método público para atualização de dados"""
        self.load_data()


class MargemLucroTab(QWidget):
    """Aba de análise de margem de lucro"""
    
    def __init__(self, parent=None):
        """Inicializa a aba de margem de lucro"""
        super().__init__(parent)
        self.parent = parent
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura a interface da aba de margem de lucro"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Header com título e seletor de período
        header = QHBoxLayout()
        title = QLabel("Análise de Margem")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.addWidget(title)
        
        header.addStretch()
        
        period_label = QLabel("Período:")
        period_label.setFont(QFont("Segoe UI", 12))
        header.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["Este Mês", "Últimos 3 Meses", "Este Ano"])
        self.period_combo.setFont(QFont("Segoe UI", 12))
        self.period_combo.currentIndexChanged.connect(self.update_data)
        header.addWidget(self.period_combo)
        
        refresh_btn = QPushButton("🔄 Atualizar")
        refresh_btn.setFont(QFont("Segoe UI", 11))
        refresh_btn.clicked.connect(self.update_data)
        header.addWidget(refresh_btn)
        
        self.layout.addLayout(header)
        
        # Cards de métricas
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(15)
        
        # Cards com cores temáticas para diferentes métricas
        self.sales_card = self._create_metric_card("Total Vendas", "R$ 0,00", "#4CAF50")
        self.expenses_card = self._create_metric_card("Total Gastos", "R$ 0,00", "#FF9800")
        self.profit_card = self._create_metric_card("Lucro Líquido", "R$ 0,00", "#2196F3")
        self.margin_card = self._create_metric_card("Margem", "0%", "#9C27B0")
        
        metrics_grid.addWidget(self.sales_card, 0, 0)
        metrics_grid.addWidget(self.expenses_card, 0, 1)
        metrics_grid.addWidget(self.profit_card, 1, 0)
        metrics_grid.addWidget(self.margin_card, 1, 1)
        
        self.layout.addLayout(metrics_grid)
        
        # Área de gráfico
        if MATPLOTLIB_AVAILABLE:
            chart_group = QGroupBox("Evolução Mensal")
            chart_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            chart_layout = QVBoxLayout(chart_group)
            
            self.figure = Figure(figsize=(8, 4))
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("background: #2d2d2d;")
            chart_layout.addWidget(self.canvas)
            
            self.layout.addWidget(chart_group)
        else:
            msg = QLabel("📊 Gráficos indisponíveis\n\nPara visualizar gráficos, instale matplotlib:\npip install matplotlib")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("color: #888; padding: 20px;")
            self.layout.addWidget(msg)
        
        self.layout.addStretch()
        
        # Carregar dados iniciais
        self.update_data()
        
    def _create_metric_card(self, title, value, color):
        """Cria um card de métrica com estilo consistente"""
        card = QFrame()
        card.setObjectName("metricCard")
        card.setStyleSheet(f"""
            #metricCard {{
                background: #2d2d2d;
                border: 1px solid {color};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12))
        title_label.setStyleSheet("color: #b0b0b0;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        card.value_label = value_label
        return card
    
    def update_data(self):
        """Atualiza os dados conforme o período selecionado"""
        try:
            # Definir período
            hoje = datetime.now()
            idx = self.period_combo.currentIndex()
            
            if idx == 0:  # Este Mês
                inicio = hoje.replace(day=1)
            elif idx == 1:  # Últimos 3 Meses
                inicio = hoje - timedelta(days=90)
            else:  # Este Ano
                inicio = hoje.replace(month=1, day=1)
            
            # Buscar dados
            vendas = db_manager.calcular_resumo_vendas(
                inicio.strftime('%Y-%m-%d'),
                hoje.strftime('%Y-%m-%d')
            )
            total_vendas = float(vendas[0] if vendas else 0)
            
            total_gastos = float(db_manager.soma_gastos_periodo(
                inicio.strftime('%Y-%m-%d'),
                hoje.strftime('%Y-%m-%d')
            ) or 0)
            
            # Calcular métricas
            lucro = total_vendas - total_gastos
            margem = (lucro / total_vendas * 100) if total_vendas > 0 else 0
            
            # Atualizar cards
            self.sales_card.value_label.setText(f"R$ {total_vendas:,.2f}")
            self.expenses_card.value_label.setText(f"R$ {total_gastos:,.2f}")
            self.profit_card.value_label.setText(f"R$ {lucro:,.2f}")
            self.margin_card.value_label.setText(f"{margem:.1f}%")
            
            # Atualizar gráfico
            if MATPLOTLIB_AVAILABLE and hasattr(self, 'canvas'):
                self._update_chart(inicio, hoje)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar dados: {e}")
    
    def _update_chart(self, start_date, end_date):
        """Atualiza o gráfico de evolução"""
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#2d2d2d')
            self.figure.patch.set_facecolor('#2d2d2d')
            
            # Dados de exemplo
            months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
            profit = [15000, 18000, 16500, 19000, 22000, 25000]
            
            # Criar gráfico
            bars = ax.bar(months, profit, color='#00c48c', alpha=0.8)
            
            # Estilo
            ax.set_title('Evolução do Lucro', color='white', pad=15)
            ax.set_xlabel('Mês', color='white')
            ax.set_ylabel('Valor (R$)', color='white')
            ax.tick_params(colors='white')
            ax.grid(True, alpha=0.2, color='white')
            
            for spine in ax.spines.values():
                spine.set_color('#404040')
            
            # Valores sobre as barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'R${int(height):,}',
                       ha='center', va='bottom', color='white')
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Erro ao atualizar gráfico: {e}")

    def atualizar_dados(self):
        """Método público para atualização de dados"""
        self.update_data()
