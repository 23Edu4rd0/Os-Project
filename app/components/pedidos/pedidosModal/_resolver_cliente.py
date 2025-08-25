from .__init__ import PedidosModal

def _resolver_cliente(self, texto: str):
    if not texto:
        return None
    if texto in self.clientes_dict:
        cli = self.clientes_dict[texto]
        return (texto, cli)
    low = texto.strip().lower()
    nome_parte = low.split('|')[0].strip()
    digitos = ''.join(ch for ch in texto if ch.isdigit())
    candidatos = []
    for k, v in self.clientes_dict.items():
        k_low = k.lower()
        if k_low == low:
            return (k, v)
        nome_cli = (v.get('nome') or '').lower()
        if nome_parte and (nome_cli == nome_parte or nome_cli.startswith(nome_parte)):
            candidatos.append((k, v))
            continue
        if digitos and ''.join(ch for ch in str(v.get('telefone','')) if ch.isdigit()).endswith(digitos):
            candidatos.append((k, v))
    if len(candidatos) == 1:
        return candidatos[0]
    if not candidatos and nome_parte:
        for k, v in self.clientes_dict.items():
            if nome_parte in (v.get('nome') or '').lower():
                candidatos.append((k, v))
    if len(candidatos) == 1:
        return candidatos[0]
    return None
