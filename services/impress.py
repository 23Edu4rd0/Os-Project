import platform
import subprocess


def imprimir_pdf(caminho_arquivo: str) -> tuple[bool, str]:
    """
    Tenta imprimir um arquivo PDF no sistema operacional atual.

    Args:
        caminho_arquivo (str): Caminho do arquivo PDF a ser impresso.
    Returns:
        (bool, str): (True, '') se sucesso,
            (False, mensagem de erro) se falhar.
    """
    sistema = platform.system()

    if sistema == "Windows":
        try:
            import win32api
            win32api.ShellExecute(0, "print", caminho_arquivo, None, ".", 0)
            return True, ''
        except ImportError:
            return False, (
                "Biblioteca 'pywin32' não instalada. "
                "Use 'pip install pywin32'."
            )
        except Exception as e:
            return False, f"Erro ao imprimir no Windows: {e}"

    elif sistema == "Linux":
        try:
            subprocess.run(["lp", caminho_arquivo], check=True)
            return True, ''
        except FileNotFoundError:
            return False, (
                "O comando 'lp' não está disponível. "
                "Instale o CUPS com 'sudo apt install cups'."
            )
        except Exception as e:
            return False, f"Erro ao imprimir no Linux: {e}"

    else:
        return False, (
            f"Sistema operacional '{sistema}' não suportado para impressão."
        )
