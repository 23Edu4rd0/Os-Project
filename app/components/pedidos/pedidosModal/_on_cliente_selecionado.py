from .__init__ import PedidosModal

def _on_cliente_selecionado(self, texto):
    key_cli = self._resolver_cliente(texto)
    if not key_cli:
        return
    key, cliente = key_cli
    try:
        telefone_fmt = self._format_phone(cliente.get('telefone', ''))
        display = f"{cliente.get('nome','')} | {telefone_fmt}" if telefone_fmt else cliente.get('nome','')
        self.campos['nome_cliente'].setText(str(display))
    except Exception:
        pass
    self._preencher_dados_cliente(cliente)
