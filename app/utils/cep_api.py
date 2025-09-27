"""
Módulo para integração com API do ViaCEP
"""
import requests
import re
from typing import Dict, Optional

class CepAPI:
    """Classe para buscar informações de endereço via CEP"""
    
    BASE_URL = "https://viacep.com.br/ws"
    
    @staticmethod
    def format_cep(cep: str) -> str:
        """Formata CEP removendo caracteres especiais"""
        if not cep:
            return ""
        return re.sub(r'[^0-9]', '', cep)
    
    @staticmethod
    def is_valid_cep(cep: str) -> bool:
        """Valida formato do CEP"""
        formatted_cep = CepAPI.format_cep(cep)
        return len(formatted_cep) == 8 and formatted_cep.isdigit()
    
    @classmethod
    def buscar_endereco(cls, cep: str) -> Optional[Dict[str, str]]:
        """
        Busca endereço pelo CEP usando a API do ViaCEP
        
        Args:
            cep: CEP a ser consultado
            
        Returns:
            Dict com dados do endereço ou None se não encontrado
        """
        formatted_cep = cls.format_cep(cep)
        
        if not cls.is_valid_cep(formatted_cep):
            return None
        
        try:
            url = f"{cls.BASE_URL}/{formatted_cep}/json/"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # ViaCEP retorna {"erro": True} para CEPs inexistentes
                if data.get('erro'):
                    return None
                
                return {
                    'cep': data.get('cep', ''),
                    'rua': data.get('logradouro', ''),
                    'bairro': data.get('bairro', ''),
                    'cidade': data.get('localidade', ''),
                    'estado': data.get('uf', ''),
                    'ibge': data.get('ibge', ''),
                    'gia': data.get('gia', ''),
                    'ddd': data.get('ddd', '')
                }
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao consultar CEP {formatted_cep}: {e}")
        except ValueError as e:
            print(f"Erro ao processar resposta da API para CEP {formatted_cep}: {e}")
        
        return None
    
    @classmethod
    def format_cep_display(cls, cep: str) -> str:
        """
        Formata CEP para exibição (XXXXX-XXX)
        
        Args:
            cep: CEP para formatar
            
        Returns:
            CEP formatado ou string vazia
        """
        formatted_cep = cls.format_cep(cep)
        
        if len(formatted_cep) == 8:
            return f"{formatted_cep[:5]}-{formatted_cep[5:]}"
        
        return cep