"""Wrapper: re-exports the modular PedidosModal implementation.

This file only re-exports the `PedidosModal` class and helpers contained in the
`orders_modal_legacy` package. Keeping it simple avoids duplication and resolves
import errors related to legacy definitions (e.g., NameError: QDialog is
not defined) that occurred when there was direct UI code in this file.
"""

from .orders_modal_legacy import PedidosModal, abrir_modal_novo, abrir_modal_edicao

__all__ = ["PedidosModal", "abrir_modal_novo", "abrir_modal_edicao"]
