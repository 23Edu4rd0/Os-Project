"""
Módulo que define o widget do cartão de pedido na aplicação de Ordem de Serviço (OS).

Este módulo contém a classe `PedidoCard`, que representa um cartão de pedido na interface
gráfica da aplicação. O cartão exibe informações relevantes sobre o pedido e permite
interações como edição, exclusão e envio de mensagens pelo WhatsApp.

A classe `PedidoCard` emite sinais para notificar mudanças de status e atualização de dados
do pedido.

"""

from datetime import datetime, date
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QMenu)

class PedidoCard(QWidget):
    """Classe que representa um cartão de pedido na interface da aplicação."""

    # Sinal emitido quando o status do pedido é alterado
    status_changed = pyqtSignal(object, str)  # (pedido_id, novo_status)

    def __init__(self, pedido: dict, *args, **kwargs):
        """Inicializa o cartão de pedido com as informações fornecidas."""
        super().__init__(*args, **kwargs)
        self.pedido = pedido

        # Layout principal do cartão
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(10, 10, 10, 10)
        layout_principal.setSpacing(10)

        # --- Cabeçalho do cartão ---
        layout_cabecalho = QHBoxLayout()
        layout_principal.addLayout(layout_cabecalho)

        # Label com o número do pedido
        self.lbl_numero = QLabel(f"Pedido #{self.pedido.get('id')}")
        self.lbl_numero.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout_cabecalho.addWidget(self.lbl_numero)

        # --- Informações do pedido ---
        layout_info = QVBoxLayout()
        layout_principal.addLayout(layout_info)

        # Label com o status do pedido
        self.lbl_status = QLabel(f"Status: {self.pedido.get('status', '')}")
        self.lbl_status.setStyleSheet("color: #cfcfcf;")
        layout_info.addWidget(self.lbl_status)

        # --- Substitui "Criada em" por label de prazo ---
        self.lbl_deadline = QLabel()
        self.lbl_deadline.setStyleSheet("color: #cfcfcf;")
        layout_info.addWidget(self.lbl_deadline)

        # --- Rodapé de botões ---
        layout_rodape = QHBoxLayout()
        layout_principal.addLayout(layout_rodape)

        # Botão para editar o pedido
        self.btn_editar = QPushButton("Editar")
        try:
            cursor_shape = Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else getattr(Qt, 'PointingHandCursor')
        except Exception:
            cursor_shape = getattr(Qt, 'PointingHandCursor', 0)
        self.btn_editar.setCursor(cursor_shape)
        # ...connect self.btn_editar...

        # Botão para excluir o pedido
        self.btn_excluir = QPushButton("Excluir")
        try:
            cursor_shape = Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else getattr(Qt, 'PointingHandCursor')
        except Exception:
            cursor_shape = getattr(Qt, 'PointingHandCursor', 0)
        self.btn_excluir.setCursor(cursor_shape)
        # ...connect self.btn_excluir...

        # Botão para enviar mensagem pelo WhatsApp
        self.btn_whatsapp = QPushButton("WhatsApp")
        try:
            cursor_shape = Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else getattr(Qt, 'PointingHandCursor')
        except Exception:
            cursor_shape = getattr(Qt, 'PointingHandCursor', 0)
        self.btn_whatsapp.setCursor(cursor_shape)
        # ...connect self.btn_whatsapp...

        # Botão para alterar o status do pedido
        self.btn_status = QPushButton("Status")
        try:
            cursor_shape = Qt.CursorShape.PointingHandCursor if hasattr(Qt, 'CursorShape') else getattr(Qt, 'PointingHandCursor')
        except Exception:
            cursor_shape = getattr(Qt, 'PointingHandCursor', 0)
        self.btn_status.setCursor(cursor_shape)
        self.btn_status.clicked.connect(self._open_status_menu)

        # Adiciona os botões ao layout do rodapé
        layout_rodape.addWidget(self.btn_editar)
        layout_rodape.addWidget(self.btn_excluir)
        layout_rodape.addWidget(self.btn_status)
        layout_rodape.addWidget(self.btn_whatsapp)

        # Atualiza os rótulos com as informações do pedido
        self._refresh_deadline_label()
        self._refresh_status_label()

    # --- Novos métodos ---
    def _parse_data_combinada(self):
        """Obtém a data combinada (ou prevista/entrega) como date."""
        valor = (
            self.pedido.get("data_combinada")
            or self.pedido.get("data_prevista")
            or self.pedido.get("data_entrega")
        )
        if not valor:
            return None
        if isinstance(valor, date):
            return valor
        if isinstance(valor, datetime):
            return valor.date()
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(str(valor), fmt).date()
            except Exception:
                pass
        try:
            return datetime.fromisoformat(str(valor)).date()
        except Exception:
            return None

    def _refresh_deadline_label(self):
        """Atualiza o rótulo da data de entrega do pedido."""
        due = self._parse_data_combinada()
        if not due:
            self.lbl_deadline.setText("Entrega: data não informada")
            self.lbl_deadline.setStyleSheet("color: #ffb74d;")
            return

        today = date.today()
        delta = (due - today).days
        due_str = due.strftime("%d/%m/%Y")

        if delta > 1:
            txt = f"Entrega: faltam {delta} dias ({due_str})"
            color = "#cfcfcf"
        elif delta == 1:
            txt = f"Entrega: amanhã ({due_str})"
            color = "#ffd166"
        elif delta == 0:
            txt = f"Entrega: hoje ({due_str})"
            color = "#ffd166"
        else:
            txt = f"Entrega: atrasado há {abs(delta)} dias ({due_str})"
            color = "#ff6b6b"

        self.lbl_deadline.setText(txt)
        self.lbl_deadline.setStyleSheet(f"color: {color};")

    def _open_status_menu(self):
        """Abre o menu para seleção de novo status do pedido."""
        menu = QMenu(self)
        opcoes = ["EM ANDAMENTO", "EM PRODUÇÃO", "ENVIADO", "CONCLUÍDO"]
        actions = [menu.addAction(op) for op in opcoes]
        act = menu.exec(self.btn_status.mapToGlobal(self.btn_status.rect().bottomLeft()))
        if act:
            self._set_status(act.text())

    def _set_status(self, status: str):
        """Define o novo status para o pedido e atualiza o cartão."""
        self.pedido["status"] = status
        # atualiza visual no card
        self._refresh_status_label()
        # notifica o container para persistir e re-filtrar
        pid = self.pedido.get("id") or self.pedido.get("numero") or self.pedido.get("os_id")
        self.status_changed.emit(pid, status)

    def _refresh_status_label(self):
        """Atualiza o rótulo de status do pedido."""
        self.lbl_status.setText(f"Status: {self.pedido.get('status', '')}")

    # Caso os dados do card mudem externamente:
    def refresh(self, novo_pedido: dict | None = None):
        """Atualiza as informações do cartão com os dados do novo pedido."""
        if novo_pedido:
            self.pedido.update(novo_pedido)
        self._refresh_deadline_label()
        self._refresh_status_label()
        # ...existing code...