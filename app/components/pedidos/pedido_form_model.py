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
        # Determine default status from persisted list when not provided
        try:
            from app.utils.statuses import load_statuses
            _sts = load_statuses()
            default_status = _sts[0] if _sts else 'em produção'
        except Exception:
            default_status = 'em produção'

        self.dados = {
            'nome_cliente': dados.get('nome_cliente', ''),
            'telefone_cliente': dados.get('telefone_cliente', ''),
            'cpf_cliente': dados.get('cpf_cliente', ''),
            'endereco_cliente': dados.get('endereco_cliente', ''),
            'entrada': f"{float(dados.get('valor_entrada', 0) or 0):.2f}",
            'frete': f"{float(dados.get('frete', 0) or 0):.2f}",
            'desconto': f"{float(dados.get('desconto', 0) or 0):.2f}",
            'status': dados.get('status', default_status),
            'forma_pagamento': dados.get('forma_pagamento', 'pix'),
            'prazo_entrega': str(int(dados.get('prazo', 0) or 0)),
            'cor': dados.get('cor', ''),
            'reforco': 'sim' if str(dados.get('reforco', False)).lower() in ('1','true','sim','yes') else 'não',
            'valor_total': f"{float(dados.get('valor_total', dados.get('valor_produto', 0)) or 0):.2f}",
        }
        # Produtos: prefer structured 'produtos' provided by newer UI
        self.produtos_list = []
        if isinstance(dados.get('produtos'), (list, tuple)) and len(dados.get('produtos')) > 0:
            for p in dados.get('produtos'):
                try:
                    desc = str(p.get('descricao') or p.get('nome') or '').strip()
                    valor = float(p.get('valor') or p.get('preco') or 0)
                except Exception:
                    desc = str(p.get('descricao') or '').strip()
                    try:
                        valor = float(str(p.get('valor') or '0').replace(',', '.'))
                    except Exception:
                        valor = 0.0
                self.produtos_list.append({'descricao': desc, 'valor': valor})
        else:
            detalhes = dados.get('detalhes_produto', '') or ''
            for linha in [l.strip() for l in detalhes.replace('\r', '\n').split('\n') if l.strip() and not l.strip().startswith('-')]:
                if ' - R$ ' in linha:
                    try:
                        desc, valtxt = linha.rsplit(' - R$ ', 1)
                        valtxt_original = valtxt.strip()
                        valconv = valtxt_original.replace('.', '').replace(',', '.') if ',' in valtxt_original else valtxt_original
                        print(f"[DEBUG] Valor original: '{valtxt_original}' | Valor convertido: '{valconv}'")
                        valor = float(valconv) if valconv else 0.0
                        self.produtos_list.append({'descricao': desc.strip('\u2022 ').strip(), 'valor': valor})
                    except Exception as e:
                        print(f"[DEBUG] Erro ao converter valor: {e} | Linha: {linha}")
                        self.produtos_list.append({'descricao': linha.strip('\u2022 ').strip(), 'valor': 0.0})
                else:
                    self.produtos_list.append({'descricao': linha.strip('\u2022 ').strip(), 'valor': 0.0})
