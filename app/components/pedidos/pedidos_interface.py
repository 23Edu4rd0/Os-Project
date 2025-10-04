"""Interface principal dos pedidos em PyQt6 (reescrita do zero, sem placeholders)"""

import time
from PyQt6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QComboBox,
	QPushButton,
	QScrollArea,
	QFrame,
	QGridLayout,
	QSizePolicy,
	QLineEdit,
	QDateEdit,
	QCheckBox,
	QCalendarWidget,
	QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from app.signals import get_signals
from app.utils.keyboard_shortcuts import setup_standard_shortcuts

# Import robusto do gerenciador de banco de dados
try:
	from database import db_manager  # singleton
except ModuleNotFoundError:
	import sys, pathlib
	ROOT = pathlib.Path(__file__).resolve().parents[3]
	if str(ROOT) not in sys.path:
		sys.path.insert(0, str(ROOT))
	from database import db_manager  # type: ignore

# Imports dos componentes (funciona tanto como pacote quanto executado direto)
try:
	from .pedidos_card import PedidosCard
	from .novo_pedidos_modal import NovoPedidosModal
except Exception:
	import sys, pathlib
	ROOT = pathlib.Path(__file__).resolve().parents[3]
	if str(ROOT) not in sys.path:
		sys.path.insert(0, str(ROOT))
	from app.components.pedidos.pedidos_card import PedidosCard  # type: ignore
	from app.components.pedidos.novo_pedidos_modal import NovoPedidosModal  # type: ignore


class CustomDateEdit(QDateEdit):
	"""QDateEdit customizado com calendário que força a visibilidade dos números"""
	
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setCalendarPopup(True)
		self.setup_styles()
		# Timer para configurar o calendário após ele ser criado
		self.calendar_timer = QTimer()
		self.calendar_timer.setSingleShot(True)
		self.calendar_timer.timeout.connect(self.configure_calendar)
	
	def configure_calendar(self):
		"""Configura o calendário para garantir que todos os números apareçam"""
		calendar = self.calendarWidget()
		if calendar:
			# Configurar tamanho do calendário - mais largo para acomodar todos os números
			calendar.setMinimumSize(400, 300)
			calendar.setMaximumSize(500, 400)
			calendar.resize(420, 320)
			
			# Encontrar e configurar a tabela interna
			table_views = calendar.findChildren(QWidget)
			for widget in table_views:
				if hasattr(widget, 'setRowHeight') or 'TableView' in str(type(widget)):
					widget.setMinimumSize(350, 220)
			
			# Aplicar estilos com configurações mais robustas
			calendar_style = """
				QCalendarWidget {
					background-color: #2b2b2b;
					color: #ffffff;
					border: 2px solid #007ACC;
					border-radius: 8px;
					font-family: 'Segoe UI', Arial;
					font-size: 14px;
				}
				
				/* Configuração específica para a área de exibição dos dias */
				QCalendarWidget QAbstractItemView {
					color: #ffffff !important;
					background-color: #2b2b2b !important;
					outline: none;
					selection-background-color: #007ACC;
					selection-color: #ffffff;
					font-size: 16px;
					font-weight: bold;
				}
				
				/* Tabela principal onde ficam os números dos dias */
				QCalendarWidget QTableView {
					color: #ffffff !important;
					background-color: #2b2b2b !important;
					gridline-color: #555555;
					outline: none;
					selection-background-color: #007ACC;
					selection-color: #ffffff;
					font-size: 16px;
					font-weight: bold;
					border: none;
				}
				
				/* Células individuais dos dias - MAIS ESPECÍFICO */
				QCalendarWidget QAbstractItemView::item,
				QCalendarWidget QTableView::item {
					color: #ffffff !important;
					background-color: #2b2b2b !important;
					padding: 8px !important;
					margin: 1px !important;
					font-size: 16px !important;
					font-weight: bold !important;
					border: 1px solid #444444 !important;
					min-width: 40px !important;
					min-height: 32px !important;
					max-width: none !important;
					max-height: none !important;
					text-align: center !important;
				}
				
				/* Estados hover e selecionado */
				QCalendarWidget QAbstractItemView::item:hover,
				QCalendarWidget QTableView::item:hover {
					background-color: #404040 !important;
					color: #ffffff !important;
					border: 1px solid #007ACC !important;
				}
				
				QCalendarWidget QAbstractItemView::item:selected,
				QCalendarWidget QTableView::item:selected {
					background-color: #007ACC !important;
					color: #ffffff !important;
					border: 1px solid #005AA0 !important;
				}
				
				/* Cabeçalho com dias da semana */
				QCalendarWidget QHeaderView::section {
					background-color: #3a3a3a;
					color: #ffffff;
					padding: 8px;
					font-weight: bold;
					font-size: 14px;
					border: 1px solid #555555;
					min-height: 25px;
				}
				
				/* Botões de navegação */
				QCalendarWidget QToolButton {
					background-color: #3a3a3a;
					color: #ffffff;
					border: 1px solid #555555;
					border-radius: 4px;
					padding: 6px;
					font-weight: bold;
					font-size: 12px;
					min-width: 60px;
				}
				
				QCalendarWidget QToolButton:hover {
					background-color: #007ACC;
					color: #ffffff;
				}
				
				/* SpinBox para ano */
				QCalendarWidget QSpinBox {
					background-color: #3a3a3a;
					color: #ffffff;
					border: 1px solid #555555;
					padding: 4px;
					font-weight: bold;
					font-size: 12px;
					min-width: 70px;
				}
			"""
			calendar.setStyleSheet(calendar_style)
			
			# Forçar atualização do layout
			calendar.updateGeometry()
			calendar.update()
	
	def showEvent(self, event):
		"""Configurar calendário quando mostrado"""
		super().showEvent(event)
		# Atrasar a configuração para garantir que o calendário esteja criado
		self.calendar_timer.start(100)
	
	def setup_styles(self):
		"""Aplica estilos completos ao QDateEdit"""
		self.setStyleSheet("""
			QDateEdit {
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
					stop: 0 #3a3a3a, stop: 1 #2a2a2a);
				color: white;
				border: 2px solid #505050;
				padding: 8px 12px;
				border-radius: 6px;
				font-size: 12px;
				min-width: 120px;
				font-weight: 500;
			}
			QDateEdit:hover {
				border: 2px solid #007ACC;
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
					stop: 0 #404040, stop: 1 #303030);
			}
			QDateEdit:focus {
				border: 2px solid #007ACC;
				background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
					stop: 0 #404040, stop: 1 #2f2f2f);
				box-shadow: 0 0 5px rgba(0, 122, 204, 0.3);
			}
			QDateEdit::drop-down {
				subcontrol-origin: padding;
				subcontrol-position: top right;
				width: 26px;
				border-left: 1px solid #666666;
				background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
					stop:0 #4a4a4a, stop:1 #3a3a3a);
				border-top-right-radius: 4px;
				border-bottom-right-radius: 4px;
			}
			QDateEdit::drop-down:hover {
				background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
					stop:0 #007ACC, stop:1 #005AA0);
			}
			QDateEdit::down-arrow {
				image: none;
				border-left: 5px solid transparent;
				border-right: 5px solid transparent;
				border-top: 6px solid #cccccc;
				width: 0px;
				height: 0px;
				margin-right: 2px;
			}
			QDateEdit::drop-down:hover QDateEdit::down-arrow {
				border-top-color: #ffffff;
			}
		""")


class PedidosInterface(QWidget):
	"""Gerencia a interface principal de pedidos."""

	dados_carregados = pyqtSignal()

	def __init__(self, parent):
		super().__init__(parent)
		self.parent = parent

		# Estado
		self.status_filter = "todos"
		self._cache_pedidos = None
		self._cache_timestamp = 0.0
		self._cache_timeout = 20  # segundos
		
		# Variáveis de filtro
		self.search_text = ""

		# Helpers
		self.card_manager = PedidosCard(self)
		
		# Conectar sinais para atualizações em tempo real
		self._conectar_sinais()

		# UI
		self._setup_interface()
		
		# Configurar atalhos de teclado
		self._setup_keyboard_shortcuts()
	
	def _conectar_sinais(self):
		"""Conecta os sinais globais para atualização em tempo real"""
		try:
			signals = get_signals()
			# Sinais de status
			signals.statuses_updated.connect(self._on_statuses_updated)
			# Sinais de pedidos
			signals.pedido_criado.connect(self._on_pedido_atualizado)
			signals.pedido_editado.connect(self._on_pedido_atualizado)
			signals.pedido_excluido.connect(self._on_pedido_atualizado)
			signals.pedido_status_atualizado.connect(self._on_status_atualizado)
			signals.pedidos_atualizados.connect(self._on_pedidos_atualizados)
		except Exception as e:
			print(f"Erro ao conectar sinais: {e}")
	
	def _on_pedido_atualizado(self, pedido_id: int = None):
		"""Atualiza a lista quando um pedido é modificado"""
		self.carregar_dados(force_refresh=True)
	
	def _on_status_atualizado(self, pedido_id: int, novo_status: str):
		"""Atualiza a lista quando o status de um pedido muda"""
		self.carregar_dados(force_refresh=True)
	
	def _on_pedidos_atualizados(self):
		"""Atualiza a lista quando há mudança geral nos pedidos"""
		self.carregar_dados(force_refresh=True)
		# Mostrar estado de carregamento inicial (será substituído após carregar)
		self._mostrar_msg("Carregando pedidos...", cor="#bbbbbb")
		self.carregar_dados(force_refresh=True)

	def _setup_interface(self):
		layout = QVBoxLayout(self)
		layout.setContentsMargins(15, 15, 15, 15)  # Margens mais generosas
		layout.setSpacing(15)  # Maior espaçamento vertical

		# Header moderno com gradiente
		header_container = QFrame()
		header_container.setStyleSheet("""
			QFrame {
				background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
					stop:0 #323232, stop:1 #2a2a2a);
				border-radius: 10px;
				padding: 5px;
			}
		""")
		header_container.setFixedHeight(50)
		header_layout = QHBoxLayout(header_container)
		header_layout.setContentsMargins(15, 0, 15, 0)
		
		titulo = QLabel("Pedidos")
		titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff; background-color: transparent;")
		header_layout.addWidget(titulo)
		
		header_layout.addStretch()
		
		# Botão recarregar
		self.btn_recarregar = QPushButton("🔄 Recarregar")
		self.btn_recarregar.setStyleSheet("""
			QPushButton {
				background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
					stop:0 #48bb78, stop:1 #38a169);
				color: white;
				border: none;
				border-radius: 6px;
				border-bottom: 2px solid #2f855a;
				padding: 8px 15px;
				font-size: 12px;
				font-weight: 600;
			}
			QPushButton:hover {
				background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
					stop:0 #4fd88b, stop:1 #43bd7d);
			}
			QPushButton:pressed {
				padding-top: 9px;
				padding-bottom: 7px;
			}
		""")
		self.btn_recarregar.setToolTip("Recarregar lista de pedidos")
		self.btn_recarregar.clicked.connect(self.recarregar_pedidos)
		header_layout.addWidget(self.btn_recarregar)
		
		# Botão novo pedido modernizado
		self.btn_novo = QPushButton("Novo Pedido")
		self.btn_novo.setStyleSheet("""
			QPushButton {
				background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
					stop:0 #3281e8, stop:1 #1565c0);
				color: white;
				border: none;
				border-radius: 6px;
				border-bottom: 2px solid #104d92;
				padding: 8px 15px;
				font-size: 12px;
				font-weight: 600;
			}
			QPushButton:hover {
				background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
					stop:0 #3a8af0, stop:1 #1976d2);
			}
			QPushButton:pressed {
				padding-top: 9px;
				padding-bottom: 7px;
			}
		""")
		self.btn_novo.clicked.connect(self.novo_pedido)
		header_layout.addWidget(self.btn_novo)
		
		layout.addWidget(header_container)
		
		# Filtros e pesquisa avançados
		filtros_container = QFrame()
		filtros_container.setStyleSheet("""
			QFrame {
				background: rgba(255, 255, 255, 0.05);
				border-radius: 8px;
			}
		""")
		filtros_main_layout = QVBoxLayout(filtros_container)
		filtros_main_layout.setContentsMargins(15, 10, 15, 10)
		filtros_main_layout.setSpacing(8)
		
		# Primeira linha: Status e pesquisa por nome/CPF/telefone
		primeira_linha = QHBoxLayout()
		
		# Status
		status_label = QLabel("Status:")
		status_label.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: 600; background-color: transparent;")
		primeira_linha.addWidget(status_label)
		
		self.filtro_status = QComboBox()
		# Carregar status do banco de dados
		try:
			from app.utils.statuses import load_statuses
			status_list = ["Todos"] + [s.title() for s in load_statuses()]
		except Exception:
			status_list = ["Todos", "Pendente", "Em Andamento", "Concluído", "Cancelado"]
		self.filtro_status.addItems(status_list)
		self.filtro_status.setStyleSheet("""
			QComboBox {
				background-color: #3a3a3a;
				color: white;
				border: 1px solid #505050;
				padding: 6px 10px;
				border-radius: 5px;
				min-width: 130px;
				font-size: 12px;
			}
			QComboBox::drop-down {
				border: none;
				width: 24px;
			}
			QComboBox QAbstractItemView {
				background-color: #3a3a3a;
				color: white;
				selection-background-color: #505050;
				border: 1px solid #505050;
			}
		""")
		self.filtro_status.currentTextChanged.connect(self._filtrar_pedidos)
		primeira_linha.addWidget(self.filtro_status)
		
		primeira_linha.addSpacing(20)
		
		# Campo de pesquisa por nome/CPF/telefone
		search_label = QLabel("Buscar:")
		search_label.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: 600; background-color: transparent;")
		primeira_linha.addWidget(search_label)
		
		self.search_input = QLineEdit()
		self.search_input.setPlaceholderText("Nome, CPF ou telefone do cliente...")
		self.search_input.setStyleSheet("""
			QLineEdit {
				background-color: #3a3a3a;
				color: white;
				border: 2px solid #505050;
				padding: 8px 12px;
				border-radius: 6px;
				font-size: 12px;
				min-width: 250px;
			}
			QLineEdit:focus {
				border: 2px solid #007ACC;
			}
			QLineEdit::placeholder {
				color: #888888;
			}
		""")
		self.search_input.textChanged.connect(self._on_search_changed)
		primeira_linha.addWidget(self.search_input)
		
		primeira_linha.addSpacing(8)  # Pequeno espaço entre busca e botão
		
		# Botão limpar filtros
		self.btn_limpar = QPushButton("🧹 Limpar")
		self.btn_limpar.setStyleSheet("""
			QPushButton {
				background-color: #d32f2f;
				color: white;
				border: none;
				border-radius: 5px;
				padding: 8px 12px;
				font-size: 11px;
				font-weight: 600;
			}
			QPushButton:hover {
				background-color: #f44336;
			}
		""")
		self.btn_limpar.clicked.connect(self._limpar_filtros)
		primeira_linha.addWidget(self.btn_limpar)
		
		primeira_linha.addStretch()
		
		# Contador de resultados (alinhado à direita)
		self.label_resultados = QLabel("")
		self.label_resultados.setStyleSheet("""
			color: #b0b0b0; 
			font-size: 12px; 
			font-style: italic; 
			font-weight: 500;
			padding: 0 8px;
		""")
		self.label_resultados.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
		primeira_linha.addWidget(self.label_resultados)
		
		filtros_main_layout.addLayout(primeira_linha)
		
		layout.addWidget(filtros_container)
		
		# Área de scroll modernizada
		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
		self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.scroll_area.setStyleSheet("""
			QScrollArea {
				background-color: #252525; 
				border: none;
				border-radius: 10px;
			}
			QScrollBar:vertical {
				background-color: #2d2d2d;
				width: 14px;
				border-radius: 7px;
				margin: 0px;
			}
			QScrollBar::handle:vertical {
				background-color: #505050;
				border-radius: 7px;
				min-height: 30px;
				margin: 2px;
			}
			QScrollBar::handle:vertical:hover {
				background-color: #606060;
			}
			QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
				height: 0px;
			}
			QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
				background: none;
			}
		""")
		
		self.scroll_widget = QWidget()
		self.scroll_widget.setStyleSheet("background-color: #252525;")
		self.scroll_layout = QVBoxLayout(self.scroll_widget)
		self.scroll_layout.setContentsMargins(10, 10, 10, 20)  # Margens reduzidas
		self.scroll_layout.setSpacing(10)  # Espaçamento reduzido
		
		# Configurar scroll suave
		self.scroll_area.verticalScrollBar().setSingleStep(25)
		self.scroll_area.verticalScrollBar().setPageStep(150)
		
		# Configurar política de tamanho do widget de scroll
		self.scroll_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
		
		self.scroll_area.setWidget(self.scroll_widget)
		layout.addWidget(self.scroll_area)

	def _on_status_changed(self, status: str):
		self.status_filter = status
		self.carregar_dados()

	def carregar_dados(self, force_refresh: bool = False):
		now = time.time()
		if not force_refresh and self._cache_pedidos and (now - self._cache_timestamp) < self._cache_timeout:
			pedidos = self._cache_pedidos
		else:
			try:
				pedidos = db_manager.listar_pedidos_ordenados_por_prazo(limite=50)
				self._cache_pedidos = pedidos
				self._cache_timestamp = now
			except Exception as e:
				print(f"Erro ao carregar pedidos: {e}")
				self._mostrar_msg("❌ Erro ao carregar pedidos", cor="#ff6b6b")
				return

		# Filtrar por status
		if self.status_filter and self.status_filter.lower() != "todos":
			filtro = self.status_filter.lower()
			pedidos_filtrados = []
			for p in pedidos:
				status_pedido = (p.get("status", "") or "").lower().strip()
				# Normalizar para comparação
				if filtro == status_pedido:
					pedidos_filtrados.append(p)
			pedidos = pedidos_filtrados
		
		# Filtrar por texto de busca (nome, CPF, telefone)
		if hasattr(self, 'search_text') and self.search_text:
			def _match_search(pedido):
				search_fields = [
					pedido.get('nome_cliente', '').lower(),
					pedido.get('cpf_cliente', '').lower(),
					pedido.get('telefone_cliente', '').lower(),
				]
				return any(self.search_text in field for field in search_fields if field)
			
			pedidos = [p for p in pedidos if _match_search(p)]
		# Render
		# Separar pedidos concluídos e ativos, ordenar por data de entrega
		def _is_concluido(status: str) -> bool:
			st = (status or "").lower()
			return (st == "entregue") or ("conclu" in st)
		
		pedidos_ativos = [p for p in pedidos if not _is_concluido(p.get("status", ""))]
		pedidos_concluidos = [p for p in pedidos if _is_concluido(p.get("status", ""))]
		
		# Ordenar por data de entrega mais próxima (asc)
		try:
			def _dias_restantes(p):
				from datetime import datetime, timedelta
				# Preferir data_entrega; se não existir, usar data_criacao + prazo
				data_entrega = p.get("data_entrega")
				if data_entrega:
					try:
						if isinstance(data_entrega, str):
							for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
								try:
									return (datetime.strptime(data_entrega, fmt).date() - datetime.now().date()).days
								except Exception:
									pass
							try:
								return (datetime.fromisoformat(str(data_entrega)[:19]).date() - datetime.now().date()).days
							except Exception:
								pass
					except Exception:
						pass
				try:
					prazo = int(p.get("prazo") or 0)
				except Exception:
					prazo = 0
				data_criacao = p.get("data_criacao")
				if prazo > 0 and data_criacao:
					try:
						if isinstance(data_criacao, str):
							base = datetime.fromisoformat(data_criacao[:19]) if len(data_criacao) >= 10 else datetime.strptime(data_criacao, "%Y-%m-%d")
						elif hasattr(data_criacao, "date"):
							base = data_criacao
						else:
							base = datetime.now()
						return ((base + timedelta(days=prazo)).date() - datetime.now().date()).days
					except Exception:
						pass
				# Sem data, colocar no fim
				return 10**9
			pedidos_ativos = sorted(pedidos_ativos, key=_dias_restantes)
			pedidos_concluidos = sorted(pedidos_concluidos, key=_dias_restantes)
		except Exception:
			pass
		
		# Juntar: ativos primeiro, concluídos depois
		pedidos = pedidos_ativos + pedidos_concluidos

		self._limpar_layout()
		
		# Atualizar contador de resultados
		if hasattr(self, 'label_resultados'):
			total = len(pedidos)
			if total == 0:
				self.label_resultados.setText("Nenhum resultado encontrado")
			elif total == 1:
				self.label_resultados.setText("1 pedido encontrado")
			else:
				self.label_resultados.setText(f"{total} pedidos encontrados")
		
		if not pedidos:
			self._mostrar_msg("📋 Nenhum pedido encontrado", cor="#aaaaaa")
		else:
			self._criar_grid_cards(pedidos)
			self.dados_carregados.emit()

	def _limpar_layout(self):
		while self.scroll_layout.count():
			item = self.scroll_layout.takeAt(0)
			w = item.widget()
			if w is not None:
				w.deleteLater()

	def recarregar_pedidos(self):
		"""Recarrega a lista de pedidos com feedback visual"""
		# Desabilitar botão temporariamente
		self.btn_recarregar.setEnabled(False)
		self.btn_recarregar.setText("🔄 Recarregando...")
		
		# Processar eventos para atualizar a UI
		from PyQt6.QtWidgets import QApplication
		QApplication.processEvents()
		
		# Recarregar dados
		self.carregar_dados(force_refresh=True)
		
		# Reabilitar botão
		self.btn_recarregar.setEnabled(True)
		self.btn_recarregar.setText("🔄 Recarregar")

	def _mostrar_msg(self, texto: str, cor: str = "#cccccc"):
		lbl = QLabel(texto)
		lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
		lbl.setStyleSheet(f"color: {cor}; font-size: 15px; padding: 40px;")
		self.scroll_layout.addWidget(lbl)

	def _criar_grid_cards(self, pedidos):
		grid = QWidget()
		grid_l = QGridLayout(grid)
		grid_l.setSpacing(12)  # Espaçamento reduzido entre cards
		# Margens maiores para evitar corte
		try:
			grid_l.setContentsMargins(15, 10, 15, 10)
		except Exception:
			pass

		# Conectar sinais uma vez
		try:
			self.card_manager.visualizar_clicked.disconnect()
		except Exception:
			pass
		try:
			self.card_manager.editar_clicked.disconnect()
		except Exception:
			pass
		try:
			self.card_manager.excluir_clicked.disconnect()
		except Exception:
			pass
		try:
			self.card_manager.status_changed.disconnect()
		except Exception:
			pass
		self.card_manager.visualizar_clicked.connect(self.visualizar_pedido)
		self.card_manager.editar_clicked.connect(self.editar_pedido)
		self.card_manager.excluir_clicked.connect(self.excluir_pedido)
		self.card_manager.status_changed.connect(self.atualizar_status)

		# Forçar 3 colunas fixas (cards estão mais largos agora com 450-500px)
		cols = 3
		
		print(f"Grid configurado para {cols} colunas")
		
		# Configurar stretch igual para todas as colunas
		for col in range(cols):
			grid_l.setColumnStretch(col, 1)
		
		r = c = 0
		for pedido in pedidos:
			try:
				w = self.card_manager.criar_card(pedido)
				grid_l.addWidget(w, r, c)
				c += 1
				if c >= cols:
					c = 0
					r += 1
			except Exception as e:
				print(f"Erro ao criar card para pedido {pedido.get('id')}: {e}")

		# Configurar política de tamanho do grid para permitir scroll adequado
		grid.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
		
		self.scroll_layout.addWidget(grid)
		
		# Espaçamento no final usando stretch
		self.scroll_layout.addStretch()

	def _on_statuses_updated(self):
		# reload the status combo and refresh data
		try:
			from app.utils.statuses import load_statuses
			itens = ["todos"] + load_statuses()
			self.status_combo.clear()
			self.status_combo.addItems(itens)
		except Exception:
			pass
		# force refresh of cards
		try:
			self.carregar_dados(force_refresh=True)
		except Exception:
			pass
	
	def _setup_keyboard_shortcuts(self):
		"""Configura os atalhos de teclado para a interface de pedidos"""
		try:
			callbacks = {
				'new': self.novo_pedido,  # Ctrl+N
				'save': None,  # Não aplicável nesta tela
				'search': lambda: self.search_input.setFocus(),  # Ctrl+F
				'reload': self.recarregar_pedidos,  # F5
				'delete': None,  # Delete individual por card
			}
			self.shortcut_manager = setup_standard_shortcuts(self, callbacks)
			
			# Atualizar tooltips dos botões com atalhos
			self.btn_novo.setToolTip("Criar novo pedido (Ctrl+N)")
			self.btn_recarregar.setToolTip("Recarregar lista de pedidos (F5)")
			self.search_input.setToolTip("Buscar pedido (Ctrl+F)")
		except Exception as e:
			print(f"Erro ao configurar atalhos: {e}")

	# Ações públicas ---------------------------------------------------------
	def novo_pedido(self):
		modal = NovoPedidosModal(self)
		modal.pedido_salvo.connect(self._on_novo_pedido_salvo)
		modal._criar_modal_completo()
	
	def _on_novo_pedido_salvo(self):
		"""Callback quando um novo pedido é salvo"""
		signals = get_signals()
		signals.pedidos_atualizados.emit()
		# O sinal já vai atualizar a interface através de _on_pedidos_atualizados

	def visualizar_pedido(self, pedido_id: int):
		"""Abre o dialog de resumo do pedido para visualização"""
		try:
			print(f"Visualizando pedido ID: {pedido_id}")
			from app.components.dialogs.pedido_resumo_dialog import PedidoResumoDialog
			dialog = PedidoResumoDialog(pedido_id, self)
			dialog.exec()
		except Exception as e:
			print(f"Erro ao visualizar pedido: {e}")
			from PyQt6.QtWidgets import QMessageBox
			QMessageBox.critical(self, "Erro", f"Erro ao abrir resumo do pedido: {e}")

	def editar_pedido(self, pedido_id: int):
		modal = NovoPedidosModal(self)
		modal.pedido_salvo.connect(lambda: self._on_pedido_editado(pedido_id))
		modal.abrir_modal_edicao(pedido_id)
	
	def _on_pedido_editado(self, pedido_id: int):
		"""Callback quando um pedido é editado"""
		signals = get_signals()
		signals.pedido_editado.emit(pedido_id)

	def excluir_pedido(self, pedido_id: int):
		"""Exclui pedido com confirmação"""
		from PyQt6.QtWidgets import QMessageBox
		
		# Mostrar confirmação ANTES de deletar
		reply = QMessageBox.question(
			self,
			"⚠️ Confirmar Exclusão",
			f"Tem certeza que deseja excluir o pedido #{pedido_id}?\n\n"
			f"⚠️ O pedido será movido para a lixeira!\n"
			f"Você poderá recuperá-lo dentro de 30 dias.\n"
			f"Após esse período, será removido permanentemente.",
			QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
			QMessageBox.StandardButton.No
		)
		
		if reply != QMessageBox.StandardButton.Yes:
			return  # Cancelou
		
		try:
			if hasattr(db_manager, "deletar_pedido"):
				db_manager.deletar_pedido(pedido_id)
			else:
				db_manager.deletar_ordem(pedido_id)
			
			# Emitir sinal de exclusão
			signals = get_signals()
			signals.pedido_excluido.emit(pedido_id)
			
			# Mostrar mensagem de sucesso
			QMessageBox.information(
				self,
				"✅ Sucesso",
				f"Pedido #{pedido_id} movido para a lixeira!\n\n"
				f"Você pode recuperá-lo em Backup → Registros Deletados."
			)
		except Exception as e:
			QMessageBox.critical(self, "❌ Erro", f"Erro ao excluir pedido: {e}")
			print(f"Erro ao excluir: {e}")

	def atualizar_status(self, pedido_id: int, novo_status: str):
		try:
			db_manager.atualizar_status_pedido(pedido_id, novo_status)
			
			# Emitir sinal de atualização de status
			signals = get_signals()
			signals.pedido_status_atualizado.emit(pedido_id, novo_status)
		except Exception as e:
			print(f"Erro ao atualizar status: {e}")

	def _filtrar_pedidos(self):
		"""Filtra pedidos baseado no status selecionado"""
		try:
			status_selecionado = self.filtro_status.currentText()
			self.status_filter = status_selecionado.lower()
			self.carregar_dados(force_refresh=True)
		except Exception as e:
			print(f"Erro ao filtrar pedidos: {e}")
	
	def _on_search_changed(self, text):
		"""Chamado quando o texto de busca muda"""
		self.search_text = text.lower().strip()
		self._aplicar_filtros()
	
	def _limpar_filtros(self):
		"""Limpa todos os filtros aplicados"""
		self.search_input.clear()
		self.filtro_status.setCurrentIndex(0)  # "Todos"
		self.search_text = ""
		self._aplicar_filtros()
	
	def _aplicar_filtros(self):
		"""Aplica todos os filtros combinados"""
		try:
			self.carregar_dados(force_refresh=True)
		except Exception as e:
			print(f"Erro ao aplicar filtros: {e}")

	def _build_cards(self):
		"""Constrói os cards dos pedidos - alias para carregar_dados"""
		try:
			self.carregar_dados()
		except Exception as e:
			print(f"Erro ao construir cards: {e}")

	def refresh_data(self):
		self.carregar_dados(force_refresh=True)
	
	def resizeEvent(self, event):
		"""Recalcula o layout quando a janela é redimensionada"""
		super().resizeEvent(event)
		# Agendar recálculo do layout após um pequeno delay
		if hasattr(self, 'resize_timer'):
			self.resize_timer.stop()
		
		from PyQt6.QtCore import QTimer
		self.resize_timer = QTimer()
		self.resize_timer.setSingleShot(True)
		self.resize_timer.timeout.connect(self._recalcular_layout)
		self.resize_timer.start(100)  # 100ms de delay
	
	def _recalcular_layout(self):
		"""Recalcula o layout dos cards"""
		try:
			self.carregar_dados(force_refresh=False)
		except Exception as e:
			print(f"Erro ao recalcular layout: {e}")