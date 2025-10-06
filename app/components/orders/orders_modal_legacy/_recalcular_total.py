from .__init__ import PedidosModal, _recalcular_total_part

def _recalcular_total(self):
    if _recalcular_total_part:
        _recalcular_total_part(self)
        return
    # ...existing code for recalcular_total...
