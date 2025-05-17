import os
import platform

class Contador:
    """
    Classe utilitária para gerenciar um contador persistente baseado no sistema operacional.

    Essa classe identifica o sistema (Windows ou Linux) e armazena o número da OS
    em um arquivo localizado em uma pasta apropriada ao sistema, evitando problemas
    de compatibilidade entre diferentes SOs.
    """

    @staticmethod
    def caminho_arquivo():
        """
        Gera o caminho do arquivo onde o contador será salvo, de acordo com o sistema operacional.

        Returns:
            str: Caminho completo do arquivo 'contador.txt'.
        """
        if platform.system() == "Windows":
            pasta = os.path.join(os.environ["LOCALAPPDATA"], "ProjetoOs")
        else:
            pasta = os.path.join(os.path.expanduser("~/.local/share"), "ProjetoOs")

        if not os.path.exists(pasta):
            os.makedirs(pasta)

        return os.path.join(pasta, "contador.txt")

    @staticmethod
    def ler_contador():
        """
        Lê o valor atual do contador do arquivo.

        Se o arquivo não existir ou estiver vazio, retorna 0.

        Returns:
            int: Valor atual do contador.
        """
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
    def salvar_contador(valor: int):
        """
        Salva um novo valor no contador.

        Args:
            valor (int): Novo valor a ser salvo no contador.
        """
        caminho = Contador.caminho_arquivo()
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(str(valor))
