import os
import platform


class Contador:
    """
    Classe utilitária para gerenciar um contador persistente baseado no
    sistema operacional.

    Essa classe identifica o sistema (Windows ou Linux) e armazena o número
    da OS em um arquivo localizado em uma pasta apropriada ao sistema,
    evitando problemas de permissão ou localização inadequada de arquivos
    de configuração.
    """
    NOME_ARQUIVO = "numero_os.txt"
    NOME_PASTA_APP = "ProjetoOs"  # Nome da pasta da aplicação

    @staticmethod
    def _get_pasta_dados():
        """
        Gera o caminho da pasta onde o contador será salvo, de acordo com o
        sistema operacional.
        """
        system = platform.system()
        if system == "Windows":
            # AppData\\Roaming\\ProjetoOs
            pasta = os.path.join(
                os.getenv("APPDATA"), Contador.NOME_PASTA_APP
            )
        elif system == "Linux":
            # ~/.local/share/ProjetoOs
            pasta = os.path.join(
                os.path.expanduser("~/.local/share"), Contador.NOME_PASTA_APP
            )
        else:
            # Fallback para outros sistemas (ex: macOS) ou se caminhos
            # específicos falharem
            # ~/.ProjetoOs
            pasta = os.path.join(
                os.path.expanduser("~"), "." + Contador.NOME_PASTA_APP
            )

        if not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)
        return pasta

    @staticmethod
    def _get_caminho_arquivo():
        """Retorna o caminho completo para o arquivo do contador."""
        return os.path.join(Contador._get_pasta_dados(), Contador.NOME_ARQUIVO)

    @staticmethod
    def ler_contador():
        """
        Lê o número atual do contador do arquivo.
        Se o arquivo não existir ou estiver vazio/corrompido, retorna 1.
        """
        caminho = Contador._get_caminho_arquivo()
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 1  # Retorna 1 se o arquivo não existir ou for inválido

    @staticmethod
    def salvar_contador(numero):
        """
        Salva o número fornecido no arquivo do contador.
        """
        caminho = Contador._get_caminho_arquivo()
        try:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(str(numero))
        except IOError as e:
            print(f"Erro ao salvar o contador: {e}")
            # Considerar lançar uma exceção personalizada ou logar o erro
            # de forma mais robusta, dependendo dos requisitos da aplicação.

    @staticmethod
    def proximo_numero():
        """
        Lê o contador atual, incrementa, salva e retorna o novo número.
        Esta função garante que o número da OS seja sempre incrementado
        corretamente.
        """
        numero_atual = Contador.ler_contador()
        proximo = numero_atual + 1
        Contador.salvar_contador(proximo)
        return proximo
