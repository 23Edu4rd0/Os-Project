""" Pega as informações do cliente e produto, gerando um PDF com os dados

    Returns:
        PDF : Dados do cliente e do produto
"""

import ttkbootstrap as tb
from tkinter import messagebox, filedialog
import tkinter as tk
import os  # Adicionar import os
import platform  # Added import platform
import subprocess  # Added import subprocess
import datetime
# Certifique-se que o nome da classe está correto
from documents.os_pdf import OrdemServicoPDF
from app.numero_os import Contador
# Renomear para evitar conflito
from services.impress import imprimir_pdf as imprimir_pdf_service, verificar_disponibilidade_impressao
from ttkbootstrap.constants import PRIMARY, SUCCESS, DANGER, INFO, WARNING
from app.impressApp import ImpressApp
# Importar o gerenciador do banco de dados
from database.db_manager import db_manager

# It's good practice to handle platform-specific imports gracefully
win32print = None
if platform.system() == "Windows":
    try:
        import win32print
    except ImportError:
        win32print = None  # Define it as None if import fails


class OrdemServicoApp:
    """
    Classe principal da aplicação de Ordem de Serviço.
    Responsável por criar a interface gráfica, coletar e validar dados,
    gerar PDF, imprimir e selecionar impressora.
    """

    def __init__(self, root):
        """
        Inicializa a interface gráfica principal da Ordem de Serviço.
        Configura todos os widgets, menus e dicas de preenchimento.
        """
        self.root = root
        self.root.title("Ordem de Serviço")
        self.root.geometry("520x680")
        self.root.minsize(380, 600)
        self.numero_os = Contador.ler_contador()
        self.arquivo_pdf = "ordem_servico.pdf"  # Nome do arquivo PDF gerado
        self.impressora_padrao = None  # Impressora padrão selecionada
        self.impressora_menu = ImpressApp(self.root)
        self.tamanho_folha_selecionado = tb.StringVar(value="pequena")

        # Parâmetros base para ajuste dinâmico de fonte/layout
        self.base_width = 420
        self.base_height = 600
        self.base_font_size = 10
        self.base_font_size_label = 10

        # Notebook com 2 abas: Formulário e Banco de Dados
        self.notebook = tb.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        formulario_tab = tb.Frame(self.notebook)
        self.notebook.add(formulario_tab, text="Formulário")

        banco_tab = tb.Frame(self.notebook)
        self.notebook.add(banco_tab, text="Banco de Dados")

        # Área rolável na aba de formulário
        canvas = tk.Canvas(formulario_tab, highlightthickness=0)
        vscroll = tb.Scrollbar(formulario_tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        form_frame = tb.Frame(canvas)
        self._form_inner = form_frame
        form_window = canvas.create_window((0, 0), window=form_frame, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(form_window, width=event.width)

        form_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)
        # Rolagem pelo mouse (Windows/Linux)
        def _on_mousewheel(event):
            try:
                delta = event.delta
                if delta == 0:
                    return
                canvas.yview_scroll(int(-1*(delta/120)), "units")
            except Exception:
                pass
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        # Layout: labels acima, campos ocupando toda a largura
        row = 0
        # OS Number Display
        os_frame = tb.Frame(form_frame)
        os_frame.grid(row=row, column=0, columnspan=2, padx=10,
                      pady=(5, 2), sticky="ew")

        tb.Label(
            os_frame, text="Nº OS:", font=("Montserrat", 11, "bold")
        ).pack(side="left", padx=(0, 3))
        self.numero_os_label = tb.Label(
            os_frame, text=str(self.numero_os),
            font=("Montserrat", 11, "bold"), bootstyle="PRIMARY"
        )
        self.numero_os_label.pack(side="left")

        # Botões para aumentar/diminuir o número da OS
        btn_diminuir_os = tb.Button(
            os_frame, text="-", command=self.diminuir_os, width=2,
            bootstyle="secondary"
        )
        btn_diminuir_os.pack(
            side="left", padx=(5, 2), ipady=2
        )
        btn_aumentar_os = tb.Button(
            os_frame, text="+", command=self.aumentar_os, width=2,
            bootstyle="secondary"
        )
        btn_aumentar_os.pack(
            side="left", padx=(0, 5), ipady=2
        )

        row += 1
        tb.Label(form_frame, text="Nome do Cliente:", font=("Montserrat", 11)).grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(3, 2), sticky="w"
        )
        row += 1
        self.nome_cliente_entry = tb.Entry(form_frame, font=("Montserrat", 11))
        self.nome_cliente_entry.grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 5), sticky="ew"
        )
        row += 1
        tb.Label(form_frame, text="CPF:", font=("Montserrat", 11)).grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 2), sticky="w"
        )
        row += 1
        self.cpf_entry = tb.Entry(form_frame, font=("Montserrat", 11))
        self.cpf_entry.grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 5), sticky="ew"
        )
        row += 1
        tb.Label(form_frame, text="Telefone:", font=("Montserrat", 11)).grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 2), sticky="w"
        )
        row += 1
        self.telefone_entry = tb.Entry(form_frame, font=("Montserrat", 11))
        self.telefone_entry.grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 5), sticky="ew"
        )
        row += 1
        tb.Label(form_frame, text="Detalhes do Produto/Serviço:",
                 font=("Montserrat", 11)).grid(
            row=row, column=0, columnspan=2, padx=10, pady=(0, 2), sticky="w"
        )
        row += 1
        self.detalhes_text = tb.Text(form_frame, height=4,
                                     font=("Montserrat", 11), wrap="word")
        self.detalhes_text.grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 2), sticky="ew"
        )
        row += 1
        tb.Label(form_frame, text="Valor do Produto:", font=("Montserrat", 11)).grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(3, 2), sticky="w"
        )
        row += 1
        self.valor_produto_entry = tb.Entry(form_frame, font=("Montserrat", 11))
        self.valor_produto_entry.grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 2), sticky="ew"
        )
        row += 1
        tb.Label(form_frame, text="Valor da Entrada:", font=("Montserrat", 11)).grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(3, 2), sticky="w"
        )
        row += 1
        self.valor_entrada_entry = tb.Entry(form_frame, font=("Montserrat", 11))
        self.valor_entrada_entry.grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 2), sticky="ew"
        )
        row += 1
        tb.Label(form_frame, text="Frete:", font=("Montserrat", 11)).grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(3, 2), sticky="w"
        )
        row += 1
        self.frete_entry = tb.Entry(form_frame, font=("Montserrat", 11))
        self.frete_entry.grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 2), sticky="ew"
        )
        row += 1
        tb.Label(form_frame, text="Forma de Pagamento:",
                 font=("Montserrat", 11)).grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(3, 2), sticky="w"
        )
        row += 1
        self.pagamento_combo = tb.Combobox(
            form_frame, values=["Pix", "Crédito", "Débito", "Dinheiro"],
            font=("Montserrat", 11)
        )
        self.pagamento_combo.grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 2), sticky="ew"
        )
        row += 1
        tb.Label(form_frame, text="Prazo (dias):", font=("Montserrat", 11)).grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(3, 2), sticky="w"
        )
        row += 1
        self.prazo_entry = tb.Entry(form_frame, font=("Montserrat", 11))
        self.prazo_entry.grid(
            row=row, column=0, columnspan=2, padx=10,
            pady=(0, 10), sticky="ew"
        )
        row += 1
        self.gerar_pdf_btn = tb.Button(
            form_frame, text="Gerar PDF", bootstyle=PRIMARY, width=16,
            command=self.gerar_pdf
        )
        self.gerar_pdf_btn.grid(
            row=row, column=0, padx=(10, 5), pady=(5, 10),
            sticky="ew", ipady=2
        )

        # Frame para botões de PDF
        pdf_buttons_frame = tb.Frame(form_frame)
        pdf_buttons_frame.grid(
            row=row, column=1, padx=(5, 10), pady=(5, 10),
            sticky="ew"
        )
        pdf_buttons_frame.grid_columnconfigure(0, weight=1)
        pdf_buttons_frame.grid_columnconfigure(1, weight=1)

        self.imprimir_btn = tb.Button(
            pdf_buttons_frame, text="Imprimir PDF", bootstyle=PRIMARY, width=12,
            command=self.imprimir_pdf
        )
        self.imprimir_btn.grid(
            row=0, column=0, padx=(0, 5), sticky="ew", ipady=2
        )

        self.abrir_pdf_btn = tb.Button(
            pdf_buttons_frame, text="Abrir PDF", bootstyle="info-outline", width=12,
            command=self.abrir_pdf
        )
        self.abrir_pdf_btn.grid(
            row=0, column=1, padx=(5, 0), sticky="ew", ipady=2
        )
        # Seções da aba Banco de Dados
        self._montar_aba_banco(banco_tab)

        # Menu principal
        menu_bar = tb.Menu(self.root)
        self.root.config(menu=menu_bar)
        arquivo_menu = tb.Menu(menu_bar, tearoff=0)
        tamanho_menu = tb.Menu(arquivo_menu, tearoff=0)
        tamanho_menu.add_radiobutton(
            label="Pequena (Bobina)", variable=self.tamanho_folha_selecionado, value="pequena"
        )
        tamanho_menu.add_radiobutton(
            label="Grande (A4)", variable=self.tamanho_folha_selecionado, value="grande"
        )
        arquivo_menu.add_cascade(label="Tamanho da Folha", menu=tamanho_menu)
        
        # Menu de ordens anteriores
        arquivo_menu.add_separator()
        arquivo_menu.add_command(
            label="Gerenciar Ordens Anteriores",
            command=self.abrir_gerenciador_ordens
        )
        arquivo_menu.add_command(
            label="Buscar por Número de OS",
            command=self.buscar_os_por_numero
        )
        
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Sair", command=self.root.quit)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)
        
        # Menu de histórico
        historico_menu = tb.Menu(menu_bar, tearoff=0)
        self.historico_menu = historico_menu
        menu_bar.add_cascade(label="Histórico", menu=historico_menu)
        # Carrega as últimas ordens no menu de histórico
        self.atualizar_menu_historico()
        
        ajuda_menu = tb.Menu(menu_bar, tearoff=0)
        ajuda_menu.add_command(label="Sobre", command=self.mostrar_sobre)
        menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)
        impressora_menu = tb.Menu(menu_bar, tearoff=0)
        impressora_menu.add_command(
            label="Selecionar Impressora",
            command=self.impressora_menu.selecionar_impressora
        )
        menu_bar.add_cascade(label="Impressora", menu=impressora_menu)

        # Lista de widgets para ajuste dinâmico de fonte
        self.widgets_to_resize = [
            self.nome_cliente_entry, self.cpf_entry, self.telefone_entry,
            self.detalhes_text, self.valor_produto_entry, self.valor_entrada_entry,
            self.frete_entry, self.pagamento_combo, self.prazo_entry, self.gerar_pdf_btn, self.imprimir_btn,
            self.numero_os_label
        ]

        # Ajuste dinâmico de fonte ao redimensionar a janela
        self.root.bind('<Configure>', self._ajustar_fontes)

        # Dicas de preenchimento (placeholders) para os campos
        self.add_placeholder(
            self.nome_cliente_entry, "Digite o nome do cliente"
        )
        self.add_placeholder(
            self.cpf_entry, "Somente números, 11 dígitos"
        )
        self.add_placeholder(
            self.telefone_entry, "Ex: 37999999999"
        )
        self.add_placeholder(
            self.valor_produto_entry, "Ex: 100,00"
        )
        self.add_placeholder(
            self.valor_entrada_entry, "Ex: 50,00"
        )
        self.add_placeholder(
            self.frete_entry, "Ex: 10,00"
        )
        self.add_placeholder(
            self.prazo_entry,
            "Insira o número de dias. Ex: 30 -> daqui a 30 dias"
        )

        # Navegação entre campos com Enter
        self.nome_cliente_entry.bind(
            "<Return>", lambda e: self.cpf_entry.focus_set()
        )
        self.cpf_entry.bind(
            "<Return>", lambda e: self.telefone_entry.focus_set()
        )
        self.telefone_entry.bind(
            "<Return>", lambda e: self.detalhes_text.focus_set()
        )
        # No Text, Enter deve inserir uma nova linha. Use Ctrl+Enter para ir ao próximo campo.
        # Removemos o atalho de Enter que pulava de campo e adicionamos Ctrl+Enter.
        self.detalhes_text.bind(
            "<Control-Return>", lambda e: (self.valor_produto_entry.focus_set(), "break")[1]
        )
        self.valor_produto_entry.bind(
            "<Return>", lambda e: self.valor_entrada_entry.focus_set()
        )
        self.valor_entrada_entry.bind(
            "<Return>", lambda e: self.frete_entry.focus_set()
        )
        self.frete_entry.bind(
            "<Return>", lambda e: self.pagamento_combo.focus_set()
        )
        self.pagamento_combo.bind(
            "<Return>", lambda e: self.prazo_entry.focus_set()
        )
        self.prazo_entry.bind(
            "<Return>", lambda e: self.gerar_pdf_btn.focus_set()
        )

        def open_combo_options(event):
            self.pagamento_combo.event_generate('<Down>')

        def on_combo_selected(event):
            self.prazo_entry.focus_set()
        self.pagamento_combo.bind("<Return>", open_combo_options)
        self.pagamento_combo.bind("<<ComboboxSelected>>", on_combo_selected)

    def _montar_aba_banco(self, parent):
        """Cria a aba Banco de Dados com visualização e CRUD de Clientes, Ordens, Prazos e Produtos."""
        # Notebook interno
        self.db_inner_nb = tb.Notebook(parent)
        self.db_inner_nb.pack(fill="both", expand=True, padx=8, pady=8)

        # Tabs
        self.tab_clientes = tb.Frame(self.db_inner_nb)
        self.tab_ordens = tb.Frame(self.db_inner_nb)
        self.tab_prazos = tb.Frame(self.db_inner_nb)
        self.tab_produtos = tb.Frame(self.db_inner_nb)
        self.db_inner_nb.add(self.tab_clientes, text="Clientes")
        self.db_inner_nb.add(self.tab_ordens, text="Ordens")
        self.db_inner_nb.add(self.tab_prazos, text="Prazos")
        self.db_inner_nb.add(self.tab_produtos, text="Produtos")

        # Clientes
        top_c = tb.Frame(self.tab_clientes)
        top_c.pack(fill="x")
        tb.Button(top_c, text="Novo", bootstyle=SUCCESS, command=self._novo_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_c, text="Editar", command=self._editar_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_c, text="Excluir", bootstyle=DANGER, command=self._excluir_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_c, text="Ver pedidos", bootstyle=INFO, command=self._ver_pedidos_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_c, text="Recarregar", command=self._carregar_grid_clientes).pack(side="right", padx=5, pady=5)

        cols_c = ("id","nome","cpf","telefone","email","created_at")
        self.tree_clientes = tb.Treeview(self.tab_clientes, columns=cols_c, show="headings")
        for col, text, w, anchor in [
            ("id","ID",60,"center"),
            ("nome","Nome",220,"w"),
            ("cpf","CPF",120,"center"),
            ("telefone","Telefone",140,"center"),
            ("email","Email",200,"w"),
            ("created_at","Criado em",140,"center"),
        ]:
            self.tree_clientes.heading(col, text=text)
            self.tree_clientes.column(col, width=w, anchor=anchor)
        ysc = tb.Scrollbar(self.tab_clientes, orient="vertical", command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscroll=ysc.set)
        self.tree_clientes.pack(side="left", fill="both", expand=True, padx=(8,0), pady=(0,8))
        ysc.pack(side="right", fill="y", pady=(0,8))
        # Duplo clique abre pedidos do cliente
        self.tree_clientes.bind('<Double-1>', self._ver_pedidos_cliente)

    # Ordens
    top_o = tb.Frame(self.tab_ordens)
    top_o.pack(fill="x")
    tb.Button(top_o, text="Editar", command=self._editar_ordem).pack(side="left", padx=5, pady=5)
    tb.Button(top_o, text="Excluir", bootstyle=DANGER, command=self._excluir_ordem).pack(side="left", padx=5, pady=5)
    tb.Button(top_o, text="Limpar filtro", command=self._limpar_filtro_ordens).pack(side="left", padx=5, pady=5)
    tb.Button(top_o, text="Recarregar", bootstyle=SUCCESS, command=self._carregar_grid_ordens).pack(side="right", padx=5, pady=5)

        cols_o = ("id","numero_os","nome_cliente","data_emissao","data_entrega","valor_produto","forma_pagamento")
        self.tree_ordens = tb.Treeview(self.tab_ordens, columns=cols_o, show="headings")
        for col, text, w, anchor in [
            ("id","ID",60,"center"),
            ("numero_os","OS",70,"center"),
            ("nome_cliente","Cliente",220,"w"),
            ("data_emissao","Emissão",120,"center"),
            ("data_entrega","Entrega",120,"center"),
            ("valor_produto","Valor",100,"e"),
            ("forma_pagamento","Pagamento",120,"center"),
        ]:
            self.tree_ordens.heading(col, text=text)
            self.tree_ordens.column(col, width=w, anchor=anchor)
    yso = tb.Scrollbar(self.tab_ordens, orient="vertical", command=self.tree_ordens.yview)
        self.tree_ordens.configure(yscroll=yso.set)
        self.tree_ordens.pack(side="left", fill="both", expand=True, padx=(8,0), pady=(0,8))
        yso.pack(side="right", fill="y", pady=(0,8))

        # Prazos
    top_p = tb.Frame(self.tab_prazos)
        top_p.pack(fill="x")
        tb.Button(top_p, text="Recarregar", bootstyle=SUCCESS, command=self._carregar_grid_prazos).pack(side="right", padx=5, pady=5)

        cols_p = ("id","numero_os","nome_cliente","prazo","data_emissao","data_entrega","status")
    self.tree_prazos = tb.Treeview(self.tab_prazos, columns=cols_p, show="headings")
        for col, text, w, anchor in [
            ("id","ID",60,"center"),
            ("numero_os","OS",70,"center"),
            ("nome_cliente","Cliente",220,"w"),
            ("prazo","Prazo (dias)",110,"center"),
            ("data_emissao","Emissão",120,"center"),
            ("data_entrega","Entrega",120,"center"),
            ("status","Status",100,"center"),
        ]:
            self.tree_prazos.heading(col, text=text)
            self.tree_prazos.column(col, width=w, anchor=anchor)
    ysp = tb.Scrollbar(self.tab_prazos, orient="vertical", command=self.tree_prazos.yview)
        self.tree_prazos.configure(yscroll=ysp.set)
        self.tree_prazos.pack(side="left", fill="both", expand=True, padx=(8,0), pady=(0,8))
        ysp.pack(side="right", fill="y", pady=(0,8))

        # Produtos
    top_r = tb.Frame(self.tab_produtos)
        top_r.pack(fill="x")
    tb.Button(top_r, text="Editar", command=self._editar_produto).pack(side="left", padx=5, pady=5)
    tb.Button(top_r, text="Excluir", bootstyle=DANGER, command=self._excluir_produto).pack(side="left", padx=5, pady=5)
        tb.Button(top_r, text="Recarregar", bootstyle=SUCCESS, command=self._carregar_grid_produtos).pack(side="right", padx=5, pady=5)

        cols_r = ("id","numero_os","nome_cliente","descricao","created_at")
    self.tree_produtos = tb.Treeview(self.tab_produtos, columns=cols_r, show="headings")
        for col, text, w, anchor in [
            ("id","ID",60,"center"),
            ("numero_os","OS",70,"center"),
            ("nome_cliente","Cliente",200,"w"),
            ("descricao","Produto/Linha",380,"w"),
            ("created_at","Criado em",140,"center"),
        ]:
            self.tree_produtos.heading(col, text=text)
            self.tree_produtos.column(col, width=w, anchor=anchor)
    ysr = tb.Scrollbar(self.tab_produtos, orient="vertical", command=self.tree_produtos.yview)
        self.tree_produtos.configure(yscroll=ysr.set)
        self.tree_produtos.pack(side="left", fill="both", expand=True, padx=(8,0), pady=(0,8))
        ysr.pack(side="right", fill="y", pady=(0,8))

        # Carregamento inicial (após criar todas as treeviews)
    self._carregar_grid_clientes()
        self._carregar_grid_ordens()
        self._carregar_grid_prazos()
        self._carregar_grid_produtos()

    def _carregar_grid_ordens(self):
        # Limpa
        tree = getattr(self, 'tree_ordens', None)
        if not tree:
            return
        for i in tree.get_children():
            tree.delete(i)
        # Busca
        try:
            filtro_nome = getattr(self, '_filtro_cliente_nome', None)
            if filtro_nome:
                ordens = db_manager.buscar_ordem_por_cliente(filtro_nome) or []
            else:
                ordens = db_manager.listar_ultimas_ordens(200)
            for o in ordens:
                valor = o.get('valor_produto')
                if isinstance(valor, (int, float)):
                    valor_fmt = f"R$ {valor:.2f}".replace('.', ',')
                else:
                    valor_fmt = ''
                tree.insert('', 'end', values=(
                    o.get('id'), o.get('numero_os'), o.get('nome_cliente'),
                    o.get('data_emissao'), o.get('data_entrega'), valor_fmt,
                    o.get('forma_pagamento')
                ))
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao carregar ordens: {e}')

    def _carregar_grid_prazos(self):
        # Limpa
        tree = getattr(self, 'tree_prazos', None)
        if not tree:
            return
        for i in tree.get_children():
            tree.delete(i)
        # Busca
        try:
            prazos = db_manager.listar_prazos(300)
            for p in prazos:
                tree.insert('', 'end', values=(
                    p.get('id'), p.get('numero_os'), p.get('nome_cliente'), p.get('prazo'),
                    p.get('data_emissao'), p.get('data_entrega'), p.get('status')
                ))
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao carregar prazos: {e}')

    def _carregar_grid_produtos(self):
        # Limpa
        tree = getattr(self, 'tree_produtos', None)
        if not tree:
            return
        for i in tree.get_children():
            tree.delete(i)
        # Busca
        try:
            registros = db_manager.listar_produtos(500)
            for r in registros:
                tree.insert('', 'end', values=(
                    r.get('id'), r.get('numero_os'), r.get('nome_cliente'), r.get('descricao'), r.get('created_at')
                ))
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao carregar produtos: {e}')

    def _carregar_grid_clientes(self):
        tree = getattr(self, 'tree_clientes', None)
        if not tree:
            return
        for i in tree.get_children():
            tree.delete(i)
        try:
            clientes = db_manager.listar_clientes(500)
            for c in clientes:
                tree.insert('', 'end', values=(
                    c.get('id'), c.get('nome'), c.get('cpf'), c.get('telefone'), c.get('email'), c.get('created_at')
                ))
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao carregar clientes: {e}')

    # ===== Ações Clientes =====
    def _get_selected(self, tree):
        sel = tree.selection()
        if not sel:
            return None, None
        item_id = sel[0]
        values = tree.item(item_id, 'values')
        return item_id, values

    def _novo_cliente(self):
        self._abrir_modal_cliente()

    def _editar_cliente(self):
        _, vals = self._get_selected(self.tree_clientes)
        if not vals:
            messagebox.showinfo('Info', 'Selecione um cliente para editar.')
            return
        data = {
            'id': vals[0], 'nome': vals[1], 'cpf': vals[2], 'telefone': vals[3], 'email': vals[4]
        }
        self._abrir_modal_cliente(data)

    def _excluir_cliente(self):
        item, vals = self._get_selected(self.tree_clientes)
        if not vals:
            messagebox.showinfo('Info', 'Selecione um cliente para excluir.')
            return
        if not messagebox.askyesno('Confirmar', f"Excluir cliente '{vals[1]}'?"):
            return
        ok = db_manager.deletar_cliente(int(vals[0]))
        if ok:
            self._carregar_grid_clientes()
        else:
            messagebox.showerror('Erro', 'Não foi possível excluir o cliente.')

    def _ver_pedidos_cliente(self, event=None):
        _, vals = self._get_selected(self.tree_clientes)
        if not vals:
            return
        nome = vals[1]
        self._filtro_cliente_nome = nome
        # troca para a aba Ordens e recarrega
        try:
            self.db_inner_nb.select(self.tab_ordens)
        except Exception:
            pass
        self._carregar_grid_ordens()

    def _abrir_modal_cliente(self, data=None):
        win = tb.Toplevel(self.root)
        win.title('Cliente')
        win.transient(self.root)
        win.grab_set()
        frm = tb.Frame(win, padding=10)
        frm.pack(fill='both', expand=True)
        tb.Label(frm, text='Nome:').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='CPF:').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Telefone:').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Email:').grid(row=3, column=0, sticky='e', padx=5, pady=5)
        nome_e = tb.Entry(frm, width=40)
        cpf_e = tb.Entry(frm, width=30)
        tel_e = tb.Entry(frm, width=30)
        email_e = tb.Entry(frm, width=40)
        nome_e.grid(row=0, column=1, sticky='w')
        cpf_e.grid(row=1, column=1, sticky='w')
        tel_e.grid(row=2, column=1, sticky='w')
        email_e.grid(row=3, column=1, sticky='w')
        if data:
            nome_e.insert(0, data.get('nome') or '')
            cpf_e.insert(0, data.get('cpf') or '')
            tel_e.insert(0, data.get('telefone') or '')
            email_e.insert(0, data.get('email') or '')

        def salvar():
            nome = nome_e.get().strip()
            cpf = cpf_e.get().strip() or None
            tel = tel_e.get().strip() or None
            email = email_e.get().strip() or None
            if not nome:
                messagebox.showerror('Erro', 'Nome é obrigatório.')
                return
            if data and data.get('id'):
                ok = db_manager.atualizar_cliente(int(data['id']), nome, cpf, tel, email)
            else:
                ok = db_manager.upsert_cliente(nome, cpf, tel, email) is not None
            if ok:
                self._carregar_grid_clientes()
                win.destroy()
            else:
                messagebox.showerror('Erro', 'Falha ao salvar cliente.')

        btns = tb.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, pady=10)
        tb.Button(btns, text='Salvar', bootstyle=SUCCESS, command=salvar).pack(side='left', padx=5)
        tb.Button(btns, text='Cancelar', command=win.destroy).pack(side='left', padx=5)

    # ===== Ações Ordens =====
    def _limpar_filtro_ordens(self):
        self._filtro_cliente_nome = None
        self._carregar_grid_ordens()

    def _editar_ordem(self):
        _, vals = self._get_selected(self.tree_ordens)
        if not vals:
            messagebox.showinfo('Info', 'Selecione uma ordem para editar.')
            return
        data = {
            'id': int(vals[0]),
            'numero_os': vals[1],
            'nome_cliente': vals[2],
            'data_emissao': vals[3],
            'data_entrega': vals[4]
        }
        self._abrir_modal_ordem(data)

    def _excluir_ordem(self):
        _, vals = self._get_selected(self.tree_ordens)
        if not vals:
            messagebox.showinfo('Info', 'Selecione uma ordem para excluir.')
            return
        if not messagebox.askyesno('Confirmar', f"Excluir OS #{vals[1]}?"):
            return
        ok = db_manager.deletar_ordem(int(vals[0]))
        if ok:
            self._carregar_grid_ordens()
            self._carregar_grid_prazos()
            self._carregar_grid_produtos()
        else:
            messagebox.showerror('Erro', 'Não foi possível excluir a OS.')

    def _abrir_modal_ordem(self, data):
        win = tb.Toplevel(self.root)
        win.title(f"Editar OS #{data.get('numero_os')}")
        win.transient(self.root)
        win.grab_set()
        frm = tb.Frame(win, padding=10)
        frm.pack(fill='both', expand=True)
        # Campos básicos
        labels = ['Cliente','Telefone','Valor (total)','Entrada','Frete','Pagamento','Prazo (dias)']
        for i, t in enumerate(labels):
            tb.Label(frm, text=t+':').grid(row=i, column=0, sticky='e', padx=5, pady=5)
        c_nome = tb.Entry(frm, width=40)
        c_tel = tb.Entry(frm, width=30)
        c_val = tb.Entry(frm, width=15)
        c_ent = tb.Entry(frm, width=15)
        c_fre = tb.Entry(frm, width=15)
        c_pag = tb.Entry(frm, width=25)
        c_pra = tb.Entry(frm, width=10)
        c_nome.grid(row=0, column=1, sticky='w')
        c_tel.grid(row=1, column=1, sticky='w')
        c_val.grid(row=2, column=1, sticky='w')
        c_ent.grid(row=3, column=1, sticky='w')
        c_fre.grid(row=4, column=1, sticky='w')
        c_pag.grid(row=5, column=1, sticky='w')
        c_pra.grid(row=6, column=1, sticky='w')

        # Pré-carregar tentando buscar OS completa
        try:
            os_full = db_manager.buscar_ordem_por_numero(int(data['numero_os']))
        except Exception:
            os_full = None
        if os_full:
            c_nome.insert(0, os_full.get('nome_cliente') or '')
            c_tel.insert(0, os_full.get('telefone_cliente') or '')
            c_val.insert(0, str(os_full.get('valor_produto') or ''))
            c_ent.insert(0, str(os_full.get('valor_entrada') or ''))
            c_fre.insert(0, str(os_full.get('frete') or ''))
            c_pag.insert(0, os_full.get('forma_pagamento') or '')
            c_pra.insert(0, str(os_full.get('prazo') or ''))

        def salvar():
            campos = {
                'nome_cliente': c_nome.get().strip() or None,
                'telefone_cliente': c_tel.get().strip() or None,
                'valor_produto': self._to_float_or_none(c_val.get()),
                'valor_entrada': self._to_float_or_none(c_ent.get()),
                'frete': self._to_float_or_none(c_fre.get()),
                'forma_pagamento': c_pag.get().strip() or None,
                'prazo': self._to_int_or_none(c_pra.get())
            }
            campos = {k:v for k,v in campos.items() if v is not None}
            if not campos:
                win.destroy()
                return
            ok = db_manager.atualizar_ordem(int(data['id']), campos)
            if ok:
                self._carregar_grid_ordens()
                self._carregar_grid_prazos()
                win.destroy()
            else:
                messagebox.showerror('Erro', 'Falha ao salvar OS.')

        btns = tb.Frame(frm)
        btns.grid(row=7, column=0, columnspan=2, pady=10)
        tb.Button(btns, text='Salvar', bootstyle=SUCCESS, command=salvar).pack(side='left', padx=5)
        tb.Button(btns, text='Cancelar', command=win.destroy).pack(side='left', padx=5)

    # ===== Ações Produtos =====
    def _editar_produto(self):
        _, vals = self._get_selected(self.tree_produtos)
        if not vals:
            messagebox.showinfo('Info', 'Selecione um item para editar.')
            return
        produto_id = int(vals[0])
        atual = vals[3]
        win = tb.Toplevel(self.root)
        win.title('Editar item')
        win.transient(self.root)
        win.grab_set()
        frm = tb.Frame(win, padding=10)
        frm.pack(fill='both', expand=True)
        tb.Label(frm, text='Descrição:').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        ent = tb.Entry(frm, width=60)
        ent.grid(row=0, column=1, sticky='w')
        ent.insert(0, atual)
        def salvar():
            desc = ent.get().strip()
            if not desc:
                messagebox.showerror('Erro', 'Descrição não pode ser vazia.')
                return
            ok = db_manager.atualizar_produto(produto_id, desc)
            if ok:
                self._carregar_grid_produtos()
                win.destroy()
            else:
                messagebox.showerror('Erro', 'Falha ao salvar item.')
        tb.Button(frm, text='Salvar', bootstyle=SUCCESS, command=salvar).grid(row=1, column=0, columnspan=2, pady=10)

    def _excluir_produto(self):
        _, vals = self._get_selected(self.tree_produtos)
        if not vals:
            messagebox.showinfo('Info', 'Selecione um item para excluir.')
            return
        if not messagebox.askyesno('Confirmar', f"Excluir item '{vals[3]}'?"):
            return
        ok = db_manager.deletar_produto(int(vals[0]))
        if ok:
            self._carregar_grid_produtos()
        else:
            messagebox.showerror('Erro', 'Não foi possível excluir o item.')

    # ===== Helpers =====
    def _to_float_or_none(self, s):
        try:
            txt = (s or '').replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(txt) if txt != '' else None
        except Exception:
            return None

    def _to_int_or_none(self, s):
        try:
            txt = (s or '').strip()
            return int(txt) if txt != '' else None
        except Exception:
            return None

    def add_placeholder(self, entry, placeholder_text):
        """
        Adiciona uma dica de preenchimento (placeholder) ao campo Entry.
        O texto aparece em cinza e some ao focar no campo.
        """
        # Limpa o campo primeiro para evitar duplicação
        entry.delete(0, 'end')
        entry.insert(0, placeholder_text)
        entry.config(foreground='grey')

        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, 'end')
                entry.config(foreground='black')  # Cor normal ao digitar

        def on_focus_out(event):
            if not entry.get():
                entry.delete(0, 'end')  # Limpa completamente antes de inserir
                entry.insert(0, placeholder_text)
                entry.config(foreground='grey')

        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    def diminuir_os(self):
        """
        Diminui o número da OS, atualizando o contador e o rótulo.
        Não permite valores menores que 1.
        """
        atual = Contador.ler_contador()
        if atual > 1:
            novo_valor = atual - 1
            Contador.salvar_contador(novo_valor)
            self.numero_os = novo_valor
            self.numero_os_label.config(text=str(self.numero_os))
        else:
            messagebox.showwarning(
                "Aviso",
                "Não é possível diminuir o número da OS abaixo de 1."
            )

    def aumentar_os(self):
        """
        Aumenta o número da OS, atualizando o contador e o rótulo.
        """
        atual = Contador.ler_contador()
        novo_valor = atual + 1
        Contador.salvar_contador(novo_valor)
        self.numero_os = novo_valor
        self.numero_os_label.config(text=str(self.numero_os))

    def coletar_dados(self):
        """
        Coleta os dados dos campos da interface e retorna um dicionário.
        Placeholders e campos vazios são tratados como string vazia ou None.
        """
        dados = {}
        dados["numero_os"] = self.numero_os_label['text']

        # Nome Cliente
        nome_cliente = self.nome_cliente_entry.get().strip()
        if nome_cliente == "Digite o nome do cliente":
            nome_cliente = ""
        dados["nome_cliente"] = nome_cliente

        # CPF Cliente
        cpf_cliente = self.cpf_entry.get().strip()
        if cpf_cliente == "Somente números, 11 dígitos":
            cpf_cliente = ""
        dados["cpf_cliente"] = cpf_cliente

        # Telefone Cliente
        telefone_cliente = self.telefone_entry.get().strip()
        if telefone_cliente == "Ex: 37999999999":
            telefone_cliente = ""
        dados["telefone_cliente"] = telefone_cliente

        # Detalhes Produto
        detalhes_produto = self.detalhes_text.get("1.0", "end-1c").strip()
        dados["detalhes_produto"] = detalhes_produto

        # Valor Estimado
        valor_produto_str = self.valor_produto_entry.get().strip()
        if valor_produto_str == "Ex: 100,00" or not valor_produto_str:
            valor_produto = None
        else:
            try:
                valor_produto = float(valor_produto_str.replace(',', '.'))
            except ValueError:
                valor_produto = None
        dados["valor_produto"] = valor_produto

        valor_entrada_str = self.valor_entrada_entry.get().strip()
        if valor_entrada_str == "Ex: 50,00" or not valor_entrada_str:
            valor_entrada = None
        else:
            try:
                valor_entrada = float(valor_entrada_str.replace(',', '.'))
            except ValueError:
                valor_entrada = None
        dados["valor_entrada"] = valor_entrada

        frete_str = self.frete_entry.get().strip()
        if frete_str == "Ex: 10,00" or not frete_str:
            frete = 0.0
        else:
            try:
                frete = float(frete_str.replace(',', '.'))
            except ValueError:
                frete = 0.0
        dados["frete"] = frete

        # Forma de Pagamento
        forma_pagamento = self.pagamento_combo.get().strip()
        dados["forma_pagamento"] = forma_pagamento

        # Prazo
        prazo_str = self.prazo_entry.get().strip()
        placeholder_prazo = ("Insira o numero de dias. "
                             "Ex: 30 -> daqui a 30 dias")
        if prazo_str == placeholder_prazo or not prazo_str:
            prazo = None
        else:
            try:
                prazo = int(prazo_str)
            except ValueError:
                prazo = None
        dados["prazo"] = prazo

        return dados

    def validar_dados(self, dados: dict):
        """
        Valida os dados coletados dos campos.
        Exibe mensagens de erro se algum campo estiver inválido.
        """
        if (len(dados["cpf_cliente"]) != 11 or
                not dados["cpf_cliente"].isdigit()):
            messagebox.showerror(
                "Erro",
                "CPF inválido. Insira somente números e 11 dígitos."
            )
            return False
        if dados["valor_produto"] is None or dados["valor_produto"] <= 0:
            messagebox.showerror(
                "Erro",
                "Valor do produto inválido. Insira um valor válido."
            )
            return False
        if dados["valor_entrada"] is None or dados["valor_entrada"] < 0:
            messagebox.showerror(
                "Erro",
                "Valor da entrada inválido. Insira um valor válido (0 ou maior)."
            )
            return False
        if dados["prazo"] is None or dados["prazo"] <= 0:
            messagebox.showerror(
                "Erro",
                "Prazo inválido. Insira um número inteiro positivo."
            )
            return False
        if not all([
            dados["numero_os"],
            dados["nome_cliente"],
            dados["cpf_cliente"],
            dados["telefone_cliente"],
            dados["detalhes_produto"],
            dados["valor_produto"],
            dados["valor_entrada"],
            dados["forma_pagamento"]
        ]):
            messagebox.showerror(
                "Erro",
                "Todos os campos devem ser preenchidos."
            )
            return False
        return True

    def gerar_pdf(self):
        """
        Gera o PDF da Ordem de Serviço com os dados coletados e validados.
        Atualiza o número da OS após gerar o PDF e salva no banco de dados.
        """
        dados = self.coletar_dados()

        # Define fields to check for the "all empty" condition
        campos_chave_formulario = [
            "nome_cliente", "cpf_cliente", "telefone_cliente",
            "detalhes_produto", "valor_produto", "valor_entrada", "frete", "forma_pagamento", "prazo"
        ]

        # Check if all relevant fields are effectively empty
        if not any(dados.get(key) for key in campos_chave_formulario):
            messagebox.showerror(
                "Erro",
                ("Todos os campos estão vazios.\n"
                 "Por favor, preencha os dados para gerar a OS.")
            )
            return

        # If we are here, at least one field was filled.
        # Now, apply default for prazo if it was left empty by the user.
        if dados["prazo"] is None:
            dados["prazo"] = 30  # Default prazo

        # Now, validate the (potentially modified) data
        if not self.validar_dados(dados):
            # validar_dados already shows specific error messages
            return

        tamanho_folha = self.tamanho_folha_selecionado.get()

        try:
            # O número da OS já deve estar nos dados coletados do label
            numero_os_str = dados.get("numero_os")
            if not numero_os_str or not numero_os_str.isdigit():
                messagebox.showerror("Erro", "Número da OS inválido.")
                return

            numero_os = int(numero_os_str)

            # Gera o PDF com nome único baseado no cliente e data
            pdf = OrdemServicoPDF(dados, self.arquivo_pdf, tamanho_folha=tamanho_folha)
            pdf.gerar()
            
            # Atualiza o arquivo_pdf com o caminho gerado pelo OrdemServicoPDF
            self.arquivo_pdf = pdf.arquivo_pdf
            
            # Salva os dados no banco de dados
            try:
                db_manager.salvar_ordem(dados, self.arquivo_pdf)
                print(f"Ordem {numero_os} salva no banco de dados.")
            except Exception as e:
                print(f"Erro ao salvar no banco de dados: {e}")
                # Continua mesmo se falhar o salvamento no banco

            # Salva o número da OS que foi usada
            Contador.salvar_contador(numero_os)

            # Atualiza o label para o próximo número disponível
            proximo_numero_os = Contador.ler_contador()  # Lê o próximo número
            if hasattr(self, 'numero_os_label') and self.numero_os_label:
                self.numero_os_label.config(text=str(proximo_numero_os))
                
            # Atualiza o menu de histórico
            self.atualizar_menu_historico()

            messagebox.showinfo(
                "Sucesso",
                f"PDF da OS Nº {numero_os} gerado com sucesso!\n"
                f"Salvo em: {os.path.basename(self.arquivo_pdf)}"
            )

        except Exception as e:
            messagebox.showerror(
                "Erro ao Gerar PDF",
                f"Ocorreu um erro inesperado: {e}"
            )

    def imprimir_pdf(self):
        """
        Envia o PDF gerado para a impressora padrão selecionada.
        Exibe mensagens de sucesso ou erro conforme o resultado.
        Funciona mesmo sem aplicativos de impressão específicos.
        """
        if not os.path.exists(self.arquivo_pdf):
            messagebox.showerror(
                "Erro de Impressão",
                (f"O arquivo '{self.arquivo_pdf}' não foi encontrado.\n"
                 "Por favor, gere o PDF primeiro.")
            )
            return

        try:
            # Verifica disponibilidade de métodos de impressão
            info_impressao = verificar_disponibilidade_impressao()
            
            # Chama a função de impressão do módulo de serviço
            # A função imprimir_pdf_service deve retornar uma tupla
            # (bool_sucesso, mensagem_string)
            sucesso, mensagem = imprimir_pdf_service(self.arquivo_pdf)
            
            if sucesso:
                if mensagem:
                    # Se há mensagem, é provavelmente um fallback (abertura manual)
                    messagebox.showinfo(
                        "PDF Aberto", 
                        f"{mensagem}\n\n"
                        "O PDF foi aberto com o programa padrão. "
                        "Para imprimir, use Ctrl+P no programa aberto."
                    )
                else:
                    # Impressão direta bem-sucedida
                    messagebox.showinfo(
                        "Impressão", 
                        "PDF enviado para impressão com sucesso!"
                    )
            else:
                # Erro na impressão - oferecer alternativas
                opcoes_msg = self._obter_mensagem_opcoes_impressao(info_impressao)
                messagebox.showerror(
                    "Erro de Impressão", 
                    f"{mensagem}\n\n{opcoes_msg}"
                )
                
        except Exception as e:
            messagebox.showerror(
                "Erro ao Imprimir",
                f"Ocorreu um erro inesperado: {e}\n\n"
                f"Você pode tentar abrir o arquivo manualmente em:\n{self.arquivo_pdf}"
            )

    def _obter_mensagem_opcoes_impressao(self, info_impressao):
        """
        Gera uma mensagem com opções alternativas baseada na disponibilidade do sistema.
        """
        sistema = info_impressao['sistema']
        
        if sistema == "Windows":
            return (
                "Opções alternativas:\n"
                "1. Abra o arquivo PDF manualmente e use Ctrl+P\n"
                "2. Instale 'pywin32' com: pip install pywin32\n"
                "3. Verifique se há impressoras instaladas no Windows"
            )
        elif sistema == "Linux":
            return (
                "Opções alternativas:\n"
                "1. Instale CUPS: sudo apt install cups\n"
                "2. Abra o arquivo PDF manualmente e use Ctrl+P\n"
                "3. Verifique se há impressoras configuradas"
            )
        else:
            return (
                "Opções alternativas:\n"
                "1. Abra o arquivo PDF manualmente\n"
                "2. Verifique se há impressoras instaladas no sistema"
            )

    def abrir_pdf(self):
        """
        Abre o PDF gerado com o programa padrão do sistema.
        Funciona independentemente de impressoras instaladas.
        """
        if not os.path.exists(self.arquivo_pdf):
            messagebox.showerror(
                "Erro",
                (f"O arquivo '{self.arquivo_pdf}' não foi encontrado.\n"
                 "Por favor, gere o PDF primeiro.")
            )
            return

        try:
            import platform
            sistema = platform.system()
            
            if sistema == "Windows":
                os.startfile(self.arquivo_pdf)
            elif sistema == "Darwin":  # macOS
                subprocess.run(["open", self.arquivo_pdf])
            else:  # Linux e outros
                subprocess.run(["xdg-open", self.arquivo_pdf])
            
            messagebox.showinfo(
                "PDF Aberto", 
                "PDF aberto com sucesso!\n\n"
                "Para imprimir, use Ctrl+P (ou Cmd+P no Mac) "
                "no programa que abriu o arquivo."
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erro ao Abrir PDF",
                f"Não foi possível abrir o PDF: {e}\n\n"
                f"Você pode tentar abrir manualmente o arquivo em:\n{self.arquivo_pdf}"
            )

    def mostrar_sobre(self):
        """
        Exibe informações sobre o aplicativo.
        """
        messagebox.showinfo(
            "Sobre",
            "Aplicação de Ordem de Serviço v2.0\n"
            "Desenvolvido por Eduardo\n\n"
            "- Ordens de serviço salvas automaticamente\n"
            "- Reimpressão de ordens anteriores\n"
            "- Gerenciador de histórico"
        )
        
    def atualizar_menu_historico(self):
        """
        Atualiza o menu de histórico com as últimas ordens de serviço.
        """
        # Limpa o menu de histórico atual
        self.historico_menu.delete(0, 'end')
        
        # Obtém as últimas ordens
        try:
            ultimas_ordens = db_manager.listar_ultimas_ordens(10)
            
            if not ultimas_ordens:
                self.historico_menu.add_command(
                    label="Nenhuma ordem encontrada",
                    state="disabled"
                )
                return
                
            # Adiciona as ordens ao menu
            for ordem in ultimas_ordens:
                numero = ordem.get('numero_os', '?')
                nome = ordem.get('nome_cliente', 'Cliente')
                data = ordem.get('data_emissao', '')
                if data:
                    try:
                        # Formata a data para DD/MM/YYYY
                        data_obj = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                        data = data_obj.strftime('%d/%m/%Y')
                    except:
                        pass
                
                label = f"OS {numero:04d} - {nome[:20]} - {data}"
                
                # Cria uma função que carrega essa OS específica
                # Usa uma função lambda com closure para capturar o valor atual
                self.historico_menu.add_command(
                    label=label,
                    command=lambda o=ordem: self.carregar_os_antiga(o)
                )
        except Exception as e:
            print(f"Erro ao atualizar menu de histórico: {e}")
            self.historico_menu.add_command(
                label="Erro ao carregar histórico",
                state="disabled"
            )

    def carregar_os_antiga(self, ordem):
        """
        Carrega uma OS antiga nos campos do formulário.
        
        Args:
            ordem (dict): Dicionário com os dados da ordem
        """
        # Perguntar ao usuário se deseja carregar os dados
        resposta = messagebox.askyesno(
            "Carregar OS Antiga",
            f"Deseja carregar os dados da OS {ordem.get('numero_os')}?\n"
            f"Cliente: {ordem.get('nome_cliente')}\n"
            f"Data: {ordem.get('data_emissao')}"
        )
        
        if not resposta:
            return
            
        # Limpa os campos atuais
        self.limpar_campos()
        
        # Preenche com os dados da OS antiga
        # Nome do cliente
        if ordem.get('nome_cliente'):
            self.nome_cliente_entry.delete(0, 'end')
            self.nome_cliente_entry.insert(0, ordem.get('nome_cliente', ''))
            
        # CPF
        if ordem.get('cpf_cliente'):
            self.cpf_entry.delete(0, 'end')
            self.cpf_entry.insert(0, ordem.get('cpf_cliente', ''))
            
        # Telefone
        if ordem.get('telefone_cliente'):
            self.telefone_entry.delete(0, 'end')
            self.telefone_entry.insert(0, ordem.get('telefone_cliente', ''))
            
        # Detalhes do produto
        if ordem.get('detalhes_produto'):
            self.detalhes_text.delete('1.0', 'end')
            self.detalhes_text.insert('1.0', ordem.get('detalhes_produto', ''))
            
        # Valor do produto
        if ordem.get('valor_produto') is not None:
            self.valor_produto_entry.delete(0, 'end')
            self.valor_produto_entry.insert(0, str(ordem.get('valor_produto', '')).replace('.', ','))
            
        # Valor da entrada
        if ordem.get('valor_entrada') is not None:
            self.valor_entrada_entry.delete(0, 'end')
            self.valor_entrada_entry.insert(0, str(ordem.get('valor_entrada', '')).replace('.', ','))
            
        # Frete
        if ordem.get('frete') is not None:
            self.frete_entry.delete(0, 'end')
            self.frete_entry.insert(0, str(ordem.get('frete', '')).replace('.', ','))
            
        # Forma de pagamento
        if ordem.get('forma_pagamento'):
            self.pagamento_combo.set(ordem.get('forma_pagamento', ''))
            
        # Prazo
        if ordem.get('prazo') is not None:
            self.prazo_entry.delete(0, 'end')
            self.prazo_entry.insert(0, str(ordem.get('prazo', '')))
            
        # Atualiza o número da OS (mas não salva ainda)
        self.numero_os = ordem.get('numero_os')
        self.numero_os_label.config(text=str(self.numero_os))
        
        # Atualiza o caminho do PDF
        self.arquivo_pdf = ordem.get('caminho_pdf', self.arquivo_pdf)
        
        messagebox.showinfo(
            "OS Carregada",
            f"Ordem de Serviço Nº {ordem.get('numero_os')} carregada com sucesso!\n"
            "Para reimprimir, clique em 'Abrir PDF' ou 'Imprimir PDF'."
        )

    def abrir_gerenciador_ordens(self):
        """
        Abre uma janela para gerenciar ordens de serviço anteriores.
        """
        # Cria uma nova janela
        gerenciador = tb.Toplevel(self.root)
        gerenciador.title("Gerenciador de Ordens de Serviço")
        gerenciador.geometry("800x600")
        gerenciador.grab_set()  # Modal
        
        # Frame de pesquisa
        pesquisa_frame = tb.Frame(gerenciador)
        pesquisa_frame.pack(fill="x", padx=10, pady=10)
        
        tb.Label(pesquisa_frame, text="Buscar por:").pack(side="left", padx=5)
        
        busca_var = tb.StringVar()
        busca_entry = tb.Entry(pesquisa_frame, width=30, textvariable=busca_var)
        busca_entry.pack(side="left", padx=5)
        
        tipo_busca = tb.StringVar(value="cliente")
        rb_cliente = tb.Radiobutton(
            pesquisa_frame, text="Cliente", 
            variable=tipo_busca, value="cliente"
        )
        rb_cliente.pack(side="left", padx=5)
        
        rb_os = tb.Radiobutton(
            pesquisa_frame, text="Número OS", 
            variable=tipo_busca, value="os"
        )
        rb_os.pack(side="left", padx=5)
        
        # Treeview para exibir resultados
        colunas = ("numero_os", "nome_cliente", "data_emissao", "valor_produto")
        
        # Frame para conter a treeview e scrollbar
        tree_frame = tb.Frame(gerenciador)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar vertical
        scrollbar = tb.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        tree = tb.Treeview(
            tree_frame, 
            columns=colunas,
            show="headings",
            selectmode="browse",
            yscrollcommand=scrollbar.set
        )
        
        # Configurar colunas
        tree.heading("numero_os", text="OS Nº")
        tree.heading("nome_cliente", text="Cliente")
        tree.heading("data_emissao", text="Data Emissão")
        tree.heading("valor_produto", text="Valor")
        
        tree.column("numero_os", width=60, anchor="center")
        tree.column("nome_cliente", width=200)
        tree.column("data_emissao", width=100, anchor="center")
        tree.column("valor_produto", width=100, anchor="e")
        
        tree.pack(fill="both", expand=True)
        
        # Configurar scrollbar
        scrollbar.config(command=tree.yview)
        
        # Frame de botões
        botoes_frame = tb.Frame(gerenciador)
        botoes_frame.pack(fill="x", padx=10, pady=10)
        
        # Função para carregar ordens na treeview
        def carregar_ordens():
            # Limpa a treeview
            for item in tree.get_children():
                tree.delete(item)
                
            # Obtém as últimas ordens
            try:
                if busca_var.get():
                    if tipo_busca.get() == "cliente":
                        ordens = db_manager.buscar_ordem_por_cliente(busca_var.get())
                    else:
                        try:
                            numero_os = int(busca_var.get())
                            ordem = db_manager.buscar_ordem_por_numero(numero_os)
                            ordens = [ordem] if ordem else []
                        except ValueError:
                            messagebox.showerror(
                                "Erro", 
                                "Número de OS inválido. Informe apenas números."
                            )
                            return
                else:
                    ordens = db_manager.listar_ultimas_ordens(100)
                
                # Adiciona as ordens à treeview
                for ordem in ordens:
                    if not ordem:
                        continue
                        
                    # Formata data
                    data = ordem.get('data_emissao', '')
                    if data:
                        try:
                            data_obj = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
                            data_fmt = data_obj.strftime('%d/%m/%Y')
                        except:
                            data_fmt = data
                    else:
                        data_fmt = ''
                    
                    # Formata valor
                    valor = ordem.get('valor_produto')
                    if valor is not None:
                        valor_fmt = f"R$ {valor:.2f}".replace('.', ',')
                    else:
                        valor_fmt = ''
                    
                    tree.insert(
                        "", "end",
                        values=(
                            ordem.get('numero_os', ''),
                            ordem.get('nome_cliente', ''),
                            data_fmt,
                            valor_fmt
                        ),
                        tags=(str(ordem.get('id')),)  # Usamos o ID como tag para recuperar depois
                    )
                    
                # Mensagem se não encontrar nada
                if not ordens:
                    messagebox.showinfo(
                        "Busca", 
                        "Nenhuma ordem encontrada com os critérios informados."
                    )
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar ordens: {e}")
        
        # Função para carregar uma ordem selecionada
        def carregar_ordem_selecionada():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showerror("Erro", "Nenhuma ordem selecionada.")
                return
                
            # Obtém o ID da ordem (que está na tag)
            item_id = tree.item(selecionado, "tags")[0]
            try:
                # Busca a ordem com base no número da OS
                os_num = tree.item(selecionado, "values")[0]
                ordem = db_manager.buscar_ordem_por_numero(int(os_num))
                
                if ordem:
                    gerenciador.destroy()  # Fecha a janela do gerenciador
                    self.carregar_os_antiga(ordem)
                else:
                    messagebox.showerror("Erro", "Ordem não encontrada no banco de dados.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar ordem: {e}")
        
        # Função para abrir o PDF de uma ordem selecionada
        def abrir_pdf_selecionado():
            selecionado = tree.selection()
            if not selecionado:
                messagebox.showerror("Erro", "Nenhuma ordem selecionada.")
                return
                
            # Obtém o número da OS
            os_num = tree.item(selecionado, "values")[0]
            try:
                # Busca a ordem
                ordem = db_manager.buscar_ordem_por_numero(int(os_num))
                
                if not ordem:
                    messagebox.showerror("Erro", "Ordem não encontrada no banco de dados.")
                    return
                    
                # Verifica se o PDF existe
                caminho_pdf = ordem.get('caminho_pdf')
                if not caminho_pdf or not os.path.exists(caminho_pdf):
                    messagebox.showerror(
                        "Erro", 
                        f"PDF não encontrado: {caminho_pdf}\n"
                        "O arquivo pode ter sido movido ou excluído."
                    )
                    return
                
                # Abre o PDF
                try:
                    sistema = platform.system()
                    if sistema == "Windows":
                        os.startfile(caminho_pdf)
                    elif sistema == "Darwin":  # macOS
                        subprocess.run(["open", caminho_pdf])
                    else:  # Linux
                        subprocess.run(["xdg-open", caminho_pdf])
                    
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao abrir PDF: {e}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar ordem: {e}")
        
        # Botão de Buscar
        btn_buscar = tb.Button(
            pesquisa_frame, text="Buscar", 
            command=carregar_ordens, bootstyle=SUCCESS
        )
        btn_buscar.pack(side="left", padx=5)
        
        # Enter na caixa de pesquisa também busca
        busca_entry.bind("<Return>", lambda e: carregar_ordens())
        
        # Botões de ação
        btn_carregar = tb.Button(
            botoes_frame, text="Carregar OS", 
            command=carregar_ordem_selecionada, bootstyle=PRIMARY, width=15
        )
        btn_carregar.pack(side="left", padx=5)
        
        btn_abrir_pdf = tb.Button(
            botoes_frame, text="Abrir PDF", 
            command=abrir_pdf_selecionado, bootstyle=INFO, width=15
        )
        btn_abrir_pdf.pack(side="left", padx=5)
        
        btn_imprimir = tb.Button(
            botoes_frame, text="Imprimir", 
            command=lambda: self.imprimir_os_selecionada(tree), bootstyle=WARNING, width=15
        )
        btn_imprimir.pack(side="left", padx=5)
        
        btn_fechar = tb.Button(
            botoes_frame, text="Fechar", 
            command=gerenciador.destroy, bootstyle=DANGER, width=15
        )
        btn_fechar.pack(side="right", padx=5)
        
        # Duplo clique na treeview carrega a ordem
        tree.bind("<Double-1>", lambda e: carregar_ordem_selecionada())
        
        # Carrega as ordens iniciais
        carregar_ordens()

    def imprimir_os_selecionada(self, tree):
        """
        Imprime a OS selecionada no gerenciador.
        """
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showerror("Erro", "Nenhuma ordem selecionada.")
            return
            
        # Obtém o número da OS
        os_num = tree.item(selecionado, "values")[0]
        
        try:
            # Busca a ordem
            ordem = db_manager.buscar_ordem_por_numero(int(os_num))
            
            if not ordem:
                messagebox.showerror("Erro", "Ordem não encontrada no banco de dados.")
                return
                
            # Verifica se o PDF existe
            caminho_pdf = ordem.get('caminho_pdf')
            if not caminho_pdf or not os.path.exists(caminho_pdf):
                messagebox.showerror(
                    "Erro", 
                    f"PDF não encontrado: {caminho_pdf}\n"
                    "O arquivo pode ter sido movido ou excluído."
                )
                return
            
            # Imprime o PDF
            info_impressao = verificar_disponibilidade_impressao()
            sucesso, mensagem = imprimir_pdf_service(caminho_pdf)
            
            if sucesso:
                if mensagem:
                    # Se há mensagem, é provavelmente um fallback (abertura manual)
                    messagebox.showinfo(
                        "PDF Aberto", 
                        f"{mensagem}\n\n"
                        "O PDF foi aberto com o programa padrão. "
                        "Para imprimir, use Ctrl+P no programa aberto."
                    )
                else:
                    # Impressão direta bem-sucedida
                    messagebox.showinfo(
                        "Impressão", 
                        "PDF enviado para impressão com sucesso!"
                    )
            else:
                # Erro na impressão
                messagebox.showerror("Erro de Impressão", mensagem)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao imprimir ordem: {e}")
            
    def buscar_os_por_numero(self):
        """
        Busca uma ordem de serviço pelo número.
        """
        # Solicita o número da OS
        from tkinter.simpledialog import askinteger
        numero = askinteger(
            "Buscar OS", 
            "Informe o número da OS:",
            minvalue=1
        )
        
        if not numero:
            return
            
        # Busca a ordem
        try:
            ordem = db_manager.buscar_ordem_por_numero(numero)
            
            if ordem:
                self.carregar_os_antiga(ordem)
            else:
                messagebox.showinfo(
                    "Busca", 
                    f"Ordem de Serviço Nº {numero} não encontrada."
                )
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar ordem: {e}")
            
    def limpar_campos(self):
        """
        Limpa todos os campos do formulário.
        """
        self.nome_cliente_entry.delete(0, 'end')
        self.cpf_entry.delete(0, 'end')
        self.telefone_entry.delete(0, 'end')
        self.detalhes_text.delete('1.0', 'end')
        self.valor_produto_entry.delete(0, 'end')
        self.valor_entrada_entry.delete(0, 'end')
        self.frete_entry.delete(0, 'end')
        self.pagamento_combo.set('')
        self.prazo_entry.delete(0, 'end')
        
        # Readiciona os placeholders
        self.add_placeholder(
            self.nome_cliente_entry, "Digite o nome do cliente"
        )
        self.add_placeholder(
            self.cpf_entry, "Somente números, 11 dígitos"
        )
        self.add_placeholder(
            self.telefone_entry, "Ex: 37999999999"
        )
        self.add_placeholder(
            self.valor_produto_entry, "Ex: 100,00"
        )
        self.add_placeholder(
            self.valor_entrada_entry, "Ex: 50,00"
        )
        self.add_placeholder(
            self.frete_entry, "Ex: 10,00"
        )
        self.add_placeholder(
            self.prazo_entry,
            "Insira o número de dias. Ex: 30 -> daqui a 30 dias"
        )

    def _ajustar_fontes(self, event):
        """
        Ajusta o tamanho das fontes dos widgets principais conforme o tamanho
        da janela, mantendo a responsividade da interface.
        """
        # Ajuste de fonte proporcional ao tamanho da janela
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        fator = min(largura / self.base_width, altura / self.base_height)
        tamanho_base = 11
        tamanho = max(int(tamanho_base * fator), 9)
        for widget in self.widgets_to_resize:
            try:
                widget.config(font=("Montserrat", tamanho))
            except Exception:
                pass
