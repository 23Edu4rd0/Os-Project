"""
Gerenciamento de cards de pedidos em PyQt6
"""

from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QPalette, QFontMetrics, QCursor


class PedidosCard(QWidget):
    """Gerencia a criação e exibição de cards de pedidos"""
    
    # Sinais para comunicação
    visualizar_clicked = pyqtSignal(int)  # pedido_id
    editar_clicked = pyqtSignal(int)  # pedido_id
    excluir_clicked = pyqtSignal(int)  # pedido_id
    status_changed = pyqtSignal(int, str)  # pedido_id, novo_status
    pedido_atualizado = pyqtSignal()  # Para refresh da lista
    
    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        
    def criar_card(self, pedido):
        """Cria um card completo com todas as informações do pedido"""
        # Frame principal com design moderno
        card_widget = QFrame()
        card_widget.setMinimumSize(320, 280)  # Altura reduzida para layout mais compacto
        card_widget.setMaximumSize(380, 280)  # Altura máxima também reduzida
        card_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #323232, stop:1 #212121);
                border: 1px solid #505050;
                border-radius: 10px;
            }
        """)

        # Layout principal bem estruturado
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(14, 14, 14, 12)  # Margens reduzidas
        card_layout.setSpacing(8)  # Espaçamento ajustado

        # Extrair informações do pedido
        pedido_id = pedido.get('id', 'N/A')
        cliente_nome = pedido.get('nome_cliente', 'Cliente não informado')
        cliente_telefone = pedido.get('telefone_cliente', '')
        status = pedido.get('status', 'pendente')
        produtos = pedido.get('produtos', [])
        endereco = pedido.get('endereco_cliente', 'Endereço não informado')
        valor_total = pedido.get('valor_total', 0)

        # === HEADER DO CARD ===
        header_layout = QHBoxLayout()
        
        # Nome do cliente com estilo melhorado
        cliente_label = QLabel(cliente_nome)
        cliente_label.setStyleSheet("""
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            margin: 0px;
            padding: 2px 4px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        """)
        cliente_label.setWordWrap(False)
        header_layout.addWidget(cliente_label)
        
        header_layout.addStretch()
        
        # ID do pedido com estilo melhorado 
        id_label = QLabel(f"#{pedido_id}")
        id_label.setStyleSheet("""
            color: #bbbbbb;
            font-size: 14px;
            font-weight: 600;
            padding: 2px 6px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 4px;
        """)
        header_layout.addWidget(id_label)
        
        card_layout.addLayout(header_layout)

        # === INFORMAÇÕES SECUNDÁRIAS ===
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)  # Aumentado de 6 para 8
        
        # Telefone (se disponível)
        if cliente_telefone:
            telefone_label = QLabel(f"📞 {cliente_telefone}")
            telefone_label.setStyleSheet("""
                color: #b0b0b0;
                font-size: 12px;
                margin: 0px;
            """)
            info_layout.addWidget(telefone_label)
        
        # Status e prazo em uma linha
        status_prazo_layout = QHBoxLayout()
        
        # Status com cor
        status_colors = {
            'pendente': '#ffa726',
            'em andamento': '#42a5f5', 
            'em produção': '#42a5f5',
            'concluído': '#66bb6a',
            'cancelado': '#ef5350'
        }
        status_cor = status_colors.get(status.lower(), '#888888')
        
        status_label = QLabel(f"● {status.title()}")
        status_label.setStyleSheet(f"""
            color: {status_cor};
            font-size: 12px;
            font-weight: 600;
        """)
        status_prazo_layout.addWidget(status_label)
        
        status_prazo_layout.addStretch()
        
        # Dias restantes
        dias_restantes = self._calcular_dias_restantes(pedido)
        if dias_restantes is not None:
            if dias_restantes > 0:
                prazo_text = f"{dias_restantes} dias"
                prazo_cor = "#66bb6a" if dias_restantes > 7 else "#ffa726" if dias_restantes > 2 else "#ef5350"
            elif dias_restantes == 0:
                prazo_text = "Hoje"
                prazo_cor = "#ff9800"
            else:
                prazo_text = f"Atrasado {abs(dias_restantes)}d"
                prazo_cor = "#ef5350"
                
            prazo_label = QLabel(prazo_text)
            prazo_label.setStyleSheet(f"""
                color: {prazo_cor};
                font-size: 11px;
                font-weight: 500;
            """)
            status_prazo_layout.addWidget(prazo_label)
        
        info_layout.addLayout(status_prazo_layout)
        card_layout.addLayout(info_layout)

        # === SEÇÃO DE PRODUTOS ===
        produtos_container = QFrame()
        produtos_container.setFixedHeight(80)  # Altura reduzida para mostrar apenas uma linha
        produtos_container.setStyleSheet("""
            QFrame {
                background: rgba(20, 20, 20, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                padding: 6px;
            }
        """)
        produtos_layout = QHBoxLayout(produtos_container)  # Mudado para horizontal
        produtos_layout.setContentsMargins(10, 8, 10, 8)  # Margens reduzidas
        produtos_layout.setSpacing(6)  # Espaçamento menor
        
        # Título mais compacto
        produtos_titulo = QLabel("📦")
        produtos_titulo.setStyleSheet("""
            color: #f0f0f0;
            font-size: 14px;
            padding: 0 4px;
        """)
        produtos_layout.addWidget(produtos_titulo)
        
        # Lista de produtos simplificada
        if produtos and len(produtos) > 0:
            if len(produtos) >= 2:
                # Se tem 2 ou mais produtos, mostrar apenas o total
                resumo_label = QLabel(f"{len(produtos)} itens")
                resumo_label.setStyleSheet("""
                    color: #ffa726;
                    font-size: 13px;
                    font-weight: 500;
                    padding: 4px 8px;
                    background: rgba(255, 167, 38, 0.1);
                    border-radius: 4px;
                """)
                resumo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                produtos_layout.addWidget(resumo_label)
                
                # Mostrar o primeiro produto como exemplo
                produto = produtos[0]
                descricao = produto.get('descricao', produto.get('nome', 'Produto'))
                if len(descricao) > 25:
                    descricao = descricao[:22] + "..."
                
                # Criar tooltip com todos os produtos
                tooltip_text = "Produtos:\n"
                for p in produtos:
                    nome = p.get('descricao', p.get('nome', 'Produto'))
                    cor = p.get('cor', 'Não especificada')
                    tooltip_text += f"- {nome} (Cor: {cor})\n"
                
                produto_item = QLabel(f"• {descricao}")
                produto_item.setToolTip(tooltip_text)
                produto_item.setStyleSheet("""
                    QLabel {
                        color: #e8e8e8;
                        font-size: 13px;
                        padding: 4px 8px;
                        margin-left: 4px;
                        background: rgba(255, 255, 255, 0.03);
                        border-radius: 4px;
                    }
                    QLabel:hover {
                        background: rgb(0, 0, 0);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }
                    margin-left: 4px;
                    background: rgba(255, 255, 255, 0.03);
                    border-radius: 4px;
                """)
                produtos_layout.addWidget(produto_item)
                
                # Indicar se há mais itens
                if len(produtos) > 1:
                    info_label = QLabel(f"+{len(produtos) - 1}")
                    info_label.setStyleSheet("""
                        color: #aaaaaa;
                        font-size: 12px;
                        font-weight: bold;
                        padding: 2px 6px;
                        background: rgba(255, 255, 255, 0.05);
                        border-radius: 3px;
                    """)
                    info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                    produtos_layout.addWidget(info_label)
            else:
                # Se tem apenas 1 produto, mostrar de forma simples
                produto = produtos[0]
                descricao = produto.get('descricao', produto.get('nome', 'Produto'))
                if len(descricao) > 25:
                    descricao = descricao[:22] + "..."
                
                # Criar tooltip com detalhes completos
                nome_completo = produto.get('descricao', produto.get('nome', 'Produto'))
                cor = produto.get('cor', 'Não especificada')
                tooltip = f"Produto: {nome_completo}\nCor: {cor}"
                
                produto_item = QLabel(f"• {descricao}")
                produto_item.setToolTip(tooltip)
                produto_item.setStyleSheet("""
                    QLabel {
                        color: #e8e8e8;
                        font-size: 13px;
                        padding: 4px 8px;
                        margin-left: 4px;
                        background: rgba(255, 255, 255, 0.03);
                        border-radius: 4px;
                    }
                    QLabel:hover {
                        background: rgb(0, 0, 0);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                    }
                """)
                produtos_layout.addWidget(produto_item)
        else:
            sem_produtos = QLabel("Sem produtos")
            sem_produtos.setStyleSheet("""
                color: #999999;
                font-size: 13px;
                font-style: italic;
                padding: 4px 8px;
                background: rgba(255, 255, 255, 0.02);
                border-radius: 4px;
            """)
            sem_produtos.setAlignment(Qt.AlignmentFlag.AlignCenter)
            produtos_layout.addWidget(sem_produtos)
        
        card_layout.addWidget(produtos_container)
        
        # Pequeno espaçamento para melhor distribuição vertical
        card_layout.addSpacing(5)

        # === VALOR E ENDEREÇO ===
        detalhes_layout = QHBoxLayout()
        
        # Valor (lado esquerdo)
        try:
            valor_formatado = f"R$ {float(valor_total):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            valor_formatado = f"R$ {valor_total}"
            
        valor_label = QLabel(valor_formatado)
        valor_label.setStyleSheet("""
            color: #4caf50;
            font-size: 14px;
            font-weight: bold;
        """)
        detalhes_layout.addWidget(valor_label)
        
        detalhes_layout.addStretch()
        
        # Ícone de localização (lado direito)
        if endereco and endereco != "Endereço não informado":
            endereco_curto = endereco[:15] + "..." if len(endereco) > 15 else endereco
            endereco_label = QLabel(f"📍 {endereco_curto}")
            endereco_label.setStyleSheet("""
                color: #999999;
                font-size: 9px;
            """)
            endereco_label.setToolTip(endereco)  # Tooltip com endereço completo
            detalhes_layout.addWidget(endereco_label)
        
        card_layout.addLayout(detalhes_layout)
        
        # Espaço flexível
        card_layout.addStretch()

        # === BOTÕES DE AÇÃO ===
        self._criar_botoes_modernos(card_layout, pedido)

        return card_widget
    

    
    # (Remove this entire duplicate block; keep only the most complete version of _calcular_dias_restantes)
    

    
    def _abrir_menu_status(self, pedido_id):
        """Abre menu para alterar status do pedido"""
        # Cria um menu de contexto com opções de status e emite o sinal
        try:
            menu = QMenu()

            # Status disponíveis (texto interno em minúsculas)
            status_list = ["pendente", "em andamento", "concluído", "cancelado"]

            for status in status_list:
                # Exibir título amigável
                action = menu.addAction(status.title())

                # Ao acionar, emitir sinal com pedido_id e o status selecionado
                # usamos uma closure para capturar o valor correto de `status`
                action.triggered.connect(lambda checked, s=status: self.status_changed.emit(pedido_id, s))

            # Mostrar o menu na posição do cursor
            menu.exec(QCursor.pos())

        except Exception as e:
            print(f"Erro ao abrir menu de status: {e}")
    
    def _gerar_codigo_produto(self, descricao, index):
        """Gera um código de produto realista baseado na descrição"""
        # Usar hash da descrição para gerar código consistente
        base = hash(descricao) % 100000000  # 8 dígitos máximo
        if base < 0:
            base = -base
            
        # Garantir que começa com 18 (como no exemplo)
        codigo = 18000000 + (base % 999999)
        return f"{codigo:08d}"
    

            
    # Métodos auxiliares necessários para funcionalidade básica
    
    def _criar_secao_valores(self, layout, dados):
        """Cria a seção de valores"""
        valor_total = float(dados.get('valor_total', 0))
        
        valor_container = QWidget()
        valor_layout = QHBoxLayout(valor_container)
        valor_layout.setContentsMargins(0, 0, 0, 0)
        
        valor_label = QLabel("Valor Total:")
        valor_label.setStyleSheet("font-weight: 600; color: #b0b0b0; font-size: 14px;")
        
        valor_valor = QLabel(f"R$ {valor_total:.2f}")
        valor_valor.setStyleSheet("font-weight: 700; color: #4CAF50; font-size: 16px;")
        
        valor_layout.addWidget(valor_label)
        valor_layout.addWidget(valor_valor)
        valor_layout.addStretch()
        
        layout.addWidget(valor_container)
    
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
    
    def _criar_botoes_modernos(self, layout, pedido):
        """Cria botões de ação modernos e compactos"""
        botoes_container = QFrame()
        botoes_container.setStyleSheet("background: transparent; border: none;")
        botoes_layout = QHBoxLayout(botoes_container)
        botoes_layout.setContentsMargins(0, 8, 0, 0)
        botoes_layout.setSpacing(6)  # Espaçamento reduzido entre botões
        
        pedido_id = pedido.get('id')
        telefone = pedido.get('telefone_cliente', '')
        
        # Botões com design melhorado e mais compactos
        btn_base = """
            QPushButton {
                border: none;
                border-radius: 5px;
                padding: 6px 5px;
                font-size: 11px;
                font-weight: 600;
                min-width: 70px;
                height: 30px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                padding-top: 7px;
                padding-bottom: 5px;
            }
        """
        
        # Visualizar (azul - destaque primário)
        btn_visualizar = QPushButton("Visualizar")
        btn_visualizar.setStyleSheet(btn_base + """
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3281e8, stop:1 #1565c0);
                color: white; 
                border-bottom: 2px solid #104d92;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a8af0, stop:1 #1976d2);
            }
        """)
        btn_visualizar.clicked.connect(lambda: self.visualizar_clicked.emit(pedido_id))
        botoes_layout.addWidget(btn_visualizar)
        
        # Status (cinza - normal)
        btn_status = QPushButton("Status")
        btn_status.setStyleSheet(btn_base + """
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a5a5a, stop:1 #454545); 
                color: white;
                border-bottom: 2px solid #353535;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #656565, stop:1 #505050); 
            }
        """)
        btn_status.clicked.connect(lambda: self._abrir_menu_status(pedido_id))
        botoes_layout.addWidget(btn_status)
        
        # WhatsApp (verde)
        btn_whatsapp = QPushButton("WhatsApp")
        if telefone:
            btn_whatsapp.setStyleSheet(btn_base + """
                QPushButton { 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2eda71, stop:1 #25c15d);
                    color: white; 
                    border-bottom: 2px solid #1ea351;
                }
                QPushButton:hover { 
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #33e077, stop:1 #27cc60);
                }
            """)
            btn_whatsapp.clicked.connect(lambda: self._abrir_whatsapp_com_feedback(btn_whatsapp, pedido))
        else:
            btn_whatsapp.setStyleSheet(btn_base + """
                QPushButton { 
                    background: #666666; 
                    color: #aaaaaa;
                    border-bottom: 2px solid #555555;
                }
            """)
            btn_whatsapp.setEnabled(False)
            btn_whatsapp.setToolTip("Telefone não informado")
        botoes_layout.addWidget(btn_whatsapp)
        
        # Deletar (vermelho)
        btn_deletar = QPushButton("Deletar")
        btn_deletar.setStyleSheet(btn_base + """
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e53935, stop:1 #c62828);
                color: white; 
                border-bottom: 2px solid #b71c1c;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f44336, stop:1 #d32f2f);
            }
        """)
        btn_deletar.clicked.connect(lambda: self.excluir_clicked.emit(pedido_id))
        botoes_layout.addWidget(btn_deletar)
        
        layout.addWidget(botoes_container)
    


    # --- Prazo / Entrega helpers -------------------------------------------------
    def _formatar_prazo_texto(self, pedido):
        """Retorna (texto, cor) para o rótulo de prazo.
        Usa data_entrega se presente; caso contrário, calcula com data_criacao + prazo(dias).
        """
        try:
            due_date = self._obter_data_entrega(pedido)
            if not due_date:
                return ("Entrega: data não informada", "#ffb74d")

            hoje = datetime.now().date()
            diff = (due_date - hoje).days
            data_fmt = due_date.strftime("%d/%m/%Y")

            if diff > 1:
                return (f"Entrega: faltam {diff} dias ({data_fmt})", "#cccccc")
            if diff == 1:
                return (f"Entrega: amanhã ({data_fmt})", "#ffd166")
            if diff == 0:
                return (f"Entrega: hoje ({data_fmt})", "#ffd166")
            return (f"Entrega: atrasado há {abs(diff)} dias ({data_fmt})", "#ff6b6b")
        except Exception:
            return ("Entrega: data inválida", "#ffb74d")

    def _obter_data_entrega(self, pedido):
        """Determina a data de entrega acordada.
        Preferência: pedido['data_entrega'] -> date; senão data_criacao + prazo(dias).
        """
        data_entrega = pedido.get('data_entrega')
        if data_entrega:
            try:
                if isinstance(data_entrega, str):
                    # tentar formatos comuns
                    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S'):
                        try:
                            return datetime.strptime(data_entrega, fmt).date()
                        except Exception:
                            pass
                    # ISO genérico
                    return datetime.fromisoformat(data_entrega[:19]).date()
                if hasattr(data_entrega, 'date'):
                    return data_entrega.date()
                return data_entrega  # presume date
            except Exception:
                pass

        # Sem data_entrega explícita: usar data_criacao + prazo
        data_criacao = pedido.get('data_criacao')
        prazo = int(pedido.get('prazo') or 0)
        if not data_criacao or prazo <= 0:
            return None
        try:
            if isinstance(data_criacao, str):
                # aceitar "YYYY-MM-DD HH:MM:SS" ou só data
                base = datetime.fromisoformat(data_criacao[:19]) if len(data_criacao) >= 10 else datetime.strptime(data_criacao, '%Y-%m-%d')
            elif hasattr(data_criacao, 'date'):
                base = data_criacao
            else:
                base = datetime.now()
            return (base + timedelta(days=prazo)).date()
        except Exception:
            try:
                return (datetime.strptime(str(data_criacao), '%Y-%m-%d') + timedelta(days=prazo)).date()
            except Exception:
                return None

    # --- Status menu -------------------------------------------------------------
    def _abrir_menu_status(self, pedido_id: int):
        menu = QMenu(self)
        # Opções de status - carregar do storage centralizado para consistência
        try:
            from app.utils.statuses import load_statuses
            opcoes = load_statuses()
        except Exception:
            opcoes = ['em produção', 'em andamento', 'enviado', 'concluído', 'cancelado']
        # Rótulos bonitos
        labels = {
            'em produção': 'Em produção',
            'em andamento': 'Em andamento',
            'enviado': 'Enviado',
            'concluído': 'Concluído',
            'cancelado': 'Cancelado',
        }
        _ = [menu.addAction(labels.get(op, op.title())) for op in opcoes]

        # Abrir o menu ACIMA do botão que disparou o clique (quando possível)
        pos_global = self.mapToGlobal(self.rect().bottomLeft())
        try:
            sender = self.sender()
            if isinstance(sender, QPushButton):
                top_left = sender.mapToGlobal(sender.rect().topLeft())
                # calcular altura aproximada do menu e posicionar acima
                h = menu.sizeHint().height()
                pos_global = QPoint(top_left.x(), top_left.y() - h)
        except Exception:
            pass

        act = menu.exec(pos_global)
        if act:
            novo_status = act.text().lower()
            # Atualiza rótulo local
            cor = self._get_status_color(novo_status)
            try:
                self._status_label.setText(f"Status: {novo_status.upper()}")
                self._status_label.setStyleSheet(f"color: {cor}; background: transparent;")
            except Exception:
                pass
            # Emite sinal para persistência
            try:
                self.status_changed.emit(int(pedido_id), novo_status)
            except Exception:
                # se id não for int, tente emitir como está
                self.status_changed.emit(pedido_id, novo_status)
    
    def _aplicar_estilo_card(self, card_widget, pedido):
        """Aplica estilo muito simples ao card"""
        status = pedido.get('status', 'pendente').lower()
        
        # Cor da borda muito simples baseada no status
        if status == 'entregue':
            border_color = '#4CAF50'
        elif status == 'em andamento':
            border_color = '#2196F3'
        elif status == 'cancelado':
            border_color = '#F44336'
        else:
            border_color = '#FFC107'
        
        card_widget.setStyleSheet(f"""
            QFrame {{
                background-color: #333333;
                border: 1px solid {border_color};
                border-radius: 4px;
                margin: 2px;
                padding: 8px;
            }}
        """)

    def _aplicar_estilo_basico(self, card_widget, status):
        """Aplica estilo básico ao card_widget baseado no status (compatibilidade com chamadas existentes).

        Mantém aparência coerente com _aplicar_estilo_card e usa cores helper.
        """
        try:
            status = (status or 'pendente').lower()
            border = self._get_status_border_color(status)
            bg = '#2f2f2f' if status != 'entregue' else '#263822'
            light_bg = self._lighten_color(border)

            # Aplicar estilo simples ao QFrame
            card_widget.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg};
                    border: 1px solid {border};
                    border-radius: 4px;
                    margin: 2px;
                    padding: 8px;
                }}
            """)

            # Se o widget tiver um _status_label, atualize sua cor
            try:
                if hasattr(self, '_status_label'):
                    cor = self._get_status_color(status)
                    self._status_label.setStyleSheet(f"color: {cor}; background: transparent;")
            except Exception:
                pass
        except Exception as e:
            # Nunca levante exceção de estilização — apenas logue
            print(f"Erro ao aplicar estilo básico: {e}")
    
    def _aplicar_estilo_botoes(self, botoes_frame):
        """Aplica estilo muito simples aos botões do card"""
        botoes_frame.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: 1px solid #666666;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 10px;
                min-width: 70px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
    
    def _get_status_color(self, status):
        """Retorna a cor do status"""
        colors = {
            'em produção': '#ffaa00',
            'em andamento': '#ffaa00',
            'enviado': '#00aaff',
            'entregue': '#00ff88',
            'concluído': '#00ff88',
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
        """Calcula os dias restantes até a entrega.
        Usa data_entrega se existir; caso contrário, data_criacao + prazo.
        """
        try:
            due = self._obter_data_entrega(pedido)
            if not due:
                return None
            hoje = datetime.now().date()
            return (due - hoje).days
        except Exception as e:
            print(f"Erro ao calcular dias restantes: {e}")
            return None
    
    def _mostrar_menu_whatsapp(self, btn_whatsapp, pedido):
        """Mostra menu com opções de WhatsApp: mensagem ou PDF"""
        try:
            from PyQt6.QtWidgets import QMenu, QMessageBox
            from PyQt6.QtGui import QAction
            
            telefone = pedido.get('telefone_cliente', '').strip()
            
            if not telefone:
                QMessageBox.warning(self, "WhatsApp", "Telefone não informado para este cliente.")
                return
            
            # Criar menu de contexto
            menu = QMenu(self)
            menu.setStyleSheet("""
                QMenu {
                    background-color: #3a3a3a;
                    border: 1px solid #555555;
                    border-radius: 6px;
                    color: #e6e6e6;
                    font-size: 12px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 8px 16px;
                    margin: 2px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #25d366;
                    color: white;
                }
            """)
            
            # Ação: Enviar mensagem normal
            acao_mensagem = QAction("📱 Enviar mensagem", self)
            acao_mensagem.setToolTip("Enviar mensagem de texto com informações da OS")
            acao_mensagem.triggered.connect(lambda: self._abrir_whatsapp_com_feedback(btn_whatsapp, pedido))
            menu.addAction(acao_mensagem)
            
            # Separador
            menu.addSeparator()
            
            # Ação: Enviar PDF via App
            acao_pdf_app = QAction("📄 PDF via App", self)
            acao_pdf_app.setToolTip("Gerar PDF e abrir WhatsApp App (mobile)")
            acao_pdf_app.triggered.connect(lambda: self._enviar_pdf_whatsapp_app(btn_whatsapp, pedido))
            menu.addAction(acao_pdf_app)
            
            # Ação: Enviar PDF via Web  
            acao_pdf_web = QAction("🌐 PDF via Web", self)
            acao_pdf_web.setToolTip("Gerar PDF e abrir WhatsApp Web (arrastar arquivo)")
            acao_pdf_web.triggered.connect(lambda: self._enviar_pdf_whatsapp_web(btn_whatsapp, pedido))
            menu.addAction(acao_pdf_web)
            
            # Mostrar menu próximo ao botão
            menu.exec(btn_whatsapp.mapToGlobal(btn_whatsapp.rect().bottomLeft()))
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao abrir menu WhatsApp: {str(e)}")
            print(f"Erro no menu WhatsApp: {e}")
    
    def _enviar_pdf_whatsapp_web(self, btn_whatsapp, pedido):
        """Gera PDF da OS e envia via WhatsApp"""
        try:
            import webbrowser
            import urllib.parse
            import os
            from PyQt6.QtCore import QTimer
            from PyQt6.QtWidgets import QMessageBox
            from documents.os_pdf import OrdemServicoPDF
            
            telefone = pedido.get('telefone_cliente', '').strip()
            numero_os = pedido.get('numero_os', pedido.get('id', 'N/A'))
            cliente = pedido.get('nome_cliente', 'Cliente')
            
            if not telefone:
                QMessageBox.warning(self, "WhatsApp", "Telefone não informado para este cliente.")
                return
            
            # Feedback visual: gerando PDF
            texto_original = btn_whatsapp.text()
            btn_whatsapp.setText("Gerando PDF...")
            btn_whatsapp.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: 1px solid #F57C00;
                    border-radius: 4px;
                    padding: 5px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    min-width: 70px;
                    max-height: 28px;
                }
            """)
            btn_whatsapp.setEnabled(False)
            
            # Gerar PDF
            pdf_generator = OrdemServicoPDF(pedido)
            caminho_pdf = pdf_generator.gerar()
            
            if not os.path.exists(caminho_pdf):
                raise Exception("Erro ao gerar PDF")
            
            # Preparar WhatsApp
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            if len(telefone_limpo) < 10:
                QMessageBox.warning(self, "WhatsApp", "Telefone inválido.")
                return
            
            # Adicionar código do país se necessário
            if len(telefone_limpo) == 11 and telefone_limpo.startswith('55'):
                pass  # Já tem código do país
            elif len(telefone_limpo) == 11:
                telefone_limpo = '55' + telefone_limpo
            elif len(telefone_limpo) == 10:
                telefone_limpo = '5511' + telefone_limpo
            
            # Mensagem para acompanhar o PDF
            mensagem = f"""Olá {cliente}!

Segue em anexo o PDF da sua Ordem de Serviço #{numero_os}.

📋 Documento contém todos os detalhes do seu pedido.
📞 Qualquer dúvida, estou à disposição!

*Arquivo: {os.path.basename(caminho_pdf)}*"""
            
            # Codificar mensagem
            mensagem_encoded = urllib.parse.quote(mensagem)
            
            # URL do WhatsApp Web (sem mensagem pré-definida para facilitar anexo)
            url_web = f"https://web.whatsapp.com/send?phone={telefone_limpo}"
            
            # Feedback: PDF pronto
            btn_whatsapp.setText("Abrindo Web...")
            btn_whatsapp.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: 1px solid #1976D2;
                    border-radius: 4px;
                    padding: 5px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    min-width: 70px;
                    max-height: 28px;
                }
            """)
            
            # Abrir WhatsApp Web
            webbrowser.open(url_web)
            
            # Abrir pasta do PDF para facilitar o drag & drop
            import subprocess
            import platform
            pasta_pdf = os.path.dirname(caminho_pdf)
            
            try:
                if platform.system() == "Linux":
                    subprocess.run(["xdg-open", pasta_pdf])
                elif platform.system() == "Windows":
                    subprocess.run(["explorer", pasta_pdf])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", pasta_pdf])
            except Exception as e:
                print(f"Não foi possível abrir pasta: {e}")
            
            # Mostrar instruções detalhadas
            instrucoes = f"""✅ WhatsApp Web aberto para {cliente}!

�️ Pasta do PDF aberta: {os.path.basename(pasta_pdf)}
📄 Arquivo: {os.path.basename(caminho_pdf)}

📋 COMO ENVIAR O PDF:
1️⃣ No WhatsApp Web, localize a conversa com {cliente}
2️⃣ Clique no ícone � (anexar arquivo) na conversa
3️⃣ Selecione "Documento" ou arraste o PDF da pasta
4️⃣ Adicione uma mensagem se desejar
5️⃣ Clique em Enviar ✅

💡 DICA: Você pode arrastar o arquivo direto da pasta para a conversa!"""
            
            QMessageBox.information(self, "📱 WhatsApp Web + PDF", instrucoes)
            
            # Após 3 segundos, volta ao normal
            QTimer.singleShot(3000, lambda: self._restaurar_botao_whatsapp(btn_whatsapp, texto_original))
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao enviar PDF: {str(e)}")
            print(f"Erro ao enviar PDF via WhatsApp Web: {e}")
            # Restaurar botão em caso de erro
            self._restaurar_botao_whatsapp(btn_whatsapp, "WhatsApp")

    def _enviar_pdf_whatsapp_app(self, btn_whatsapp, pedido):
        """Gera PDF da OS e abre WhatsApp App com mensagem sobre o PDF"""
        try:
            import webbrowser
            import urllib.parse
            import os
            from PyQt6.QtCore import QTimer
            from PyQt6.QtWidgets import QMessageBox
            from documents.os_pdf import OrdemServicoPDF
            
            telefone = pedido.get('telefone_cliente', '').strip()
            numero_os = pedido.get('numero_os', pedido.get('id', 'N/A'))
            cliente = pedido.get('nome_cliente', 'Cliente')
            
            if not telefone:
                QMessageBox.warning(self, "WhatsApp", "Telefone não informado para este cliente.")
                return
            
            # Feedback visual: gerando PDF
            texto_original = btn_whatsapp.text()
            btn_whatsapp.setText("Gerando PDF...")
            btn_whatsapp.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: 1px solid #F57C00;
                    border-radius: 4px;
                    padding: 5px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    min-width: 70px;
                    max-height: 28px;
                }
            """)
            btn_whatsapp.setEnabled(False)
            
            # Gerar PDF
            pdf_generator = OrdemServicoPDF(pedido)
            caminho_pdf = pdf_generator.gerar()
            
            if not os.path.exists(caminho_pdf):
                raise Exception("Erro ao gerar PDF")
            
            # Preparar WhatsApp
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            if len(telefone_limpo) < 10:
                QMessageBox.warning(self, "WhatsApp", "Telefone inválido.")
                return
            
            # Adicionar código do país se necessário
            if len(telefone_limpo) == 11 and telefone_limpo.startswith('55'):
                pass  # Já tem código do país
            elif len(telefone_limpo) == 11:
                telefone_limpo = '55' + telefone_limpo
            elif len(telefone_limpo) == 10:
                telefone_limpo = '5511' + telefone_limpo
            
            # Mensagem informando sobre o PDF (app não pode anexar automaticamente)
            mensagem = f"""Olá {cliente}!

📋 Sua Ordem de Serviço #{numero_os} está pronta!

📄 Geramos o PDF com todos os detalhes do seu pedido.
🗂️ Arquivo: {os.path.basename(caminho_pdf)}

Em breve enviaremos o documento completo.

📞 Qualquer dúvida, estou à disposição!"""
            
            # Codificar mensagem
            mensagem_encoded = urllib.parse.quote(mensagem)
            
            # URL do WhatsApp App
            url_app = f"https://wa.me/{telefone_limpo}?text={mensagem_encoded}"
            
            # Feedback: PDF pronto
            btn_whatsapp.setText("App Aberto!")
            btn_whatsapp.setStyleSheet("""
                QPushButton {
                    background-color: #25d366;
                    color: white;
                    border: 1px solid #1da851;
                    border-radius: 4px;
                    padding: 5px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    min-width: 70px;
                    max-height: 28px;
                }
            """)
            
            # Abrir WhatsApp App
            webbrowser.open(url_app)
            
            # Mostrar informações
            QMessageBox.information(self, "📱 WhatsApp App", 
                f"WhatsApp App aberto para {cliente}!\n\n"
                f"📄 PDF gerado: {os.path.basename(caminho_pdf)}\n"
                f"📁 Local: {os.path.dirname(caminho_pdf)}\n\n"
                f"💡 O PDF foi salvo localmente.\n"
                f"Envie manualmente ou use a opção 'PDF via Web'.")
            
            # Após 3 segundos, volta ao normal
            QTimer.singleShot(3000, lambda: self._restaurar_botao_whatsapp(btn_whatsapp, texto_original))
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao enviar PDF via App: {str(e)}")
            print(f"Erro ao enviar PDF via WhatsApp App: {e}")
            # Restaurar botão em caso de erro
            self._restaurar_botao_whatsapp(btn_whatsapp, "WhatsApp")

    def _abrir_whatsapp_com_feedback(self, btn_whatsapp, pedido):
        """Abre o WhatsApp com mensagem pré-formatada e feedback visual no botão"""
        try:
            import webbrowser
            import urllib.parse
            from PyQt6.QtCore import QTimer
            from PyQt6.QtWidgets import QMessageBox
            
            telefone = pedido.get('telefone_cliente', '').strip()
            numero_os = pedido.get('numero_os', pedido.get('id', 'N/A'))
            cliente = pedido.get('nome_cliente', 'Cliente')
            
            if not telefone:
                QMessageBox.warning(self, "WhatsApp", "Telefone não informado para este cliente.")
                return
            
            # Remover caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            if len(telefone_limpo) < 10:
                QMessageBox.warning(self, "WhatsApp", "Telefone inválido.")
                return
            
            # Adicionar código do país se necessário
            if len(telefone_limpo) == 11 and telefone_limpo.startswith('55'):
                pass  # Já tem código do país
            elif len(telefone_limpo) == 11:
                telefone_limpo = '55' + telefone_limpo
            elif len(telefone_limpo) == 10:
                telefone_limpo = '5511' + telefone_limpo
            
            # Feedback visual: mudança no botão
            texto_original = btn_whatsapp.text()
            btn_whatsapp.setText("Abrindo...")
            btn_whatsapp.setStyleSheet("""
                QPushButton {
                    background-color: #1da851;
                    color: white;
                    border: 1px solid #128c39;
                    border-radius: 4px;
                    padding: 5px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    min-width: 70px;
                    max-height: 28px;
                }
            """)
            btn_whatsapp.setEnabled(False)
            
            # Mensagem pré-formatada
            mensagem = f"""Olá {cliente}!

Tudo bem? Aqui é sobre sua Ordem de Serviço #{numero_os}.

Gostaria de passar uma atualização sobre o andamento do seu pedido.

Qualquer dúvida, estou à disposição!"""
            
            # Codificar mensagem para URL
            mensagem_encoded = urllib.parse.quote(mensagem)
            
            # Criar URL do WhatsApp
            url = f"https://wa.me/{telefone_limpo}?text={mensagem_encoded}"
            
            # Abrir WhatsApp
            webbrowser.open(url)
            
            # Após 2 segundos, mostra sucesso e restaura botão
            def restaurar_botao():
                btn_whatsapp.setText("✓ Enviado")
                btn_whatsapp.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 1px solid #45a049;
                        border-radius: 4px;
                        padding: 5px 8px;
                        font-size: 10px;
                        font-weight: bold;
                        min-width: 70px;
                        max-height: 28px;
                    }
                """)
                
                # Após mais 3 segundos, volta ao estado original
                QTimer.singleShot(3000, lambda: self._restaurar_botao_whatsapp(btn_whatsapp, texto_original))
            
            QTimer.singleShot(2000, restaurar_botao)
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao abrir WhatsApp: {str(e)}")
            print(f"Erro ao abrir WhatsApp: {e}")
            # Restaurar botão em caso de erro
            self._restaurar_botao_whatsapp(btn_whatsapp, "WhatsApp")

    def _restaurar_botao_whatsapp(self, btn_whatsapp, texto_original):
        """Restaura o estado original do botão WhatsApp"""
        btn_whatsapp.setText(texto_original)
        btn_whatsapp.setStyleSheet("""
            QPushButton {
                background-color: #25d366;
                color: white;
                border: 1px solid #1da851;
                border-radius: 4px;
                padding: 5px 8px;
                font-size: 10px;
                font-weight: bold;
                min-width: 70px;
                max-height: 28px;
            }
            QPushButton:hover {
                background-color: #1da851;
                border: 1px solid #128c39;
            }
            QPushButton:pressed {
                background-color: #0e7a2b;
            }
        """)
        btn_whatsapp.setEnabled(True)
    
    def _abrir_whatsapp(self, pedido):
        """Abre o WhatsApp com mensagem pré-formatada e feedback visual"""
        try:
            import webbrowser
            import urllib.parse
            from PyQt6.QtWidgets import QMessageBox
            
            telefone = pedido.get('telefone_cliente', '').strip()
            numero_os = pedido.get('numero_os', pedido.get('id', 'N/A'))
            cliente = pedido.get('nome_cliente', 'Cliente')
            
            if not telefone:
                QMessageBox.warning(self, "WhatsApp", "Telefone não informado para este cliente.")
                return
            
            # Remover caracteres não numéricos
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            if len(telefone_limpo) < 10:
                QMessageBox.warning(self, "WhatsApp", "Telefone inválido.")
                return
            
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
            
            # Abrir WhatsApp
            webbrowser.open(url)
            
            # Feedback visual de sucesso
            QMessageBox.information(self, "WhatsApp", f"WhatsApp aberto para {cliente}!\nTelefone: {telefone}")
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao abrir WhatsApp: {str(e)}")
            print(f"Erro ao abrir WhatsApp: {e}")
