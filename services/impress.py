import platform
import subprocess
import os
import sys


def imprimir_pdf(caminho_arquivo: str) -> tuple[bool, str]:
    """
    Tenta imprimir um arquivo PDF no sistema operacional atual.
    Usa múltiplos métodos como fallback para garantir funcionamento.

    Args:
        caminho_arquivo (str): Caminho do arquivo PDF a ser impresso.
    Returns:
        (bool, str): (True, '') se sucesso,
            (False, mensagem de erro) se falhar.
    """
    if not os.path.exists(caminho_arquivo):
        return False, f"Arquivo não encontrado: {caminho_arquivo}"
    
    sistema = platform.system()

    if sistema == "Windows":
        # Método 1: Tentar com pywin32
        try:
            import win32api
            win32api.ShellExecute(0, "print", caminho_arquivo, None, ".", 0)
            return True, ''
        except ImportError:
            pass  # Continua para o próximo método
        except Exception as e:
            pass  # Continua para o próximo método
        
        # Método 2: Usar comando do sistema Windows
        try:
            # Abre o arquivo com o programa padrão e simula Ctrl+P
            subprocess.run([
                'powershell', '-Command', 
                f'Start-Process -FilePath "{caminho_arquivo}" -Verb Print'
            ], check=True, capture_output=True)
            return True, ''
        except Exception:
            pass
        
        # Método 3: Abrir com programa padrão (fallback final)
        try:
            os.startfile(caminho_arquivo)
            return True, "PDF aberto. Use Ctrl+P para imprimir manualmente."
        except Exception as e:
            return False, f"Não foi possível abrir o PDF: {e}"

    elif sistema == "Linux":
        # Método 1: Tentar com lp (CUPS)
        try:
            subprocess.run(["lp", caminho_arquivo], check=True, capture_output=True)
            return True, ''
        except FileNotFoundError:
            pass  # Continua para o próximo método
        except Exception:
            pass
        
        # Método 2: Tentar com lpr
        try:
            subprocess.run(["lpr", caminho_arquivo], check=True, capture_output=True)
            return True, ''
        except FileNotFoundError:
            pass
        except Exception:
            pass
        
        # Método 3: Abrir com programa padrão (fallback final)
        try:
            subprocess.run(["xdg-open", caminho_arquivo], check=True)
            return True, "PDF aberto. Use Ctrl+P para imprimir manualmente."
        except Exception as e:
            return False, f"Não foi possível abrir o PDF: {e}"

    elif sistema == "Darwin":  # macOS
        try:
            subprocess.run(["lpr", caminho_arquivo], check=True, capture_output=True)
            return True, ''
        except Exception:
            try:
                subprocess.run(["open", caminho_arquivo], check=True)
                return True, "PDF aberto. Use Cmd+P para imprimir manualmente."
            except Exception as e:
                return False, f"Não foi possível abrir o PDF: {e}"

    else:
        # Fallback genérico - tentar abrir o arquivo
        try:
            if hasattr(os, 'startfile'):
                os.startfile(caminho_arquivo)
            else:
                subprocess.run([sys.executable, "-m", "webbrowser", caminho_arquivo])
            return True, "PDF aberto. Use Ctrl+P para imprimir manualmente."
        except Exception as e:
            return False, f"Sistema '{sistema}' não suportado: {e}"


def verificar_disponibilidade_impressao() -> dict:
    """
    Verifica quais métodos de impressão estão disponíveis no sistema.
    
    Returns:
        dict: Dicionário com informações sobre disponibilidade de impressão
    """
    sistema = platform.system()
    resultado = {
        'sistema': sistema,
        'metodos_disponiveis': [],
        'impressao_direta': False,
        'pode_abrir_arquivo': False
    }
    
    if sistema == "Windows":
        # Verifica pywin32
        try:
            import win32api
            resultado['metodos_disponiveis'].append('pywin32')
            resultado['impressao_direta'] = True
        except ImportError:
            pass
        
        # Verifica PowerShell
        try:
            subprocess.run(['powershell', '-Command', 'Get-Host'], 
                          capture_output=True, check=True, timeout=5)
            resultado['metodos_disponiveis'].append('powershell')
            resultado['impressao_direta'] = True
        except Exception:
            pass
        
        # Windows sempre pode abrir arquivos
        resultado['pode_abrir_arquivo'] = True
        resultado['metodos_disponiveis'].append('startfile')
    
    elif sistema == "Linux":
        # Verifica lp (CUPS)
        try:
            subprocess.run(['which', 'lp'], capture_output=True, check=True)
            resultado['metodos_disponiveis'].append('lp')
            resultado['impressao_direta'] = True
        except Exception:
            pass
        
        # Verifica lpr
        try:
            subprocess.run(['which', 'lpr'], capture_output=True, check=True)
            resultado['metodos_disponiveis'].append('lpr')
            resultado['impressao_direta'] = True
        except Exception:
            pass
        
        # Verifica xdg-open
        try:
            subprocess.run(['which', 'xdg-open'], capture_output=True, check=True)
            resultado['metodos_disponiveis'].append('xdg-open')
            resultado['pode_abrir_arquivo'] = True
        except Exception:
            pass
    
    elif sistema == "Darwin":  # macOS
        try:
            subprocess.run(['which', 'lpr'], capture_output=True, check=True)
            resultado['metodos_disponiveis'].append('lpr')
            resultado['impressao_direta'] = True
        except Exception:
            pass
        
        resultado['metodos_disponiveis'].append('open')
        resultado['pode_abrir_arquivo'] = True
    
    return resultado
