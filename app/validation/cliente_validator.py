"""
Módulo para validação de dados do cliente
"""
from app.validation.cnpj_validator import validar_cnpj, validar_inscricao_estadual, cnpj_existe_na_receita


def validar_nome_cliente(nome):
    """Valida nome do cliente"""
    if not nome or not nome.strip():
        return False, "Nome do cliente é obrigatório!"
    return True, ""


def validar_cpf(cpf):
    """Valida CPF do cliente"""
    if not cpf:
        return True, ""  # CPF é opcional se tiver CNPJ
    
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


def validar_dados_cliente(cliente_data):
    """
    Valida todos os dados do cliente
    Retorna (is_valid, message)
    """
    nome = cliente_data.get('nome', '') or ''
    nome = nome.strip()
    
    cpf = cliente_data.get('cpf', '') or ''
    cpf = cpf.strip()
    
    cnpj = cliente_data.get('cnpj', '') or ''
    cnpj = cnpj.strip()
    
    inscricao_estadual = cliente_data.get('inscricao_estadual', '') or ''
    inscricao_estadual = inscricao_estadual.strip()
    
    telefone = cliente_data.get('telefone', '') or ''
    telefone = telefone.strip()
    
    # Nome é obrigatório
    if not nome:
        return False, "Nome é obrigatório!"
    
    # Telefone é obrigatório
    if not telefone:
        return False, "Telefone é obrigatório!"
    
    # Deve ter CPF ou CNPJ
    if not cpf and not cnpj:
        return False, "Informe CPF ou CNPJ!"
    
    # Não pode ter CPF e CNPJ ao mesmo tempo
    if cpf and cnpj:
        return False, "Informe apenas CPF ou CNPJ, não ambos!"
    
    # Validar CPF se informado
    if cpf:
        is_valid, msg = validar_cpf(cpf)
        if not is_valid:
            return False, msg
    
    # Validar CNPJ se informado
    if cnpj:
        if not validar_cnpj(cnpj):
            return False, "CNPJ inválido!"
        
        if not cnpj_existe_na_receita(cnpj):
            return False, "CNPJ não encontrado na Receita Federal!"
        
        # Se tem CNPJ, Inscrição Estadual é obrigatória
        if not inscricao_estadual:
            return False, "Inscrição Estadual é obrigatória para CNPJ!"
    
    # Validar Inscrição Estadual se informada
    if inscricao_estadual:
        estado = cliente_data.get('estado', 'MG')
        if not validar_inscricao_estadual(inscricao_estadual, estado):
            return False, "Inscrição Estadual inválida!"
    
    return True, "Dados válidos!"
