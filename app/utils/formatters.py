"""
Módulo para formatação de valores
"""

def formatar_valor(valor):
    """Formata valor monetário"""
    try:
        valor_float = float(valor.replace(',', '.'))
        return f"R$ {valor_float:.2f}".replace('.', ',')
    except:
        return "R$ 0,00"

def formatar_data(data):
    """Formata data para exibição"""
    if data:
        return data.strftime("%d/%m/%Y")
    return ""

def formatar_data_hora(data):
    """Formata data e hora para exibição"""
    if data:
        return data.strftime("%d/%m/%Y %H:%M")
    return ""


def formatar_cpf(cpf):
    """Formata CPF para exibição: 000.000.000-00. Recebe string com dígitos ou None."""
    if not cpf:
        return ''
    s = ''.join(ch for ch in str(cpf) if ch.isdigit())
    if len(s) != 11:
        return s
    return f"{s[0:3]}.{s[3:6]}.{s[6:9]}-{s[9:11]}"

def formatar_cnpj(cnpj):
    """Formata CNPJ para exibição: 00.000.000/0000-00. Recebe string com dígitos ou None."""
    if not cnpj:
        return ''
    s = ''.join(ch for ch in str(cnpj) if ch.isdigit())
    if len(s) != 14:
        return s
    return f"{s[0:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:14]}"
