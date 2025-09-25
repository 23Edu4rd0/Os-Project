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
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from app.signals import get_signals

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

		# Helpers
		self.card_manager = PedidosCard(self)
		
		# Conectar sinais para atualizações em tempo real
		self._conectar_sinais()

		# UI
		self._setup_interface()
	
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
		titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
		header_layout.addWidget(titulo)
		
		header_layout.addStretch()
		
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
		
		# Filtro modernizado
		filtros_container = QFrame()
		filtros_container.setStyleSheet("""
			QFrame {
				background: rgba(255, 255, 255, 0.05);
				border-radius: 8px;
			}
		""")
		filtros_layout = QHBoxLayout(filtros_container)
		filtros_layout.setContentsMargins(15, 8, 15, 8)
		
		status_label = QLabel("Status:")
		status_label.setStyleSheet("color: #cccccc; font-size: 12px;")
		filtros_layout.addWidget(status_label)
		
		self.filtro_status = QComboBox()
		self.filtro_status.addItems(["Todos", "Pendente", "Em Andamento", "Concluído", "Cancelado"])
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
		filtros_layout.addWidget(self.filtro_status)
		
		filtros_layout.addStretch()
		
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

		# Filtrar
		if self.status_filter != "todos":
			# Tratar sinônimos: 'entregue' ~ 'concluído'
			filtro = self.status_filter.lower()
			if filtro in ("entregue", "concluído", "concluido"):
				pedidos = [p for p in pedidos if (p.get("status", "") or "").lower() in ("entregue", "concluído", "concluido") or "conclu" in (p.get("status", "") or "").lower()]
			else:
				pedidos = [p for p in pedidos if (p.get("status", "") or "").lower() == filtro]
		else:
			# 'todos' deve ocultar pedidos concluídos/entregues
			def _is_concluido(status: str) -> bool:
				st = (status or "").lower()
				return (st == "entregue") or ("conclu" in st)
			pedidos = [p for p in pedidos if not _is_concluido(p.get("status", ""))]

		# Render
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
			pedidos = sorted(pedidos, key=_dias_restantes)
		except Exception:
			pass

		self._limpar_layout()
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

	def _mostrar_msg(self, texto: str, cor: str = "#cccccc"):
		lbl = QLabel(texto)
		lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
		lbl.setStyleSheet(f"color: {cor}; font-size: 15px; padding: 40px;")
		self.scroll_layout.addWidget(lbl)

	def _criar_grid_cards(self, pedidos):
		grid = QWidget()
		grid_l = QGridLayout(grid)
		grid_l.setSpacing(12)  # Espaçamento reduzido para permitir mais cards
		# Margens ajustadas para melhor uso do espaço
		try:
			grid_l.setContentsMargins(10, 10, 10, 16)  # Margens reduzidas
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

		# Calcular colunas dinamicamente baseado na largura da tela
		largura_disponivel = max(400, self.width() - 30)  # Margem de segurança menor
		largura_card = 300  # Largura do card reduzida ainda mais
		espacamento = 10   # Espaçamento entre cards menor
		
		# Forçar 4 colunas se a largura for maior que 1280px
		if self.width() >= 1280:
			cols = 4
		else:
			cols = max(1, (largura_disponivel + espacamento) // (largura_card + espacamento))
			cols = min(cols, 4)  # Limitar a 4 conforme solicitado
		
		print(f"Largura disponível: {largura_disponivel}px, Colunas calculadas: {cols}")
		
		# Configurar stretch para ocupar toda a largura
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
		try:
			if hasattr(db_manager, "deletar_pedido"):
				db_manager.deletar_pedido(pedido_id)
			else:
				db_manager.deletar_ordem(pedido_id)
			
			# Emitir sinal de exclusão
			signals = get_signals()
			signals.pedido_excluido.emit(pedido_id)
		except Exception as e:
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
			self.carregar_dados(force_refresh=True)
		except Exception as e:
			print(f"Erro ao filtrar pedidos: {e}")

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