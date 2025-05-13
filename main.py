"""
Módulo principal que inicia a aplicação de Ordem de Serviço (OS).

Este script inicializa a interface gráfica usando ttkbootstrap e
executa a aplicação principal definida em `os_app.py`.

Lembrar de criar uma area de imposto e um area no tk para colocar o valor
"""

import ttkbootstrap as tb
from os_app import OrdemServicoApp

if __name__ == "__main__": 
    root = tb.Window(themename="darkly")  # Temas possíveis: darkly, flatly, cyborg.
    app = OrdemServicoApp(root)           
    root.mainloop()                       