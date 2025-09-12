def limpar_campos_produto(self):
    from ._limpar_campos_produto import limpar_campos_produto as _limpar_campos_produto
    _limpar_campos_produto(self)
def _limpar_campos_produto(self):
    if 'nome_produto' in self.campos:
        self.campos['nome_produto'].clear()
    if 'valor_produto' in self.campos:
        self.campos['valor_produto'].clear()
    if 'categoria_produto' in self.campos:
        self.campos['categoria_produto'].setCurrentIndex(0)
from ..modal_parts.cliente import criar_secao_cliente as _criar_secao_cliente_part
from ..modal_parts.produtos import criar_secao_produtos as _criar_secao_produtos_part
from ..modal_parts.pagamento import criar_secao_pagamento as _criar_secao_pagamento_part
from ..modal_parts.resumo import criar_secao_resumo as _criar_secao_resumo_part, recalcular_total as _recalcular_total_part
from ..modal_parts.botoes import criar_botoes as _criar_botoes_part
# -*- coding: utf-8 -*-
"""
Classe principal PedidosModal e imports compartilhados
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QTextEdit, QComboBox,
    QGroupBox, QFormLayout, QScrollArea, QWidget,
    QFrame, QMessageBox, QCompleter, QListWidget,
    QListWidgetItem)
from PyQt6.QtCore import Qt, QStringListModel, pyqtSignal
from PyQt6.QtGui import QFont

try:
    from documents.os_pdf import OrdemServicoPDF
except ModuleNotFoundError:
    import sys, pathlib
    ROOT = pathlib.Path(__file__).resolve().parents[3]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from documents.os_pdf import OrdemServicoPDF  # type: ignore

try:
    from app.numero_os import Contador
except ModuleNotFoundError:
    import sys, pathlib
    ROOT = pathlib.Path(__file__).resolve().parents[3]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from app.numero_os import Contador  # type: ignore

from database import db_manager
from ..pedido_form_model import PedidoFormModel

# Modular parts (imported as needed)
try:
    from .modal_parts.cliente import criar_secao_cliente as _criar_secao_cliente_part
    from .modal_parts.produtos import criar_secao_produtos as _criar_secao_produtos_part
    from .modal_parts.pagamento import criar_secao_pagamento as _criar_secao_pagamento_part
    from .modal_parts.resumo import criar_secao_resumo as _criar_secao_resumo_part, recalcular_total as _recalcular_total_part
    from .modal_parts.botoes import criar_botoes as _criar_botoes_part
except Exception:
    try:
        from app.components.pedidos.modal_parts.cliente import criar_secao_cliente as _criar_secao_cliente_part
        from app.components.pedidos.modal_parts.produtos import criar_secao_produtos as _criar_secao_produtos_part
        from app.components.pedidos.modal_parts.pagamento import criar_secao_pagamento as _criar_secao_pagamento_part
        from app.components.pedidos.modal_parts.resumo import criar_secao_resumo as _criar_secao_resumo_part, recalcular_total as _recalcular_total_part
        from app.components.pedidos.modal_parts.botoes import criar_botoes as _criar_botoes_part
    except Exception:
        _criar_secao_cliente_part = None
        _criar_secao_produtos_part = None
        _criar_secao_pagamento_part = None
        _criar_secao_resumo_part = None
        _recalcular_total_part = None
        _criar_botoes_part = None

class PedidosModal(QDialog):
    def _criar_secao_cliente(self, layout, pedido_data):
        from ._criar_secao_cliente import _criar_secao_cliente
        return _criar_secao_cliente(self, layout, pedido_data)

    def _criar_secao_produtos(self, layout, pedido_data):
        from ._criar_secao_produtos import _criar_secao_produtos
        return _criar_secao_produtos(self, layout, pedido_data)

    def _carregar_produtos(self):
        from ._carregar_produtos import _carregar_produtos
        return _carregar_produtos(self)

    def _montar_produtos_completer(self, categoria=None):
        from ._montar_produtos_completer import _montar_produtos_completer
        return _montar_produtos_completer(self, categoria)

    def _filtrar_produtos_por_categoria(self, cat):
        from ._filtrar_produtos_por_categoria import _filtrar_produtos_por_categoria
        return _filtrar_produtos_por_categoria(self, cat)

    def _on_produto_completer_activated(self, texto):
        from ._on_produto_completer_activated import _on_produto_completer_activated
        return _on_produto_completer_activated(self, texto)

    def _on_produto_text_changed(self, texto):
        from ._on_produto_text_changed import _on_produto_text_changed
        return _on_produto_text_changed(self, texto)

    def _criar_secao_pagamento(self, layout, pedido_data):
        from ._criar_secao_pagamento import _criar_secao_pagamento
        return _criar_secao_pagamento(self, layout, pedido_data)

    def _criar_secao_resumo(self, layout):
        from ._criar_secao_resumo import _criar_secao_resumo
        return _criar_secao_resumo(self, layout)

    def _criar_botoes(self, layout, numero_os, pedido_data):
        from ._criar_botoes import _criar_botoes
        return _criar_botoes(self, layout, numero_os, pedido_data)

    def _salvar_pedido(self, numero_os=None, pedido_data=None):
        from ._salvar_pedido import _salvar_pedido
        return _salvar_pedido(self, numero_os, pedido_data)

    def _format_phone(self, telefone):
        from ._format_phone import _format_phone
        return _format_phone(self, telefone)

    def _on_cliente_completer_activated(self, texto):
        from ._on_cliente_completer_activated import _on_cliente_completer_activated
        return _on_cliente_completer_activated(self, texto)

    def _refresh_produtos_ui(self):
        from ._refresh_produtos_ui import _refresh_produtos_ui
        return _refresh_produtos_ui(self)

    def _add_produto(self):
        from ._add_produto import _add_produto
        return _add_produto(self)

    def _editar_produto(self, index):
        from ._editar_produto import _editar_produto
        return _editar_produto(self, index)

    def _limpar_campos_cliente(self):
        from ._limpar_campos_cliente import _limpar_campos_cliente
        return _limpar_campos_cliente(self)

    def _limpar_campos_produto(self):
        from ._limpar_campos_produto import limpar_campos_produto as _limpar_campos_produto
        return _limpar_campos_produto(self)

    def _remove_produto(self, index):
        from ._remove_produto import _remove_produto
        return _remove_produto(self, index)

    def _recalcular_total(self):
        from ._recalcular_total import _recalcular_total
        return _recalcular_total(self)

    def _on_cliente_selecionado(self, texto):
        from ._on_cliente_selecionado import _on_cliente_selecionado
        return _on_cliente_selecionado(self, texto)

    def _preencher_dados_cliente(self, cli):
        from ._preencher_dados_cliente import _preencher_dados_cliente
        return _preencher_dados_cliente(self, cli)

    def _resolver_cliente(self, texto):
        from ._resolver_cliente import _resolver_cliente
        return _resolver_cliente(self, texto)

    def _gerar_pdf(self, pedido_data):
        from ._gerar_pdf import _gerar_pdf
        return _gerar_pdf(self, pedido_data)

    def _aplicar_estilo(self):
        from ._aplicar_estilo import _aplicar_estilo
        return _aplicar_estilo(self)
    def _criar_header(self, layout, numero_os, is_edit):
        from ._criar_header import _criar_header
        return _criar_header(self, layout, numero_os, is_edit)
    def _carregar_clientes(self):
        from ._carregar_clientes import _carregar_clientes
        return _carregar_clientes(self)

    def _criar_modal_completo(self, pedido_data=None, cliente_fixo=False, nome_cliente_label=None):
        from ._criar_modal_completo import _criar_modal_completo
        return _criar_modal_completo(self, pedido_data, cliente_fixo=cliente_fixo, nome_cliente_label=nome_cliente_label)
    """Gerencia os modais de pedidos"""
    pedido_salvo = pyqtSignal()
    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        self.model = PedidoFormModel()
        self.clientes_dict = {}
        self.produtos_dict = {}

    def abrir_modal_novo(self):
        from .abrir_modal_novo import abrir_modal_novo
        return abrir_modal_novo(self)

    def abrir_modal_edicao(self, pedido_id):
        from .abrir_modal_edicao import abrir_modal_edicao
        return abrir_modal_edicao(self, pedido_id)
