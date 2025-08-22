"""
Módulo de contas/financeiro em PyQt6 - Versão Completa
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTabWidget, QFrame, QGridLayout, QGroupBox, QScrollArea,
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                             QDateEdit, QSpinBox, QDoubleSpinBox, QMessageBox,
                             QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
from datetime import datetime, timedelta
import calendar

from database import db_manager

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
        
        # Aba Dashboard
        self.dashboard_tab = FinanceiroDashboard(self)
        self.tab_widget.addTab(self.dashboard_tab, "📊 Dashboard")
        
        # Aba Receitas
        self.receitas_tab = ReceitasTab(self)
        self.tab_widget.addTab(self.receitas_tab, "💰 Receitas")
        
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
        """Configura interface de gastos"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Placeholder
        label = QLabel("💸 Módulo de Gastos\n\nEm desenvolvimento...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Segoe UI", 16))
        label.setStyleSheet("color: #cccccc; padding: 50px;")
        layout.addWidget(label)
    
    def atualizar_dados(self):
        """Atualiza dados de gastos"""
        pass


class MargemLucroTab(QWidget):
    """Aba de margem de lucro"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self._setup_interface()
    
    def _setup_interface(self):
        """Configura interface de margem de lucro"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Placeholder
        label = QLabel("📈 Módulo de Margem de Lucro\n\nEm desenvolvimento...")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Segoe UI", 16))
        label.setStyleSheet("color: #cccccc; padding: 50px;")
        layout.addWidget(label)
    
    def atualizar_dados(self):
        """Atualiza dados de margem de lucro"""
        pass
