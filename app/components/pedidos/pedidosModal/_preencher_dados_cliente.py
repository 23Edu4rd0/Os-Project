from .__init__ import PedidosModal

def _preencher_dados_cliente(self, cli: dict):
    try:
        self.campos['telefone_cliente'].setText(str(cli.get('telefone', '')))
    except Exception:
        pass
    try:
        self.campos['cpf_cliente'].setText(str(cli.get('cpf', '')))
    except Exception:
        pass
    try:
        rua = cli.get('rua', '')
        numero = cli.get('numero', '')
        endereco = f"{rua}, {numero}" if rua and numero else (rua or numero or '')
        self.campos['endereco_cliente'].setText(str(endereco))
    except Exception:
        pass
