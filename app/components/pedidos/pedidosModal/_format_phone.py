from .__init__ import PedidosModal

def _format_phone(self, telefone: str) -> str:
    if not telefone:
        return ""
    dig = ''.join(filter(str.isdigit, str(telefone)))
    if len(dig) == 11:
        return f"({dig[:2]}) {dig[2:7]}-{dig[7:]}"
    if len(dig) == 10:
        return f"({dig[:2]}) {dig[2:6]}-{dig[6:]}"
    return telefone
