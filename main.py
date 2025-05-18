"""
Módulo principal que inicia a aplicação de Ordem de Serviço (OS).

Este script inicializa a interface gráfica usando ttkbootstrap e
executa a aplicação principal definida em `os_app.py`.

"""

import ttkbootstrap as tb
from app.os_app import OrdemServicoApp

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = OrdemServicoApp(root)
    root.mainloop()
