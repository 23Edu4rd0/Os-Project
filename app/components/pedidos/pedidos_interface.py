"""
Interface principal dos pedidos
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS

from database import db_manager
from .pedidos_card import PedidosCard
from .pedidos_modal import PedidosModal
from .pedidos_actions import PedidosActions


class PedidosInterface:
    """Gerencia a interface principal de pedidos"""
    
    def __init__(self, parent):
        self.parent = parent
        self.status_var = tk.StringVar(value="todos")
        self.canvas = None
        self.scrollable_frame = None
        
        # Inicializar módulos
        self.card_manager = PedidosCard(self)
        self.modal_manager = PedidosModal(self)
        self.actions_manager = PedidosActions(self)
        
        self._setup_interface()
        self.carregar_dados()
        
    def _setup_interface(self):
        """Configura a interface principal"""
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
        
        tb.Button(btn_frame, text="➕ Novo Pedido", bootstyle="success-outline", 
                 command=self.novo_pedido, width=15).pack(side="left", padx=3)
        tb.Button(btn_frame, text="🔄 Atualizar", bootstyle="info-outline",
                 command=self.carregar_dados, width=12).pack(side="left", padx=3)
        
        # Frame principal com scroll
        main_frame = tb.Frame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Setup do canvas e scroll
        self._setup_scroll(main_frame)
        
    def _setup_scroll(self, parent):
        """Configura o sistema de scroll"""
        self.canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = tb.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tb.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar scroll com mouse
        def scroll_mouse(event):
            direction = -1 if event.delta > 0 else 1
            self.canvas.yview_scroll(direction, "units")
        
        self.canvas.bind("<MouseWheel>", scroll_mouse)
        self.scrollable_frame.bind("<MouseWheel>", scroll_mouse)
        
        print("Scroll configurado para pedidos com debug ativo")
    
    def carregar_dados(self):
        """Carrega os dados dos pedidos"""
        # Limpar canvas
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        try:
            # Criar dados de teste se necessário
            db_manager.criar_dados_teste()
            
            # Buscar pedidos do banco
            status_filtro = self.status_var.get()
            
            # Usar o método correto do db_manager
            pedidos = db_manager.listar_pedidos_ordenados_por_prazo(limite=100)
            
            # Filtrar por status se necessário
            if status_filtro != "todos":
                pedidos_filtrados = []
                for p in pedidos:
                    status_pedido = p.get('status', '').lower()
                    if status_pedido == status_filtro.lower():
                        pedidos_filtrados.append(p)
                pedidos = pedidos_filtrados
            
            if not pedidos:
                self._mostrar_sem_pedidos()
                return
            
            # Criar grid de cards (3 colunas)
            self._criar_grid_pedidos(pedidos)
            
        except Exception as e:
            print(f"Erro ao carregar pedidos: {e}")
            import traceback
            traceback.print_exc()
            self._mostrar_erro()
    
    def _mostrar_sem_pedidos(self):
        """Mostra mensagem quando não há pedidos"""
        tb.Label(self.scrollable_frame, 
                text="📋 Nenhum pedido encontrado",
                font=("Arial", 14),
                foreground="gray").pack(pady=50)
    
    def _mostrar_erro(self):
        """Mostra mensagem de erro"""
        tb.Label(self.scrollable_frame, 
                text="❌ Erro ao carregar pedidos",
                font=("Arial", 14),
                foreground="red").pack(pady=50)
    
    def _criar_grid_pedidos(self, pedidos):
        """Cria o grid de pedidos em 3 colunas"""
        # Configurar grid com weights para melhor distribuição
        for i in range(3):
            self.scrollable_frame.columnconfigure(i, weight=1, minsize=300)
        
        # Configurar altura uniforme das linhas
        max_row = (len(pedidos) - 1) // 3
        for i in range(max_row + 1):
            self.scrollable_frame.rowconfigure(i, weight=1)
        
        # Criar cards
        for i, pedido in enumerate(pedidos):
            row = i // 3
            col = i % 3
            self.card_manager.criar_card(pedido, row, col)
    
    def novo_pedido(self):
        """Abre modal para novo pedido"""
        self.modal_manager.abrir_modal_novo()
    
    def editar_pedido(self, pedido):
        """Abre modal para editar pedido"""
        self.modal_manager.abrir_modal_edicao(pedido)
    
    def alterar_status(self, pedido):
        """Altera status do pedido"""
        self.actions_manager.alterar_status(pedido)
    
    def excluir_pedido(self, pedido):
        """Exclui um pedido"""
        self.actions_manager.excluir_pedido(pedido)
    
    def enviar_whatsapp_card(self, pedido):
        """Envia WhatsApp para o cliente"""
        self.actions_manager.enviar_whatsapp(pedido)
