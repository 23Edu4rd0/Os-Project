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
        
        # Cache para melhor performance
        self._cache_pedidos = None
        self._cache_timestamp = 0
        self._cache_timeout = 30  # 30 segundos
        
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
        
        self.canvas.create_window((25, 0), window=self.scrollable_frame, anchor="nw")
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
    
    def carregar_dados(self, force_refresh=False):
        """Carrega os dados dos pedidos com cache otimizado"""
        import time
        
        # Verificar cache
        current_time = time.time()
        if (not force_refresh and 
            self._cache_pedidos and 
            current_time - self._cache_timestamp < self._cache_timeout):
            pedidos = self._cache_pedidos
        else:
            # Buscar dados do banco
            try:
                pedidos = db_manager.listar_pedidos_ordenados_por_prazo(limite=25)  # Reduzido para melhor performance
                self._cache_pedidos = pedidos
                self._cache_timestamp = current_time
            except Exception as e:
                print(f"Erro ao carregar pedidos: {e}")
                self._mostrar_erro()
                return
        
        # Limpar canvas de forma eficiente
        self._limpar_canvas()
        
        # Filtrar por status
        status_filtro = self.status_var.get()
        if status_filtro != "todos":
            pedidos = [p for p in pedidos if p.get('status', '').lower() == status_filtro.lower()]
        
        if not pedidos:
            self._mostrar_sem_pedidos()
            return
        
        # Criar grid de cards (3 colunas)
        self._criar_grid_pedidos(pedidos)
    
    def _limpar_canvas(self):
        """Limpa o canvas de forma otimizada"""
        if hasattr(self, 'scrollable_frame') and self.scrollable_frame:
            children = self.scrollable_frame.winfo_children()
            for widget in children:
                widget.destroy()
    
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
        """Cria o grid de pedidos de forma otimizada"""
        colunas = 3
        
        # Configurar grid uma única vez - largura otimizada para eliminar espaço branco excessivo
        for i in range(colunas):
            self.scrollable_frame.columnconfigure(i, weight=1, minsize=430)
        
        # Criar cards de forma eficiente
        for i, pedido in enumerate(pedidos):
            row = i // colunas
            col = i % colunas
            
            try:
                self.card_manager.criar_card(pedido, row, col)
            except Exception as e:
                print(f"Erro ao criar card {i}: {e}")
                continue
        
        # Atualizar layout apenas uma vez no final
        self.scrollable_frame.update_idletasks()
    
    def novo_pedido(self):
        """Abre modal para novo pedido"""
        self.modal_manager.abrir_modal_novo()
        # Invalidar cache após operação
        self._invalidar_cache()
    
    def editar_pedido(self, pedido):
        """Abre modal para editar pedido"""
        self.modal_manager.abrir_modal_edicao(pedido)
        # Invalidar cache após operação
        self._invalidar_cache()
    
    def alterar_status(self, pedido):
        """Altera status do pedido"""
        self.actions_manager.alterar_status(pedido)
        # Invalidar cache após operação
        self._invalidar_cache()
    
    def _invalidar_cache(self):
        """Invalida o cache para forçar refresh na próxima consulta"""
        self._cache_pedidos = None
        self._cache_timestamp = 0
    
    def atualizar(self):
        """Método público para atualizar dados forçando refresh"""
        self.carregar_dados(force_refresh=True)
    
    def excluir_pedido(self, pedido):
        """Exclui um pedido"""
        self.actions_manager.excluir_pedido(pedido)
    
    def enviar_whatsapp_card(self, pedido):
        """Envia WhatsApp para o cliente"""
        self.actions_manager.enviar_whatsapp(pedido)
