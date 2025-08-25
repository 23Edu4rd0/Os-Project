from .__init__ import PedidosModal

def _limpar_campos_cliente(self):
    try:
        self.campos['nome_cliente'].clear()
    except Exception:
        pass
    try:
        self.campos['telefone_cliente'].clear()
    except Exception:
        pass
    try:
        self.campos['cpf_cliente'].clear()
    except Exception:
        pass
    try:
        self.campos['endereco_cliente'].clear()
    except Exception:
        pass
    try:
        self.campos['nome_cliente'].setFocus()
    except Exception:
        pass
