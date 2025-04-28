def imprimir_pdf(caminho_arquivo, imprimir=True):
    if not imprimir:
        return
    import win32print
    import win32api
    impressora = win32print.GetDefaultPrinter()
    win32api.ShellExecute(0, "print", caminho_arquivo, None, ".", 0)

