"""
Gerenciador principal da aba de contas
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, DANGER, INFO, WARNING
from tkinter import messagebox
import sys
import os

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from database import db_manager
from .contas_financeiro import ContasFinanceiro
from .contas_gastos import ContasGastos
from .contas_margem import ContasMargem


class ContasManager:
    """Gerenciador principal da aba de contas"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_tab = None
        self._setup_interface()
        
    def _setup_interface(self):
        """Configura a interface principal"""
        # Notebook para as abas
        self.notebook = tb.Notebook(self.parent)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Aba Financeiro
        self.financeiro_frame = tb.Frame(self.notebook)
        self.notebook.add(self.financeiro_frame, text="💰 Financeiro")
        self.financeiro = ContasFinanceiro(self.financeiro_frame)
        
        # Aba Gastos
        self.gastos_frame = tb.Frame(self.notebook)
        self.notebook.add(self.gastos_frame, text="💸 Gastos")
        self.gastos = ContasGastos(self.gastos_frame)
        
        # Aba Margem de Lucro
        self.margem_frame = tb.Frame(self.notebook)
        self.notebook.add(self.margem_frame, text="📊 Margem de Lucro")
        self.margem = ContasMargem(self.margem_frame)
        
        # Bind para mudança de aba
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
    def _on_tab_changed(self, event):
        """Executado quando a aba é alterada"""
        selected_tab = self.notebook.tab(self.notebook.select(), "text")
        if "Financeiro" in selected_tab:
            self.financeiro.atualizar_dados()
        elif "Gastos" in selected_tab:
            self.gastos.atualizar_dados()
        elif "Margem" in selected_tab:
            self.margem.atualizar_dados()
    
    def carregar_dados(self):
        """Carrega dados de todas as abas"""
        try:
            self.financeiro.atualizar_dados()
            self.gastos.atualizar_dados()
            self.margem.atualizar_dados()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
    
    def atualizar_graficos(self):
        """Atualiza gráficos de todas as abas"""
        try:
            self.financeiro.atualizar_graficos()
            self.gastos.atualizar_graficos()
            self.margem.atualizar_graficos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar gráficos: {e}")
    
    def filtrar_por_periodo(self, periodo):
        """Filtra dados por período"""
        try:
            self.financeiro.filtrar_por_periodo(periodo)
            self.gastos.filtrar_por_periodo(periodo)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao filtrar por período: {e}")
