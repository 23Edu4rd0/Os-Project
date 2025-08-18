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
