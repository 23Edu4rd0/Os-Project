import platform
import subprocess

def imprimir_pdf(caminho_arquivo: str, imprimir: bool = True) -> None:
    """
    Imprime um arquivo PDF no sistema operacional atual.

    Parâmetros:
    ----------
    caminho_arquivo : str
        Caminho completo para o arquivo PDF que será impresso.
    imprimir : bool, opcional (padrão=True)
        Se False, a função não faz nada.

    Funciona em:
    ------------
    - Windows: usa win32api e win32print.
    - Linux: usa o comando `lp` (requer CUPS instalado).

    Observações:
    ------------
    - Em sistemas Linux, é necessário que o utilitário 'lp' esteja disponível.
    - Em sistemas Windows, requer pywin32 instalado.
    """
    if not imprimir:
        return

    sistema = platform.system()

    if sistema == "Windows":
        try:
            import win32print
            import win32api
            impressora = win32print.GetDefaultPrinter()
            win32api.ShellExecute(0, "print", caminho_arquivo, None, ".", 0)
        except ImportError:
            print("Erro: Biblioteca 'pywin32' não instalada. Use 'pip install pywin32'.")
        except Exception as e:
            print(f"Erro ao imprimir no Windows: {e}")

    elif sistema == "Linux":
        try:
            subprocess.run(["lp", caminho_arquivo], check=True)
        except FileNotFoundError:
            print("Erro: O comando 'lp' não está disponível. Instale o CUPS com 'sudo apt install cups'.")
        except Exception as e:
            print(f"Erro ao imprimir no Linux: {e}")

    else:
        print(f"Sistema operacional '{sistema}' não suportado para impressão.")
