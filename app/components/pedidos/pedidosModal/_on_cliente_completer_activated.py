from .__init__ import PedidosModal

def _on_cliente_completer_activated(self, texto: str):
    key_cli = self._resolver_cliente(texto)
    if key_cli:
        key, cli = key_cli
        try:
            telefone_fmt = self._format_phone(cli.get('telefone', ''))
            display = f"{cli.get('nome','')} | {telefone_fmt}" if telefone_fmt else cli.get('nome','')
            self.campos['nome_cliente'].setText(display)
        except Exception:
            pass
        self._preencher_dados_cliente(cli)
