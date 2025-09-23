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

		# listen to status updates so UI can refresh when statuses change
		try:
			sig = get_signals()
			sig.statuses_updated.connect(lambda: self._on_statuses_updated())
		except Exception:
			pass

		# Estado
		self.status_filter = "todos"
		self._cache_pedidos = None
		self._cache_timestamp = 0.0
		self._cache_timeout = 20  # segundos

		# Helpers
		self.card_manager = PedidosCard(self)
		# Removido modal_manager fixo; agora cada modal é criado sob demanda

		# UI
		self._setup_interface()
		# Mostrar estado de carregamento inicial (será substituído após carregar)
		self._mostrar_msg("Carregando pedidos...", cor="#bbbbbb")
		self.carregar_dados(force_refresh=True)

	def _setup_interface(self):
		layout = QVBoxLayout(self)
		layout.setContentsMargins(10, 10, 10, 10)
		layout.setSpacing(10)

		# Header muito simples
		header_layout = QHBoxLayout()
		
		titulo = QLabel("Pedidos")
		titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
		header_layout.addWidget(titulo)
		
		header_layout.addStretch()
		
		# Botão novo pedido muito simples
		self.btn_novo = QPushButton("Novo Pedido")
		self.btn_novo.setStyleSheet("""
			QPushButton {
				background-color: #555555;
				color: white;
				border: 1px solid #666666;
				padding: 8px 15px;
				border-radius: 3px;
				font-size: 11px;
			}
			QPushButton:hover {
				background-color: #666666;
			}
		""")
		self.btn_novo.clicked.connect(self.novo_pedido)
		header_layout.addWidget(self.btn_novo)
		
		layout.addLayout(header_layout)
		
		# Filtro muito simples
		filtros_layout = QHBoxLayout()
		
		filtros_layout.addWidget(QLabel("Status:"))
		
		self.filtro_status = QComboBox()
		self.filtro_status.addItems(["Todos", "Pendente", "Em Andamento", "Concluído", "Cancelado"])
		self.filtro_status.setStyleSheet("""
			QComboBox {
				background-color: #404040;
				color: white;
				border: 1px solid #555555;
				padding: 6px;
				border-radius: 3px;
			}
		""")
		self.filtro_status.currentTextChanged.connect(self._filtrar_pedidos)
		filtros_layout.addWidget(self.filtro_status)
		
		filtros_layout.addStretch()
		
		layout.addLayout(filtros_layout)
		
		# Área de scroll muito simples
		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setStyleSheet("background-color: #2d2d2d; border: 1px solid #555555;")
		
		self.scroll_widget = QWidget()
		self.scroll_layout = QVBoxLayout(self.scroll_widget)
		self.scroll_layout.setContentsMargins(5, 5, 5, 5)
		self.scroll_layout.setSpacing(8)
		
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
		grid_l.setSpacing(14)
		# Margens assimétricas: menos à esquerda, mais à direita
		# para que a última coluna não fique colada na parede
		try:
			# Diminuir ainda mais a margem esquerda (zero) e manter folga maior à direita
			grid_l.setContentsMargins(0, 0, 44, 0)
		except Exception:
			pass

		# Conectar sinais uma vez
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
		self.card_manager.editar_clicked.connect(self.editar_pedido)
		self.card_manager.excluir_clicked.connect(self.excluir_pedido)
		self.card_manager.status_changed.connect(self.atualizar_status)

		cols = 3
		# Adicionar uma coluna extra de "respiro" à direita
		try:
			grid_l.setColumnStretch(cols, 1)
		except Exception:
			pass
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

		self.scroll_layout.addWidget(grid)
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
		modal.pedido_salvo.connect(lambda: self.carregar_dados(force_refresh=True))
		modal._criar_modal_completo()

	def editar_pedido(self, pedido_id: int):
		modal = NovoPedidosModal(self)
		modal.pedido_salvo.connect(lambda: self.carregar_dados(force_refresh=True))
		modal.abrir_modal_edicao(pedido_id)

	def excluir_pedido(self, pedido_id: int):
		try:
			if hasattr(db_manager, "deletar_pedido"):
				db_manager.deletar_pedido(pedido_id)
			else:
				db_manager.deletar_ordem(pedido_id)
			self.carregar_dados(force_refresh=True)
		except Exception as e:
			print(f"Erro ao excluir: {e}")

	def atualizar_status(self, pedido_id: int, novo_status: str):
		try:
			db_manager.atualizar_status_pedido(pedido_id, novo_status)
			self.carregar_dados(force_refresh=True)
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