"""Wrapper: re-exporta a implementação modular de PedidosModal.

Este arquivo apenas re-exporta a classe `PedidosModal` e helpers contidos no
pacote `pedidosModal`. Mantê-lo simples evita duplicação e resolve erros de
import relacionados a definições legadas (por exemplo, NameError: QDialog is
not defined) que ocorriam quando havia código UI direto neste arquivo.
"""

from .pedidosModal import PedidosModal, abrir_modal_novo, abrir_modal_edicao

__all__ = ["PedidosModal", "abrir_modal_novo", "abrir_modal_edicao"]
