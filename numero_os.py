""" Gera o caminhoo do arquivo do contaddor e salva o numero da OS

    Returns:
        String: Numero da Os
"""

import os
import platform

class Contador:
    """ Descobre o sistema operacional e gera o caminho do arquivo do contador
    Criado para evitar erros que podiam occorer em diferentes SO

    Returns:
        arquivo: retorna o caminho do arquivo criado
    """
    @staticmethod
    def caminho_arquivo(): 
        if platform.system() == "Windows":
            pasta = os.path.join(os.environ["LOCALAPPDATA"], "ProjetoOs")
        else:  
            pasta = os.path.join(os.path.expanduser("~/.local/share"), "ProjetoOs")  
        
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        
        return os.path.join(pasta, "contador.txt")
    
    @staticmethod
    def ler_contador():
        caminho = Contador.caminho_arquivo()
        if not os.path.exists(caminho):
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write('0')
            return 0
        with open(caminho, 'r', encoding='utf-8') as f:
            conteudo = f.read().strip()
            if conteudo == '':
                return 0
            return int(conteudo)
    
    @staticmethod
    def salvar_contador(valor):
        caminho = Contador.caminho_arquivo()
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(str(valor))

