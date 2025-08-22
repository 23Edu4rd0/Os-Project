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
	QWidget,
	QFrame,
	QGridLayout,
	QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from database import db_manager  # singleton
from .pedidos_card import PedidosCard
from .pedidos_modal import PedidosModal


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
		self.modal_manager = PedidosModal(self)

		# UI
		self._setup_interface()
		# Mostrar estado de carregamento inicial (será substituído após carregar)
		self._mostrar_msg("Carregando pedidos...", cor="#bbbbbb")
		self.carregar_dados(force_refresh=True)

	def _setup_interface(self):
		layout = QVBoxLayout(self)
		layout.setContentsMargins(10, 10, 10, 10)
		layout.setSpacing(10)

		top = QFrame()
		top_l = QHBoxLayout(top)
		top_l.setContentsMargins(5, 5, 5, 5)

		lbl = QLabel("Filtrar:")
		lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
		top_l.addWidget(lbl)

		self.status_combo = QComboBox()
		self.status_combo.addItems(["todos", "em produção", "enviado", "entregue", "cancelado"])
		self.status_combo.currentTextChanged.connect(self._on_status_changed)
		top_l.addWidget(self.status_combo)

		btn_refresh = QPushButton("🔄 Atualizar")
		btn_refresh.clicked.connect(lambda: self.carregar_dados(force_refresh=True))
		top_l.addWidget(btn_refresh)

		btn_novo = QPushButton("➕ Novo Pedido")
		btn_novo.clicked.connect(self.novo_pedido)
		btn_novo.setStyleSheet(
			"""
			QPushButton { background-color: #28a745; color: #fff; padding: 8px 14px; border-radius: 6px; }
			QPushButton:hover { background-color: #218838; }
			"""
		)
		top_l.addWidget(btn_novo)

		top_l.addStretch()
		layout.addWidget(top)

		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
		self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

		self.scroll_widget = QWidget()
		self.scroll_layout = QVBoxLayout(self.scroll_widget)
		# Reduzir margem esquerda para aproximar a 1ª OS da borda esquerda
		self.scroll_layout.setContentsMargins(4, 10, 10, 10)
		self.scroll_layout.setSpacing(14)
		self.scroll_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

		self.scroll_area.setWidget(self.scroll_widget)
		self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		layout.addWidget(self.scroll_area)

		self.setStyleSheet(
			"""
			QWidget { background-color: #2d2d2d; color: #ffffff; }
			QComboBox { background-color: #404040; border: 1px solid #606060; border-radius: 4px; padding: 6px; }
			QPushButton { background-color: #0d7377; color: white; border: none; border-radius: 6px; padding: 8px 14px; }
			QPushButton:hover { background-color: #0a5d61; }
			QScrollArea { border: none; }
			"""
		)

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
			pedidos = [p for p in pedidos if p.get("status", "").lower() == self.status_filter.lower()]

		# Render
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

	# Ações públicas ---------------------------------------------------------
	def novo_pedido(self):
		self.modal_manager.pedido_salvo.connect(lambda: self.carregar_dados(force_refresh=True))
		self.modal_manager.abrir_modal_novo()

	def editar_pedido(self, pedido_id: int):
		self.modal_manager.pedido_salvo.connect(lambda: self.carregar_dados(force_refresh=True))
		self.modal_manager.abrir_modal_edicao(pedido_id)

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

	def refresh_data(self):
		self.carregar_dados(force_refresh=True)