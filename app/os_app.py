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

        # Tabs - apenas Clientes e Pedidos
        self.tab_clientes = tb.Frame(self.db_inner_nb)
        self.tab_pedidos = tb.Frame(self.db_inner_nb)
        self.db_inner_nb.add(self.tab_clientes, text="Clientes")
        self.db_inner_nb.add(self.tab_pedidos, text="Pedidos")

        # Clientes
        top_c = tb.Frame(self.tab_clientes)
        top_c.pack(fill="x")
        tb.Button(top_c, text="Novo", bootstyle=SUCCESS, command=self._novo_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_c, text="Editar", command=self._editar_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_c, text="Excluir", bootstyle=DANGER, command=self._excluir_cliente).pack(side="left", padx=5, pady=5)
        tb.Button(top_c, text="Recarregar", command=self._carregar_grid_clientes).pack(side="right", padx=5, pady=5)
        cols_c = ("id","nome","cpf","telefone","email","endereco","referencia")
        self.tree_clientes = tb.Treeview(self.tab_clientes, columns=cols_c, show="headings")
        for col, text, w, anchor in [
            ("id","ID",60,"center"),
            ("nome","Nome",180,"w"),
            ("cpf","CPF",120,"center"),
            ("telefone","Telefone",120,"center"),
            ("email","Email",150,"w"),
            ("endereco","Endereço",200,"w"),
            ("referencia","Referência",150,"w"),
        ]:
            self.tree_clientes.heading(col, text=text)
            self.tree_clientes.column(col, width=w, anchor=anchor)
        ysc = tb.Scrollbar(self.tab_clientes, orient="vertical", command=self.tree_clientes.yview)
        self.tree_clientes.configure(yscroll=ysc.set)
        self.tree_clientes.pack(side="left", fill="both", expand=True, padx=(8,0), pady=(0,8))
        ysc.pack(side="right", fill="y", pady=(0,8))

        # Pedidos (Layout Moderno com Cards)
        top_ped = tb.Frame(self.tab_pedidos)
        top_ped.pack(fill="x", padx=10, pady=5)
        
        # Filtro de status
        self.status_var = tk.StringVar(value="todos")
        status_options = ["todos", "em produção", "enviado", "entregue", "cancelado"]
        tb.Label(top_ped, text="Filtrar por Status:", font=("Arial", 10, "bold")).pack(side="left", padx=(5,0))
        status_combo = tb.Combobox(top_ped, textvariable=self.status_var, values=status_options, width=15, state="readonly")
        status_combo.pack(side="left", padx=5, pady=5)
        status_combo.bind("<<ComboboxSelected>>", lambda e: self._carregar_cards_pedidos())
        
        # Botões CRUD para Pedidos
        btn_frame = tb.Frame(top_ped)
        btn_frame.pack(side="right", padx=5)
        tb.Button(btn_frame, text="➕ Novo", bootstyle=SUCCESS, command=self._novo_pedido).pack(side="left", padx=2)
        tb.Button(btn_frame, text="🔄 Recarregar", command=self._carregar_cards_pedidos).pack(side="left", padx=2)
        
        # Frame principal com scroll para os cards
        self.pedidos_main_frame = tb.Frame(self.tab_pedidos)
        self.pedidos_main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Canvas com scrollbar para cards
        self.pedidos_canvas = tk.Canvas(self.pedidos_main_frame, highlightthickness=0)
        self.pedidos_scrollbar = tb.Scrollbar(self.pedidos_main_frame, orient="vertical", command=self.pedidos_canvas.yview)
        self.pedidos_scrollable_frame = tb.Frame(self.pedidos_canvas)
        
        self.pedidos_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.pedidos_canvas.configure(scrollregion=self.pedidos_canvas.bbox("all"))
        )
        
        self.pedidos_canvas.create_window((0, 0), window=self.pedidos_scrollable_frame, anchor="nw")
        self.pedidos_canvas.configure(yscrollcommand=self.pedidos_scrollbar.set)
        
        self.pedidos_canvas.pack(side="left", fill="both", expand=True)
        self.pedidos_scrollbar.pack(side="right", fill="y")

        # Carregamento inicial (após criar todas as treeviews)
        self._carregar_grid_clientes()
        self._carregar_cards_pedidos()

    def _carregar_cards_pedidos(self):
        """Carrega pedidos em formato de cards modernos."""
        # Limpa cards existentes
        for widget in self.pedidos_scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            # Busca pedidos do banco
            status_filtro = self.status_var.get() if hasattr(self, 'status_var') else "todos"
            pedidos = db_manager.listar_pedidos_ordenados_por_prazo() or []
            if status_filtro and status_filtro != "todos":
                pedidos = [p for p in pedidos if p.get('status', 'em produção') == status_filtro]
            
            if not pedidos:
                # Mensagem quando não há pedidos
                tb.Label(
                    self.pedidos_scrollable_frame, 
                    text="📋 Nenhum pedido encontrado", 
                    font=("Arial", 14),
                    foreground="gray"
                ).pack(pady=50)
                return
            
            # Criar cards para cada pedido
            for i, pedido in enumerate(pedidos):
                self._criar_card_pedido(pedido, i)
                
        except Exception as e:
            tb.Label(
                self.pedidos_scrollable_frame, 
                text=f"❌ Erro ao carregar pedidos: {e}", 
                font=("Arial", 12),
                foreground="red"
            ).pack(pady=20)

    def _criar_card_pedido(self, pedido, index):
        """Cria um card moderno para exibir um pedido."""
        
        # Calcular cor do card baseada no prazo de entrega
        card_bg_color = "#37474F"  # Cor padrão (cinza escuro)
        border_color = "#546E7A"   # Borda padrão
        
        prazo = pedido.get('data_entrega', pedido.get('prazo_entrega', 'N/A'))
        try:
            from datetime import datetime
            if prazo != 'N/A' and prazo and '-' in str(prazo):
                prazo_obj = datetime.strptime(str(prazo), '%Y-%m-%d')
                hoje = datetime.now()
                dias_restantes = (prazo_obj - hoje).days
                
                if dias_restantes < 0:
                    # Vermelho para atrasado
                    card_bg_color = "#4A2C2A"  # Vermelho escuro
                    border_color = "#F44336"   # Borda vermelha
                elif dias_restantes <= 10:
                    # Amarelo para próximo do prazo (≤ 10 dias)
                    card_bg_color = "#4A3C1D"  # Amarelo escuro
                    border_color = "#FF9800"   # Borda laranja/amarela
                else:
                    # Verde para prazo bom (> 10 dias)
                    card_bg_color = "#2E4A2E"  # Verde escuro
                    border_color = "#4CAF50"   # Borda verde
        except:
            pass
        
        # Frame principal do card com design moderno
        card = tb.Frame(self.pedidos_scrollable_frame, padding=20, relief="solid", borderwidth=2)
        card.pack(fill="x", padx=10, pady=8)
        card.configure(style="Card.TFrame")
        
        # Aplicar cores personalizadas ao card
        try:
            card.configure(background=card_bg_color)
            card.configure(relief="solid", borderwidth=2)
            # A cor da borda será aplicada via estilo se necessário
        except:
            pass
        
        # Configurar cores baseadas no status (cores melhores para modo escuro)
        status = pedido.get('status', 'em produção')
        status_colors = {
            'em produção': ('#FF6B35', 'EM PRODUÇÃO'),     # Laranja vibrante
            'enviado': ('#4ECDC4', 'ENVIADO'),         # Verde água
            'entregue': ('#45B7D1', 'ENTREGUE'),        # Azul claro
            'cancelado': ('#F7931E', 'CANCELADO')        # Laranja escuro
        }
        status_color, icon = status_colors.get(status, ('#9B59B6', 'STATUS'))  # Roxo como padrão
        
        # === HEADER DO CARD ===
        header = tb.Frame(card)
        header.pack(fill="x", pady=(0, 15))
        
        # Lado esquerdo: OS e ID
        left_header = tb.Frame(header)
        left_header.pack(side="left", fill="x", expand=True)
        
        # Número da OS em destaque
        os_label = tb.Label(
            left_header, 
            text=f"OS #{pedido.get('numero_os', 'N/A')}", 
            font=("Segoe UI", 16, "bold"),
            foreground="#FFFFFF"
        )
        os_label.pack(anchor="w")
        
        # ID menor embaixo
        id_label = tb.Label(
            left_header, 
            text=f"ID: {pedido.get('id', 'N/A')}", 
            font=("Segoe UI", 10),
            foreground="#B0BEC5"
        )
        id_label.pack(anchor="w")
        
        # Lado direito: Status
        status_frame = tb.Frame(header)
        status_frame.pack(side="right")
        
        status_label = tb.Label(
            status_frame,
            text=f"{status.upper()}",
            font=("Segoe UI", 11, "bold"),
            foreground="#FFFFFF",
            background=status_color,
            padding=(12, 6),
            relief="flat"
        )
        status_label.pack()
        
        # === INFORMAÇÕES PRINCIPAIS ===
        info_grid = tb.Frame(card)
        info_grid.pack(fill="x", pady=(0, 15))
        info_grid.columnconfigure(1, weight=1)
        info_grid.columnconfigure(3, weight=1)
        
        # Linha 1: Cliente e Valor
        cliente_label = tb.Label(
            info_grid, 
            text=f"Cliente: {pedido.get('nome_cliente', 'N/A')}", 
            font=("Segoe UI", 12, "bold"),
            foreground="#ECEFF1"
        )
        cliente_label.grid(row=0, column=0, sticky="w", padx=(0, 30))
        
        # === USAR VALOR TOTAL SEMPRE ===
        valor_total = pedido.get('valor_total', 0)
        
        try:
            valor_total_float = float(valor_total) if valor_total else 0.0
            valor_texto = f"R$ {valor_total_float:,.2f}"
            valor_formatado = valor_texto.replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            valor_formatado = "R$ 0,00"
            
        valor_label = tb.Label(
            info_grid, 
            text=f"Valor Total: {valor_formatado}", 
            font=("Segoe UI", 12, "bold"),
            foreground="#4CAF50"
        )
        valor_label.grid(row=0, column=1, sticky="w")
        
        # Linha 2: Data do Pedido e Prazo de Entrega
        data_pedido = pedido.get('data_emissao', 'N/A')
        try:
            from datetime import datetime
            if data_pedido != 'N/A':
                data_obj = datetime.strptime(data_pedido, '%Y-%m-%d')
                data_pedido = data_obj.strftime('%d/%m/%Y')
        except:
            pass
            
        data_label = tb.Label(
            info_grid, 
            text=f"Pedido: {data_pedido}", 
            font=("Segoe UI", 11),
            foreground="#CFD8DC"
        )
        data_label.grid(row=1, column=1, sticky="w", pady=(8, 0), padx=(0, 30))
        # === CALCULAR PRAZO - USAR APENAS CAMPO prazo_dias ===
        prazo_texto = "Prazo não definido"
        prazo_color = "#9E9E9E"
        
        # Usar APENAS o campo prazo_dias (em dias)
        prazo_dias = pedido.get('prazo_dias')
        
        if prazo_dias is not None:
            try:
                prazo_dias = int(prazo_dias)
                
                # Determinar cor e texto baseado nos dias
                if prazo_dias <= 0:
                    prazo_texto = f"{prazo_dias} dias (ATRASADO)"
                    prazo_color = "#FF5252"
                elif prazo_dias == 1:
                    prazo_texto = "1 dia (HOJE)"
                    prazo_color = "#FF9800"
                elif prazo_dias <= 3:
                    prazo_texto = f"{prazo_dias} dias (URGENTE)"
                    prazo_color = "#FFC107"
                elif prazo_dias <= 10:
                    prazo_texto = f"{prazo_dias} dias (PRÓXIMO)"
                    prazo_color = "#FF9800"
                else:
                    prazo_texto = f"{prazo_dias} dias (OK)"
                    prazo_color = "#4CAF50"
                    
            except Exception as e:
                prazo_texto = "Erro no prazo"
                prazo_color = "#F44336"
        
        prazo_label = tb.Label(
            info_grid, 
            text="Prazo: " + prazo_texto, 
            font=("Segoe UI", 11),
            foreground=prazo_color
        )
        prazo_label.grid(row=1, column=1, sticky="w", pady=(8, 0))
        
        # === SEÇÃO DE PRODUTOS ===
        produtos_frame = tb.LabelFrame(card, text="Produtos/Serviços", padding=10)
        produtos_frame.pack(fill="x", pady=(0, 15))
        
        descricao = pedido.get('detalhes_produto', pedido.get('descricao', 'Sem descrição'))
        
        # Quebrar descrição em linhas se for muito longa
        if len(descricao) > 100:
            # Tentar quebrar em parágrafos se existirem
            linhas = descricao.split('\n')
            descricao_exibida = []
            char_count = 0
            for linha in linhas:
                if char_count + len(linha) > 150:
                    descricao_exibida.append("...")
                    break
                descricao_exibida.append(linha)
                char_count += len(linha)
            descricao = '\n'.join(descricao_exibida)
            
        produto_text = tb.Label(
            produtos_frame, 
            text=descricao, 
            font=("Segoe UI", 10),
            foreground="#E0E0E0",
            wraplength=650,
            justify="left"
        )
        produto_text.pack(anchor="w")
        
        # Observações se existirem
        observacoes = pedido.get('observacoes', '').strip()
        if observacoes:
            obs_frame = tb.LabelFrame(card, text="📝 Observações", padding=8)
            obs_frame.pack(fill="x", pady=(0, 15))
            
            obs_text = tb.Label(
                obs_frame, 
                text=observacoes, 
                font=("Segoe UI", 9),
                foreground="#FFC107",
                wraplength=650,
                justify="left"
            )
            obs_text.pack(anchor="w")
        
        # === BOTÕES DE AÇÃO ===
        btn_frame = tb.Frame(card)
        btn_frame.pack(fill="x", pady=(15, 0))
        
        # Botão Editar
        edit_btn = tb.Button(
            btn_frame,
            text="✏️ Editar",
            bootstyle="primary-outline",
            width=12,
            command=lambda p=pedido: self._editar_pedido_card(p)
        )
        edit_btn.pack(side="left", padx=(0, 10))
        
        # Botão Status
        status_btn = tb.Button(
            btn_frame,
            text="🔄 Status",
            bootstyle="info-outline",
            width=12,
            command=lambda p=pedido: self._alterar_status_pedido(p)
        )
        status_btn.pack(side="left", padx=(0, 10))
        
        # Botão Excluir
        delete_btn = tb.Button(
            btn_frame,
            text="🗑️ Excluir",
            bootstyle="danger-outline",
            width=12,
            command=lambda p=pedido: self._excluir_pedido_card(p)
        )
        delete_btn.pack(side="left", padx=(0, 10))
        
        # Separador visual entre cards
        separator = tb.Separator(self.pedidos_scrollable_frame, orient="horizontal")
        separator.pack(fill="x", padx=20, pady=5)

    def _editar_pedido_card(self, pedido):
        """Edita um pedido específico do card."""
        data = {
            'id': pedido.get('id'),
            'numero_os': pedido.get('numero_os'),
            'cliente': pedido.get('nome_cliente', ''),
            'descricao': pedido.get('detalhes_produto', ''),
            'valor': pedido.get('valor_produto', 0),
            'status': pedido.get('status', 'em produção'),
            'observacoes': pedido.get('observacoes', '')
        }
        self._abrir_modal_pedido(data)

    def _alterar_status_pedido(self, pedido):
        """Altera rapidamente o status de um pedido."""
        status_atual = pedido.get('status', 'em produção')
        statuses = ["em produção", "enviado", "entregue", "cancelado"]
        
        win = tb.Toplevel(self.root)
        win.title('Alterar Status')
        win.transient(self.root)
        win.grab_set()
        win.geometry('350x200')
        
        frm = tb.Frame(win, padding=20)
        frm.pack(fill='both', expand=True)
        
        tb.Label(frm, text=f'OS #{pedido.get("numero_os")} - {pedido.get("nome_cliente")}', 
                font=('Segoe UI', 12, 'bold')).pack(pady=(0, 15))
        
        tb.Label(frm, text='Novo Status:', font=('Segoe UI', 10)).pack(anchor='w')
        
        status_var = tb.StringVar(value=status_atual)
        status_combo = tb.Combobox(frm, textvariable=status_var, values=statuses, 
                                  state="readonly", width=20, font=('Segoe UI', 10))
        status_combo.pack(pady=(5, 20))
        
        def salvar_status():
            novo_status = status_var.get()
            if novo_status != status_atual:
                success = db_manager.atualizar_status_pedido(pedido['id'], novo_status)
                if success:
                    self._carregar_cards_pedidos()
                    messagebox.showinfo('Sucesso', f'Status alterado para "{novo_status}"!')
                    win.destroy()
                else:
                    messagebox.showerror('Erro', 'Falha ao alterar status.')
            else:
                win.destroy()
        
        btn_frame = tb.Frame(frm)
        btn_frame.pack()
        
        tb.Button(btn_frame, text='💾 Salvar', bootstyle="success", 
                 command=salvar_status).pack(side='left', padx=5)
        tb.Button(btn_frame, text='❌ Cancelar', command=win.destroy).pack(side='left', padx=5)

    def _excluir_pedido_card(self, pedido):
        """Exclui um pedido específico do card."""
        if messagebox.askyesno('Confirmar Exclusão', 
                              f'Tem certeza que deseja excluir a OS #{pedido.get("numero_os")}?\n\n'
                              f'Cliente: {pedido.get("nome_cliente")}\n'
                              f'Esta ação não pode ser desfeita.'):
            success = db_manager.deletar_pedido(pedido['id'])
            if success:
                self._carregar_cards_pedidos()
                messagebox.showinfo('Sucesso', 'Pedido excluído com sucesso!')
            else:
                messagebox.showerror('Erro', 'Falha ao excluir pedido.')

    # ===== Ações Clientes =====
        
        tb.Button(
            btn_right, 
            text="🗑️ Excluir", 
            bootstyle="outline-danger",
            command=lambda: self._excluir_pedido_card(pedido)
        ).pack(side="left", padx=2)

    def _editar_pedido_card(self, pedido):
        """Edita pedido a partir do card."""
        data = {
            'id': pedido.get('id'),
            'numero_os': pedido.get('numero_os'),
            'nome_cliente': pedido.get('nome_cliente'),
            'descricao': pedido.get('descricao'),
            'valor_produto': pedido.get('valor_produto'),
            'data_emissao': pedido.get('data_emissao'),
            'prazo_entrega': pedido.get('prazo_entrega'),
            'status': pedido.get('status')
        }
        self._abrir_modal_pedido(data)

    # ===== Ações Clientes =====
        """Altera o status do pedido selecionado."""
        _, vals = self._get_selected(self.tree_pedidos)
        if not vals:
            messagebox.showinfo('Info', 'Selecione um pedido para alterar o status.')
            return
        
        pedido_id = vals[0]
        status_atual = vals[6] if len(vals) > 6 else "em produção"
        
        # Criar janela para alterar status
        win = tb.Toplevel(self.root)
        win.title('Alterar Status do Pedido')
        win.transient(self.root)
        win.grab_set()
        win.geometry('300x200')
        
        frm = tb.Frame(win, padding=10)
        frm.pack(fill='both', expand=True)
        
        tb.Label(frm, text=f'Pedido ID: {pedido_id}').pack(pady=5)
        tb.Label(frm, text=f'Status atual: {status_atual}').pack(pady=5)
        tb.Label(frm, text='Novo status:').pack(pady=(10, 5))
        
        status_var = tb.StringVar(value=status_atual)
        status_options = ["em produção", "enviado", "entregue", "cancelado"]
        status_combo = tb.Combobox(frm, textvariable=status_var, values=status_options, state="readonly")
        status_combo.pack(pady=5)
        
        def salvar_status():
            novo_status = status_var.get()
            if novo_status == status_atual:
                win.destroy()
                return
                
            try:
                # Assumindo que existe um método no db_manager para atualizar status
                success = db_manager.atualizar_status_pedido(pedido_id, novo_status)
                if success:
                    self._carregar_grid_pedidos()
                    messagebox.showinfo('Sucesso', f'Status alterado para: {novo_status}')
                    win.destroy()
                else:
                    messagebox.showerror('Erro', 'Não foi possível alterar o status.')
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao alterar status: {e}')
        
        btns = tb.Frame(frm)
        btns.pack(pady=10)
        tb.Button(btns, text='Salvar', bootstyle=SUCCESS, command=salvar_status).pack(side='left', padx=5)
        tb.Button(btns, text='Cancelar', command=win.destroy).pack(side='left', padx=5)

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
                    c.get('id'), 
                    c.get('nome'), 
                    c.get('cpf'), 
                    c.get('telefone'), 
                    c.get('email'), 
                    c.get('endereco', ''), 
                    c.get('referencia', '')
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
            'id': vals[0], 
            'nome': vals[1], 
            'cpf': vals[2], 
            'telefone': vals[3], 
            'email': vals[4],
            'endereco': vals[5] if len(vals) > 5 else '',
            'referencia': vals[6] if len(vals) > 6 else ''
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
        # troca para a aba Pedidos e recarrega
        try:
            self.db_inner_nb.select(self.tab_pedidos)
        except Exception:
            pass
        self._carregar_grid_pedidos()

    def _abrir_modal_cliente(self, data=None):
        win = tb.Toplevel(self.root)
        win.title('Cliente')
        win.transient(self.root)
        win.grab_set()
        win.geometry('500x450')
        frm = tb.Frame(win, padding=10)
        frm.pack(fill='both', expand=True)
        
        # Labels e campos
        tb.Label(frm, text='Nome:').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='CPF:').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Telefone:').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Email:').grid(row=3, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Endereço:').grid(row=4, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Referência:').grid(row=5, column=0, sticky='e', padx=5, pady=5)
        
        nome_e = tb.Entry(frm, width=40)
        cpf_e = tb.Entry(frm, width=30)
        tel_e = tb.Entry(frm, width=30)
        email_e = tb.Entry(frm, width=40)
        endereco_e = tb.Entry(frm, width=40)
        referencia_e = tb.Entry(frm, width=40)
        
        nome_e.grid(row=0, column=1, sticky='w')
        cpf_e.grid(row=1, column=1, sticky='w')
        tel_e.grid(row=2, column=1, sticky='w')
        email_e.grid(row=3, column=1, sticky='w')
        endereco_e.grid(row=4, column=1, sticky='w')
        referencia_e.grid(row=5, column=1, sticky='w')
        
        # Labels informativas para campos opcionais
        tb.Label(frm, text='(obrigatório)', font=('Arial', 8), foreground='red').grid(row=0, column=2, sticky='w', padx=5)
        tb.Label(frm, text='(opcional)', font=('Arial', 8), foreground='gray').grid(row=4, column=2, sticky='w', padx=5)
        tb.Label(frm, text='(opcional)', font=('Arial', 8), foreground='gray').grid(row=5, column=2, sticky='w', padx=5)
        
        if data:
            nome_e.insert(0, data.get('nome') or '')
            cpf_e.insert(0, data.get('cpf') or '')
            tel_e.insert(0, data.get('telefone') or '')
            email_e.insert(0, data.get('email') or '')
            endereco_e.insert(0, data.get('endereco') or '')
            referencia_e.insert(0, data.get('referencia') or '')

        def salvar():
            nome = nome_e.get().strip()
            cpf = cpf_e.get().strip() or None
            tel = tel_e.get().strip() or None
            email = email_e.get().strip() or None
            endereco = endereco_e.get().strip() or None
            referencia = referencia_e.get().strip() or None
            
            if not nome:
                messagebox.showerror('Erro', 'Nome é obrigatório.')
                return
            
            if data and data.get('id'):
                ok = db_manager.atualizar_cliente(int(data['id']), nome, cpf, tel, email, endereco, referencia)
            else:
                ok = db_manager.upsert_cliente(nome, cpf, tel, email, endereco, referencia) is not None
            if ok:
                self._carregar_grid_clientes()
                win.destroy()
            else:
                messagebox.showerror('Erro', 'Falha ao salvar cliente.')

        btns = tb.Frame(frm)
        btns.grid(row=6, column=0, columnspan=3, pady=10)
        tb.Button(btns, text='Salvar', bootstyle=SUCCESS, command=salvar).pack(side='left', padx=5)
        tb.Button(btns, text='Cancelar', command=win.destroy).pack(side='left', padx=5)

    # ===== Ações Pedidos =====
    def _novo_pedido(self):
        """Abre modal para criar novo pedido."""
        self._abrir_modal_pedido()

    def _editar_pedido(self):
        """Função mantida por compatibilidade - agora usa cards."""
        messagebox.showinfo('Info', 'Use o botão "Editar" no card do pedido desejado.')

    def _excluir_pedido(self):
        """Função mantida por compatibilidade - agora usa cards."""
        messagebox.showinfo('Info', 'Use o botão "Excluir" no card do pedido desejado.')

    def _abrir_modal_pedido(self, data=None):
        """Abre modal para criar/editar pedido."""
        win = tb.Toplevel(self.root)
        win.title('Novo Pedido' if not data else f'Editar Pedido #{data.get("numero_os")}')
        win.transient(self.root)
        win.grab_set()
        win.geometry('700x800')
        
        # Frame principal com scroll
        main_canvas = tb.Canvas(win)
        scrollbar = tb.Scrollbar(win, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tb.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        frm = tb.Frame(scrollable_frame, padding=15)
        frm.pack(fill='both', expand=True)
        
        # === SEÇÃO CLIENTE ===
        client_frame = tb.LabelFrame(frm, text="📋 Informações do Cliente", padding=10)
        client_frame.pack(fill='x', pady=(0, 15))
        
        # Buscar lista de clientes para autocompletar
        try:
            clientes = db_manager.listar_clientes(1000)
            nomes_clientes = [c.get('nome', '') for c in clientes if c.get('nome')]
        except:
            nomes_clientes = []
        
        # Frame para cliente com combobox e botão
        cliente_frame = tb.Frame(client_frame)
        cliente_frame.pack(fill='x', pady=5)
        cliente_frame.columnconfigure(0, weight=1)
        
        tb.Label(cliente_frame, text='Cliente:', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        cliente_combo = tb.Combobox(cliente_frame, values=nomes_clientes, width=50, state="normal", font=('Segoe UI', 10))
        cliente_combo.pack(fill='x', pady=(5, 0))
        
        # Botão "Novo Cliente" (inicialmente escondido)
        btn_novo_cliente = tb.Button(
            cliente_frame, 
            text='➕ Adicionar Novo Cliente', 
            bootstyle="success-outline",
            command=lambda: self._abrir_novo_cliente_rapido(win, cliente_combo, cliente_combo.get())
        )
        
        # Label de aviso (inicialmente escondido)
        aviso_label = tb.Label(cliente_frame, text='', foreground='#ffa500', font=('Segoe UI', 9))
        
        # === SEÇÃO PRAZO ===
        prazo_frame = tb.LabelFrame(frm, text="⏰ Prazo de Entrega", padding=10)
        prazo_frame.pack(fill='x', pady=(0, 15))
        
        tb.Label(prazo_frame, text='Dias para entrega:', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        prazo_var = tb.StringVar(value="30")
        prazo_entry = tb.Entry(prazo_frame, textvariable=prazo_var, width=10, font=('Segoe UI', 10))
        prazo_entry.pack(anchor='w', pady=(5, 5))
        
        # Label para mostrar data calculada
        data_entrega_label = tb.Label(prazo_frame, text='', foreground='#4CAF50', font=('Segoe UI', 9))
        data_entrega_label.pack(anchor='w')
        
        def atualizar_data_entrega():
            try:
                dias = int(prazo_var.get())
                from datetime import datetime, timedelta
                data_futura = datetime.now() + timedelta(days=dias)
                data_entrega_label.config(text=f"📅 Data de entrega: {data_futura.strftime('%d/%m/%Y')}")
            except:
                data_entrega_label.config(text="⚠️ Número de dias inválido")
        
        prazo_var.trace_add('write', lambda *args: atualizar_data_entrega())
        atualizar_data_entrega()  # Atualizar inicialmente
        
        # === SEÇÃO PRODUTOS ===
        produtos_frame = tb.LabelFrame(frm, text="📦 Produtos", padding=10)
        produtos_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        # Lista de produtos
        self.produtos_list = []
        produtos_container = tb.Frame(produtos_frame)
        produtos_container.pack(fill='both', expand=True)
        
        def adicionar_produto():
            produto_frame = tb.Frame(produtos_container, relief='ridge', borderwidth=1, padding=8)
            produto_frame.pack(fill='x', pady=5)
            
            # Cabeçalho do produto
            header_frame = tb.Frame(produto_frame)
            header_frame.pack(fill='x')
            
            tb.Label(header_frame, text=f'🏷️ Produto {len(self.produtos_list) + 1}', 
                    font=('Segoe UI', 10, 'bold'), foreground='#FF6B35').pack(side='left')
            
            # Botão remover produto
            if len(self.produtos_list) > 0:  # Não permite remover se é o único
                remove_btn = tb.Button(header_frame, text='🗑️ Remover', bootstyle="danger-outline",
                                     command=lambda pf=produto_frame: remover_produto(pf))
                remove_btn.pack(side='right')
            
            # Campos do produto
            campos_frame = tb.Frame(produto_frame)
            campos_frame.pack(fill='x', pady=(10, 0))
            campos_frame.columnconfigure(1, weight=1)
            
            # Linha 1: Descrição
            tb.Label(campos_frame, text='Descrição:').grid(row=0, column=0, sticky='e', padx=(0, 10), pady=5)
            desc_entry = tb.Entry(campos_frame, width=40, font=('Segoe UI', 10))
            desc_entry.grid(row=0, column=1, sticky='ew', pady=5)
            
            # Linha 2: Cor e Gavetas
            tb.Label(campos_frame, text='Cor:').grid(row=1, column=0, sticky='e', padx=(0, 10), pady=5)
            cor_frame = tb.Frame(campos_frame)
            cor_frame.grid(row=1, column=1, sticky='ew', pady=5)
            cor_frame.columnconfigure(0, weight=1)
            
            cor_combo = tb.Combobox(cor_frame, values=[
                "Branco", "Preto", "Madeira Natural", "Carvalho", "Mogno", 
                "Cinza", "Azul", "Verde", "Vermelho", "Personalizada"
            ], state="readonly", width=20)
            cor_combo.grid(row=0, column=0, sticky='w')
            
            tb.Label(cor_frame, text='Gavetas:').grid(row=0, column=1, padx=(20, 10))
            gavetas_var = tb.StringVar(value="0")
            gavetas_spinbox = tb.Spinbox(cor_frame, from_=0, to=10, textvariable=gavetas_var, width=5)
            gavetas_spinbox.grid(row=0, column=2)
            
            # Linha 3: Valor
            tb.Label(campos_frame, text='Valor (R$):').grid(row=2, column=0, sticky='e', padx=(0, 10), pady=5)
            valor_entry = tb.Entry(campos_frame, width=15, font=('Segoe UI', 10))
            valor_entry.grid(row=2, column=1, sticky='w', pady=5)
            
            # Armazenar referências
            produto_data = {
                'frame': produto_frame,
                'descricao': desc_entry,
                'cor': cor_combo,
                'gavetas': gavetas_var,
                'valor': valor_entry
            }
            
            self.produtos_list.append(produto_data)
            return produto_data
        
        def remover_produto(produto_frame):
            # Encontrar e remover o produto da lista
            for i, produto in enumerate(self.produtos_list):
                if produto['frame'] == produto_frame:
                    self.produtos_list.pop(i)
                    break
            produto_frame.destroy()
            
            # Renumerar produtos restantes
            for i, produto in enumerate(self.produtos_list):
                header = produto['frame'].winfo_children()[0]  # header_frame
                label = header.winfo_children()[0]  # label
                label.config(text=f'🏷️ Produto {i + 1}')
        
        # Adicionar primeiro produto
        adicionar_produto()
        
        # Botão para adicionar mais produtos
        add_produto_btn = tb.Button(produtos_frame, text='➕ Adicionar Outro Produto', 
                                   bootstyle="info-outline", command=adicionar_produto)
        add_produto_btn.pack(pady=10)
        
        # === SEÇÃO STATUS E OBSERVAÇÕES ===
        bottom_frame = tb.LabelFrame(frm, text="📝 Detalhes Finais", padding=10)
        bottom_frame.pack(fill='x', pady=(0, 15))
        
        # Status
        status_frame = tb.Frame(bottom_frame)
        status_frame.pack(fill='x', pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        tb.Label(status_frame, text='Status:', font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w')
        status_combo = tb.Combobox(status_frame, values=["em produção", "enviado", "entregue", "cancelado"], 
                                  state="readonly", width=20, font=('Segoe UI', 10))
        status_combo.set("em produção")
        status_combo.grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        # Valor de entrega/frete (opcional)
        tb.Label(status_frame, text='Frete (R$):', font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, sticky='w', padx=(30, 10))
        frete_entry = tb.Entry(status_frame, width=15, font=('Segoe UI', 10))
        frete_entry.grid(row=0, column=3, sticky='w')
        frete_entry.insert(0, "0.00")
        
        # Observações
        tb.Label(bottom_frame, text='Observações:', font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        obs_text = tb.Text(bottom_frame, width=60, height=4, font=('Segoe UI', 10))
        obs_text.pack(fill='x', pady=(5, 0))
        
        # === AUTOCOMPLETE PARA CLIENTE ===
        def on_cliente_change(event=None):
            valor_digitado = cliente_combo.get().lower().strip()
            
            if len(valor_digitado) >= 1:
                clientes_filtrados = [nome for nome in nomes_clientes if valor_digitado in nome.lower()]
                cliente_combo['values'] = clientes_filtrados
                
                if clientes_filtrados and event and event.keysym not in ['Tab', 'Return', 'Escape']:
                    cliente_combo.event_generate('<Button-1>')
                    win.after(10, lambda: cliente_combo.event_generate('<Down>'))
                
                cliente_exato = any(nome.lower() == valor_digitado for nome in nomes_clientes)
                
                if valor_digitado and not cliente_exato:
                    btn_novo_cliente.pack(pady=(10, 0))
                    aviso_label.pack(pady=(5, 0))
                    aviso_label.config(text=f'⚠️ Cliente "{cliente_combo.get()}" não encontrado!')
                else:
                    btn_novo_cliente.pack_forget()
                    aviso_label.pack_forget()
            else:
                cliente_combo['values'] = nomes_clientes
                btn_novo_cliente.pack_forget()
                aviso_label.pack_forget()
        
        def on_focus_in(event):
            if not cliente_combo.get():
                cliente_combo['values'] = nomes_clientes
        
        def on_key_press(event):
            win.after(10, on_cliente_change)
        
        cliente_combo.bind('<KeyRelease>', on_cliente_change)
        cliente_combo.bind('<KeyPress>', on_key_press)
        cliente_combo.bind('<<ComboboxSelected>>', on_cliente_change)
        cliente_combo.bind('<FocusIn>', on_focus_in)
        cliente_combo.bind('<Button-1>', lambda e: on_cliente_change())
        
        # === PREENCHER DADOS SE EDITANDO ===
        if data:
            cliente_combo.set(data.get('cliente', data.get('nome_cliente', '')))
            
            # Calcular prazo em dias baseado na data de entrega
            prazo_dias = 30
            try:
                data_entrega = data.get('data_entrega')
                if data_entrega:
                    from datetime import datetime
                    entrega_obj = datetime.strptime(data_entrega, '%Y-%m-%d')
                    emissao_obj = datetime.strptime(data.get('data_emissao', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d')
                    prazo_dias = (entrega_obj - emissao_obj).days
            except:
                pass
            
            prazo_var.set(str(prazo_dias))
            status_combo.set(data.get('status', 'em produção'))
            
            # Preencher produtos - tentar fazer parse da descrição
            descricao = data.get('descricao', data.get('detalhes_produto', ''))
            if descricao:
                # Se a descrição parece ser de múltiplos produtos (contém "Produto 1:", "Produto 2:", etc.)
                if 'Produto 1:' in descricao:
                    linhas = descricao.split('\n')
                    produtos_parseados = []
                    
                    for linha in linhas:
                        if linha.startswith('Produto '):
                            # Parse: "Produto 1: Caixa Linda - Cor: Mogno - 5 gaveta(s) - R$ 760.00"
                            try:
                                parts = linha.split(': ', 1)[1]  # Remove "Produto X: "
                                desc_produto = parts.split(' - ')[0]  # Primeira parte é a descrição
                                
                                cor = ''
                                gavetas = 0
                                valor = 0.0
                                
                                # Procurar por padrões
                                if ' - Cor: ' in parts:
                                    cor_part = parts.split(' - Cor: ')[1].split(' - ')[0]
                                    cor = cor_part
                                
                                if ' gaveta(s)' in parts:
                                    gavetas_text = parts.split(' gaveta(s)')[0].split(' - ')[-1]
                                    gavetas = int(gavetas_text)
                                
                                if 'R$ ' in parts:
                                    valor_text = parts.split('R$ ')[1].split(' ')[0]
                                    valor = float(valor_text.replace(',', '.'))
                                
                                produtos_parseados.append({
                                    'descricao': desc_produto,
                                    'cor': cor,
                                    'gavetas': gavetas,
                                    'valor': valor
                                })
                            except:
                                # Se falhar o parse, usar como descrição simples
                                produtos_parseados.append({
                                    'descricao': linha,
                                    'cor': '',
                                    'gavetas': 0,
                                    'valor': 0.0
                                })
                    
                    # Adicionar produtos extras se necessário
                    while len(produtos_parseados) > len(self.produtos_list):
                        adicionar_produto()
                    
                    # Preencher os produtos
                    for i, produto_data in enumerate(produtos_parseados):
                        if i < len(self.produtos_list):
                            produto = self.produtos_list[i]
                            produto['descricao'].delete(0, 'end')
                            produto['descricao'].insert(0, produto_data['descricao'])
                            produto['cor'].set(produto_data['cor'])
                            produto['gavetas'].set(str(produto_data['gavetas']))
                            produto['valor'].delete(0, 'end')
                            produto['valor'].insert(0, str(produto_data['valor']))
                else:
                    # Descrição simples, preencher no primeiro produto
                    if self.produtos_list:
                        self.produtos_list[0]['descricao'].insert(0, descricao)
                        self.produtos_list[0]['valor'].insert(0, str(data.get('valor', data.get('valor_produto', ''))))
            
            if data.get('observacoes'):
                obs_text.insert('1.0', data.get('observacoes', ''))
            
            # Preencher frete se existir
            frete_valor = data.get('frete', 0)
            if frete_valor:
                frete_entry.delete(0, 'end')
                frete_entry.insert(0, str(frete_valor))
        
        # === BOTÕES DE AÇÃO ===
        def salvar_pedido():
            # Validar cliente
            cliente_nome = cliente_combo.get().strip()
            if not cliente_nome:
                messagebox.showerror('Erro', 'Selecione um cliente.')
                return
            
            if cliente_nome not in nomes_clientes:
                messagebox.showerror('Erro', 'Cliente deve existir no sistema. Use o botão "Adicionar Novo Cliente".')
                return
            
            # Validar produtos
            if not self.produtos_list:
                messagebox.showerror('Erro', 'Adicione pelo menos um produto.')
                return
            
            produtos_data = []
            valor_total = 0
            
            for i, produto in enumerate(self.produtos_list):
                desc = produto['descricao'].get().strip()
                cor = produto['cor'].get()
                gavetas = produto['gavetas'].get()
                valor_str = produto['valor'].get().strip()
                
                if not desc:
                    messagebox.showerror('Erro', f'Descrição do produto {i+1} é obrigatória.')
                    return
                
                try:
                    valor = float(valor_str) if valor_str else 0.0
                    valor_total += valor
                except ValueError:
                    messagebox.showerror('Erro', f'Valor do produto {i+1} deve ser um número.')
                    return
                
                produtos_data.append({
                    'descricao': desc,
                    'cor': cor,
                    'gavetas': int(gavetas),
                    'valor': valor
                })
            
            # Montar descrição completa dos produtos
            descricao_completa = []
            for i, p in enumerate(produtos_data):
                desc_produto = f"Produto {i+1}: {p['descricao']}"
                if p['cor']:
                    desc_produto += f" - Cor: {p['cor']}"
                if p['gavetas'] > 0:
                    desc_produto += f" - {p['gavetas']} gaveta(s)"
                if p['valor'] > 0:
                    desc_produto += f" - R$ {p['valor']:.2f}"
                descricao_completa.append(desc_produto)
            
            # Dados do pedido
            frete_valor = 0.0
            try:
                frete_str = frete_entry.get().strip().replace(',', '.')
                frete_valor = float(frete_str) if frete_str else 0.0
            except ValueError:
                pass  # Se não conseguir converter, mantém 0.0
            
            pedido_data = {
                'cliente': cliente_nome,
                'descricao': '\n'.join(descricao_completa),
                'valor': valor_total,
                'frete': frete_valor,
                'valor_total_com_frete': valor_total + frete_valor,
                'status': status_combo.get(),
                'prazo_dias': int(prazo_var.get()),
                'observacoes': obs_text.get('1.0', 'end-1c').strip()
            }
            
            if data and data.get('id'):
                pedido_data['id'] = data['id']
            
            self._salvar_pedido_form(pedido_data, win)
        
        # Frame dos botões
        btn_frame = tb.Frame(frm)
        btn_frame.pack(fill='x', pady=20)
        
        # Botões com cores modernas
        tb.Button(btn_frame, text='💾 Salvar Pedido', bootstyle="success", 
                 command=salvar_pedido, width=20).pack(side='left', padx=10)
        tb.Button(btn_frame, text='❌ Cancelar', bootstyle="secondary", 
                 command=win.destroy, width=15).pack(side='left', padx=5)
        
        # Função para autocomplete em tempo real com dropdown forçado
        def on_cliente_change(event=None):
            valor_digitado = cliente_combo.get().lower().strip()
            
            if len(valor_digitado) >= 1:  # Começa a filtrar com 1 caractere
                # Filtrar clientes que contêm o texto digitado
                clientes_filtrados = [nome for nome in nomes_clientes if valor_digitado in nome.lower()]
                
                # Atualizar valores do combobox
                cliente_combo['values'] = clientes_filtrados
                
                # Forçar abertura do dropdown se há resultados
                if clientes_filtrados and event and event.keysym not in ['Tab', 'Return', 'Escape']:
                    cliente_combo.event_generate('<Button-1>')
                    win.after(10, lambda: cliente_combo.event_generate('<Down>'))
                
                # Verificar se cliente existe exatamente
                cliente_exato = any(nome.lower() == valor_digitado for nome in nomes_clientes)
                
                # Mostrar/esconder botão "Novo Cliente" baseado na busca
                if valor_digitado and not cliente_exato:
                    btn_novo_cliente.grid(row=0, column=1, sticky='w')
                    aviso_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(2, 0))
                    aviso_label.config(text=f'⚠️ Cliente "{cliente_combo.get()}" não encontrado!')
                else:
                    btn_novo_cliente.grid_remove()
                    aviso_label.grid_remove()
            else:
                # Se campo vazio, mostrar todos os clientes
                cliente_combo['values'] = nomes_clientes
                btn_novo_cliente.grid_remove()
                aviso_label.grid_remove()
        
        def on_focus_in(event):
            # Quando o campo ganha foco, mostrar todas as opções
            if not cliente_combo.get():
                cliente_combo['values'] = nomes_clientes
        
        def on_key_press(event):
            # Aguardar um pouco após a tecla ser pressionada para processar o novo valor
            win.after(10, on_cliente_change)
        
        # Bind múltiplos eventos para capturar todas as formas de input
        cliente_combo.bind('<KeyRelease>', on_cliente_change)
        cliente_combo.bind('<KeyPress>', on_key_press)
        cliente_combo.bind('<<ComboboxSelected>>', on_cliente_change)
        cliente_combo.bind('<FocusIn>', on_focus_in)
        cliente_combo.bind('<Button-1>', lambda e: on_cliente_change())

    def _abrir_novo_cliente_rapido(self, parent_win, cliente_combo, nome_inicial=""):
        """Abre modal rápido para adicionar novo cliente."""
        win = tb.Toplevel(parent_win)
        win.title('Adicionar Novo Cliente')
        win.transient(parent_win)
        win.grab_set()
        win.geometry('450x400')
        
        frm = tb.Frame(win, padding=10)
        frm.pack(fill='both', expand=True)
        
        # Campos obrigatórios e opcionais
        tb.Label(frm, text='Nome:').grid(row=0, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='CPF:').grid(row=1, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Telefone:').grid(row=2, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Email:').grid(row=3, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Endereço:').grid(row=4, column=0, sticky='e', padx=5, pady=5)
        tb.Label(frm, text='Referência:').grid(row=5, column=0, sticky='e', padx=5, pady=5)
        
        nome_e = tb.Entry(frm, width=35)
        cpf_e = tb.Entry(frm, width=35)
        tel_e = tb.Entry(frm, width=35)
        email_e = tb.Entry(frm, width=35)
        endereco_e = tb.Entry(frm, width=35)
        referencia_e = tb.Entry(frm, width=35)
        
        nome_e.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        cpf_e.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        tel_e.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        email_e.grid(row=3, column=1, sticky='w', padx=5, pady=5)
        endereco_e.grid(row=4, column=1, sticky='w', padx=5, pady=5)
        referencia_e.grid(row=5, column=1, sticky='w', padx=5, pady=5)
        
        # Labels informativos
        tb.Label(frm, text='(obrigatório)', font=('Arial', 8), foreground='red').grid(row=0, column=2, sticky='w', padx=5)
        tb.Label(frm, text='(opcional)', font=('Arial', 8), foreground='gray').grid(row=4, column=2, sticky='w', padx=5)
        tb.Label(frm, text='(opcional)', font=('Arial', 8), foreground='gray').grid(row=5, column=2, sticky='w', padx=5)
        
        # Preenche nome inicial se fornecido
        if nome_inicial:
            nome_e.insert(0, nome_inicial)
        
        def salvar_e_fechar():
            nome = nome_e.get().strip()
            cpf = cpf_e.get().strip() or None
            tel = tel_e.get().strip() or None
            email = email_e.get().strip() or None
            endereco = endereco_e.get().strip() or None
            referencia = referencia_e.get().strip() or None
            
            if not nome:
                messagebox.showerror('Erro', 'Nome é obrigatório.')
                return
            
            try:
                cliente_id = db_manager.upsert_cliente(nome, cpf, tel, email, endereco, referencia)
                if cliente_id:
                    # Atualizar a lista de clientes no combobox
                    clientes = db_manager.listar_clientes(1000)
                    nomes_clientes = [c.get('nome', '') for c in clientes if c.get('nome')]
                    cliente_combo['values'] = nomes_clientes
                    cliente_combo.set(nome)  # Selecionar o cliente recém-criado
                    
                    self._carregar_grid_clientes()  # Atualizar grid de clientes
                    messagebox.showinfo('Sucesso', f'Cliente "{nome}" adicionado com sucesso!')
                    win.destroy()
                else:
                    messagebox.showerror('Erro', 'Falha ao salvar cliente.')
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao salvar cliente: {e}')
        
        btns = tb.Frame(frm)
        btns.grid(row=6, column=0, columnspan=3, pady=15)
        tb.Button(btns, text='Salvar e Usar', bootstyle=SUCCESS, command=salvar_e_fechar).pack(side='left', padx=5)
        tb.Button(btns, text='Cancelar', command=win.destroy).pack(side='left', padx=5)

    def _salvar_pedido_form(self, data, win):
        try:
            if data.get('id'):
                # Editar pedido existente
                campos = {
                    'nome_cliente': data['cliente'],
                    'detalhes_produto': data['descricao'],
                    'valor_produto': float(data['valor']) if data['valor'] else 0.0
                }
                success = db_manager.atualizar_ordem(int(data['id']), campos)
                # Atualizar status separadamente
                if success:
                    db_manager.atualizar_status_pedido(int(data['id']), data['status'])
            else:
                # Criar novo pedido
                from datetime import datetime, timedelta
                numero_os = Contador.ler_contador()
                prazo_dias = data.get('prazo_dias', 30)
                
                dados_pedido = {
                    'numero_os': numero_os,
                    'nome_cliente': data['cliente'],
                    'detalhes_produto': data['descricao'],
                    'valor_produto': float(data['valor']) if data['valor'] else 0.0,
                    'frete': float(data.get('frete', 0.0)),
                    'data_emissao': datetime.now().strftime('%Y-%m-%d'),
                    'data_entrega': (datetime.now() + timedelta(days=prazo_dias)).strftime('%Y-%m-%d'),
                    'status': data['status'],
                    'observacoes': data.get('observacoes', ''),
                    'prazo': prazo_dias
                }
                
                # Salvar no banco
                ordem_id = db_manager.salvar_ordem(dados_pedido, '')
                if ordem_id:
                    Contador.salvar_contador(numero_os + 1)
                    success = True
                else:
                    success = False
            
            if success:
                self._carregar_cards_pedidos()
                messagebox.showinfo('Sucesso', 'Pedido salvo com sucesso!')
                win.destroy()
            else:
                messagebox.showerror('Erro', 'Falha ao salvar pedido.')
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro detalhado ao salvar pedido: {error_details}")
            messagebox.showerror('Erro', f'Erro ao salvar: {str(e)}\n\nDetalhes no console.')

    # ===== Ações Produtos (removidos - agora usando Pedidos) =====
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
