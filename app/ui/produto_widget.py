"""
Módulo para criação de widgets de produto
"""
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb

class ProdutoWidget:
    def __init__(self, parent, produto_data=None):
        self.frame = tb.Frame(parent)
        self.setup_widgets()
        if produto_data:
            self.load_data(produto_data)
    
    def setup_widgets(self):
        """Cria os widgets para o produto"""
        # Frame principal
        main_frame = tb.Frame(self.frame)
        main_frame.pack(fill='x', padx=5, pady=2)
        
        # Linha 1: Tipo e Cor
        linha1 = tb.Frame(main_frame)
        linha1.pack(fill='x', pady=2)
        
        tb.Label(linha1, text="Tipo:").pack(side='left')
        self.tipo = tb.Entry(linha1, width=20)
        self.tipo.pack(side='left', padx=5)
        
        tb.Label(linha1, text="Cor:").pack(side='left', padx=(10,0))
        self.cor = tb.Entry(linha1, width=15)
        self.cor.pack(side='left', padx=5)
        
        # Linha 2: Gavetas, Valor e Reforço
        linha2 = tb.Frame(main_frame)
        linha2.pack(fill='x', pady=2)
        
        tb.Label(linha2, text="Gavetas:").pack(side='left')
        self.gavetas = tb.Entry(linha2, width=8)
        self.gavetas.pack(side='left', padx=5)
        
        tb.Label(linha2, text="Valor:").pack(side='left', padx=(10,0))
        self.valor = tb.Entry(linha2, width=12)
        self.valor.pack(side='left', padx=5)
        
        self.reforco_var = tk.BooleanVar()
        self.reforco = tb.Checkbutton(linha2, text="Reforço (+R$ 15)", 
                                     variable=self.reforco_var)
        self.reforco.pack(side='left', padx=(10,0))
    
    def load_data(self, data):
        """Carrega dados no widget"""
        self.tipo.insert(0, data.get('tipo', ''))
        self.cor.insert(0, data.get('cor', ''))
        self.gavetas.insert(0, data.get('gavetas', ''))
        self.valor.insert(0, data.get('valor', ''))
        self.reforco_var.set(data.get('reforco', False))
    
    def get_data(self):
        """Retorna dados do widget"""
        return {
            'tipo': self.tipo,
            'cor': self.cor,
            'gavetas': self.gavetas,
            'valor': self.valor,
            'reforco_var': self.reforco_var
        }
    
    def destroy(self):
        """Remove o widget"""
        self.frame.destroy()
