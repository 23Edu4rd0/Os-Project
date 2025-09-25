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
            # Priorizar CNPJ se existe, senão CPF
            documento = cli.get('cnpj', '') or cli.get('cpf', '')
            widget.setText(str(documento))
            widget.blockSignals(was_blocked)
    except Exception:
        pass
    try:
        # Montar endereço completo
        rua = cli.get('rua', '')
        numero = cli.get('numero', '')
        bairro = cli.get('bairro', '')
        cidade = cli.get('cidade', '')
        estado = cli.get('estado', '')
        
        endereco_parts = []
        if rua:
            endereco_parts.append(rua)
        if numero:
            endereco_parts.append(numero)
        if bairro:
            endereco_parts.append(bairro)
        if cidade:
            endereco_parts.append(cidade)
        if estado:
            endereco_parts.append(estado)
        
        endereco = ', '.join(endereco_parts) if endereco_parts else ''
        
        widget = self.campos.get('endereco_cliente')
        if widget is not None:
            was_blocked = widget.blockSignals(True)
            widget.setText(str(endereco))
            widget.blockSignals(was_blocked)
    except Exception:
        pass
