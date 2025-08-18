"""
Módulo para validação de dados do cliente
"""

def validar_nome_cliente(nome):
    """Valida nome do cliente"""
    if not nome or not nome.strip():
        return False, "Nome do cliente é obrigatório!"
    return True, ""

def validar_cpf(cpf):
    """Valida CPF do cliente"""
    cpf = cpf.strip()
    if len(cpf) != 11 or not cpf.isdigit():
        return False, "CPF deve ter 11 dígitos!"
    return True, ""

def validar_telefone(telefone):
    """Valida telefone do cliente"""
    telefone = telefone.strip()
    if not telefone:
        return False, "Telefone é obrigatório!"
    return True, ""
