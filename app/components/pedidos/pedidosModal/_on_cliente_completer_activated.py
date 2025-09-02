from .__init__ import PedidosModal

def _on_cliente_completer_activated(self, texto: str):
    key_cli = self._resolver_cliente(texto)
    if key_cli:
        key, cli = key_cli
        try:
            telefone_fmt = self._format_phone(cli.get('telefone', ''))
            display = f"{cli.get('nome','')} | {telefone_fmt}" if telefone_fmt else cli.get('nome','')
            widget = self.campos.get('nome_cliente')
            if widget is not None:
                was_blocked = widget.blockSignals(True)
                widget.setText(display)
                widget.blockSignals(was_blocked)
        except Exception:
            pass
        self._preencher_dados_cliente(cli)
