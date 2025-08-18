"""
Módulo para configuração de entrada de dados
"""
import tkinter as tk
from tkinter import ttk

def configurar_entry_monetario(entry):
    """Configura entry para aceitar apenas valores monetários"""
    def validar_entrada(char):
        return char.isdigit() or char in ',.+'
    
    vcmd = (entry.register(validar_entrada), '%S')
    entry.config(validate='key', validatecommand=vcmd)

def configurar_entry_numerico(entry):
    """Configura entry para aceitar apenas números"""
    def validar_entrada(char):
        return char.isdigit()
    
    vcmd = (entry.register(validar_entrada), '%S')
    entry.config(validate='key', validatecommand=vcmd)

def configurar_entry_telefone(entry):
    """Configura entry para telefone"""
    def validar_entrada(char):
        return char.isdigit() or char in '()-+ '
    
    vcmd = (entry.register(validar_entrada), '%S')
    entry.config(validate='key', validatecommand=vcmd)
