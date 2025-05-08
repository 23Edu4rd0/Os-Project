import platform
import subprocess

def imprimir_pdf(caminho_arquivo: str) -> None:
    """
    Função para imprimir um arquivo PDF no sistema operacional atual.

    Args:
        caminho_arquivo (str): Caminho do arquivo PDF a ser impresso.
    """
    sistema = platform.system()

    if sistema == "Windows":
        try:
            import win32print
            import win32api
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
