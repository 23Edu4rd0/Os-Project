from .__init__ import PedidosModal

def _remove_produto(self, index: int):
    if 0 <= index < len(self.produtos_list):
        self.produtos_list.pop(index)
        self._refresh_produtos_ui()
