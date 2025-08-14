"""
Módulo da aba de banco de dados - Interface para gerenciar dados
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, DANGER
from tkinter import messagebox

from app.components.clientes_manager import ClientesManager
from app.components.pedidos_manager import PedidosManager
from database.db_manager import db_manager


class DatabaseTab:
    """Gerencia a aba do banco de dados"""
    
    def __init__(self, parent):
        self.parent = parent
        self._setup_notebook()
        self._setup_tabs()
        
    def _setup_notebook(self):
        """Cria o notebook interno"""
        self.inner_notebook = tb.Notebook(self.parent)
        self.inner_notebook.pack(fill="both", expand=True, padx=8, pady=8)
        
    def _setup_tabs(self):
        """Configura as abas internas"""
        # Aba Clientes
        clientes_frame = tb.Frame(self.inner_notebook)
        self.inner_notebook.add(clientes_frame, text="👥 Clientes")
        self.clientes_manager = ClientesManager(clientes_frame)
        
        # Aba Pedidos
        pedidos_frame = tb.Frame(self.inner_notebook)
        self.inner_notebook.add(pedidos_frame, text="📋 Pedidos")
        self.pedidos_manager = PedidosManager(pedidos_frame)
        
    def refresh_data(self):
        """Atualiza os dados de todas as abas"""
        try:
            self.clientes_manager.carregar_dados()
            self.pedidos_manager.carregar_dados()
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao atualizar dados: {e}')
