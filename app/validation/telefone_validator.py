"""
Módulo de validação e formatação de telefones brasileiros.

Suporta:
- Telefones fixos: (11) 3456-7890 (10 dígitos)
- Celulares: (11) 98765-4321 (11 dígitos)
- Remove caracteres especiais automaticamente
- Formatação automática durante digitação
"""

import re
from typing import Tuple, Optional


class TelefoneValidator:
    """Validador e formatador de telefones brasileiros"""
    
    @staticmethod
    def limpar_telefone(telefone: str) -> str:
        """
        Remove todos os caracteres não numéricos do telefone.
        
        Args:
            telefone: Telefone com ou sem formatação
            
        Returns:
            String contendo apenas números
        """
        if not telefone:
            return ""
        return re.sub(r'\D', '', telefone)
    
    @staticmethod
    def validar_telefone(telefone: str) -> Tuple[bool, str]:
        """
        Valida se o telefone tem 10 ou 11 dígitos.
        
        Args:
            telefone: Telefone a ser validado
            
        Returns:
            Tupla (válido: bool, mensagem: str)
        """
        if not telefone:
            return False, "Telefone não pode estar vazio"
        
        # Limpar telefone
        apenas_numeros = TelefoneValidator.limpar_telefone(telefone)
        
        # Verificar se tem apenas números
        if not apenas_numeros.isdigit():
            return False, "Telefone deve conter apenas números"
        
        # Verificar comprimento
        tamanho = len(apenas_numeros)
        if tamanho < 10:
            return False, "Telefone deve ter pelo menos 10 dígitos (com DDD)"
        elif tamanho > 11:
            return False, "Telefone deve ter no máximo 11 dígitos"
        
        # Validar DDD (primeiros 2 dígitos)
        ddd = int(apenas_numeros[:2])
        ddds_validos = [11, 12, 13, 14, 15, 16, 17, 18, 19,  # SP
                       21, 22, 24,  # RJ/ES
                       27, 28,  # ES
                       31, 32, 33, 34, 35, 37, 38,  # MG
                       41, 42, 43, 44, 45, 46,  # PR
                       47, 48, 49,  # SC
                       51, 53, 54, 55,  # RS
                       61,  # DF
                       62, 64,  # GO/TO
                       63,  # TO
                       65, 66,  # MT/MS
                       67,  # MS
                       68,  # AC
                       69,  # RO
                       71, 73, 74, 75, 77,  # BA
                       79,  # SE
                       81, 87,  # PE
                       82,  # AL
                       83,  # PB
                       84,  # RN
                       85, 88,  # CE
                       86, 89,  # PI
                       91, 93, 94,  # PA
                       92, 97,  # AM
                       95,  # RR
                       96,  # AP
                       98, 99]  # MA
        
        if ddd not in ddds_validos:
            return False, f"DDD {ddd} não é válido"
        
        # Validar se celular começa com 9
        if tamanho == 11:
            if apenas_numeros[2] != '9':
                return False, "Celular (11 dígitos) deve começar com 9 após o DDD"
        
        return True, "Telefone válido"
    
    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        """
        Formata telefone no padrão brasileiro.
        
        Args:
            telefone: Telefone para formatar
            
        Returns:
            Telefone formatado: (11) 98765-4321 ou (11) 3456-7890
        """
        if not telefone:
            return ""
        
        # Limpar
        apenas_numeros = TelefoneValidator.limpar_telefone(telefone)
        
        # Se não tem números suficientes, retornar como está
        if len(apenas_numeros) < 10:
            return telefone
        
        # Formatar
        if len(apenas_numeros) == 10:
            # Fixo: (11) 3456-7890
            return f"({apenas_numeros[:2]}) {apenas_numeros[2:6]}-{apenas_numeros[6:]}"
        elif len(apenas_numeros) == 11:
            # Celular: (11) 98765-4321
            return f"({apenas_numeros[:2]}) {apenas_numeros[2:7]}-{apenas_numeros[7:]}"
        else:
            # Mais de 11 dígitos, retornar apenas os primeiros 11
            apenas_numeros = apenas_numeros[:11]
            return f"({apenas_numeros[:2]}) {apenas_numeros[2:7]}-{apenas_numeros[7:]}"
    
    @staticmethod
    def formatar_enquanto_digita(telefone: str, cursor_pos: int) -> Tuple[str, int]:
        """
        Formata telefone enquanto o usuário digita, mantendo posição do cursor.
        
        Args:
            telefone: Texto atual do campo
            cursor_pos: Posição atual do cursor
            
        Returns:
            Tupla (texto_formatado: str, nova_posicao_cursor: int)
        """
        # Limpar
        apenas_numeros = TelefoneValidator.limpar_telefone(telefone)
        
        # Limitar a 11 dígitos
        apenas_numeros = apenas_numeros[:11]
        
        # Formatar baseado no comprimento
        if len(apenas_numeros) == 0:
            return "", 0
        elif len(apenas_numeros) <= 2:
            # (11
            formatado = f"({apenas_numeros}"
            nova_pos = len(formatado)
        elif len(apenas_numeros) <= 6:
            # (11) 3456
            formatado = f"({apenas_numeros[:2]}) {apenas_numeros[2:]}"
            nova_pos = len(formatado)
        elif len(apenas_numeros) <= 10:
            # (11) 3456-78
            formatado = f"({apenas_numeros[:2]}) {apenas_numeros[2:6]}-{apenas_numeros[6:]}"
            nova_pos = len(formatado)
        else:
            # (11) 98765-4321
            formatado = f"({apenas_numeros[:2]}) {apenas_numeros[2:7]}-{apenas_numeros[7:]}"
            nova_pos = len(formatado)
        
        return formatado, nova_pos
    
    @staticmethod
    def criar_mascara_input() -> str:
        """
        Retorna a máscara de input para telefone.
        Útil para widgets de entrada com máscara.
        
        Returns:
            String com máscara: "(00) 00000-0000"
        """
        return "(00) 00000-0000"
    
    @staticmethod
    def extrair_ddd(telefone: str) -> Optional[str]:
        """
        Extrai o DDD do telefone.
        
        Args:
            telefone: Telefone formatado ou não
            
        Returns:
            DDD (2 dígitos) ou None se inválido
        """
        apenas_numeros = TelefoneValidator.limpar_telefone(telefone)
        if len(apenas_numeros) >= 2:
            return apenas_numeros[:2]
        return None
    
    @staticmethod
    def extrair_numero_sem_ddd(telefone: str) -> Optional[str]:
        """
        Extrai o número sem o DDD.
        
        Args:
            telefone: Telefone formatado ou não
            
        Returns:
            Número sem DDD ou None se inválido
        """
        apenas_numeros = TelefoneValidator.limpar_telefone(telefone)
        if len(apenas_numeros) >= 10:
            return apenas_numeros[2:]
        return None
    
    @staticmethod
    def eh_celular(telefone: str) -> bool:
        """
        Verifica se o telefone é celular (11 dígitos).
        
        Args:
            telefone: Telefone a verificar
            
        Returns:
            True se for celular, False caso contrário
        """
        apenas_numeros = TelefoneValidator.limpar_telefone(telefone)
        return len(apenas_numeros) == 11
    
    @staticmethod
    def eh_fixo(telefone: str) -> bool:
        """
        Verifica se o telefone é fixo (10 dígitos).
        
        Args:
            telefone: Telefone a verificar
            
        Returns:
            True se for fixo, False caso contrário
        """
        apenas_numeros = TelefoneValidator.limpar_telefone(telefone)
        return len(apenas_numeros) == 10
