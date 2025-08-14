"""
Módulo principal que inicia a aplicação de Ordem de Serviço (OS).

Este script inicializa a interface gráfica usando ttkbootstrap e
executa a aplicação principal modularizada.

"""

import ttkbootstrap as tb
from app.components.pedidos_manager import PedidosManager
from app.components.clientes_manager import ClientesManager


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Ordem de Serviço - Versão Corrigida")
        self.root.geometry("1200x800")
        
        # Notebook principal
        notebook = tb.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Aba Clientes
        clientes_frame = tb.Frame(notebook)
        notebook.add(clientes_frame, text="👥 Clientes")
        self.clientes_manager = ClientesManager(clientes_frame)
        
        # Aba Pedidos
        pedidos_frame = tb.Frame(notebook)
        notebook.add(pedidos_frame, text="📋 Pedidos")
        self.pedidos_manager = PedidosManager(pedidos_frame)


if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    root.title("Ordem de Serviço")
    root.geometry("1200x800")
    
    app = MainApp(root)
    root.mainloop()
