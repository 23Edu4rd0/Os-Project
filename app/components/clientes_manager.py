"""
Gerenciador de clientes
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, DANGER
from tkinter import messagebox

from database import db_manager


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
        top_frame.pack(fill="x", padx=5, pady=5)
        
        # Frame esquerdo - botões
        buttons_frame = tb.Frame(top_frame)
        buttons_frame.pack(side="left")
        
        tb.Button(buttons_frame, text="Novo", bootstyle=SUCCESS, 
                 command=self.novo_cliente).pack(side="left", padx=5)
        tb.Button(buttons_frame, text="Editar", 
                 command=self.editar_cliente).pack(side="left", padx=5)
        tb.Button(buttons_frame, text="Excluir", bootstyle="danger", 
                 command=self.excluir_cliente).pack(side="left", padx=5)
        tb.Button(buttons_frame, text="Recarregar", 
                 command=self.carregar_dados).pack(side="left", padx=5)
        
        # Frame direito - pesquisa
        search_frame = tb.Frame(top_frame)
        search_frame.pack(side="right")
        
        tb.Label(search_frame, text="Pesquisar:", font=("Arial", 10)).pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = tb.Entry(search_frame, textvariable=self.search_var, width=25,
                                    font=("Arial", 10))
        self.search_entry.pack(side="left", padx=(0, 5))
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        tb.Button(search_frame, text="🔍", command=self.pesquisar_clientes,
                 bootstyle="info-outline", width=3).pack(side="left", padx=(0, 5))
        tb.Button(search_frame, text="✖", command=self.limpar_pesquisa,
                 bootstyle="secondary-outline", width=3).pack(side="left")
        
        # TreeView
        columns = ("id", "nome", "cpf", "telefone", "email", "rua", "numero", "bairro", "cidade", "estado", "referencia")
        self.tree = tb.Treeview(self.parent, columns=columns, show="headings")
        
        # Configurar colunas
        column_configs = [
            ("id", "ID", 60, "center"),
            ("nome", "Nome", 180, "w"),
            ("cpf", "CPF", 120, "center"),
            ("telefone", "Telefone", 120, "center"),
            ("email", "Email", 150, "w"),
            ("rua", "Rua", 150, "w"),
            ("numero", "Nº", 60, "center"),
            ("bairro", "Bairro", 120, "w"),
            ("cidade", "Cidade", 120, "w"),
            ("estado", "UF", 60, "center"),
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
                # cliente é uma tupla: (id, nome, cpf, telefone, email, rua, numero, bairro, cidade, estado, referencia)
                if len(cliente) >= 11:
                    self.tree.insert('', 'end', values=(
                        cliente[0] or '',   # id
                        cliente[1] or '',   # nome
                        cliente[2] or '',   # cpf
                        cliente[3] or '',   # telefone
                        cliente[4] or '',   # email
                        cliente[5] or '',   # rua
                        cliente[6] or '',   # numero
                        cliente[7] or '',   # bairro
                        cliente[8] or '',   # cidade
                        cliente[9] or '',   # estado
                        cliente[10] or ''   # referencia
                    ))
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao carregar clientes: {e}')
        
        # Restaurar título original
        try:
            self.parent.master.title("Sistema de Ordem de Serviço - Versão Modular")
        except:
            pass  # Ignorar se não conseguir acessar o master
    
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
        win.geometry('600x600')
        
        # Container principal
        main_frame = tb.Frame(win)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Canvas e Scrollbar para scroll
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = tb.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)
        
        # Configurar scroll
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para o conteúdo (dentro do scrollable_frame)
        frame = tb.Frame(scrollable_frame, padding=15)
        frame.pack(fill='both', expand=True)
        
        # Campos
        fields = {}
        
        # Dados pessoais
        tb.Label(frame, text="DADOS PESSOAIS", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')
        
        personal_fields = [
            ('nome', 'Nome:'),
            ('cpf', 'CPF:'),
            ('telefone', 'Telefone:'),
            ('email', 'Email:')
        ]
        
        for i, (key, label) in enumerate(personal_fields, 1):
            tb.Label(frame, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            fields[key] = tb.Entry(frame, width=40)
            fields[key].grid(row=i, column=1, sticky='w', padx=5, pady=5)
        
        # Endereço
        tb.Label(frame, text="ENDEREÇO", font=('Arial', 12, 'bold')).grid(row=6, column=0, columnspan=2, pady=(15, 10), sticky='w')
        
        address_fields = [
            ('rua', 'Rua:'),
            ('numero', 'Número:'),
            ('bairro', 'Bairro:'),
            ('cidade', 'Cidade:'),
            ('estado', 'Estado:')
        ]
        
        for i, (key, label) in enumerate(address_fields, 7):
            tb.Label(frame, text=label).grid(row=i, column=0, sticky='e', padx=5, pady=5)
            if key == 'numero':
                fields[key] = tb.Entry(frame, width=15)
            elif key == 'estado':
                fields[key] = tb.Entry(frame, width=10)
            else:
                fields[key] = tb.Entry(frame, width=40)
            fields[key].grid(row=i, column=1, sticky='w', padx=5, pady=5)
        
        # Referência
        tb.Label(frame, text="OUTROS", font=('Arial', 12, 'bold')).grid(row=12, column=0, columnspan=2, pady=(15, 10), sticky='w')
        
        tb.Label(frame, text='Referência:').grid(row=13, column=0, sticky='e', padx=5, pady=5)
        fields['referencia'] = tb.Entry(frame, width=40)
        fields['referencia'].grid(row=13, column=1, sticky='w', padx=5, pady=5)
        
        # Preencher dados se editando
        if data:
            fields['nome'].insert(0, data[1] if len(data) > 1 else '')
            fields['cpf'].insert(0, data[2] if len(data) > 2 and data[2] else '')
            fields['telefone'].insert(0, data[3] if len(data) > 3 and data[3] else '')
            fields['email'].insert(0, data[4] if len(data) > 4 and data[4] else '')
            fields['rua'].insert(0, data[5] if len(data) > 5 and data[5] else '')
            fields['numero'].insert(0, data[6] if len(data) > 6 and data[6] else '')
            fields['bairro'].insert(0, data[7] if len(data) > 7 and data[7] else '')
            fields['cidade'].insert(0, data[8] if len(data) > 8 and data[8] else '')
            fields['estado'].insert(0, data[9] if len(data) > 9 and data[9] else '')
            fields['referencia'].insert(0, data[10] if len(data) > 10 and data[10] else '')
        
        # Botões
        btn_frame = tb.Frame(frame)
        btn_frame.grid(row=14, column=0, columnspan=2, pady=20)
        
        # Função para scroll com mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind scroll events
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_mousewheel)
        canvas.bind('<Leave>', _unbind_mousewheel)
        
        def salvar():
            dados = {key: field.get().strip() for key, field in fields.items()}
            
            if not dados['nome']:
                messagebox.showerror('Erro', 'Nome é obrigatório.')
                return
            
            try:
                if data and data[0]:  # tem ID
                    # Atualizar
                    db_manager.atualizar_cliente(
                        int(data[0]), dados['nome'], dados['cpf'] or None,
                        dados['telefone'] or None, dados['email'] or None,
                        None, dados['referencia'] or None,  # endereco antigo = None
                        dados['rua'] or None, dados['numero'] or None,
                        dados['bairro'] or None, dados['cidade'] or None,
                        dados['estado'] or None
                    )
                else:
                    # Criar - usar nova função completa
                    db_manager.upsert_cliente_completo(
                        dados['nome'], dados['cpf'] or None, dados['telefone'] or None,
                        dados['email'] or None, None, dados['referencia'] or None,
                        dados['rua'] or None, dados['numero'] or None,
                        dados['bairro'] or None, dados['cidade'] or None,
                        dados['estado'] or None
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

    def on_search(self, event=None):
        """Pesquisa automaticamente enquanto digita (com debounce)"""
        # Cancelar timer anterior se existir
        if hasattr(self, '_search_timer'):
            self.parent.after_cancel(self._search_timer)
        
        # Criar novo timer para evitar pesquisas excessivas
        self._search_timer = self.parent.after(500, self.pesquisar_clientes)  # 500ms de delay

    def pesquisar_clientes(self):
        """Pesquisa clientes por nome, ID ou telefone"""
        termo_pesquisa = self.search_var.get().strip()
        
        # Limpar TreeView
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not termo_pesquisa:
            # Se não há termo de pesquisa, carregar todos
            self.carregar_dados()
            return
        
        try:
            # Buscar clientes do banco
            clientes = db_manager.listar_clientes(limite=1000)  # Buscar muitos para filtrar
            
            # Filtrar clientes
            clientes_filtrados = []
            termo_lower = termo_pesquisa.lower()
            
            for cliente in clientes:
                encontrou = False
                
                # cliente é uma tupla: (nome_cliente, cpf_cliente, telefone_cliente)
                if len(cliente) >= 3:
                    nome = str(cliente[0] or '').lower()
                    cpf = str(cliente[1] or '').lower()
                    telefone = str(cliente[2] or '').lower()
                    
                    # Pesquisar nos campos disponíveis
                    if (termo_lower in nome or 
                        termo_lower in cpf or 
                        termo_lower in telefone):
                        encontrou = True
                        clientes_filtrados.append(cliente)
            
            # Exibir clientes filtrados
            for cliente in clientes_filtrados:
                if len(cliente) >= 3:
                    self.tree.insert('', 'end', values=(
                        '',  # id (não disponível)
                        cliente[0] or '',  # nome
                        cliente[1] or '',  # cpf
                        cliente[2] or '',  # telefone
                        '',  # email (não disponível)
                        '',  # rua (não disponível)
                        '',  # numero (não disponível)
                        '',  # bairro (não disponível)
                        '',  # cidade (não disponível)
                        '',  # estado (não disponível)
                        ''   # referencia (não disponível)
                    ))
                
                # Pesquisar por telefone (remover caracteres especiais)
                telefone = cliente.get('telefone', '') or ''
                if telefone:
                    telefone_limpo = ''.join(filter(str.isdigit, telefone))
                    termo_limpo = ''.join(filter(str.isdigit, termo_pesquisa))
                    if termo_limpo and termo_limpo in telefone_limpo:
                        clientes_filtrados.append(cliente)
                        encontrou = True
                        continue
            
            # Exibir resultados
            for cliente in clientes_filtrados:
                self.tree.insert('', 'end', values=(
                    cliente.get('id'),
                    cliente.get('nome'),
                    cliente.get('cpf'),
                    cliente.get('telefone'),
                    cliente.get('email'),
                    cliente.get('rua', ''),
                    cliente.get('numero', ''),
                    cliente.get('bairro', ''),
                    cliente.get('cidade', ''),
                    cliente.get('estado', ''),
                    cliente.get('referencia', '')
                ))
            
            # Mostrar quantidade de resultados (apenas se não encontrou nada)
            total = len(clientes_filtrados)
            if total == 0:
                # Não mostrar popup para evitar loop infinito, apenas limpar título
                try:
                    self.parent.master.title("Sistema de Ordem de Serviço - Nenhum resultado")
                except:
                    pass
            else:
                try:
                    self.parent.master.title(f"Sistema de Ordem de Serviço - {total} cliente(s) encontrado(s)")
                except:
                    pass
                
        except Exception as e:
            print(f"Erro ao pesquisar: {e}")  # Log em vez de popup para evitar loops

    def limpar_pesquisa(self):
        """Limpa a pesquisa e recarrega todos os dados"""
        self.search_var.set("")
        self.carregar_dados()
        self.parent.master.title("Sistema de Ordem de Serviço - Versão Modular")

        self.parent.master.title("Sistema de Ordem de Serviço - Versão Modular")
