"""
Módulo para validação de dados do serviço
"""

def validar_servico(descricao, defeito, tipo, status, valor):
    """Valida dados do serviço"""
    if not descricao or not descricao.strip():
        return False, "Descrição do equipamento é obrigatória!"
    
    if not defeito or not defeito.strip():
        return False, "Defeito relatado é obrigatório!"
    
    if not tipo:
        return False, "Tipo de serviço é obrigatório!"
    
    if not status:
        return False, "Status é obrigatório!"
    
    try:
        float(valor.replace(',', '.'))
    except ValueError:
        return False, "Valor deve ser um número válido!"
    
    return True, ""
