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
        
        # SCROLL COM MOUSE WHEEL - COM DEBUG
        def on_mousewheel(event):
            print(f"SCROLL PEDIDOS! Delta: {event.delta}")
            direction = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(direction, "units")
        
        # Bind do scroll
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", on_mousewheel)
        print("Scroll configurado para pedidos com debug ativo")
        
    def carregar_dados(self):
        """Carrega pedidos em formato de cards com layout 3x3"""
        # Limpar cards existentes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Configurar grid do scrollable_frame
        self.scrollable_frame.columnconfigure(0, weight=1)
        self.scrollable_frame.columnconfigure(1, weight=1)
        self.scrollable_frame.columnconfigure(2, weight=1)
        
        try:
            status_filtro = self.status_var.get()
            pedidos = db_manager.listar_pedidos_ordenados_por_prazo() or []
            
            if status_filtro != "todos":
                pedidos = [p for p in pedidos if p.get('status', 'em produção') == status_filtro]
            
            if not pedidos:
                empty_label = tb.Label(
                    self.scrollable_frame,
                    text="📋 Nenhum pedido encontrado",
                    font=("Arial", 14),
                    foreground="gray"
                )
                empty_label.grid(row=0, column=0, columnspan=3, pady=50)
                return
            
            # Criar cards em grid 3x3
            for i, pedido in enumerate(pedidos):
                row = i // 3  # Linha atual
                col = i % 3   # Coluna atual (0, 1, 2)
                self._criar_card_pedido(pedido, row, col)
                
        except Exception as e:
            error_label = tb.Label(
                self.scrollable_frame,
                text=f"❌ Erro ao carregar pedidos: {e}",
                font=("Arial", 12),
                foreground="red"
            )
            error_label.grid(row=0, column=0, columnspan=3, pady=20)
    
    def _criar_card_pedido(self, pedido, row, col):
        """Cria um card para exibir pedido em grid 3x3"""
        # Frame do card com tamanho fixo
        card = tb.Frame(self.scrollable_frame, padding=12, relief="solid", borderwidth=1)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        # Definir tamanho mínimo do card
        card.configure(width=350, height=280)
        
        # Header compacto
        header = tb.Frame(card)
        header.pack(fill="x", pady=(0, 8))
        
        # OS e ID em layout compacto
        os_label = tb.Label(header, text=f"OS #{pedido.get('numero_os', 'N/A')}", 
                           font=("Arial", 12, "bold"), foreground="#0066CC")
        os_label.pack(side="left")
        
        # Status compacto
        status = pedido.get('status', 'em produção')
        status_colors = {
            'em produção': '#FF6B35',
            'enviado': '#4ECDC4',
            'entregue': '#45B7D1',
            'cancelado': '#F7931E'
        }
        status_color = status_colors.get(status, '#9B59B6')
        
        status_label = tb.Label(header, text=status.upper(), 
                               font=("Arial", 8, "bold"), 
                               foreground="white", background=status_color, padding=(6, 2))
        status_label.pack(side="right")
        
        # Info frame compacto
        info_frame = tb.Frame(card)
        info_frame.pack(fill="x", pady=(0, 8))
        
        # Cliente
        cliente_text = pedido.get('nome_cliente', 'N/A')
        if len(cliente_text) > 25:
            cliente_text = cliente_text[:25] + "..."
        tb.Label(info_frame, text=f"Cliente: {cliente_text}", 
                font=("Arial", 9, "bold"), foreground="#333").pack(anchor="w")
        
        # Valor
        valor = pedido.get('valor_total', 0) or pedido.get('valor_produto', 0)
        try:
            valor_formatado = f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            valor_formatado = "R$ 0,00"
            
        tb.Label(info_frame, text=f"Valor: {valor_formatado}", 
                font=("Arial", 9), foreground="#4CAF50").pack(anchor="w")
        
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
                    prazo_text = f"{abs(prazo_restante)}d atraso"
                    prazo_color = "#FF5252"
                elif prazo_restante <= 3:
                    prazo_text = f"{prazo_restante}d restantes"
                    prazo_color = "#FF9800"
                elif prazo_restante <= 10:
                    prazo_text = f"{prazo_restante}d restantes"
                    prazo_color = "#FFC107"
                else:
                    prazo_text = f"{prazo_restante}d restantes"
                    prazo_color = "#4CAF50"
            except:
                prazo_text = f"{prazo_original}d (orig)"
                prazo_color = "#9E9E9E"
        else:
            prazo_text = "Sem prazo"
            prazo_color = "#9E9E9E"
            
        tb.Label(info_frame, text=f"Prazo: {prazo_text}", 
                font=("Arial", 9), foreground=prazo_color).pack(anchor="w")
        
        # Descrição compacta
        descricao = pedido.get('detalhes_produto', pedido.get('descricao', 'Sem descrição'))
        if len(descricao) > 80:
            descricao = descricao[:80] + "..."
            
        desc_frame = tb.LabelFrame(card, text="Descrição", padding=3)
        desc_frame.pack(fill="both", expand=True, pady=(0, 8))
        
        tb.Label(desc_frame, text=descricao, wraplength=280, justify="left", 
                font=("Arial", 8)).pack(anchor="w", fill="both", expand=True)
        
        # Botões compactos
        btn_frame = tb.Frame(card)
        btn_frame.pack(fill="x")
        
        tb.Button(btn_frame, text="✏️", bootstyle="primary-outline", width=3,
                 command=lambda p=pedido: self.editar_pedido(p)).pack(side="left", padx=(0, 2))
        
        tb.Button(btn_frame, text="🔄", bootstyle="info-outline", width=3,
                 command=lambda p=pedido: self.alterar_status(p)).pack(side="left", padx=(0, 2))
        
        tb.Button(btn_frame, text="🗑️", bootstyle="danger-outline", width=3,
                 command=lambda p=pedido: self.excluir_pedido(p)).pack(side="left")
        
        # BIND DE SCROLL PARA TODOS OS WIDGETS DO CARD
        def scroll_card(event):
            print(f"SCROLL NO CARD! Delta: {event.delta}")
            direction = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(direction, "units")
        
        # Lista de todos os widgets do card para aplicar scroll
        widgets_card = [card, header, os_label, status_label, info_frame, desc_frame, btn_frame]
        
        # Bind scroll em todos os widgets do card
        for widget in widgets_card:
            try:
                widget.bind("<MouseWheel>", scroll_card)
            except:
                pass  # Alguns widgets podem não aceitar bind
    
    def _abrir_modal_pedido_completo(self, pedido_data=None):
        """Abre modal completo para criar/editar pedido - Formulário original com múltiplos produtos"""
        from app.numero_os import Contador
        from documents.os_pdf import OrdemServicoPDF
        from datetime import datetime
        import os
        
        win = tb.Toplevel(self.parent)
        win.title("Nova Ordem de Serviço" if not pedido_data else f"Editar OS #{pedido_data.get('numero_os')}")
        win.transient(self.parent)
        win.grab_set()
        win.geometry("700x800")
        
        # Frame com scroll
        canvas = tk.Canvas(win)
        scrollbar = tb.Scrollbar(win, orient="vertical", command=canvas.yview)
        scrollable_frame = tb.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # SCROLL COM MOUSE WHEEL NO MODAL
        def scroll_modal(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", scroll_modal)
        scrollable_frame.bind("<MouseWheel>", scroll_modal)
        
        # Conteúdo do formulário
        frame = tb.Frame(scrollable_frame, padding=20)
        frame.pack(fill="both", expand=True)
        
        # === CABEÇALHO ===
        if not pedido_data:
            numero_os = Contador.ler_contador()
        else:
            numero_os = pedido_data.get('numero_os', Contador.ler_contador())
            
        os_frame = tb.Frame(frame)
        os_frame.pack(fill="x", pady=(0, 15))
        
        tb.Label(os_frame, text="Nº OS:", font=("Arial", 14, "bold")).pack(side="left")
        numero_label = tb.Label(os_frame, text=str(numero_os), 
                               font=("Arial", 14, "bold"), foreground="blue")
        numero_label.pack(side="left", padx=(5, 0))
        
        # === SEÇÃO CLIENTE ===
        cliente_frame = tb.LabelFrame(frame, text="📋 Informações do Cliente", padding=15)
        cliente_frame.pack(fill="x", pady=(0, 15))
        
        campos = {}
        
        # Buscar clientes do banco de dados
        try:
            clientes_db = db_manager.listar_clientes(1000) or []
            nomes_clientes = [cliente.get('nome', '') for cliente in clientes_db if cliente.get('nome')]
            clientes_dict = {cliente.get('nome', ''): cliente for cliente in clientes_db if cliente.get('nome')}
        except:
            nomes_clientes = []
            clientes_dict = {}
        
        # Nome do Cliente com autocomplete
        tb.Label(cliente_frame, text="Nome do Cliente:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        
        # Frame para cliente com botão "Novo Cliente"
        cliente_input_frame = tb.Frame(cliente_frame)
        cliente_input_frame.pack(fill="x", pady=(0, 8))
        cliente_input_frame.columnconfigure(0, weight=1)
        
        campos['nome_cliente'] = tb.Combobox(cliente_input_frame, values=nomes_clientes, 
                                           font=("Arial", 11), state="normal")
        campos['nome_cliente'].grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Botão para adicionar novo cliente
        btn_novo_cliente = tb.Button(cliente_input_frame, text="➕ Novo Cliente", 
                                    bootstyle="success-outline", width=15,
                                    command=lambda: self._abrir_novo_cliente_modal(win, campos, clientes_dict))
        btn_novo_cliente.grid(row=0, column=1)
        
        # Label de status do cliente
        status_cliente_label = tb.Label(cliente_frame, text="", font=("Arial", 9), foreground="green")
        status_cliente_label.pack(anchor="w")
        
        # Função para autocomplete e preenchimento automático
        def on_cliente_change(event=None):
            nome_digitado = campos['nome_cliente'].get()
            
            if nome_digitado in clientes_dict:
                # Cliente encontrado - preencher dados automaticamente
                cliente = clientes_dict[nome_digitado]
                
                # Limpar campos
                campos['cpf'].delete(0, 'end')
                campos['telefone'].delete(0, 'end')
                
                # Preencher com dados do cliente
                if cliente.get('cpf'):
                    campos['cpf'].insert(0, cliente.get('cpf'))
                if cliente.get('telefone'):
                    campos['telefone'].insert(0, cliente.get('telefone'))
                
                status_cliente_label.config(text=f"✅ Cliente encontrado no banco de dados", foreground="green")
            else:
                status_cliente_label.config(text="ℹ️ Cliente novo - preencha os dados abaixo", foreground="blue")
                
                # Fazer autocomplete na lista
                if nome_digitado:
                    matches = [nome for nome in nomes_clientes if nome_digitado.lower() in nome.lower()]
                    campos['nome_cliente']['values'] = matches[:10]  # Limitar a 10 resultados
                else:
                    campos['nome_cliente']['values'] = nomes_clientes
        
        # Bind eventos
        campos['nome_cliente'].bind('<KeyRelease>', on_cliente_change)
        campos['nome_cliente'].bind('<<ComboboxSelected>>', on_cliente_change)
        campos['nome_cliente'].bind('<FocusIn>', lambda e: on_cliente_change())
        
        # CPF e Telefone na mesma linha
        cpf_tel_frame = tb.Frame(cliente_frame)
        cpf_tel_frame.pack(fill="x", pady=(0, 8))
        cpf_tel_frame.columnconfigure(0, weight=1)
        cpf_tel_frame.columnconfigure(1, weight=1)
        
        # CPF
        cpf_frame = tb.Frame(cpf_tel_frame)
        cpf_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tb.Label(cpf_frame, text="CPF:", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['cpf'] = tb.Entry(cpf_frame, font=("Arial", 11))
        campos['cpf'].pack(fill="x")
        
        # Telefone
        tel_frame = tb.Frame(cpf_tel_frame)
        tel_frame.grid(row=0, column=1, sticky="ew")
        tb.Label(tel_frame, text="Telefone:", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['telefone'] = tb.Entry(tel_frame, font=("Arial", 11))
        campos['telefone'].pack(fill="x")
        
        # === SEÇÃO PRODUTOS ===
        produtos_frame = tb.LabelFrame(frame, text="� Produtos", padding=15)
        produtos_frame.pack(fill="x", pady=(0, 15))
        
        # Container para lista de produtos
        produtos_container = tb.Frame(produtos_frame)
        produtos_container.pack(fill="x", pady=(0, 10))
        
        self.produtos_list = []
        
        def adicionar_produto():
            produto_idx = len(self.produtos_list)
            
            # Adicionar linha separadora se não for o primeiro produto
            if produto_idx > 0:
                separador = tb.Separator(produtos_container, orient="horizontal")
                separador.pack(fill="x", pady=10)
            
            # Frame do produto
            produto_frame = tb.Frame(produtos_container)
            produto_frame.pack(fill="x", pady=(0, 10))
            
            # Título do produto
            titulo_frame = tb.Frame(produto_frame)
            titulo_frame.pack(fill="x", pady=(0, 5))
            
            tb.Label(titulo_frame, text=f"Produto {produto_idx + 1}", 
                    font=("Arial", 11, "bold")).pack(side="left")
            
            # Botão remover (só aparece se não for o primeiro produto)
            if produto_idx > 0:
                btn_remover = tb.Button(titulo_frame, text="❌", bootstyle="danger-outline",
                                       command=lambda pf=produto_frame: remover_produto(pf))
                btn_remover.pack(side="right")
            
            # Linha 1: Tipo e Cor
            linha1 = tb.Frame(produto_frame)
            linha1.pack(fill="x", pady=(0, 5))
            linha1.columnconfigure(0, weight=1)
            linha1.columnconfigure(1, weight=1)
            
            # Tipo
            tipo_frame = tb.Frame(linha1)
            tipo_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            tb.Label(tipo_frame, text="Tipo:", font=("Arial", 10, "bold")).pack(anchor="w")
            tipo_var = tb.Combobox(tipo_frame, values=[
                "Caixa Linda Maravilhosa", "Caixa Suprema", "Caixa Encantada",
                "Caixa Premium", "Caixa Simples", "Outro"
            ])
            tipo_var.pack(fill="x")
            
            # Cor
            cor_frame = tb.Frame(linha1)
            cor_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))
            tb.Label(cor_frame, text="Cor:", font=("Arial", 10, "bold")).pack(anchor="w")
            cor_var = tb.Combobox(cor_frame, values=[
                "Carvalho", "Cinza", "Branco", "Preto", "Amadeirado", "Personalizada"
            ])
            cor_var.pack(fill="x")
            
            # Linha 2: Gavetas, Valor e Reforço
            linha2 = tb.Frame(produto_frame)
            linha2.pack(fill="x", pady=(0, 5))
            linha2.columnconfigure(0, weight=1)
            linha2.columnconfigure(1, weight=1)
            linha2.columnconfigure(2, weight=1)
            
            # Gavetas
            gavetas_frame = tb.Frame(linha2)
            gavetas_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            tb.Label(gavetas_frame, text="Gavetas:", font=("Arial", 10, "bold")).pack(anchor="w")
            gavetas_var = tb.Spinbox(gavetas_frame, from_=1, to=20)
            gavetas_var.pack(fill="x")
            gavetas_var.set("1")
            
            # Valor
            valor_frame = tb.Frame(linha2)
            valor_frame.grid(row=0, column=1, sticky="ew", padx=(5, 5))
            tb.Label(valor_frame, text="Valor (R$):", font=("Arial", 10, "bold")).pack(anchor="w")
            valor_var = tb.Entry(valor_frame)
            valor_var.pack(fill="x")
            valor_var.insert(0, "0,00")
            
            # Frame para reforço
            reforco_frame = tb.Frame(linha2)
            reforco_frame.grid(row=0, column=2, sticky="ew", padx=(5, 0))
            
            tb.Label(reforco_frame, text="Extras:", font=("Arial", 10, "bold")).pack(anchor="w")
            reforco_var = tk.BooleanVar()
            reforco_check = tb.Checkbutton(reforco_frame, text="Reforço (+R$15)", 
                                          variable=reforco_var, bootstyle="success")
            reforco_check.pack(anchor="w")
            
            # Label para valor total
            total_label = tb.Label(linha2, text="Total: R$ 0,00", 
                                  font=("Arial", 10, "bold"), foreground="#2E8B57")
            total_label.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5, 0))
            
            # Função para calcular total
            def calcular_total_produto():
                try:
                    valor_base = float(valor_var.get().replace(',', '.') or '0')
                    reforco = 15.0 if reforco_var.get() else 0.0
                    total = valor_base + reforco
                    total_label.config(text=f"Total: R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                    calcular_resumo()
                except:
                    total_label.config(text="Total: R$ 0,00")
            
            # Binds para recalcular
            valor_var.bind('<KeyRelease>', lambda e: calcular_total_produto())
            reforco_var.trace('w', lambda *args: calcular_total_produto())
            
            # Dados do produto
            produto_data = {
                'frame': produto_frame,
                'tipo': tipo_var,
                'cor': cor_var,
                'gavetas': gavetas_var,
                'valor': valor_var,
                'reforco_var': reforco_var,
                'total_label': total_label,
                'calcular_total': calcular_total_produto
            }
            
            self.produtos_list.append(produto_data)
            
            return produto_data
        
        def remover_produto(produto_frame):
            # Encontrar o produto na lista
            for i, produto in enumerate(self.produtos_list):
                if produto['frame'] == produto_frame:
                    self.produtos_list.pop(i)
                    produto_frame.destroy()
                    break
            
            # Renumerar os títulos dos produtos restantes
            for i, produto in enumerate(self.produtos_list):
                titulo_frame = produto['frame'].winfo_children()[0]
                titulo_label = titulo_frame.winfo_children()[0]
                titulo_label.config(text=f"Produto {i + 1}")
            
            calcular_resumo()
        
        # Adicionar primeiro produto
        adicionar_produto()
        
        # Botão para adicionar mais produtos
        btn_adicionar = tb.Button(produtos_frame, text="➕ Adicionar Produto", 
                                 bootstyle="info-outline", command=adicionar_produto)
        btn_adicionar.pack(anchor="e")

        # === SEÇÃO PAGAMENTO ===
        pagamento_frame = tb.LabelFrame(frame, text="💰 Pagamento e Entrega", padding=15)
        pagamento_frame.pack(fill="x", pady=(0, 15))
        
        # Primeira linha: Entrada e Frete
        pag_linha1 = tb.Frame(pagamento_frame)
        pag_linha1.pack(fill="x", pady=(0, 8))
        pag_linha1.columnconfigure(0, weight=1)
        pag_linha1.columnconfigure(1, weight=1)
        
        # Valor da entrada
        entrada_frame = tb.Frame(pag_linha1)
        entrada_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tb.Label(entrada_frame, text="Valor da Entrada (R$):", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['valor_entrada'] = tb.Entry(entrada_frame, font=("Arial", 11))
        campos['valor_entrada'].pack(fill="x")
        
        # Frete
        frete_frame = tb.Frame(pag_linha1)
        frete_frame.grid(row=0, column=1, sticky="ew")
        tb.Label(frete_frame, text="Frete (R$):", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['frete'] = tb.Entry(frete_frame, font=("Arial", 11))
        campos['frete'].pack(fill="x")
        
        # Segunda linha: Forma de pagamento e Prazo
        pag_linha2 = tb.Frame(pagamento_frame)
        pag_linha2.pack(fill="x", pady=(0, 8))
        pag_linha2.columnconfigure(0, weight=1)
        pag_linha2.columnconfigure(1, weight=1)
        
        # Forma de pagamento
        pagamento_forma_frame = tb.Frame(pag_linha2)
        pagamento_forma_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tb.Label(pagamento_forma_frame, text="Forma de Pagamento:", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['pagamento'] = tb.Combobox(pagamento_forma_frame, values=["Pix", "Crédito", "Débito", "Dinheiro"], 
                                         font=("Arial", 11), state="readonly")
        campos['pagamento'].pack(fill="x")
        
        # Prazo
        prazo_frame = tb.Frame(pag_linha2)
        prazo_frame.grid(row=0, column=1, sticky="ew")
        tb.Label(prazo_frame, text="Prazo (dias):", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['prazo'] = tb.Entry(prazo_frame, font=("Arial", 11))
        campos['prazo'].pack(fill="x")
        
        # === RESUMO FINANCEIRO ===
        resumo_frame = tb.LabelFrame(frame, text="💲 Resumo Financeiro", padding=15)
        resumo_frame.pack(fill="x", pady=(0, 15))
        
        # Labels para mostrar totais
        total_produtos_label = tb.Label(resumo_frame, text="Total Produtos: R$ 0,00", 
                                       font=("Arial", 12, "bold"), foreground="#2196F3")
        total_produtos_label.pack(anchor="w")
        
        total_geral_label = tb.Label(resumo_frame, text="Total Geral: R$ 0,00", 
                                    font=("Arial", 14, "bold"), foreground="#4CAF50")
        total_geral_label.pack(anchor="w", pady=(5, 0))
        
        def calcular_resumo():
            try:
                total_produtos = 0
                for produto in self.produtos_list:
                    try:
                        valor_base = float(produto['valor'].get().replace(',', '.') or '0')
                        reforco = 15.0 if produto['reforco_var'].get() else 0.0
                        total_produtos += valor_base + reforco
                    except:
                        pass
                
                frete = float(campos['frete'].get().replace(',', '.') or '0')
                total_geral = total_produtos + frete
                
                total_produtos_label.config(text=f"Total Produtos: R$ {total_produtos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                total_geral_label.config(text=f"Total Geral: R$ {total_geral:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            except:
                pass
        
        # Bind para recalcular quando frete mudar
        campos['frete'].bind('<KeyRelease>', lambda e: calcular_resumo())
        
        # Botão para atualizar totais
        tb.Button(resumo_frame, text="🔄 Atualizar Totais", bootstyle="info-outline", 
                 command=calcular_resumo).pack(anchor="e", pady=(10, 0))
        
        # Preencher dados se editando
        if pedido_data:
            campos['nome_cliente'].insert(0, pedido_data.get('nome_cliente', ''))
            campos['cpf'].insert(0, pedido_data.get('cpf_cliente', ''))
            campos['telefone'].insert(0, pedido_data.get('telefone_cliente', ''))
            campos['valor_entrada'].insert(0, str(pedido_data.get('valor_entrada', '')))
            campos['frete'].insert(0, str(pedido_data.get('frete', '')))
            campos['pagamento'].set(pedido_data.get('forma_pagamento', ''))
            campos['prazo'].insert(0, str(pedido_data.get('prazo', '')))
        
        def salvar_pedido():
            try:
                # Validações básicas
                if not campos['nome_cliente'].get().strip():
                    messagebox.showerror("Erro", "Nome do cliente é obrigatório!")
                    return
                    
                cpf = campos['cpf'].get().strip()
                if len(cpf) != 11 or not cpf.isdigit():
                    messagebox.showerror("Erro", "CPF deve ter 11 dígitos!")
                    return
                
                # Validar produtos
                if not self.produtos_list:
                    messagebox.showerror("Erro", "Adicione pelo menos um produto!")
                    return
                
                produtos_dados = []
                total_produtos = 0
                
                for i, produto in enumerate(self.produtos_list):
                    tipo = produto['tipo'].get().strip()
                    cor = produto['cor'].get().strip()
                    gavetas = produto['gavetas'].get() or "1"
                    valor = float(produto['valor'].get().replace(',', '.') or '0')
                    reforco = produto['reforco_var'].get()
                    
                    if not tipo or valor <= 0:
                        messagebox.showerror("Erro", f"Produto {i+1}: Tipo e valor são obrigatórios!")
                        return
                    
                    valor_final = valor + (15.0 if reforco else 0.0)
                    total_produtos += valor_final
                    
                    desc = f"{tipo} - Cor: {cor} - {gavetas} gaveta(s)"
                    if reforco:
                        desc += " - Com reforço"
                    desc += f" - R$ {valor_final:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                    produtos_dados.append(desc)
                
                # Dados finais
                dados = {
                    'numero_os': numero_os,
                    'nome_cliente': campos['nome_cliente'].get().strip(),
                    'cpf_cliente': cpf,
                    'telefone_cliente': campos['telefone'].get().strip(),
                    'detalhes_produto': '\n'.join(produtos_dados),
                    'valor_produto': total_produtos,
                    'valor_entrada': float(campos['valor_entrada'].get().replace(',', '.') or '0'),
                    'frete': float(campos['frete'].get().replace(',', '.') or '0'),
                    'forma_pagamento': campos['pagamento'].get().strip(),
                    'prazo': int(campos['prazo'].get() or '30')
                }
                
                # Gerar PDF
                pdf_generator = OrdemServicoPDF()
                arquivo_pdf = pdf_generator.gerar_pdf(dados, "pequena")
                
                # Salvar no banco
                if not pedido_data:  # Novo pedido
                    db_manager.inserir_pedido(
                        numero_os=dados['numero_os'],
                        nome_cliente=dados['nome_cliente'],
                        cpf_cliente=dados['cpf_cliente'],
                        telefone_cliente=dados['telefone_cliente'],
                        detalhes_produto=dados['detalhes_produto'],
                        valor_produto=dados['valor_produto'],
                        valor_entrada=dados['valor_entrada'],
                        frete=dados['frete'],
                        forma_pagamento=dados['forma_pagamento'],
                        prazo=dados['prazo'],
                        caminho_pdf=arquivo_pdf
                    )
                    
                    # Incrementar contador
                    Contador.salvar_contador(numero_os + 1)
                    
                    messagebox.showinfo("Sucesso", f"OS #{numero_os} criada e PDF gerado com sucesso!\n\nTotal: R$ {dados['valor_produto'] + dados['frete']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                
                # Recarregar dados e fechar modal
                self.carregar_dados()
                win.destroy()
                
            except ValueError as e:
                messagebox.showerror("Erro", "Verifique os valores numéricos inseridos!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        
        # === BOTÕES FINAIS ===
        btn_frame = tb.Frame(frame)
        btn_frame.pack(fill="x", pady=(20, 0))
        
        tb.Button(btn_frame, text="💾 Gerar PDF e Salvar", bootstyle="success", 
                 command=salvar_pedido, width=20).pack(side="left", padx=(0, 10))
        tb.Button(btn_frame, text="🔄 Calcular Totais", bootstyle="info", 
                 command=calcular_resumo, width=15).pack(side="left", padx=(0, 10))
        tb.Button(btn_frame, text="❌ Cancelar", bootstyle="secondary", 
                 command=win.destroy, width=10).pack(side="left")
        def aplicar_scroll_completo():
            aplicar_scroll_widget(frame)
        
        # Usar after para garantir que todos os widgets foram criados
        win.after(100, aplicar_scroll_completo)
    
    def _abrir_novo_cliente_modal(self, parent_win, campos, clientes_dict):
        """Abre modal para adicionar novo cliente rapidamente"""
        cliente_win = tb.Toplevel(parent_win)
        cliente_win.title("Adicionar Novo Cliente")
        cliente_win.transient(parent_win)
        cliente_win.grab_set()
        cliente_win.geometry("450x500")
        
        # Frame com scroll para o modal de cliente
        canvas_cliente = tk.Canvas(cliente_win)
        scrollbar_cliente = tb.Scrollbar(cliente_win, orient="vertical", command=canvas_cliente.yview)
        scrollable_frame_cliente = tb.Frame(canvas_cliente)
        
        scrollable_frame_cliente.bind(
            "<Configure>",
            lambda e: canvas_cliente.configure(scrollregion=canvas_cliente.bbox("all"))
        )
        
        canvas_cliente.create_window((0, 0), window=scrollable_frame_cliente, anchor="nw")
        canvas_cliente.configure(yscrollcommand=scrollbar_cliente.set)
        
        canvas_cliente.pack(side="left", fill="both", expand=True)
        scrollbar_cliente.pack(side="right", fill="y")
        
        # SCROLL COM MOUSE WHEEL NO MODAL DE CLIENTE
        def scroll_modal_cliente(event):
            canvas_cliente.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas_cliente.bind("<MouseWheel>", scroll_modal_cliente)
        scrollable_frame_cliente.bind("<MouseWheel>", scroll_modal_cliente)
        
        frame = tb.Frame(scrollable_frame_cliente, padding=20)
        frame.pack(fill="both", expand=True)
        
        tb.Label(frame, text="Cadastrar Novo Cliente", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Campos do novo cliente
        cliente_campos = {}
        
        # Nome
        tb.Label(frame, text="Nome:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        cliente_campos['nome'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['nome'].pack(fill="x", pady=(0, 10))
        
        # CPF
        tb.Label(frame, text="CPF:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        cliente_campos['cpf'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['cpf'].pack(fill="x", pady=(0, 10))
        
        # Telefone
        tb.Label(frame, text="Telefone:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        cliente_campos['telefone'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['telefone'].pack(fill="x", pady=(0, 10))
        
        # Email (opcional)
        tb.Label(frame, text="Email (opcional):", font=("Arial", 11)).pack(anchor="w", pady=(0, 2))
        cliente_campos['email'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['email'].pack(fill="x", pady=(0, 10))
        
        # Endereço (opcional)
        tb.Label(frame, text="Endereço (opcional):", font=("Arial", 11)).pack(anchor="w", pady=(0, 2))
        cliente_campos['endereco'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['endereco'].pack(fill="x", pady=(0, 10))
        
        # Referência (opcional)
        tb.Label(frame, text="Referência (opcional):", font=("Arial", 11)).pack(anchor="w", pady=(0, 2))
        cliente_campos['referencia'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['referencia'].pack(fill="x", pady=(0, 15))
        
        def salvar_novo_cliente():
            try:
                nome = cliente_campos['nome'].get().strip()
                cpf = cliente_campos['cpf'].get().strip()
                telefone = cliente_campos['telefone'].get().strip()
                
                # Validações
                if not nome:
                    messagebox.showerror("Erro", "Nome é obrigatório!")
                    return
                
                if cpf and (len(cpf) != 11 or not cpf.isdigit()):
                    messagebox.showerror("Erro", "CPF deve ter 11 dígitos!")
                    return
                
                # Salvar no banco
                novo_cliente_id = db_manager.inserir_cliente(
                    nome=nome,
                    cpf=cpf,
                    telefone=telefone,
                    email=cliente_campos['email'].get().strip(),
                    endereco=cliente_campos['endereco'].get().strip(),
                    referencia=cliente_campos['referencia'].get().strip()
                )
                
                if novo_cliente_id:
                    # Atualizar o combobox do formulário principal
                    campos['nome_cliente'].set(nome)
                    campos['cpf'].delete(0, 'end')
                    campos['cpf'].insert(0, cpf)
                    campos['telefone'].delete(0, 'end')
                    campos['telefone'].insert(0, telefone)
                    
                    # Adicionar à lista de clientes
                    clientes_dict[nome] = {
                        'nome': nome,
                        'cpf': cpf,
                        'telefone': telefone,
                        'email': cliente_campos['email'].get().strip(),
                        'endereco': cliente_campos['endereco'].get().strip(),
                        'referencia': cliente_campos['referencia'].get().strip()
                    }
                    
                    # Atualizar valores do combobox
                    current_values = list(campos['nome_cliente']['values'])
                    current_values.append(nome)
                    campos['nome_cliente']['values'] = sorted(current_values)
                    
                    messagebox.showinfo("Sucesso", f"Cliente '{nome}' cadastrado com sucesso!")
                    cliente_win.destroy()
                else:
                    messagebox.showerror("Erro", "Erro ao salvar cliente no banco de dados!")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar cliente: {str(e)}")
        
        # Botões
        btn_cliente_frame = tb.Frame(frame)
        btn_cliente_frame.pack(fill="x", pady=(10, 0))
        
        tb.Button(btn_cliente_frame, text="💾 Salvar Cliente", bootstyle="success", 
                 command=salvar_novo_cliente).pack(side="left", padx=(0, 10))
        tb.Button(btn_cliente_frame, text="❌ Cancelar", bootstyle="secondary", 
                 command=cliente_win.destroy).pack(side="left")

    def novo_pedido(self):
        """Abre modal para criar novo pedido"""
        self._abrir_modal_pedido_completo()
    
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
