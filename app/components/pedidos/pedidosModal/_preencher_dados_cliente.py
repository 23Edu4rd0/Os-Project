from .__init__ import PedidosModal

def _preencher_dados_cliente(self, cli: dict):
    # When filling the cliente fields programmatically, block signals to avoid
    # triggering textChanged -> _on_cliente_selecionado recursion.
    try:
        widget = self.campos.get('nome_cliente')
        if widget is not None:
            was_blocked = widget.blockSignals(True)
            widget.setText(str(cli.get('nome', '')))
            widget.blockSignals(was_blocked)
    except Exception:
        pass
    try:
        widget = self.campos.get('telefone_cliente')
        if widget is not None:
            was_blocked = widget.blockSignals(True)
            widget.setText(str(cli.get('telefone', '')))
            widget.blockSignals(was_blocked)
    except Exception:
        pass
    try:
        widget = self.campos.get('cpf_cliente')
        if widget is not None:
            was_blocked = widget.blockSignals(True)
            widget.setText(str(cli.get('cpf', '')))
            widget.blockSignals(was_blocked)
    except Exception:
        pass
    try:
        rua = cli.get('rua', '')
        numero = cli.get('numero', '')
        endereco = f"{rua}, {numero}" if rua and numero else (rua or numero or '')
        widget = self.campos.get('endereco_cliente')
        if widget is not None:
            was_blocked = widget.blockSignals(True)
            widget.setText(str(endereco))
            widget.blockSignals(was_blocked)
    except Exception:
        pass
