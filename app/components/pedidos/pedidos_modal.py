"""
Gerenciamento de modais de pedidos
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, INFO, SECONDARY
from tkinter import messagebox

from database import db_manager
from documents.os_pdf import OrdemServicoPDF
from app.numero_os import Contador


class PedidosModal:
    """Gerencia modais de criação e edição de pedidos"""
    
    def __init__(self, interface):
        self.interface = interface
        self.produtos_list = []
    
    def abrir_modal_novo(self):
        """Abre modal para novo pedido"""
        self._abrir_modal_pedido_completo()
    
    def abrir_modal_edicao(self, pedido):
        """Abre modal para editar pedido"""
        self._abrir_modal_pedido_completo(pedido)
    
    def _abrir_modal_pedido_completo(self, pedido_data=None):
        """Cria modal completo para pedido"""
        # Criar janela
        win = tb.Toplevel(self.interface.parent)
        titulo = f"Editar OS #{pedido_data.get('numero_os')}" if pedido_data else "Nova Ordem de Serviço"
        win.title(titulo)
        win.transient(self.interface.parent)
        win.grab_set()
        win.geometry("900x700")

        # Setup do scroll
        canvas, scrollable_frame = self._setup_modal_scroll(win)

        # Criar formulário
        frame = tb.Frame(scrollable_frame, padding=20)
        frame.pack(fill="both", expand=True)

        # Número da OS: NÃO reservar número para pedidos novos aqui.
        # Se for edição, usamos o número existente; se for novo, deixamos None
        # e só geramos/salvamos o número no momento em que o pedido for efetivamente gravado.
        numero_os = pedido_data.get('numero_os') if pedido_data else None

        # Header
        self._criar_header(frame, numero_os, pedido_data is not None)

        # Formulário
        campos = self._criar_formulario_cliente(frame, pedido_data)
        self._criar_secao_produtos(frame, pedido_data)
        self._criar_secao_pagamento(frame, campos, pedido_data)
        self._criar_resumo_financeiro(frame, campos)
        self._criar_botoes_finais(frame, win, campos, numero_os, pedido_data)

        # Configurar scroll final
        win.after(100, lambda: canvas.configure(scrollregion=canvas.bbox("all")))
    
    def _setup_modal_scroll(self, win):
        """Configura scroll no modal"""
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
        
        # Scroll com mouse
        def scroll_mouse(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", scroll_mouse)
        scrollable_frame.bind("<MouseWheel>", scroll_mouse)
        
        return canvas, scrollable_frame
    
    def _criar_header(self, parent, numero_os, is_edit):
        """Cria header do modal"""
        header_frame = tb.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 20))
        # Se não for edição (novo pedido) e numero_os for None, não mostrar número ainda
        if is_edit and numero_os is not None:
            titulo = f"Editar Ordem de Serviço #{numero_os:05d}"
        elif is_edit:
            titulo = "Editar Ordem de Serviço"
        else:
            titulo = f"Nova Ordem de Serviço" if numero_os is None else f"Nova Ordem de Serviço #{numero_os:05d}"
        tb.Label(header_frame, text=titulo, 
                font=("Arial", 16, "bold")).pack()
    
    def _criar_formulario_cliente(self, parent, pedido_data):
        """Cria formulário de dados do cliente"""
        cliente_frame = tb.LabelFrame(parent, text="👤 Dados do Cliente", padding=15)
        cliente_frame.pack(fill="x", pady=(0, 15))
        
        campos = {}
        
        # Buscar clientes para autocomplete
        try:
            clientes = db_manager.listar_clientes()
            # clientes são tuplas: (id, nome, cpf, telefone, email, rua, numero, bairro, cidade, estado, referencia)
            clientes_dict = {}
            nomes_clientes = []
            for cliente in clientes:
                if len(cliente) >= 7:  # Precisa ter pelo menos 7 campos para acessar numero
                    cliente_id = cliente[0]
                    nome = cliente[1] or ''
                    cpf = cliente[2] or ''
                    telefone = cliente[3] or ''
                    numero = cliente[6] or ''  # campo numero do endereço
                    
                    if nome:
                        # Criar nome de exibição com últimos 2 dígitos do TELEFONE
                        nome_exibicao = nome
                        if telefone and str(telefone).isdigit():
                            # Pegar apenas os dígitos do telefone
                            telefone_digitos = ''.join(filter(str.isdigit, str(telefone)))
                            if len(telefone_digitos) >= 2:
                                ultimos_digitos = telefone_digitos[-2:]
                                nome_exibicao = f"{nome} {ultimos_digitos}"
                        
                        clientes_dict[nome_exibicao] = {
                            'id': cliente_id,
                            'nome': nome,
                            'cpf': cpf,
                            'telefone': telefone,
                            'numero': numero
                        }
                        nomes_clientes.append(nome_exibicao)
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            clientes_dict = {}
            nomes_clientes = []
        
        # Nome do cliente com autocomplete
        tb.Label(cliente_frame, text="Nome do Cliente:", font=("Arial", 11, "bold")).pack(anchor="w")
        cliente_frame_nome = tb.Frame(cliente_frame)
        cliente_frame_nome.pack(fill="x", pady=(0, 10))
        
        campos['nome_cliente'] = tb.Combobox(cliente_frame_nome, values=nomes_clientes, font=("Arial", 11))
        campos['nome_cliente'].pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Botão para novo cliente
        btn_novo_cliente = tb.Button(cliente_frame_nome, text="➕", bootstyle=SUCCESS,
                                    command=lambda: self._abrir_novo_cliente_modal(parent.winfo_toplevel(), campos, clientes_dict, None))
        btn_novo_cliente.pack(side="right")
        
        # Seção de sugestão para novo cliente (inicialmente oculta)
        self.sugestao_frame = tb.Frame(cliente_frame)
        self.sugestao_label = tb.Label(self.sugestao_frame, 
                                      text="", 
                                      font=("Arial", 10), 
                                      foreground="#ff6b35",
                                      background="#fff3e0")
        self.sugestao_label.pack(side="left", padx=5, pady=3)
        
        self.btn_criar_cliente = tb.Button(self.sugestao_frame, 
                                          text="Criar Cliente", 
                                          bootstyle="warning-outline",
                                          command=lambda: self._criar_cliente_da_sugestao(parent.winfo_toplevel(), campos, clientes_dict))
        self.btn_criar_cliente.pack(side="right", padx=5)
        
        self.btn_ignorar = tb.Button(self.sugestao_frame, 
                                    text="Ignorar", 
                                    bootstyle="secondary-outline",
                                    command=self._ocultar_sugestao)
        self.btn_ignorar.pack(side="right")
        
        # Inicialmente oculta
        self.sugestao_frame.pack_forget()
        
        # Bind para preencher dados automaticamente
        def preencher_dados_cliente(event):
            nome_selecionado = campos['nome_cliente'].get()
            if nome_selecionado in clientes_dict:
                cliente = clientes_dict[nome_selecionado]
                campos['cpf'].delete(0, 'end')
                campos['cpf'].insert(0, cliente.get('cpf', ''))
                campos['telefone'].delete(0, 'end')
                campos['telefone'].insert(0, cliente.get('telefone', ''))
                # Ocultar sugestão se cliente válido for selecionado
                self._ocultar_sugestao()
        
        def verificar_cliente_inexistente(event):
            """Verifica se o cliente digitado não existe e mostra sugestão inline"""
            nome_digitado = campos['nome_cliente'].get().strip()
            if nome_digitado and nome_digitado not in clientes_dict and len(nome_digitado) > 2:
                # Extrair apenas o nome (sem dígitos) se o usuário digitou algo
                nome_limpo = nome_digitado
                if nome_digitado and len(nome_digitado.split()) > 1:
                    partes = nome_digitado.split()
                    ultima_parte = partes[-1]
                    # Se a última parte são apenas dígitos, remover
                    if ultima_parte.isdigit():
                        nome_limpo = ' '.join(partes[:-1])
                
                # Mostrar sugestão inline apenas no FocusOut
                if event.type == '10':  # FocusOut event
                    self._mostrar_sugestao(nome_limpo)
            else:
                # Se o cliente existe ou campo está vazio, ocultar sugestão
                self._ocultar_sugestao()
        
        campos['nome_cliente'].bind('<<ComboboxSelected>>', preencher_dados_cliente)
        campos['nome_cliente'].bind('<FocusOut>', verificar_cliente_inexistente)
        
        # CPF e Telefone
        cpf_tel_frame = tb.Frame(cliente_frame)
        cpf_tel_frame.pack(fill="x", pady=(0, 10))
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
        
        # Preencher dados se editando
        if pedido_data:
            campos['nome_cliente'].set(pedido_data.get('nome_cliente', ''))
            campos['cpf'].insert(0, pedido_data.get('cpf_cliente', ''))
            campos['telefone'].insert(0, pedido_data.get('telefone_cliente', ''))
        
        return campos
    
    def _criar_secao_produtos(self, parent, pedido_data):
        """Cria seção de produtos"""
        produtos_frame = tb.LabelFrame(parent, text="📦 Produtos", padding=15)
        produtos_frame.pack(fill="x", pady=(0, 15))
        
        # Container para lista de produtos
        produtos_container = tb.Frame(produtos_frame)
        produtos_container.pack(fill="x", pady=(0, 10))
        
        self.produtos_list = []
        self.produtos_container = produtos_container
        
        # Se é edição, carregar dados dos produtos
        if pedido_data:
            self._carregar_produtos_existentes(pedido_data)
        else:
            # Adicionar primeiro produto vazio
            self._adicionar_produto()
        
        # Botão para adicionar mais produtos
        btn_adicionar = tb.Button(produtos_frame, text="➕ Adicionar Produto", 
                                 bootstyle="info-outline", command=self._adicionar_produto)
        btn_adicionar.pack(anchor="e")
    
    def _carregar_produtos_existentes(self, pedido_data):
        """Carrega produtos existentes na edição - VERSÃO CORRIGIDA PARA MÚLTIPLOS PRODUTOS"""
        detalhes_produto = pedido_data.get('detalhes_produto', '')
        
        if detalhes_produto:
            # Dividir os detalhes em linhas - cada linha é um produto
            linhas_produtos = detalhes_produto.split('\\n')
            print(f"DEBUG: Carregando {len(linhas_produtos)} produtos:")
            
            for i, linha in enumerate(linhas_produtos):
                if linha.strip():  # Ignorar linhas vazias
                    print(f"  Linha {i+1}: {linha}")
                    produto = self._adicionar_produto()
                    self._parsear_produto_da_linha(produto, linha)
        else:
            # Se não tem detalhes, criar produto vazio
            self._adicionar_produto()
    
    def _parsear_produto_da_linha(self, produto, linha):
        """Parseia uma linha de detalhes e preenche os campos do produto"""
        import re
        
        # Extrair tipo do produto
        tipos = ['Caixa Linda Maravilhosa', 'Caixa Suprema', 'Caixa Encantada', 'Caixa Premium', 'Caixa Simples']
        for tipo in tipos:
            if tipo in linha:
                produto['tipo'].set(tipo)
                break
        
        # Extrair cor
        cores = ['Carvalho', 'Cinza', 'Branco', 'Preto', 'Amadeirado', 'Personalizada']
        for cor in cores:
            if f'Cor: {cor}' in linha:
                produto['cor'].set(cor)
                break
        
        # Extrair número de gavetas
        gavetas_match = re.search(r'(\d+)\s*gaveta', linha)
        if gavetas_match:
            produto['gavetas'].delete(0, 'end')
            produto['gavetas'].insert(0, gavetas_match.group(1))
        
        # Extrair valor (buscar o valor em R$)
        valor_match = re.search(r'R\$\s*([\d.,]+)', linha)
        if valor_match:
            valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
            try:
                valor_total = float(valor_str)
                
                # Verificar se tem reforço para calcular valor base
                if 'Com reforço' in linha:
                    produto['reforco_var'].set(True)
                    valor_base = valor_total - 15
                else:
                    produto['reforco_var'].set(False)
                    valor_base = valor_total
                
                # Definir valor base
                produto['valor'].delete(0, 'end')
                produto['valor'].insert(0, f"{valor_base:.2f}")
                
            except ValueError:
                print(f"Erro ao converter valor: {valor_str}")
        
        # Calcular total do produto
        produto['calcular_total']()
    
    def _adicionar_produto(self):
        """Adiciona um novo produto ao formulário"""
        produto_idx = len(self.produtos_list)
        
        # Separador se não for o primeiro
        if produto_idx > 0:
            separador = tb.Separator(self.produtos_container, orient="horizontal")
            separador.pack(fill="x", pady=10)
        
        # Frame do produto
        produto_frame = tb.Frame(self.produtos_container)
        produto_frame.pack(fill="x", pady=(0, 10))
        
        # Header do produto
        titulo_frame = tb.Frame(produto_frame)
        titulo_frame.pack(fill="x", pady=(0, 5))
        
        tb.Label(titulo_frame, text=f"Produto {produto_idx + 1}", 
                font=("Arial", 11, "bold")).pack(side="left")
        
        # Botão remover (só se não for o primeiro)
        if produto_idx > 0:
            btn_remover = tb.Button(titulo_frame, text="❌", bootstyle="danger-outline",
                                   command=lambda pf=produto_frame: self._remover_produto(pf))
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
        
        # Reforço
        reforco_frame = tb.Frame(linha2)
        reforco_frame.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        tb.Label(reforco_frame, text="Extras:", font=("Arial", 10, "bold")).pack(anchor="w")
        reforco_var = tk.BooleanVar()
        reforco_check = tb.Checkbutton(reforco_frame, text="Reforço (+R$15)", 
                                      variable=reforco_var, bootstyle="success")
        reforco_check.pack(anchor="w")
        
        # Label total do produto
        total_label = tb.Label(linha2, text="Total: R$ 0,00", 
                              font=("Arial", 10, "bold"), foreground="#2E8B57")
        total_label.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(5, 0))
        
        # Função para calcular total do produto
        def calcular_total_produto():
            try:
                valor_base = float(valor_var.get().replace(',', '.') or '0')
                reforco = 15.0 if reforco_var.get() else 0.0
                total = valor_base + reforco
                total_label.config(text=f"Total: R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                if hasattr(self, 'calcular_resumo'):
                    self.calcular_resumo()
            except:
                total_label.config(text="Total: R$ 0,00")
        
        # Binds
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
    
    def _remover_produto(self, produto_frame):
        """Remove um produto da lista"""
        for i, produto in enumerate(self.produtos_list):
            if produto['frame'] == produto_frame:
                self.produtos_list.pop(i)
                produto_frame.destroy()
                break
        
        # Renumerar produtos
        for i, produto in enumerate(self.produtos_list):
            titulo_frame = produto['frame'].winfo_children()[0]
            titulo_label = titulo_frame.winfo_children()[0]
            titulo_label.config(text=f"Produto {i + 1}")
        
        if hasattr(self, 'calcular_resumo'):
            self.calcular_resumo()
    
    def _criar_secao_pagamento(self, parent, campos, pedido_data):
        """Cria seção de pagamento"""
        pagamento_frame = tb.LabelFrame(parent, text="💰 Pagamento e Entrega", padding=15)
        pagamento_frame.pack(fill="x", pady=(0, 15))
        
        # Linha 1: Entrada e Frete
        linha1 = tb.Frame(pagamento_frame)
        linha1.pack(fill="x", pady=(0, 8))
        linha1.columnconfigure(0, weight=1)
        linha1.columnconfigure(1, weight=1)
        
        # Entrada
        entrada_frame = tb.Frame(linha1)
        entrada_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tb.Label(entrada_frame, text="Valor da Entrada (R$):", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['valor_entrada'] = tb.Entry(entrada_frame, font=("Arial", 11))
        campos['valor_entrada'].pack(fill="x")
        
        # Frete
        frete_frame = tb.Frame(linha1)
        frete_frame.grid(row=0, column=1, sticky="ew")
        tb.Label(frete_frame, text="Frete (R$):", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['frete'] = tb.Entry(frete_frame, font=("Arial", 11))
        campos['frete'].pack(fill="x")
        
        # Linha 2: Forma de pagamento e Prazo
        linha2 = tb.Frame(pagamento_frame)
        linha2.pack(fill="x", pady=(0, 8))
        linha2.columnconfigure(0, weight=1)
        linha2.columnconfigure(1, weight=1)
        
        # Forma de pagamento
        pagamento_forma_frame = tb.Frame(linha2)
        pagamento_forma_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        tb.Label(pagamento_forma_frame, text="Forma de Pagamento:", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['pagamento'] = tb.Combobox(pagamento_forma_frame, values=["Pix", "Crédito", "Débito", "Dinheiro"], 
                                         font=("Arial", 11), state="readonly")
        campos['pagamento'].pack(fill="x")
        
        # Prazo
        prazo_frame = tb.Frame(linha2)
        prazo_frame.grid(row=0, column=1, sticky="ew")
        tb.Label(prazo_frame, text="Prazo (dias):", font=("Arial", 11, "bold")).pack(anchor="w")
        campos['prazo'] = tb.Entry(prazo_frame, font=("Arial", 11))
        campos['prazo'].pack(fill="x")
        
        # Preencher dados se editando
        if pedido_data:
            campos['valor_entrada'].insert(0, str(pedido_data.get('valor_entrada', '0')))
            campos['frete'].insert(0, str(pedido_data.get('frete', '0')))
            campos['pagamento'].set(pedido_data.get('forma_pagamento', ''))
            campos['prazo'].insert(0, str(pedido_data.get('prazo', '30')))
    
    def _criar_resumo_financeiro(self, parent, campos):
        """Cria resumo financeiro"""
        resumo_frame = tb.LabelFrame(parent, text="💲 Resumo Financeiro", padding=15)
        resumo_frame.pack(fill="x", pady=(0, 15))
        
        # Labels de totais
        self.total_produtos_label = tb.Label(resumo_frame, text="Total Produtos: R$ 0,00", 
                                            font=("Arial", 12, "bold"), foreground="#2196F3")
        self.total_produtos_label.pack(anchor="w")
        
        self.total_geral_label = tb.Label(resumo_frame, text="Total Geral: R$ 0,00", 
                                         font=("Arial", 14, "bold"), foreground="#4CAF50")
        self.total_geral_label.pack(anchor="w", pady=(5, 0))
        
        # Função para calcular resumo
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
                
                self.total_produtos_label.config(text=f"Total Produtos: R$ {total_produtos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
                self.total_geral_label.config(text=f"Total Geral: R$ {total_geral:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            except:
                pass
        
        self.calcular_resumo = calcular_resumo
        
        # Bind para recalcular
        campos['frete'].bind('<KeyRelease>', lambda e: calcular_resumo())
        
        # Botão atualizar
        tb.Button(resumo_frame, text="🔄 Atualizar Totais", bootstyle="info-outline", 
                 command=calcular_resumo).pack(anchor="e", pady=(10, 0))
    
    def _criar_botoes_finais(self, parent, win, campos, numero_os, pedido_data):
        """Cria botões finais do modal"""
        # Separador
        separador = tb.Separator(parent, orient="horizontal")
        separador.pack(fill="x", pady=(20, 15))
        
        # Frame dos botões
        btn_frame = tb.Frame(parent)
        btn_frame.pack(fill="x", pady=(0, 20))
        
        btn_center = tb.Frame(btn_frame)
        btn_center.pack(anchor="center")
        
        # Botão salvar
        btn_salvar = tb.Button(btn_center, text="💾 SALVAR", bootstyle=SUCCESS, 
                              command=lambda: self._salvar_pedido(campos, numero_os, pedido_data, win), 
                              width=15)
        btn_salvar.pack(side="left", padx=(0, 10))
        
        # Botão calcular
        btn_calcular = tb.Button(btn_center, text="🔄 CALCULAR", bootstyle=INFO, 
                                command=self.calcular_resumo, width=12)
        btn_calcular.pack(side="left", padx=(0, 10))
        
        # Botão cancelar
        btn_cancelar = tb.Button(btn_center, text="❌ CANCELAR", bootstyle=SECONDARY, 
                                command=win.destroy, width=10)
        btn_cancelar.pack(side="left")
    
    def _salvar_pedido(self, campos, numero_os, pedido_data, win):
        """Salva o pedido no banco e gera PDF apenas se for novo pedido"""
        try:
            # Debug: verificar estrutura do pedido_data
            print(f"DEBUG: pedido_data = {pedido_data}")
            print(f"DEBUG: tipo = {type(pedido_data)}")
            
            # Gerar número da OS se for novo pedido
            if not pedido_data:
                contador = Contador()
                numero_os = contador.proximo_numero()
                pedido_id = None
            else:
                # pedido_data pode ser tuple ou dict
                if isinstance(pedido_data, dict):
                    numero_os = pedido_data.get('numero_os', 0)
                    pedido_id = pedido_data.get('id')
                    print(f"DEBUG: dict - numero_os={numero_os}, id={pedido_id}")
                else:
                    # Se for tupla, o primeiro elemento pode ser numero_os ou id
                    numero_os = pedido_data[0] if len(pedido_data) > 0 else 0
                    pedido_id = pedido_data[0] if len(pedido_data) > 0 else None  # Assumindo que o primeiro é o ID
                    print(f"DEBUG: tuple - numero_os={numero_os}, id={pedido_id}")
            
            # Validações
            if not campos['nome_cliente'].get().strip():
                messagebox.showerror("Erro", "Nome do cliente é obrigatório!")
                return
            
            cpf = campos['cpf'].get().strip()
            # Remover formatação do CPF para validação
            cpf_numeros = cpf.replace('-', '').replace('.', '')
            if cpf and (len(cpf_numeros) != 11 or not cpf_numeros.isdigit()):
                messagebox.showerror("Erro", "CPF deve ter 11 dígitos!")
                return
            
            if not self.produtos_list:
                messagebox.showerror("Erro", "Adicione pelo menos um produto!")
                return
            
            print(f"=== PRODUTOS LIST DEBUG ===")
            print(f"Número de produtos: {len(self.produtos_list)}")
            
            # Processar produtos
            produtos_dados = []
            total_produtos = 0
            
            for i, produto in enumerate(self.produtos_list):
                tipo = produto['tipo'].get().strip()
                cor = produto['cor'].get().strip()
                gavetas = produto['gavetas'].get() or "1"
                valor = float(produto['valor'].get().replace(',', '.') or '0')
                reforco = produto['reforco_var'].get()
                
                print(f"  Produto {i+1}: Tipo='{tipo}', Cor='{cor}', Gavetas='{gavetas}', Valor={valor}, Reforço={reforco}")
                
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
                'detalhes_produto': '\\n'.join(produtos_dados),
                'valor_produto': total_produtos,
                'valor_entrada': float(campos['valor_entrada'].get().replace(',', '.') or '0'),
                'frete': float(campos['frete'].get().replace(',', '.') or '0'),
                'forma_pagamento': campos['pagamento'].get().strip(),
                'prazo': int(campos['prazo'].get() or '30')
            }
            
            print(f"=== DADOS FINAIS ===")
            print(f"Detalhes do produto: {dados['detalhes_produto']}")
            print(f"Valor entrada: {dados['valor_entrada']}")
            print(f"Frete: {dados['frete']}")
            print(f"Forma pagamento: '{dados['forma_pagamento']}'")
            print(f"Prazo: {dados['prazo']}")
            
            if not pedido_data:  # NOVO PEDIDO
                # Salvar no banco (sem gerar PDF)
                db_manager.salvar_ordem(dados, "")
                
                total_final = dados['valor_produto'] + dados['frete']
                messagebox.showinfo("Sucesso", 
                    f"OS #{numero_os} criada com sucesso!\\n\\n"
                    f"Total: R$ {total_final:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
            
            else:  # EDITANDO PEDIDO EXISTENTE
                # Apenas atualizar banco de dados (sem gerar PDF)
                campos_atualizacao = {
                    'nome_cliente': dados['nome_cliente'],
                    'cpf_cliente': dados['cpf_cliente'],
                    'telefone_cliente': dados['telefone_cliente'],
                    'detalhes_produto': dados['detalhes_produto'],
                    'valor_produto': dados['valor_produto'],
                    'valor_entrada': dados['valor_entrada'],
                    'frete': dados['frete'],
                    'forma_pagamento': dados['forma_pagamento'],
                    'prazo': dados['prazo']
                }
                
                print(f"=== EDITANDO PEDIDO ID: {pedido_id} ===")
                print(f"Campos para atualização: {campos_atualizacao}")
                
                if pedido_id:
                    sucesso = db_manager.atualizar_pedido(pedido_id, campos_atualizacao)
                    
                    print(f"Resultado da atualização: {sucesso}")
                    
                    if sucesso:
                        messagebox.showinfo("Sucesso", f"OS #{numero_os} atualizada com sucesso!")
                    else:
                        messagebox.showerror("Erro", "Falha ao atualizar no banco de dados!")
                        return
                else:
                    messagebox.showerror("Erro", "ID do pedido não encontrado!")
                    return
            
            # Recarregar dados e fechar
            self.interface.carregar_dados()
            win.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Verifique os valores numéricos inseridos!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    
    def _abrir_novo_cliente_modal(self, parent_win, campos, clientes_dict, nome_pre_preenchido=None):
        """Abre modal para cadastrar novo cliente"""
        cliente_win = tb.Toplevel(parent_win)
        cliente_win.title("Adicionar Novo Cliente")
        cliente_win.transient(parent_win)
        cliente_win.grab_set()
        cliente_win.geometry("450x500")
        
        # Scroll para o modal de cliente
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
        
        # Scroll com mouse
        def scroll_modal_cliente(event):
            canvas_cliente.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas_cliente.bind("<MouseWheel>", scroll_modal_cliente)
        scrollable_frame_cliente.bind("<MouseWheel>", scroll_modal_cliente)
        
        frame = tb.Frame(scrollable_frame_cliente, padding=20)
        frame.pack(fill="both", expand=True)
        
        tb.Label(frame, text="Cadastrar Novo Cliente", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Campos do cliente
        cliente_campos = {}
        
        # Nome
        tb.Label(frame, text="Nome:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        cliente_campos['nome'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['nome'].pack(fill="x", pady=(0, 10))
        
        # Pré-preencher nome se fornecido
        if nome_pre_preenchido:
            cliente_campos['nome'].insert(0, nome_pre_preenchido)
        
        # CPF
        tb.Label(frame, text="CPF:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        cliente_campos['cpf'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['cpf'].pack(fill="x", pady=(0, 10))
        
        # Telefone
        tb.Label(frame, text="Telefone:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        cliente_campos['telefone'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['telefone'].pack(fill="x", pady=(0, 10))
        
        # Email
        tb.Label(frame, text="Email (opcional):", font=("Arial", 11)).pack(anchor="w", pady=(0, 2))
        cliente_campos['email'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['email'].pack(fill="x", pady=(0, 10))
        
        # Endereço
        tb.Label(frame, text="Rua (opcional):", font=("Arial", 11)).pack(anchor="w", pady=(0, 2))
        cliente_campos['rua'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['rua'].pack(fill="x", pady=(0, 10))
        
        # Número
        tb.Label(frame, text="Número:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(0, 2))
        cliente_campos['numero'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['numero'].pack(fill="x", pady=(0, 10))
        
        # Referência
        tb.Label(frame, text="Referência (opcional):", font=("Arial", 11)).pack(anchor="w", pady=(0, 2))
        cliente_campos['referencia'] = tb.Entry(frame, font=("Arial", 11))
        cliente_campos['referencia'].pack(fill="x", pady=(0, 15))
        
        def salvar_novo_cliente():
            try:
                nome = cliente_campos['nome'].get().strip()
                cpf = cliente_campos['cpf'].get().strip()
                telefone = cliente_campos['telefone'].get().strip()
                
                if not nome:
                    messagebox.showerror("Erro", "Nome é obrigatório!")
                    return
                
                if cpf:
                    cpf_numeros = cpf.replace('-', '').replace('.', '')
                    if len(cpf_numeros) != 11 or not cpf_numeros.isdigit():
                        messagebox.showerror("Erro", "CPF deve ter 11 dígitos!")
                        return
                
                # Salvar no banco
                numero = cliente_campos['numero'].get().strip()
                novo_cliente_id = db_manager.inserir_cliente(
                    nome=nome,
                    cpf=cpf,
                    telefone=telefone,
                    email=cliente_campos['email'].get().strip(),
                    endereco=cliente_campos['rua'].get().strip(),
                    referencia=cliente_campos['referencia'].get().strip(),
                    numero=numero
                )
                
                if novo_cliente_id:
                    # Criar nome de exibição com últimos 2 dígitos do TELEFONE
                    nome_exibicao = nome
                    if telefone:
                        # Pegar apenas os dígitos do telefone
                        telefone_digitos = ''.join(filter(str.isdigit, str(telefone)))
                        if len(telefone_digitos) >= 2:
                            ultimos_digitos = telefone_digitos[-2:]
                            nome_exibicao = f"{nome} {ultimos_digitos}"
                    
                    # Atualizar formulário principal com nome de exibição
                    campos['nome_cliente'].set(nome_exibicao)
                    campos['cpf'].delete(0, 'end')
                    campos['cpf'].insert(0, cpf)
                    campos['telefone'].delete(0, 'end')
                    campos['telefone'].insert(0, telefone)
                    
                    # Atualizar lista de clientes
                    clientes_dict[nome_exibicao] = {
                        'id': novo_cliente_id,
                        'nome': nome,
                        'cpf': cpf,
                        'telefone': telefone,
                        'numero': numero
                    }
                    
                    # Atualizar combobox
                    current_values = list(campos['nome_cliente']['values'])
                    current_values.append(nome_exibicao)
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
        
        tb.Button(btn_cliente_frame, text="💾 Salvar Cliente", bootstyle=SUCCESS, 
                 command=salvar_novo_cliente).pack(side="left", padx=(0, 10))
        tb.Button(btn_cliente_frame, text="❌ Cancelar", bootstyle=SECONDARY, 
                 command=cliente_win.destroy).pack(side="left")

    def _mostrar_sugestao(self, nome_cliente):
        """Mostra a seção de sugestão para criar novo cliente"""
        self.nome_sugerido = nome_cliente
        self.sugestao_label.config(text=f"👤 Cliente '{nome_cliente}' não encontrado.")
        self.sugestao_frame.pack(fill="x", pady=(5, 10))
    
    def _ocultar_sugestao(self):
        """Oculta a seção de sugestão"""
        self.sugestao_frame.pack_forget()
        self.nome_sugerido = None
    
    def _criar_cliente_da_sugestao(self, parent_win, campos, clientes_dict):
        """Abre modal para criar cliente a partir da sugestão"""
        if hasattr(self, 'nome_sugerido') and self.nome_sugerido:
            self._abrir_novo_cliente_modal(parent_win, campos, clientes_dict, self.nome_sugerido)
            self._ocultar_sugestao()
