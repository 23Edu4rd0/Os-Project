"""
Módulo para geração do número da OS
"""
from app.numero_os import Contador

def gerar_numero_os():
    """Gera próximo número da OS"""
    contador = Contador()
    return contador.proximo_numero()

def formatar_numero_os(numero):
    """Formata número da OS com zeros à esquerda"""
    return f"{numero:05d}"
