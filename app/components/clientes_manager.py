"""
Gerenciador de clientes
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, DANGER
from tkinter import messagebox

from database.db_manager import db_manager


class ClientesManager:
    """Gerencia a interface de clientes"""
    
    def __init__(self, parent):
        self.parent = parent
        self._setup_interface()
        self.carregar_dados()
        
    def _setup_interface(self):
        """Configura a interface"""
        # Botões superiores
        top_frame = tb.Frame(self.parent)
        top_frame.pack(fill="x")
        
        tb.Button(top_frame, text="Novo", bootstyle=SUCCESS, 
                 command=self.novo_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_frame, text="Editar", 
                 command=self.editar_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_frame, text="Excluir", bootstyle=DANGER, 
                 command=self.excluir_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_frame, text="Recarregar", 
                 command=self.carregar_dados).pack(side="right", padx=5, pady=5)
        
        # TreeView
        columns = ("id", "nome", "cpf", "telefone", "email", "endereco", "referencia")
        self.tree = tb.Treeview(self.parent, columns=columns, show="headings")
        
        # Configurar colunas
        column_configs = [
            ("id", "ID", 60, "center"),
            ("nome", "Nome", 180, "w"),
            ("cpf", "CPF", 120, "center"),
            ("telefone", "Telefone", 120, "center"),
            ("email", "Email", 150, "w"),
            ("endereco", "Endereço", 200, "w"),
            ("referencia", "Referência", 150, "w"),
        ]
        
        for col, text, width, anchor in column_configs:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor)
        
        # Scrollbar
        scrollbar = tb.Scrollbar(self.parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 8))
        scrollbar.pack(side="right", fill="y", pady=(0, 8))
        
        # SCROLL COM MOUSE WHEEL - COM DEBUG
        def on_mousewheel(event):
            print(f"SCROLL CLIENTES! Delta: {event.delta}")
            direction = -1 if event.delta > 0 else 1
            self.tree.yview_scroll(direction, "units")
        
        # Bind do scroll
        self.tree.bind("<MouseWheel>", on_mousewheel)
        print("Scroll configurado para clientes com debug ativo")
        
    def carregar_dados(self):
        """Carrega dados dos clientes"""
        # Limpar dados existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            clientes = db_manager.listar_clientes(500)
            for cliente in clientes:
                self.tree.insert('', 'end', values=(
                    cliente.get('id'),
                    cliente.get('nome'),
                    cliente.get('cpf'),
                    cliente.get('telefone'),
                    cliente.get('email'),
                    cliente.get('endereco', ''),
                    cliente.get('referencia', '')
                ))
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao carregar clientes: {e}')
    
    def novo_cliente(self):
        """Abre modal para novo cliente"""
        self._abrir_modal_cliente()
    
    def editar_cliente(self):
        """Edita cliente selecionado"""
        selected = self._get_selected()
        if not selected:
            messagebox.showinfo('Info', 'Selecione um cliente para editar.')
            return
            
        data = {
            'id': selected[0],
            'nome': selected[1],
            'cpf': selected[2],
            'telefone': selected[3],
            'email': selected[4],
            'endereco': selected[5] if len(selected) > 5 else '',
            'referencia': selected[6] if len(selected) > 6 else ''
        }
        self._abrir_modal_cliente(data)
    
    def excluir_cliente(self):
        """Exclui cliente selecionado"""
        selected = self._get_selected()
        if not selected:
            messagebox.showinfo('Info', 'Selecione um cliente para excluir.')
            return
            
        if messagebox.askyesno('Confirmar', f"Excluir cliente '{selected[1]}'?"):
            try:
                db_manager.deletar_cliente(int(selected[0]))
                self.carregar_dados()
                messagebox.showinfo('Sucesso', 'Cliente excluído com sucesso!')
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao excluir cliente: {e}')
    
    def _get_selected(self):
        """Obtém item selecionado"""
        selection = self.tree.selection()
        if not selection:
            return None
        return self.tree.item(selection[0], 'values')
    
    def _abrir_modal_cliente(self, data=None):
        """Abre modal de cliente"""
        win = tb.Toplevel(self.parent)
        win.title('Novo Cliente' if not data else 'Editar Cliente')
        win.transient(self.parent)
        win.grab_set()
        win.geometry('500x350')
        
        frame = tb.Frame(win, padding=10)
        frame.pack(fill='both', expand=True)
        
        # Campos
        fields = {}
        field_configs = [
            ('nome', 'Nome:'),
            ('cpf', 'CPF:'),
            ('telefone', 'Telefone:'),
            ('email', 'Email:'),
            ('endereco', 'Endereço:'),
            ('referencia', 'Referência:')
        ]
        
        for i, (key, label) in enumerate(field_configs):
            tb.Label(frame, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            fields[key] = tb.Entry(frame, width=40)
            fields[key].grid(row=i, column=1, sticky='w', padx=5, pady=5)
            
            if data and key in data:
                fields[key].insert(0, data[key] or '')
        
        # Botões
        btn_frame = tb.Frame(frame)
        btn_frame.grid(row=len(field_configs), column=0, columnspan=2, pady=10)
        
        def salvar():
            dados = {key: field.get().strip() for key, field in fields.items()}
            
            if not dados['nome']:
                messagebox.showerror('Erro', 'Nome é obrigatório.')
                return
            
            try:
                if data and data.get('id'):
                    # Atualizar
                    db_manager.atualizar_cliente(
                        int(data['id']), dados['nome'], dados['cpf'] or None,
                        dados['telefone'] or None, dados['email'] or None,
                        dados['endereco'] or None, dados['referencia'] or None
                    )
                else:
                    # Criar
                    db_manager.upsert_cliente(
                        dados['nome'], dados['cpf'] or None, dados['telefone'] or None,
                        dados['email'] or None, dados['endereco'] or None, 
                        dados['referencia'] or None
                    )
                
                self.carregar_dados()
                win.destroy()
                messagebox.showinfo('Sucesso', 'Cliente salvo com sucesso!')
                
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao salvar cliente: {e}')
        
        tb.Button(btn_frame, text='Salvar', bootstyle=SUCCESS, 
                 command=salvar).pack(side='left', padx=5)
        tb.Button(btn_frame, text='Cancelar', 
                 command=win.destroy).pack(side='left', padx=5)
