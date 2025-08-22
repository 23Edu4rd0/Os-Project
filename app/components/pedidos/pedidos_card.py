"""
Gerenciamento de cards de pedidos em PyQt6
"""

from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QFontMetrics


class PedidosCard(QWidget):
    """Gerencia a criação e exibição de cards de pedidos"""
    
    # Sinais para comunicação
    editar_clicked = pyqtSignal(int)  # pedido_id
    excluir_clicked = pyqtSignal(int)  # pedido_id
    status_changed = pyqtSignal(int, str)  # pedido_id, novo_status
    
    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        
    def criar_card(self, pedido):
        """Cria um widget card para o pedido"""
        # Frame principal do card
        card_widget = QFrame()
        card_widget.setFixedWidth(430)
        card_widget.setMinimumHeight(300)
        card_widget.setMaximumHeight(400)
        
        # Layout principal do card
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)
        
        # Header do card
        self._criar_header(card_layout, pedido)
        
        # Conteúdo do card
        self._criar_conteudo(card_layout, pedido)
        
        # Botões do card
        self._criar_botoes(card_layout, pedido)
        
        # Aplicar estilo do card
        self._aplicar_estilo_card(card_widget, pedido)
        
        return card_widget
    
    def _criar_header(self, layout, pedido):
        """Cria o header do card"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(3)
        
        # Número da OS (destacado)
        numero_os = pedido.get('numero_os', 'N/A')
        numero_label = QLabel(f"OS #{numero_os}")
        numero_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        numero_label.setStyleSheet("color: #ffffff; background: transparent;")
        header_layout.addWidget(numero_label)
        
        # Status com cor
        status = pedido.get('status', 'desconhecido')
        status_color = self._get_status_color(status)
        
        status_label = QLabel(f"Status: {status.upper()}")
        status_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        status_label.setStyleSheet(f"color: {status_color}; background: transparent;")
        header_layout.addWidget(status_label)
        
        # Dias restantes para entrega
        dias_restantes = self._calcular_dias_restantes(pedido)
        if dias_restantes is not None:
            if dias_restantes > 0:
                prazo_text = f"⏰ {dias_restantes} dias restantes"
            elif dias_restantes == 0:
                prazo_text = "⚠️ Entrega hoje!"
            else:
                prazo_text = f"Atrasado {abs(dias_restantes)} dias"
            
            prazo_label = QLabel(prazo_text)
            prazo_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            prazo_label.setStyleSheet("color: #cccccc; background: transparent;")
            header_layout.addWidget(prazo_label)
        
        layout.addWidget(header_frame)
    
    def _criar_conteudo(self, layout, pedido):
        """Cria o conteúdo do card"""
        content_frame = QFrame()
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        
        # Cliente (destacado)
        cliente = pedido.get('nome_cliente', 'Cliente não informado')
        cliente_label = QLabel(f"Cliente: {cliente}")
        cliente_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        cliente_label.setStyleSheet("color: #ffffff; background: transparent;")
        cliente_label.setWordWrap(True)
        content_layout.addWidget(cliente_label)
        
        # Data de criação da OS
        data_criacao = pedido.get('data_criacao', '')
        if data_criacao:
            if isinstance(data_criacao, str) and len(data_criacao) > 10:
                data_criacao_formatada = data_criacao[:10]  # Apenas a data, sem hora
            else:
                data_criacao_formatada = str(data_criacao)
            
            data_label = QLabel(f"Criada em: {data_criacao_formatada}")
            data_label.setFont(QFont("Segoe UI", 9))
            data_label.setStyleSheet("color: #aaaaaa; background: transparent;")
            content_layout.addWidget(data_label)
        
        # Valor (destacado)
        valor = pedido.get('valor_total', pedido.get('valor_produto', 0))
        if valor and valor > 0:
            valor_label = QLabel(f"Valor: R$ {valor:.2f}")
            valor_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            valor_label.setStyleSheet("color: #cccccc; background: transparent;")
            content_layout.addWidget(valor_label)
        
        # Resumo dos produtos
        self._criar_resumo_produtos(content_layout, pedido)
        
        layout.addWidget(content_frame)
    
    def _criar_resumo_produtos(self, layout, pedido):
        """Cria resumo dos produtos com no máximo 2 linhas, sem quebra; reduz fonte e elide quando necessário.
        Exibe todos os itens via tooltip ao passar o mouse."""
        detalhes = pedido.get('detalhes_produto', pedido.get('descricao', ''))

        if not detalhes:
            return

        # Título de produtos (apenas label, sem clique/expansão)
        produtos_label = QLabel("Produtos:")
        produtos_label.setStyleSheet("color: #cccccc; background: transparent; font-weight: bold;")
        produtos_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        layout.addWidget(produtos_label)

        # Container RESUMO com tooltip (hover mostra tudo)
        produtos_container = QFrame()
        produtos_container.setFixedHeight(85)
        produtos_container.setStyleSheet("background: transparent; border: none;")
        produtos_layout = QVBoxLayout(produtos_container)
        produtos_layout.setContentsMargins(5, 0, 5, 0)
        produtos_layout.setSpacing(2)

        # Linhas originais: respeita os \n (não quebrar produto)
        detalhes_norm = detalhes.replace('\\n', '\n')
        linhas_produtos = [l.strip('• ').strip() for l in detalhes_norm.split('\n') if l.strip()]

        # Tooltip com a lista completa
        try:
            # Tooltip compacto para não cobrir a UI
            full_text = '\n'.join([f"• {l}" for l in linhas_produtos])
            produtos_container.setToolTip(full_text)
        except Exception:
            pass

        # Mostrar até 2 linhas, cada uma forçada a caber em uma linha
        MAX_VISIBLE = 2
        for i, linha in enumerate(linhas_produtos[:MAX_VISIBLE]):
            if not linha:
                continue
            lbl = self._make_single_line_label(f"• {linha}", max_width=380)
            produtos_layout.addWidget(lbl)

        # Indicador de mais itens
        mais_label = None
        if len(linhas_produtos) > MAX_VISIBLE:
            mais_label = QLabel(f"... e mais {len(linhas_produtos) - MAX_VISIBLE} itens")
            mais_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            mais_label.setStyleSheet("color: #666666; background: transparent;")
            produtos_layout.addWidget(mais_label)

        produtos_layout.addStretch()
        layout.addWidget(produtos_container)

        # Removida a área expansível e qualquer comportamento de clique; o hover já mostra tudo via tooltip

    def _make_single_line_label(self, text: str, max_width: int = 380) -> QLabel:
        """Cria um QLabel de linha única; diminui a fonte até min 7 e elide se ainda exceder."""
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #999999; background: transparent;")
        lbl.setWordWrap(False)
        lbl.setFixedHeight(20)
        # Tentar ajustar fonte
        font_size = 9
        min_size = 7
        font = QFont("Segoe UI", font_size)
        fm = None
        while font_size >= min_size:
            font.setPointSize(font_size)
            fm = QFontMetrics(font)
            if fm.horizontalAdvance(text) <= max_width:
                break
            font_size -= 1
        lbl.setFont(font)
        # Se ainda passa, elide
        if fm and fm.horizontalAdvance(text) > max_width:
            elided = fm.elidedText(text, Qt.TextElideMode.ElideRight, max_width)
            lbl.setText(elided)
        return lbl
    
    def _dividir_produtos_otimizado(self, detalhes):
        """Divisão otimizada de produtos - CORRIGIDO PARA \\n E \n"""
        MAX_CHARS = 55
        
        if not detalhes:
            return []
        
        # Normalizar quebras de linha
        detalhes_norm = detalhes.replace('\\n', '\n')
        
        # Dividir por quebras de linha primeiro
        linhas_base = [linha.strip() for linha in detalhes_norm.split('\n') if linha.strip()]
        
        linhas_finais = []
        
        for linha in linhas_base:
            if len(linha) <= MAX_CHARS:
                linhas_finais.append(linha)
            else:
                # Quebrar linha longa em múltiplas linhas
                palavras = linha.split()
                linha_atual = ""
                
                for palavra in palavras:
                    if len(linha_atual + " " + palavra) <= MAX_CHARS:
                        if linha_atual:
                            linha_atual += " " + palavra
                        else:
                            linha_atual = palavra
                    else:
                        if linha_atual:
                            linhas_finais.append(linha_atual)
                        linha_atual = palavra
                
                if linha_atual:
                    linhas_finais.append(linha_atual)
        
        return linhas_finais
    
    def _criar_botoes(self, layout, pedido):
        """Cria os botões do card"""
        botoes_frame = QFrame()
        botoes_layout = QHBoxLayout(botoes_frame)
        botoes_layout.setContentsMargins(0, 5, 0, 0)
        botoes_layout.setSpacing(8)
        
        pedido_id = pedido.get('id')
        
        # Botão Editar
        btn_editar = QPushButton("✏️ Editar")
        btn_editar.setMinimumWidth(80)
        btn_editar.clicked.connect(lambda: self.editar_clicked.emit(pedido_id))
        botoes_layout.addWidget(btn_editar)
        
        # Botão Excluir
        btn_excluir = QPushButton("🗑️ Excluir")
        btn_excluir.setMinimumWidth(80)
        btn_excluir.clicked.connect(lambda: self.excluir_clicked.emit(pedido_id))
        botoes_layout.addWidget(btn_excluir)
        
        # Botão WhatsApp (se houver telefone)
        telefone = pedido.get('telefone_cliente', '')
        if telefone:
            btn_whatsapp = QPushButton("📱 WhatsApp")
            btn_whatsapp.setMinimumWidth(90)
            btn_whatsapp.clicked.connect(lambda: self._abrir_whatsapp(pedido))
            botoes_layout.addWidget(btn_whatsapp)
        
        botoes_layout.addStretch()
        layout.addWidget(botoes_frame)
        
        # Aplicar estilo aos botões
        self._aplicar_estilo_botoes(botoes_frame)
    
    def _aplicar_estilo_card(self, card_widget, pedido):
        """Aplica estilo moderno ao card (neutro; apenas o status é colorido)."""
        card_widget.setStyleSheet("""
            QFrame {
                background-color: #3a3a3a;
                border: 1px solid #505050;
                border-radius: 12px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: #404040;
                border-color: #6a6a6a;
            }
        """)
    
    def _aplicar_estilo_botoes(self, botoes_frame):
        """Aplica estilo aos botões do card"""
        botoes_frame.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 500;
                font-size: 11px;
            }
            
            QPushButton:hover {
                background-color: #0a5d61;
            }
            
            QPushButton:pressed {
                background-color: #084a4d;
            }
        """)
    
    def _get_status_color(self, status):
        """Retorna a cor do status"""
        colors = {
            'em produção': '#ffaa00',
            'enviado': '#00aaff',
            'entregue': '#00ff88',
            'cancelado': '#ff4444',
            'pendente': '#888888'
        }
        return colors.get(status.lower(), '#cccccc')
    
    def _get_status_border_color(self, status):
        """Retorna a cor da borda baseada no status"""
        colors = {
            'em produção': '#ffaa00',
            'enviado': '#00aaff',
            'entregue': '#00ff88',
            'cancelado': '#ff4444',
            'pendente': '#888888'
        }
        return colors.get(status.lower(), '#606060')
    
    def _lighten_color(self, color):
        """Clareia uma cor hexadecimal"""
        if color.startswith('#'):
            color = color[1:]
        
        # Converter para RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        # Clarear (adicionar 30 a cada componente, máximo 255)
        r = min(255, r + 30)
        g = min(255, g + 30)
        b = min(255, b + 30)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _calcular_dias_restantes(self, pedido):
        """Calcula os dias restantes até a entrega"""
        data_entrega = pedido.get('data_entrega')
        
        if not data_entrega:
            return None
        
        try:
            if isinstance(data_entrega, str):
                data_entrega = datetime.strptime(data_entrega, '%Y-%m-%d').date()
            elif hasattr(data_entrega, 'date'):
                data_entrega = data_entrega.date()
            
            hoje = datetime.now().date()
            diferenca = (data_entrega - hoje).days
            
            return diferenca
            
        except Exception as e:
            print(f"Erro ao calcular dias restantes: {e}")
            return None
    
    def _abrir_whatsapp(self, pedido):
        """Abre o WhatsApp com mensagem pré-formatada"""
        import webbrowser
        import urllib.parse
        
        telefone = pedido.get('telefone_cliente', '').strip()
        numero_os = pedido.get('numero_os', 'N/A')
        cliente = pedido.get('nome_cliente', 'Cliente')
        
        if not telefone:
            return
        
        # Remover caracteres não numéricos
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        
        # Adicionar código do país se necessário
        if len(telefone_limpo) == 11 and telefone_limpo.startswith('55'):
            pass  # Já tem código do país
        elif len(telefone_limpo) == 11:
            telefone_limpo = '55' + telefone_limpo
        elif len(telefone_limpo) == 10:
            telefone_limpo = '5511' + telefone_limpo
        
        # Mensagem pré-formatada
        mensagem = f"""Olá {cliente}!
        
Tudo bem? Aqui é sobre sua Ordem de Serviço #{numero_os}.

Gostaria de passar uma atualização sobre o andamento do seu pedido.

Qualquer dúvida, estou à disposição!"""
        
        # Codificar mensagem para URL
        mensagem_encoded = urllib.parse.quote(mensagem)
        
        # Criar URL do WhatsApp
        url = f"https://wa.me/{telefone_limpo}?text={mensagem_encoded}"
        
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Erro ao abrir WhatsApp: {e}")
