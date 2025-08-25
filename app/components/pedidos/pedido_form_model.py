class PedidoFormModel:
    """Model para armazenar dados temporários do formulário de OS."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.produtos_list = []
        self.campos = {}  # Só widgets
        self.dados = {}   # Dados brutos

    def preencher(self, dados):
        # Guarda dados brutos para uso posterior, mas não sobrescreve self.campos (widgets)
        self.dados = {
            'nome_cliente': dados.get('nome_cliente', ''),
            'telefone_cliente': dados.get('telefone_cliente', ''),
            'cpf_cliente': dados.get('cpf_cliente', ''),
            'endereco_cliente': dados.get('endereco_cliente', ''),
            'entrada': f"{float(dados.get('valor_entrada', 0) or 0):.2f}",
            'frete': f"{float(dados.get('frete', 0) or 0):.2f}",
            'desconto': f"{float(dados.get('desconto', 0) or 0):.2f}",
            'status': dados.get('status', 'em produção'),
            'forma_pagamento': dados.get('forma_pagamento', 'pix'),
            'prazo_entrega': str(int(dados.get('prazo', 0) or 0)),
            'cor': dados.get('cor', ''),
            'reforco': 'sim' if str(dados.get('reforco', False)).lower() in ('1','true','sim','yes') else 'não',
            'valor_total': f"{float(dados.get('valor_total', dados.get('valor_produto', 0)) or 0):.2f}",
        }
        # Produtos
        self.produtos_list = []
        detalhes = dados.get('detalhes_produto', '') or ''
        for linha in [l.strip() for l in detalhes.replace('\\n', '\n').split('\n') if l.strip() and not l.strip().startswith('-')]:
            if ' - R$ ' in linha:
                try:
                    desc, valtxt = linha.rsplit(' - R$ ', 1)
                    valtxt_original = valtxt.strip()
                    valtxt = valtxt_original
                    if '.' in valtxt and ',' in valtxt:
                        # Ex: 1.234,56 -> 1234.56
                        valtxt = valtxt.replace('.', '').replace(',', '.')
                    elif ',' in valtxt:
                        # Ex: 830,00 -> 830.00
                        valtxt = valtxt.replace(',', '.')
                    # Log para depuração
                    print(f"[DEBUG] Valor original: '{valtxt_original}' | Valor convertido: '{valtxt}'")
                    valor = float(valtxt) if valtxt else 0.0
                    self.produtos_list.append({"descricao": desc.strip('• ').strip(), "valor": valor})
                except Exception as e:
                    print(f"[DEBUG] Erro ao converter valor: {e} | Linha: {linha}")
                    self.produtos_list.append({"descricao": linha.strip('• ').strip(), "valor": 0.0})
            else:
                self.produtos_list.append({"descricao": linha.strip('• ').strip(), "valor": 0.0})
