"""
Módulo da aba de banco de dados - Interface para gerenciar dados
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, DANGER
from tkinter import messagebox

from app.components.clientes_manager import ClientesManager
from app.components.pedidos_manager import PedidosManager
from app.components.contas.contas_manager import ContasManager
from database import db_manager


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

        # Aba Contas (Financeiro)
        contas_frame = tb.Frame(self.inner_notebook)
        self.inner_notebook.add(contas_frame, text="💼 Contas")
        # Instancia o gerenciador de contas (cria subtabs: Financeiro, Gastos, Margem)
        try:
            self.contas_manager = ContasManager(contas_frame)
        except Exception as e:
            # Falha ao carregar a aba de contas: continuar sem travar a aplicação
            tb.Label(contas_frame, text=f"Erro ao carregar Contas: {e}", bootstyle="danger").pack(padx=8, pady=8)
        
    def refresh_data(self):
        """Atualiza os dados de todas as abas"""
        try:
            self.clientes_manager.carregar_dados()
            self.pedidos_manager.carregar_dados()
            # Atualiza dados da aba Contas caso exista
            if hasattr(self, 'contas_manager'):
                try:
                    self.contas_manager.carregar_dados()
                except Exception:
                    # Se falhar, não interrompe as demais atualizações
                    pass
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao atualizar dados: {e}')
