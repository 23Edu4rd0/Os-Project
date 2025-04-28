import win32print
import win32api

def imprimir_pdf(caminho_arquivo):
    # Obter a impressora padrão configurada no sistema
    impressora = win32print.GetDefaultPrinter()
    
    # Usar a impressora padrão para imprimir o arquivo PDF
    win32api.ShellExecute(0, "print", caminho_arquivo, None, ".", 0)

