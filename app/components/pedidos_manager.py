"""
Gerenciador de pedidos/ordens de serviço
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, DANGER, INFO
from tkinter import messagebox
from datetime import datetime

from database.db_manager import db_manager


class PedidosManager:
    """Gerencia a interface de pedidos"""
    
    def __init__(self, parent):
        self.parent = parent
        self.status_var = tk.StringVar(value="todos")
        self._setup_interface()
        self.carregar_dados()
        
    def _setup_interface(self):
        """Configura a interface"""
        # Frame superior com filtros e botões
        top_frame = tb.Frame(self.parent)
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # Filtro de status
        tb.Label(top_frame, text="Filtrar por Status:", 
                font=("Arial", 10, "bold")).pack(side="left", padx=(5, 0))
        
        status_options = ["todos", "em produção", "enviado", "entregue", "cancelado"]
        status_combo = tb.Combobox(top_frame, textvariable=self.status_var, 
                                  values=status_options, width=15, state="readonly")
        status_combo.pack(side="left", padx=5, pady=5)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self.carregar_dados())
        
        # Botões
        btn_frame = tb.Frame(top_frame)
        btn_frame.pack(side="right", padx=5)
        
        tb.Button(btn_frame, text="➕ Novo", bootstyle=SUCCESS, 
                 command=self.novo_pedido).pack(side="left", padx=2)
        tb.Button(btn_frame, text="🔄 Recarregar", 
                 command=self.carregar_dados).pack(side="left", padx=2)
        
        # Frame principal com scroll
        main_frame = tb.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Canvas com scrollbar
        self.canvas = tk.Canvas(main_frame, highlightthickness=0)
        self.scrollbar = tb.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tb.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
    def carregar_dados(self):
        """Carrega pedidos em formato de cards"""
        # Limpar cards existentes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            status_filtro = self.status_var.get()
            pedidos = db_manager.listar_pedidos_ordenados_por_prazo() or []
            
            if status_filtro != "todos":
                pedidos = [p for p in pedidos if p.get('status', 'em produção') == status_filtro]
            
            if not pedidos:
                tb.Label(
                    self.scrollable_frame,
                    text="📋 Nenhum pedido encontrado",
                    font=("Arial", 14),
                    foreground="gray"
                ).pack(pady=50)
                return
            
            # Criar cards
            for i, pedido in enumerate(pedidos):
                self._criar_card_pedido(pedido)
                
        except Exception as e:
            tb.Label(
                self.scrollable_frame,
                text=f"❌ Erro ao carregar pedidos: {e}",
                font=("Arial", 12),
                foreground="red"
            ).pack(pady=20)
    
    def _criar_card_pedido(self, pedido):
        """Cria um card para exibir pedido"""
        # Frame do card
        card = tb.Frame(self.scrollable_frame, padding=15, relief="solid", borderwidth=1)
        card.pack(fill="x", padx=10, pady=5)
        
        # Header
        header = tb.Frame(card)
        header.pack(fill="x", pady=(0, 10))
        
        # OS e ID
        os_label = tb.Label(header, text=f"OS #{pedido.get('numero_os', 'N/A')}", 
                           font=("Arial", 14, "bold"), foreground="#0066CC")
        os_label.pack(side="left")
        
        # Status
        status = pedido.get('status', 'em produção')
        status_colors = {
            'em produção': '#FF6B35',
            'enviado': '#4ECDC4',
            'entregue': '#45B7D1',
            'cancelado': '#F7931E'
        }
        status_color = status_colors.get(status, '#9B59B6')
        
        status_label = tb.Label(header, text=status.upper(), 
                               font=("Arial", 10, "bold"), 
                               foreground="white", background=status_color, padding=(8, 4))
        status_label.pack(side="right")
        
        # Informações principais
        info_frame = tb.Frame(card)
        info_frame.pack(fill="x", pady=(0, 10))
        
        # Cliente
        tb.Label(info_frame, text=f"Cliente: {pedido.get('nome_cliente', 'N/A')}", 
                font=("Arial", 11, "bold")).pack(anchor="w")
        
        # Valor
        valor = pedido.get('valor_total', 0) or pedido.get('valor_produto', 0)
        try:
            valor_formatado = f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            valor_formatado = "R$ 0,00"
            
        tb.Label(info_frame, text=f"Valor: {valor_formatado}", 
                font=("Arial", 11), foreground="#4CAF50").pack(anchor="w")
        
        # Prazo
        prazo_original = pedido.get('prazo_dias', pedido.get('prazo'))
        data_emissao = pedido.get('data_emissao')
        
        if prazo_original and data_emissao:
            try:
                # Calcular prazo real baseado na data de emissão
                from datetime import datetime
                data_emissao_dt = datetime.strptime(data_emissao, '%Y-%m-%d %H:%M:%S')
                agora = datetime.now()
                dias_passados = (agora - data_emissao_dt).days
                prazo_restante = int(prazo_original) - dias_passados
                
                if prazo_restante <= 0:
                    prazo_text = f"{abs(prazo_restante)} dias de atraso"
                    prazo_color = "#FF5252"
                elif prazo_restante <= 3:
                    prazo_text = f"{prazo_restante} dias restantes"
                    prazo_color = "#FF9800"
                elif prazo_restante <= 10:
                    prazo_text = f"{prazo_restante} dias restantes"
                    prazo_color = "#FFC107"
                else:
                    prazo_text = f"{prazo_restante} dias restantes"
                    prazo_color = "#4CAF50"
            except:
                prazo_text = f"{prazo_original} dias (original)"
                prazo_color = "#9E9E9E"
        else:
            prazo_text = "Sem prazo definido"
            prazo_color = "#9E9E9E"
            
        tb.Label(info_frame, text=f"Prazo: {prazo_text}", 
                font=("Arial", 10), foreground=prazo_color).pack(anchor="w")
        
        # Descrição
        descricao = pedido.get('detalhes_produto', pedido.get('descricao', 'Sem descrição'))
        if len(descricao) > 100:
            descricao = descricao[:100] + "..."
            
        desc_frame = tb.LabelFrame(card, text="Descrição", padding=5)
        desc_frame.pack(fill="x", pady=(0, 10))
        
        tb.Label(desc_frame, text=descricao, wraplength=500, justify="left").pack(anchor="w")
        
        # Botões de ação
        btn_frame = tb.Frame(card)
        btn_frame.pack(fill="x")
        
        tb.Button(btn_frame, text="✏️ Editar", bootstyle="primary-outline", width=12,
                 command=lambda p=pedido: self.editar_pedido(p)).pack(side="left", padx=(0, 5))
        
        tb.Button(btn_frame, text="🔄 Status", bootstyle="info-outline", width=12,
                 command=lambda p=pedido: self.alterar_status(p)).pack(side="left", padx=(0, 5))
        
        tb.Button(btn_frame, text="🗑️ Excluir", bootstyle="danger-outline", width=12,
                 command=lambda p=pedido: self.excluir_pedido(p)).pack(side="left")
    
    def novo_pedido(self):
        """Cria novo pedido"""
        messagebox.showinfo('Info', 'Use a aba "Formulário" para criar novos pedidos.')
    
    def editar_pedido(self, pedido):
        """Edita pedido existente"""
        win = tb.Toplevel(self.parent)
        win.title(f'Editar OS #{pedido.get("numero_os")}')
        win.transient(self.parent)
        win.grab_set()
        win.geometry('600x500')
        
        frame = tb.Frame(win, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Título
        tb.Label(frame, text=f'Editar Ordem de Serviço #{pedido.get("numero_os")}', 
                font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Campos editáveis
        fields = {}
        
        # Cliente
        tb.Label(frame, text='Cliente:', font=('Arial', 10, 'bold')).pack(anchor='w')
        fields['cliente'] = tb.Entry(frame, width=50)
        fields['cliente'].pack(fill='x', pady=(0, 10))
        fields['cliente'].insert(0, pedido.get('nome_cliente', ''))
        
        # Telefone
        tb.Label(frame, text='Telefone:', font=('Arial', 10, 'bold')).pack(anchor='w')
        fields['telefone'] = tb.Entry(frame, width=20)
        fields['telefone'].pack(anchor='w', pady=(0, 10))
        fields['telefone'].insert(0, pedido.get('telefone_cliente', ''))
        
        # Descrição/Detalhes
        tb.Label(frame, text='Descrição do Produto:', font=('Arial', 10, 'bold')).pack(anchor='w')
        fields['descricao'] = tk.Text(frame, width=60, height=8, wrap='word')
        fields['descricao'].pack(fill='both', expand=True, pady=(0, 10))
        fields['descricao'].insert('1.0', pedido.get('detalhes_produto', ''))
        
        # Frame para valores
        valores_frame = tb.Frame(frame)
        valores_frame.pack(fill='x', pady=(0, 10))
        
        # Valor do produto
        tb.Label(valores_frame, text='Valor:', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 10))
        fields['valor'] = tb.Entry(valores_frame, width=15)
        fields['valor'].grid(row=0, column=1, sticky='w', padx=(0, 20))
        valor_atual = pedido.get('valor_produto', 0)
        if valor_atual:
            fields['valor'].insert(0, f"{float(valor_atual):.2f}")
        
        # Frete
        tb.Label(valores_frame, text='Frete:', font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='w', padx=(0, 10))
        fields['frete'] = tb.Entry(valores_frame, width=15)
        fields['frete'].grid(row=0, column=3, sticky='w')
        frete_atual = pedido.get('frete', 0)
        if frete_atual:
            fields['frete'].insert(0, f"{float(frete_atual):.2f}")
        
        # Prazo
        prazo_frame = tb.Frame(frame)
        prazo_frame.pack(fill='x', pady=(0, 20))
        
        tb.Label(prazo_frame, text='Prazo (dias):', font=('Arial', 10, 'bold')).pack(side='left')
        fields['prazo'] = tb.Entry(prazo_frame, width=10)
        fields['prazo'].pack(side='left', padx=(10, 0))
        prazo_atual = pedido.get('prazo_dias', pedido.get('prazo', ''))
        if prazo_atual:
            fields['prazo'].insert(0, str(prazo_atual))
        
        def salvar_edicao():
            try:
                # Coletar dados do formulário
                novo_cliente = fields['cliente'].get().strip()
                novo_telefone = fields['telefone'].get().strip()
                nova_descricao = fields['descricao'].get('1.0', 'end-1c').strip()
                novo_valor = fields['valor'].get().strip()
                novo_frete = fields['frete'].get().strip()
                novo_prazo = fields['prazo'].get().strip()
                
                # Validações
                if not novo_cliente:
                    messagebox.showerror('Erro', 'Nome do cliente é obrigatório!')
                    return
                
                if not nova_descricao:
                    messagebox.showerror('Erro', 'Descrição do produto é obrigatória!')
                    return
                
                # Preparar dados para atualização
                campos_atualizacao = {
                    'nome_cliente': novo_cliente,
                    'telefone_cliente': novo_telefone or None,
                    'detalhes_produto': nova_descricao
                }
                
                # Processar valores numéricos
                if novo_valor:
                    try:
                        campos_atualizacao['valor_produto'] = float(novo_valor.replace(',', '.'))
                    except ValueError:
                        messagebox.showerror('Erro', 'Valor do produto inválido!')
                        return
                
                if novo_frete:
                    try:
                        campos_atualizacao['frete'] = float(novo_frete.replace(',', '.'))
                    except ValueError:
                        messagebox.showerror('Erro', 'Valor do frete inválido!')
                        return
                
                if novo_prazo:
                    try:
                        campos_atualizacao['prazo'] = int(novo_prazo)
                    except ValueError:
                        messagebox.showerror('Erro', 'Prazo deve ser um número inteiro!')
                        return
                
                # Atualizar no banco
                sucesso = db_manager.atualizar_ordem(pedido['id'], campos_atualizacao)
                
                if sucesso:
                    messagebox.showinfo('Sucesso', f'OS #{pedido.get("numero_os")} atualizada com sucesso!')
                    self.carregar_dados()  # Recarregar lista
                    win.destroy()
                else:
                    messagebox.showerror('Erro', 'Falha ao salvar alterações no banco de dados!')
                    
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao salvar: {str(e)}')
        
        # Botões
        btn_frame = tb.Frame(frame)
        btn_frame.pack(fill='x', pady=10)
        
        tb.Button(btn_frame, text='💾 Salvar', bootstyle=SUCCESS, 
                 command=salvar_edicao).pack(side='left', padx=(0, 10))
        tb.Button(btn_frame, text='❌ Cancelar', 
                 command=win.destroy).pack(side='left')
    
    def alterar_status(self, pedido):
        """Altera status do pedido"""
        status_atual = pedido.get('status', 'em produção')
        statuses = ["em produção", "enviado", "entregue", "cancelado"]
        
        win = tb.Toplevel(self.parent)
        win.title('Alterar Status')
        win.transient(self.parent)
        win.grab_set()
        win.geometry('350x200')
        
        frame = tb.Frame(win, padding=20)
        frame.pack(fill='both', expand=True)
        
        tb.Label(frame, text=f'OS #{pedido.get("numero_os")} - {pedido.get("nome_cliente")}', 
                font=('Arial', 12, 'bold')).pack(pady=(0, 15))
        
        tb.Label(frame, text='Novo Status:', font=('Arial', 10)).pack(anchor='w')
        
        status_var = tb.StringVar(value=status_atual)
        status_combo = tb.Combobox(frame, textvariable=status_var, values=statuses, 
                                  state="readonly", width=20)
        status_combo.pack(pady=(5, 20))
        
        def salvar():
            novo_status = status_var.get()
            if novo_status != status_atual:
                try:
                    success = db_manager.atualizar_status_pedido(pedido['id'], novo_status)
                    if success:
                        self.carregar_dados()
                        messagebox.showinfo('Sucesso', f'Status alterado para "{novo_status}"!')
                        win.destroy()
                    else:
                        messagebox.showerror('Erro', 'Falha ao alterar status.')
                except Exception as e:
                    messagebox.showerror('Erro', f'Erro ao alterar status: {e}')
            else:
                win.destroy()
        
        btn_frame = tb.Frame(frame)
        btn_frame.pack()
        
        tb.Button(btn_frame, text='💾 Salvar', bootstyle=SUCCESS, 
                 command=salvar).pack(side='left', padx=5)
        tb.Button(btn_frame, text='❌ Cancelar', 
                 command=win.destroy).pack(side='left', padx=5)
    
    def excluir_pedido(self, pedido):
        """Exclui pedido"""
        if messagebox.askyesno('Confirmar Exclusão', 
                              f'Tem certeza que deseja excluir a OS #{pedido.get("numero_os")}?\n\n'
                              f'Cliente: {pedido.get("nome_cliente")}\n'
                              f'Esta ação não pode ser desfeita.'):
                try:
                    success = db_manager.deletar_pedido(pedido['id'])
                    if success:
                        self.carregar_dados()
                        messagebox.showinfo('Sucesso', 'Pedido excluído com sucesso!')
                    else:
                        messagebox.showerror('Erro', 'Falha ao excluir pedido.')
                except Exception as e:
                    messagebox.showerror('Erro', f'Erro ao excluir pedido: {e}')
