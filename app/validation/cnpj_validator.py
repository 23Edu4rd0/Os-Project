"""
Validador de CNPJ
"""
import re


def limpar_cnpj(cnpj):
    """Remove caracteres especiais do CNPJ"""
    if not cnpj:
        return ""
    return re.sub(r'[^0-9]', '', cnpj)


def formatar_cnpj(cnpj):
    """Formata CNPJ com máscara XX.XXX.XXX/XXXX-XX"""
    cnpj_limpo = limpar_cnpj(cnpj)
    if len(cnpj_limpo) == 14:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:14]}"
    return cnpj


def validar_cnpj(cnpj):
    """
    Valida CNPJ brasileiro
    Retorna True se válido, False se inválido
    """
    if not cnpj:
        return True  # CNPJ é opcional
    
    cnpj_limpo = limpar_cnpj(cnpj)
    
    # Verifica se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj_limpo == cnpj_limpo[0] * 14:
        return False
    
    # Calcula primeiro dígito verificador
    soma = 0
    peso = 5
    for i in range(12):
        soma += int(cnpj_limpo[i]) * peso
        peso = peso - 1 if peso > 2 else 9
    
    digito1 = 11 - (soma % 11)
    if digito1 >= 10:
        digito1 = 0
    
    if int(cnpj_limpo[12]) != digito1:
        return False
    
    # Calcula segundo dígito verificador
    soma = 0
    peso = 6
    for i in range(13):
        soma += int(cnpj_limpo[i]) * peso
        peso = peso - 1 if peso > 2 else 9
    
    digito2 = 11 - (soma % 11)
    if digito2 >= 10:
        digito2 = 0
    
    if int(cnpj_limpo[13]) != digito2:
        return False
    
    return True


def cnpj_existe_na_receita(cnpj):
    """
    Verifica se CNPJ existe na Receita Federal
    Por enquanto retorna sempre True (implementar API futuramente)
    """
    if not cnpj or not validar_cnpj(cnpj):
        return False
    
    # Validação do formato já realizada pela função validar_cnpj
    return True


def validar_inscricao_estadual(ie, estado="MG"):
    """
    Valida Inscrição Estadual (implementação básica para MG)
    """
    if not ie:
        return True  # IE é obrigatória apenas se tiver CNPJ
    
    ie_limpa = re.sub(r'[^0-9]', '', ie)
    
    # Validação básica para Minas Gerais (13 dígitos)
    if estado.upper() == "MG":
        if len(ie_limpa) != 13:
            return False
        # Validação básica para MG implementada
        return True
    
    # Para outros estados, apenas verifica se não está vazio
    return len(ie_limpa) > 0
