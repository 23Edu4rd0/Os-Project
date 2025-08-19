"""
Gerenciamento de cards de pedidos
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import INFO, WARNING, SUCCESS, DANGER, SECONDARY
from datetime import datetime, timedelta


class PedidosCard:
    """Gerencia a criação e exibição de cards de pedidos"""
    
    def __init__(self, interface):
        self.interface = interface
        
    def criar_card(self, pedido, row, col):
        """Cria um card para o pedido"""
        # Frame do card com estilo mais clean
        card_frame = tb.Frame(self.interface.scrollable_frame, bootstyle="dark", relief="solid", borderwidth=1)
        card_frame.grid(row=row, column=col, padx=6, pady=6, sticky="nsew", ipadx=5, ipady=5)
        
        # Header do card
        self._criar_header(card_frame, pedido)
        
        # Conteúdo do card
        self._criar_conteudo(card_frame, pedido)
        
        # Botões do card
        self._criar_botoes(card_frame, pedido)
        
        return card_frame
    
    def _criar_header(self, parent, pedido):
        """Cria o header do card"""
        header_frame = tb.Frame(parent)
        header_frame.pack(fill="x", padx=8, pady=(8, 5))
        
        # Número da OS (destacado)
        numero_label = tb.Label(header_frame, 
                text=f"OS #{pedido.get('numero_os', 'N/A')}", 
                font=("Arial", 13, "bold"),
                foreground="#ffffff")
        numero_label.pack(anchor="w")
        
        # Status com cor
        status = pedido.get('status', 'desconhecido')
        status_color = self._get_status_color(status)
        
        status_label = tb.Label(header_frame, 
                text=f"Status: {status.upper()}", 
                font=("Arial", 9, "bold"),
                foreground=status_color)
        status_label.pack(anchor="w", pady=(3, 0))
        
        # Dias restantes para entrega
        dias_restantes = self._calcular_dias_restantes(pedido)
        if dias_restantes is not None:
            if dias_restantes > 0:
                prazo_text = f"⏰ {dias_restantes} dias restantes"
                prazo_color = "#ffaa00" if dias_restantes <= 7 else "#00ff88"
            elif dias_restantes == 0:
                prazo_text = "⚠️ Entrega hoje!"
                prazo_color = "#ff6600"
            else:
                prazo_text = f"🔴 Atrasado {abs(dias_restantes)} dias"
                prazo_color = "#ff4444"
            
            prazo_label = tb.Label(header_frame, 
                    text=prazo_text, 
                    font=("Arial", 9, "bold"), 
                    foreground=prazo_color)
            prazo_label.pack(anchor="w", pady=(2, 0))
    
    def _criar_conteudo(self, parent, pedido):
        """Cria o conteúdo do card"""
        content_frame = tb.Frame(parent)
        content_frame.pack(fill="x", padx=8, pady=5)
        
        # Cliente (destacado)
        cliente = pedido.get('nome_cliente', 'Cliente não informado')
        cliente_label = tb.Label(content_frame, 
                text=f"Cliente: {cliente}", 
                font=("Arial", 10, "bold"),
                foreground="#ffffff")
        cliente_label.pack(anchor="w", pady=(0, 3))
        
        # Data de criação da OS
        data_criacao = pedido.get('data_criacao', '')
        if data_criacao:
            if isinstance(data_criacao, str) and len(data_criacao) > 10:
                data_criacao_formatada = data_criacao[:10]  # Apenas a data, sem hora
            else:
                data_criacao_formatada = str(data_criacao)
            
            data_label = tb.Label(content_frame, 
                    text=f"Criada em: {data_criacao_formatada}", 
                    font=("Arial", 9),
                    foreground="#aaaaaa")
            data_label.pack(anchor="w", pady=(0, 3))
        
        # Valor (destacado)
        valor = pedido.get('valor_total', pedido.get('valor_produto', 0))
        if valor and valor > 0:
            valor_label = tb.Label(content_frame, 
                    text=f"Valor: R$ {valor:.2f}", 
                    font=("Arial", 10, "bold"),
                    foreground="#00ff88")
            valor_label.pack(anchor="w", pady=(3, 5))
        
        # Resumo dos produtos
        self._criar_resumo_produtos(content_frame, pedido)
    
    def _criar_resumo_produtos(self, parent, pedido):
        """Cria resumo dos produtos do pedido com layout otimizado para 2 linhas VISÍVEIS"""
        detalhes = pedido.get('detalhes_produto', pedido.get('descricao', ''))
        
        if not detalhes:
            return
            
        # Container principal com altura suficiente para 2 linhas completas
        resumo_frame = tb.Frame(parent, height=85)
        resumo_frame.pack(fill="x", pady=(3, 0))
        resumo_frame.pack_propagate(False)  # Evita expansão automática
        
        # Label de produtos
        produtos_label = tb.Label(resumo_frame, 
                text="Produtos:", 
                font=("Arial", 9, "bold"),
                foreground="#cccccc")
        produtos_label.pack(anchor="w", pady=(0, 3))
        
        # Container dos produtos com scrollbar se necessário
        produtos_container = tb.Frame(resumo_frame)
        produtos_container.pack(fill="both", expand=True, padx=5)
        
        # Dividir produtos de forma inteligente
        linhas_produtos = self._dividir_produtos_otimizado(detalhes)
        
        # Mostrar até 2 linhas com altura garantida
        for i, linha in enumerate(linhas_produtos[:2]):
            if linha.strip():  # Só criar se tem conteúdo
                # Frame para cada linha de produto
                linha_frame = tb.Frame(produtos_container, height=22)
                linha_frame.pack(fill="x", pady=1)
                linha_frame.pack_propagate(False)
                
                desc_label = tb.Label(linha_frame, 
                        text=f"• {linha}", 
                        font=("Arial", 8),
                        foreground="#999999",
                        anchor="w",
                        justify="left")
                desc_label.pack(side="left", anchor="w", padx=3)
    
    def _dividir_produtos_otimizado(self, detalhes):
        """Divisão otimizada de produtos - CORRIGIDO PARA \\n E \n"""
        MAX_CHARS = 55
        
        # Cache para evitar recálculos
        if not hasattr(self, '_cache_produtos'):
            self._cache_produtos = {}
        
        if detalhes in self._cache_produtos:
            return self._cache_produtos[detalhes]
        
        linhas = []
        
        # Quebras de linha naturais - lidar com \\n (escape) e \n (quebra real)
        if '\\n' in detalhes or '\n' in detalhes:
            # Primeiro tentar \\n (escape)
            if '\\n' in detalhes:
                linhas = [linha.strip() for linha in detalhes.split('\\n')[:2] if linha.strip()]
            # Senão tentar \n (quebra real)  
            else:
                linhas = [linha.strip() for linha in detalhes.split('\n')[:2] if linha.strip()]
        # Produtos separados por vírgula
        elif ',' in detalhes and len(detalhes) > MAX_CHARS:
            produtos = [p.strip() for p in detalhes.split(',')]
            linha_atual = ""
            
            for produto in produtos:
                if len(linha_atual + produto) <= MAX_CHARS:
                    linha_atual = f"{linha_atual}, {produto}" if linha_atual else produto
                else:
                    if linha_atual:
                        linhas.append(linha_atual)
                        if len(linhas) >= 2:
                            break
                    linha_atual = produto
            
            if linha_atual and len(linhas) < 2:
                linhas.append(linha_atual)
        # Texto longo - dividir simples
        else:
            if len(detalhes) > MAX_CHARS:
                linhas = [detalhes[:MAX_CHARS] + "..."]
                if len(detalhes) > MAX_CHARS * 2:
                    linhas.append("..." + detalhes[MAX_CHARS:MAX_CHARS*2])
            else:
                linhas = [detalhes]
        
        # Cache do resultado
        self._cache_produtos[detalhes] = linhas
        return linhas
    
    def _calcular_dias_restantes(self, pedido):
        """Calcula quantos dias restam para o prazo de entrega"""
        try:
            # Obter data de criação e prazo
            data_criacao = pedido.get('data_criacao', '')
            prazo_dias = pedido.get('prazo', 30)
            
            if not data_criacao or not prazo_dias:
                return None
            
            # Converter data de criação para datetime
            if isinstance(data_criacao, str):
                # Formato esperado: "2025-08-17 10:30:45" ou "2025-08-17"
                data_base = data_criacao[:10]  # Pegar apenas a data
                data_criacao_dt = datetime.strptime(data_base, '%Y-%m-%d')
            else:
                data_criacao_dt = data_criacao
            
            # Calcular data de entrega prevista
            data_entrega_prevista = data_criacao_dt + timedelta(days=int(prazo_dias))
            
            # Calcular diferença com hoje
            hoje = datetime.now()
            diferenca = (data_entrega_prevista.date() - hoje.date()).days
            
            return diferenca
            
        except Exception as e:
            print(f"Erro ao calcular dias restantes: {e}")
            return None
    
    def _criar_botoes(self, parent, pedido):
        """Cria os botões do card"""
        btn_frame = tb.Frame(parent)
        btn_frame.pack(fill="x", padx=8, pady=(8, 8))
        
        # Primeira linha de botões
        btn_row1 = tb.Frame(btn_frame)
        btn_row1.pack(fill="x", pady=(0, 4))
        
        # Botão Editar
        btn_editar = tb.Button(btn_row1, 
                 text="✏️ Editar", 
                 command=lambda: self.interface.editar_pedido(pedido),
                 bootstyle="info", 
                 width=10)
        btn_editar.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        # Botão Status
        status_text = self._get_status_button_text(pedido.get('status'))
        btn_status = tb.Button(btn_row1, 
                 text=status_text, 
                 command=lambda: self.interface.alterar_status(pedido),
                 bootstyle="warning", 
                 width=10)
        btn_status.pack(side="left", fill="x", expand=True, padx=(2, 0))
        
        # Segunda linha de botões
        btn_row2 = tb.Frame(btn_frame)
        btn_row2.pack(fill="x")
        
        # Botão WhatsApp (se houver telefone)
        telefone = pedido.get('telefone_cliente')
        if telefone:
            btn_whatsapp = tb.Button(btn_row2, 
                     text="📱 WhatsApp", 
                     command=lambda: self.interface.enviar_whatsapp_card(pedido),
                     bootstyle="success", 
                     width=10)
            btn_whatsapp.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        # Botão Excluir
        btn_excluir = tb.Button(btn_row2, 
                 text="🗑️ Excluir", 
                 command=lambda: self.interface.excluir_pedido(pedido),
                 bootstyle="danger", 
                 width=10)
        if telefone:
            btn_excluir.pack(side="left", fill="x", expand=True, padx=(2, 0))
        else:
            btn_excluir.pack(fill="x")
    
    def _get_status_color(self, status):
        """Retorna a cor para o status"""
        cores = {
            'em produção': '#e74c3c',
            'enviado': '#3498db', 
            'entregue': '#27ae60',
            'cancelado': '#95a5a6'
        }
        return cores.get(status.lower(), '#95a5a6')
    
    def _get_status_button_text(self, status):
        """Retorna o texto do botão de status"""
        proximos = {
            'em produção': '📦 Enviar',
            'enviado': '✅ Entregar',
            'entregue': '🔄 Status',
            'cancelado': '🔄 Status'
        }
        return proximos.get(status, '🔄 Status')
