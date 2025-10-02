from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMenu, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QTimer, QEvent
from PyQt6.QtGui import QFont, QPalette, QFontMetrics, QCursor, QPainter, QColor


class CustomTooltip(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        self.setStyleSheet("""
            QLabel {
                background-color: rgb(0, 0, 0);
                color: #ffffff;
                border: 2px solid #555555;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
        """)
        
        self.setWordWrap(True)
        self.setMargin(5)
        
    def show_at(self, pos):
        self.move(pos)
        self.show()
        self.raise_()


class PedidosCard(QWidget):
    visualizar_clicked = pyqtSignal(int)
    editar_clicked = pyqtSignal(int)
    excluir_clicked = pyqtSignal(int)
    status_changed = pyqtSignal(int, str)
    pedido_atualizado = pyqtSignal()
    
    PRODUTO_STYLE = """
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
    """
    
    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        self.custom_tooltip = None
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self.hide_tooltip)
    
    def show_custom_tooltip(self, text, widget):
        self.hide_tooltip()
        self.custom_tooltip = CustomTooltip(text)
        cursor_pos = QCursor.pos()
        tooltip_pos = QPoint(cursor_pos.x() + 10, cursor_pos.y() + 10)
        self.custom_tooltip.show_at(tooltip_pos)
        self.tooltip_timer.start(5000)
    
    def hide_tooltip(self):
        if self.custom_tooltip:
            self.custom_tooltip.hide()
            self.custom_tooltip = None
    
    def _setup_tooltip(self, widget, text):
        widget.enterEvent = lambda event: self.show_custom_tooltip(text, widget)
        widget.leaveEvent = lambda event: self.hide_tooltip()
    
    def _create_styled_label(self, text, style):
        label = QLabel(text)
        label.setStyleSheet(style)
        return label
        
    def criar_card(self, pedido):
        card_widget = QFrame()
        card_widget.setMinimumSize(410, 380)  # Card ajustado para 3 por linha
        card_widget.setMaximumSize(440, 380)
        card_widget.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d3748, stop:1 #1a202c);
                border: 2px solid #4a5568;
                border-radius: 12px;
            }
            QFrame:hover {
                border: 2px solid #667eea;
            }
        """)
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)
        
        # Extrair dados
        pedido_id = pedido.get('id', 'N/A')
        cliente_nome = pedido.get('nome_cliente', 'Cliente não informado')
        cliente_telefone = pedido.get('telefone_cliente', '')
        cpf_cliente = pedido.get('cpf_cliente', '')
        status = pedido.get('status', 'pendente')
        produtos = pedido.get('produtos', [])
        endereco = pedido.get('endereco_cliente', 'Endereço não informado')
        valor_total = pedido.get('valor_total', 0)
        valor_entrada = pedido.get('valor_entrada', 0)
        forma_pagamento = pedido.get('forma_pagamento', 'Não informado')
        data_criacao = pedido.get('data_criacao', '')
        prazo = pedido.get('prazo', 0)


        # === HEADER MODERNIZADO ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # Status Badge (esquerda)
        status_colors = {
            'pendente': ('#fbbf24', '#78350f'),
            'em andamento': ('#60a5fa', '#1e3a8a'),
            'em produção': ('#60a5fa', '#1e3a8a'),
            'concluído': ('#34d399', '#064e3b'),
            'cancelado': ('#f87171', '#7f1d1d')
        }
        bg_color, text_color = status_colors.get(status.lower(), ('#9ca3af', '#1f2937'))
        
        status_badge = QLabel(f"●  {status.upper()}")
        status_badge.setStyleSheet(f"""
            background: {bg_color};
            color: {text_color};
            font-size: 11px;
            font-weight: 800;
            padding: 8px 16px;
            border-radius: 8px;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(status_badge)
        
        header_layout.addStretch()
        
        # ID e Data (direita)
        info_right = QVBoxLayout()
        info_right.setSpacing(2)
        
        id_label = QLabel(f"OS #{pedido_id}")
        id_label.setStyleSheet("""
            color: #e2e8f0;
            font-size: 15px;
            font-weight: 700;
        """)
        id_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        info_right.addWidget(id_label)
        
        if data_criacao:
            try:
                from datetime import datetime
                data_obj = datetime.strptime(data_criacao, '%Y-%m-%d')
                data_formatada = data_obj.strftime('%d/%m/%Y')
            except:
                data_formatada = data_criacao
            
            data_label = QLabel(data_formatada)
            data_label.setStyleSheet("""
                color: #94a3b8;
                font-size: 11px;
            """)
            data_label.setAlignment(Qt.AlignmentFlag.AlignRight)
            info_right.addWidget(data_label)
        
        header_layout.addLayout(info_right)
        card_layout.addLayout(header_layout)
        
        # Linha separadora
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setStyleSheet("background: #4a5568; max-height: 1px;")
        card_layout.addWidget(separator1)


        # === INFORMAÇÕES DO CLIENTE ===
        cliente_section = QFrame()
        cliente_section.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)
        cliente_layout = QVBoxLayout(cliente_section)
        cliente_layout.setContentsMargins(10, 8, 10, 8)
        cliente_layout.setSpacing(6)
        
        # Nome do cliente
        nome_layout = QHBoxLayout()
        nome_icon = QLabel("👤")
        nome_icon.setStyleSheet("font-size: 16px;")
        nome_layout.addWidget(nome_icon)
        
        nome_label = QLabel(cliente_nome)
        nome_label.setStyleSheet("""
            color: #f1f5f9;
            font-size: 16px;
            font-weight: 700;
            min-height: 20px;
        """)
        nome_label.setWordWrap(False)
        if len(cliente_nome) > 40:
            nome_label.setText(cliente_nome[:40] + "...")
            nome_label.setToolTip(cliente_nome)
        nome_layout.addWidget(nome_label)
        nome_layout.addStretch()
        cliente_layout.addLayout(nome_layout)
        
        # Endereço em uma linha
        endereco_layout = QHBoxLayout()
        endereco_icon = QLabel("📍")
        endereco_icon.setStyleSheet("font-size: 14px;")
        endereco_layout.addWidget(endereco_icon)
        
        # Tenta formatar endereço compacto
        endereco_parts = []
        try:
            rua = pedido.get('rua_cliente', '')
            numero = pedido.get('numero_cliente', '')
            bairro = pedido.get('bairro_cliente', '')
            cidade = pedido.get('cidade_cliente', '')
            estado = pedido.get('estado_cliente', '')
            
            if rua:
                if numero:
                    endereco_parts.append(f"{rua}, {numero}")
                else:
                    endereco_parts.append(rua)
            if bairro:
                endereco_parts.append(bairro)
            if cidade:
                if estado:
                    endereco_parts.append(f"{cidade}/{estado}")
                else:
                    endereco_parts.append(cidade)
        except:
            pass
        
        endereco_compacto = " - ".join(endereco_parts) if endereco_parts else endereco
        if len(endereco_compacto) > 50:
            endereco_compacto = endereco_compacto[:50] + "..."
        
        endereco_label = QLabel(endereco_compacto)
        endereco_label.setStyleSheet("""
            color: #cbd5e1;
            font-size: 11px;
        """)
        endereco_label.setWordWrap(False)
        endereco_label.setToolTip(endereco if endereco else endereco_compacto)
        endereco_layout.addWidget(endereco_label)
        endereco_layout.addStretch()
        cliente_layout.addLayout(endereco_layout)
        
        card_layout.addWidget(cliente_section)


        # === SEÇÃO DE PRODUTOS MODERNIZADA ===
        produtos_container = QFrame()
        produtos_container.setStyleSheet("""
            QFrame {
                background: rgba(99, 102, 241, 0.12);
                border: 1px solid rgba(99, 102, 241, 0.4);
                border-radius: 8px;
            }
        """)
        produtos_main_layout = QVBoxLayout(produtos_container)
        produtos_main_layout.setContentsMargins(10, 10, 10, 10)
        produtos_main_layout.setSpacing(8)
        
        # Header de produtos com contador
        produtos_header = QHBoxLayout()
        produtos_titulo = QLabel("📦 PRODUTOS")
        produtos_titulo.setStyleSheet("""
            color: #a5b4fc;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.5px;
        """)
        produtos_header.addWidget(produtos_titulo)
        
        if produtos and len(produtos) > 0:
            contador = QLabel(f"{len(produtos)}")
            contador.setStyleSheet("""
                background: #6366f1;
                color: white;
                font-size: 11px;
                font-weight: 700;
                padding: 3px 10px;
                border-radius: 12px;
            """)
            produtos_header.addWidget(contador)
        
        produtos_header.addStretch()
        
        # Prazo de entrega no header
        dias_restantes = self._calcular_dias_restantes(pedido)
        if dias_restantes is not None:
            if dias_restantes > 0:
                prazo_text = f"⏱️ {dias_restantes}d"
                prazo_cor = "#34d399" if dias_restantes > 7 else "#fbbf24" if dias_restantes > 2 else "#f87171"
            elif dias_restantes == 0:
                prazo_text = "⏱️ HOJE"
                prazo_cor = "#fb923c"
            else:
                prazo_text = f"⏱️ -{abs(dias_restantes)}d"
                prazo_cor = "#ef4444"
            
            prazo_badge = QLabel(prazo_text)
            prazo_badge.setStyleSheet(f"""
                background: rgba(255, 255, 255, 0.1);
                color: {prazo_cor};
                font-size: 11px;
                font-weight: 700;
                padding: 3px 10px;
                border-radius: 12px;
            """)
            produtos_header.addWidget(prazo_badge)
        
        produtos_main_layout.addLayout(produtos_header)
        
        # Lista de produtos
        produtos_layout = QVBoxLayout()
        produtos_layout.setSpacing(6)
        
        # Lista de produtos (máximo 2 visíveis)
        if produtos and len(produtos) > 0:
            produtos_exibir = produtos[:2]  # Mostrar no máximo 2
            
            for produto in produtos_exibir:
                produto_item_layout = QHBoxLayout()
                
                descricao = produto.get('descricao', produto.get('nome', 'Produto'))
                quantidade = produto.get('quantidade', 1)
                
                # Bullet point
                bullet = QLabel("•")
                bullet.setStyleSheet("color: #818cf8; font-size: 14px; font-weight: bold;")
                produto_item_layout.addWidget(bullet)
                
                # Nome do produto
                if quantidade > 1:
                    texto_produto = f"{quantidade}x {descricao}"
                else:
                    texto_produto = descricao
                
                if len(texto_produto) > 28:
                    texto_produto = texto_produto[:28] + "..."
                
                produto_label = QLabel(texto_produto)
                produto_label.setStyleSheet("""
                    color: #e2e8f0;
                    font-size: 14px;
                    font-weight: 500;
                """)
                produto_item_layout.addWidget(produto_label)
                
                # Cor do produto (suporta formato antigo e novo)
                cor_display = ""
                
                # Tentar novo formato (string simples)
                cor = produto.get('cor', '')
                if cor and cor != '-':
                    cor_display = cor
                
                # Se não tem cor no novo formato, tentar formato antigo (cor_data)
                if not cor_display:
                    cor_data = produto.get('cor_data')
                    if cor_data:
                        if cor_data.get('tipo') == 'separadas':
                            tampa = cor_data.get('tampa', '')
                            corpo = cor_data.get('corpo', '')
                            if tampa or corpo:
                                cor_display = f"T:{tampa}/C:{corpo}"
                        elif cor_data.get('tipo') == 'unica':
                            cor_unica = cor_data.get('cor', '')
                            if cor_unica:
                                cor_display = cor_unica
                
                # Exibir a cor se houver
                if cor_display:
                    cor_label = QLabel(cor_display)
                    cor_label.setStyleSheet("""
                        background: rgba(129, 140, 248, 0.2);
                        color: #a5b4fc;
                        font-size: 10px;
                        font-weight: 600;
                        padding: 4px 10px;
                        border-radius: 6px;
                        min-width: 80px;
                    """)
                    cor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    produto_item_layout.addWidget(cor_label)
                
                produto_item_layout.addStretch()
                produtos_layout.addLayout(produto_item_layout)
            
            # Se tem mais produtos, mostrar indicador
            if len(produtos) > 2:
                mais_layout = QHBoxLayout()
                mais_label = QLabel(f"+ {len(produtos) - 2} item(s) adicional(is)")
                mais_label.setStyleSheet("""
                    color: #94a3b8;
                    font-size: 10px;
                    font-style: italic;
                """)
                mais_layout.addStretch()
                mais_layout.addWidget(mais_label)
                mais_layout.addStretch()
                produtos_layout.addLayout(mais_layout)
        else:
            sem_produtos = QLabel("Nenhum produto cadastrado")
            sem_produtos.setStyleSheet("""
                color: #94a3b8;
                font-size: 11px;
                font-style: italic;
            """)
            sem_produtos.setAlignment(Qt.AlignmentFlag.AlignCenter)
            produtos_layout.addWidget(sem_produtos)
        
        produtos_main_layout.addLayout(produtos_layout)
        card_layout.addWidget(produtos_container)
        
        # Adicionar espaço flexível antes dos botões
        card_layout.addStretch()
        
        # Linha separadora
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet("background: #4a5568; max-height: 1px;")
        card_layout.addWidget(separator2)


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
    

            
    def _criar_secao_valores(self, layout, dados):
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
            btn_whatsapp.clicked.connect(lambda: self._mostrar_menu_whatsapp(btn_whatsapp, pedido))
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
    
    def _mostrar_mensagem_auto_close(self, titulo, mensagem, icone="information", segundos=5):
        """Mostra uma mensagem não-bloqueante que fecha automaticamente após X segundos com contador"""
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtCore import QTimer, Qt
        
        # Criar mensagem não-bloqueante
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(titulo)
        msg_box.setWindowModality(Qt.WindowModality.NonModal)  # Não-bloqueante!
        
        # Definir ícone
        if icone == "information":
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif icone == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif icone == "success":
            msg_box.setIcon(QMessageBox.Icon.Information)
        
        # Estilo padrão para todos (tema escuro)
        msg_box.setStyleSheet("""
            QMessageBox { 
                min-width: 400px;
            }
            QLabel {
                font-size: 12px;
                min-width: 350px;
            }
        """)
        
        # Adicionar botão OK
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # Variáveis para o contador
        msg_box._tempo_restante = segundos
        msg_box._mensagem_original = mensagem
        
        # Atualizar texto com contador
        def atualizar_contador():
            if msg_box._tempo_restante > 0:
                texto_com_timer = f"{msg_box._mensagem_original}\n\n⏱️ Fecha automaticamente em {msg_box._tempo_restante}s"
                msg_box.setText(texto_com_timer)
                msg_box._tempo_restante -= 1
            else:
                msg_box.accept()
        
        # Mostrar texto inicial com contador
        atualizar_contador()
        
        # Timer para atualizar o contador a cada segundo
        timer = QTimer(msg_box)
        timer.timeout.connect(atualizar_contador)
        timer.start(1000)  # Atualiza a cada 1 segundo
        
        # Mostrar (não-bloqueante)
        msg_box.show()
        
        return msg_box
    
    def _buscar_telefone_atualizado_cliente(self, pedido):
        """
        Busca o telefone mais recente do cliente no banco de dados.
        
        Args:
            pedido: Dados do pedido com CPF do cliente
            
        Returns:
            Telefone atualizado ou None se não encontrar
        """
        try:
            from database import db_manager
            
            # Tentar por CPF primeiro
            cpf = pedido.get('cpf_cliente') or pedido.get('cpf', '')
            if cpf:
                cpf_limpo = ''.join(filter(str.isdigit, cpf))
                cliente = db_manager.buscar_cliente_por_cpf(cpf_limpo)
                # buscar_cliente_por_cpf retorna dicionário
                if cliente and cliente.get('telefone'):
                    print(f"[DEBUG] Telefone encontrado por CPF: '{cliente['telefone']}'")
                    return cliente['telefone']
            
            # Se não encontrou por CPF, tentar por nome
            nome = pedido.get('nome_cliente', '')
            if nome:
                clientes = db_manager.listar_clientes()
                # listar_clientes retorna lista de tuplas
                # Formato: (id, nome, cpf, cnpj, inscricao_estadual, telefone, email, cep, rua, numero, bairro, cidade, estado, referencia, numero_compras)
                for cliente_tuple in clientes:
                    if len(cliente_tuple) > 1:
                        nome_cliente = cliente_tuple[1]  # índice 1 = nome
                        telefone_cliente = cliente_tuple[5]  # índice 5 = telefone
                        
                        if nome_cliente and nome_cliente.lower() == nome.lower():
                            if telefone_cliente:
                                print(f"[DEBUG] Telefone encontrado por nome: '{telefone_cliente}'")
                                return telefone_cliente
            
            print(f"[DEBUG] Telefone não encontrado para cliente '{nome}'")
            return None
        except Exception as e:
            print(f"[DEBUG] Erro ao buscar telefone atualizado: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _validar_telefone_whatsapp(self, telefone):
        """
        Valida telefone para WhatsApp e retorna mensagem de erro detalhada se inválido.
        
        Args:
            telefone: Telefone com ou sem formatação
            
        Returns:
            Tupla (válido: bool, telefone_limpo: str, mensagem_erro: str)
        """
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        tamanho = len(telefone_limpo)
        
        # Validações
        if tamanho == 0:
            return False, "", "Telefone vazio ou não informado."
        
        if tamanho < 10:
            return False, telefone_limpo, (
                f"📱 Telefone Inválido\n\n"
                f"❌ Telefone cadastrado: {telefone}\n"
                f"❌ Apenas {tamanho} dígito{'s' if tamanho != 1 else ''}\n\n"
                f"✅ Formato esperado:\n"
                f"   • Celular: (11) 98765-4321 (11 dígitos)\n"
                f"   • Fixo: (11) 3456-7890 (10 dígitos)\n\n"
                f"💡 O telefone está sem DDD no cadastro.\n"
                f"   Corrija na aba 'Clientes' adicionando o DDD."
            )
        
        if tamanho > 11:
            return False, telefone_limpo, (
                f"📱 Telefone Inválido\n\n"
                f"❌ Telefone cadastrado: {telefone}\n"
                f"❌ Contém {tamanho} dígitos (excesso de {tamanho - 11})\n\n"
                f"✅ Formato esperado:\n"
                f"   • Celular: (11) 98765-4321 (11 dígitos)\n"
                f"   • Fixo: (11) 3456-7890 (10 dígitos)\n\n"
                f"💡 Remova o código do país (55) do cadastro.\n"
                f"   Corrija na aba 'Clientes'."
            )
        
        # Telefone válido
        return True, telefone_limpo, ""
    
    def _mostrar_menu_whatsapp(self, btn_whatsapp, pedido):
        """Mostra menu com opções de WhatsApp: mensagem ou PDF"""
        try:
            from PyQt6.QtWidgets import QMenu, QMessageBox
            from PyQt6.QtGui import QAction
            
            # Buscar telefone atualizado do cliente no banco de dados
            telefone = self._buscar_telefone_atualizado_cliente(pedido)
            
            # Se não encontrou atualizado, usar o do pedido
            if not telefone:
                telefone = pedido.get('telefone_cliente', '').strip()
            
            print(f"[DEBUG WhatsApp] Telefone usado: '{telefone}'")
            
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
            
            # Ação: Criar PDF (sem enviar)
            acao_criar_pdf = QAction("📄 Criar PDF", self)
            acao_criar_pdf.setToolTip("Gerar PDF da OS e abrir pasta")
            acao_criar_pdf.triggered.connect(lambda: self._criar_pdf_apenas(btn_whatsapp, pedido))
            menu.addAction(acao_criar_pdf)
            
            # Separador
            menu.addSeparator()
            
            # Ação: Enviar PDF via App
            acao_pdf_app = QAction("� PDF via App", self)
            acao_pdf_app.setToolTip("Criar PDF e abrir WhatsApp App com arquivo anexado")
            acao_pdf_app.triggered.connect(lambda: self._enviar_pdf_whatsapp_app(btn_whatsapp, pedido))
            menu.addAction(acao_pdf_app)
            
            # Ação: Enviar PDF via Web  
            acao_pdf_web = QAction("🌐 PDF via Web", self)
            acao_pdf_web.setToolTip("Criar PDF e abrir WhatsApp Web (arrastar arquivo)")
            acao_pdf_web.triggered.connect(lambda: self._enviar_pdf_whatsapp_web(btn_whatsapp, pedido))
            menu.addAction(acao_pdf_web)
            
            # Mostrar menu próximo ao botão
            menu.exec(btn_whatsapp.mapToGlobal(btn_whatsapp.rect().bottomLeft()))
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao abrir menu WhatsApp: {str(e)}")
            print(f"Erro no menu WhatsApp: {e}")
    
    def _criar_pdf_apenas(self, btn_whatsapp, pedido):
        """Gera apenas o PDF da OS sem enviar para WhatsApp"""
        try:
            import os
            import subprocess
            import platform
            from PyQt6.QtCore import QTimer
            from PyQt6.QtWidgets import QMessageBox
            from documents.os_pdf import OrdemServicoPDF
            
            numero_os = pedido.get('numero_os', pedido.get('id', 'N/A'))
            cliente = pedido.get('nome_cliente', 'Cliente')
            
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
            
            # Buscar dados completos do cliente se faltar endereço ou cep
            cliente_tem_endereco = bool(pedido.get('cep_cliente')) and bool(pedido.get('rua_cliente'))
            if not cliente_tem_endereco:
                try:
                    from database import db_manager
                    cpf = pedido.get('cpf_cliente') or pedido.get('cpf')
                    if cpf:
                        cpf_limpo = ''.join(filter(str.isdigit, cpf))
                        dados_cliente = db_manager.buscar_cliente_por_cpf(cpf_limpo)
                        if dados_cliente:
                            pedido['cep_cliente'] = dados_cliente.get('cep')
                            pedido['rua_cliente'] = dados_cliente.get('rua')
                            pedido['numero_cliente'] = dados_cliente.get('numero')
                            pedido['bairro_cliente'] = dados_cliente.get('bairro')
                            pedido['cidade_cliente'] = dados_cliente.get('cidade')
                            pedido['estado_cliente'] = dados_cliente.get('estado')
                except Exception:
                    pass
            
            # Gerar PDF
            gerador = OrdemServicoPDF(pedido)
            caminho_pdf = gerador.gerar()
            
            if not caminho_pdf or not os.path.exists(caminho_pdf):
                raise Exception("Falha ao gerar PDF")
            
            # Feedback: PDF pronto
            btn_whatsapp.setText("PDF Criado!")
            btn_whatsapp.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: 1px solid #388E3C;
                    border-radius: 4px;
                    padding: 5px 8px;
                    font-size: 10px;
                    font-weight: bold;
                    min-width: 70px;
                    max-height: 28px;
                }
            """)
            
            # Abrir pasta onde o PDF foi salvo
            pasta_pdf = os.path.dirname(caminho_pdf)
            sistema = platform.system()
            
            if sistema == 'Windows':
                os.startfile(pasta_pdf)
            elif sistema == 'Darwin':  # macOS
                subprocess.run(['open', pasta_pdf])
            else:  # Linux
                subprocess.run(['xdg-open', pasta_pdf])
            
            # Mostrar informações (não-bloqueante, fecha em 5 segundos)
            self._mostrar_mensagem_auto_close(
                "✅ PDF Criado com Sucesso!", 
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 Ordem de Serviço #{numero_os}\n"
                f"👤 Cliente: {cliente}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📄 Arquivo:\n   {os.path.basename(caminho_pdf)}\n\n"
                f"📁 Localização:\n   {pasta_pdf}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✨ A pasta foi aberta automaticamente!\n"
                f"💡 O PDF está pronto para ser enviado.",
                "success",
                5
            )
            
            # Após 3 segundos, volta ao normal
            QTimer.singleShot(3000, lambda: self._restaurar_botao_whatsapp(btn_whatsapp, texto_original))
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {str(e)}")
            print(f"Erro ao criar PDF: {e}")
            # Restaurar botão em caso de erro
            self._restaurar_botao_whatsapp(btn_whatsapp, "WhatsApp")
    
    def _enviar_pdf_whatsapp_web(self, btn_whatsapp, pedido):
        """Gera PDF da OS e envia via WhatsApp"""
        try:
            import webbrowser
            import urllib.parse
            import os
            from PyQt6.QtCore import QTimer
            from PyQt6.QtWidgets import QMessageBox
            from documents.os_pdf import OrdemServicoPDF
            
            # Buscar telefone atualizado do cliente no banco de dados
            telefone = self._buscar_telefone_atualizado_cliente(pedido)
            if not telefone:
                telefone = pedido.get('telefone_cliente', '').strip()
            
            numero_os = pedido.get('numero_os', pedido.get('id', 'N/A'))
            cliente = pedido.get('nome_cliente', 'Cliente')
            
            print(f"[DEBUG WhatsApp Web PDF] Telefone usado: '{telefone}'")
            
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
            
            # Buscar dados completos do cliente se faltar endereço ou cep
            cliente_tem_endereco = bool(pedido.get('cep_cliente')) and bool(pedido.get('rua_cliente'))
            if not cliente_tem_endereco:
                try:
                    from database.core.db_manager import DatabaseManager
                    db = DatabaseManager()
                    cpf = pedido.get('cpf_cliente') or pedido.get('cpf')
                    if cpf:
                        dados_cliente = db.buscar_cliente_por_cpf(cpf)
                        if dados_cliente:
                            pedido['cep_cliente'] = dados_cliente.get('cep')
                            pedido['rua_cliente'] = dados_cliente.get('rua')
                            pedido['numero_cliente'] = dados_cliente.get('numero')
                            pedido['bairro_cliente'] = dados_cliente.get('bairro')
                            pedido['cidade_cliente'] = dados_cliente.get('cidade')
                            pedido['estado_cliente'] = dados_cliente.get('estado')
                            pedido['endereco_cliente'] = f"{dados_cliente.get('rua', '')}, {dados_cliente.get('numero', '')}"
                except Exception as e:
                    print(f"Erro ao buscar dados completos do cliente para PDF: {e}")

            # Gerar PDF
            pdf_generator = OrdemServicoPDF(pedido)
            caminho_pdf = pdf_generator.gerar()
            
            if not os.path.exists(caminho_pdf):
                raise Exception("Erro ao gerar PDF")
            
            # Validar telefone
            valido, telefone_limpo, msg_erro = self._validar_telefone_whatsapp(telefone)
            if not valido:
                QMessageBox.warning(self, "WhatsApp", msg_erro)
                return
            
            # Adicionar código do país (55) se ainda não tiver
            if not telefone_limpo.startswith('55'):
                telefone_limpo = '55' + telefone_limpo
            
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
            instrucoes = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Ordem de Serviço #{numero_os}
👤 Cliente: {cliente}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ WhatsApp Web foi aberto!
✅ Pasta do PDF foi aberta!

📄 Arquivo:
   {os.path.basename(caminho_pdf)}

📁 Localização:
   {os.path.basename(pasta_pdf)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 COMO ENVIAR O PDF:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ Localize a conversa com {cliente}
2️⃣ Clique no ícone 📎 (anexar)
3️⃣ Selecione "Documento"
4️⃣ Escolha o PDF ou arraste da pasta
5️⃣ Clique em Enviar ✅

💡 Arraste direto da pasta para agilizar!"""
            
            # Mostrar instruções (não-bloqueante, fecha em 10 segundos - mais tempo para ler)
            self._mostrar_mensagem_auto_close("🌐 WhatsApp Web + PDF", instrucoes, "information", 10)
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
            import subprocess
            import platform
            from PyQt6.QtCore import QTimer
            from PyQt6.QtWidgets import QMessageBox
            from documents.os_pdf import OrdemServicoPDF
            
            # Buscar telefone atualizado do cliente no banco de dados
            telefone = self._buscar_telefone_atualizado_cliente(pedido)
            if not telefone:
                telefone = pedido.get('telefone_cliente', '').strip()
            
            numero_os = pedido.get('numero_os', pedido.get('id', 'N/A'))
            cliente = pedido.get('nome_cliente', 'Cliente')
            
            print(f"[DEBUG WhatsApp App PDF] Telefone usado: '{telefone}'")
            
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
            
            # Validar telefone
            valido, telefone_limpo, msg_erro = self._validar_telefone_whatsapp(telefone)
            if not valido:
                QMessageBox.warning(self, "WhatsApp", msg_erro)
                return
            
            # Adicionar código do país (55) se ainda não tiver
            if not telefone_limpo.startswith('55'):
                telefone_limpo = '55' + telefone_limpo
            
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
            
            # Abrir pasta do PDF para facilitar o envio manual
            pasta_pdf = os.path.dirname(caminho_pdf)
            sistema = platform.system()
            
            try:
                if sistema == 'Windows':
                    # No Windows, podemos selecionar o arquivo na pasta
                    subprocess.run(['explorer', '/select,', os.path.normpath(caminho_pdf)])
                elif sistema == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', caminho_pdf])
                else:  # Linux
                    # No Linux, abre a pasta
                    subprocess.run(['xdg-open', pasta_pdf])
            except Exception:
                # Se falhar, apenas abre a pasta normalmente
                if sistema == 'Windows':
                    os.startfile(pasta_pdf)
                elif sistema == 'Darwin':
                    subprocess.run(['open', pasta_pdf])
                else:
                    subprocess.run(['xdg-open', pasta_pdf])
            
            # Mostrar informações (não-bloqueante, fecha em 5 segundos)
            self._mostrar_mensagem_auto_close(
                "📱 WhatsApp App Aberto!", 
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 Ordem de Serviço #{numero_os}\n"
                f"👤 Cliente: {cliente}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"✅ WhatsApp App foi aberto!\n"
                f"✅ Pasta do PDF foi aberta!\n\n"
                f"📄 Arquivo:\n   {os.path.basename(caminho_pdf)}\n\n"
                f"📁 Localização:\n   {pasta_pdf}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 Arraste o PDF para o WhatsApp\n"
                f"   ou anexe manualmente.",
                "success",
                5
            )
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
            
            # Buscar telefone atualizado do cliente no banco de dados
            telefone = self._buscar_telefone_atualizado_cliente(pedido)
            if not telefone:
                telefone = pedido.get('telefone_cliente', '').strip()
            
            numero_os = pedido.get('numero_os', pedido.get('id', 'N/A'))
            cliente = pedido.get('nome_cliente', 'Cliente')
            
            print(f"[DEBUG WhatsApp Mensagem] Telefone usado: '{telefone}'")
            
            if not telefone:
                QMessageBox.warning(self, "WhatsApp", "Telefone não informado para este cliente.")
                return
            
            # Validar telefone
            valido, telefone_limpo, msg_erro = self._validar_telefone_whatsapp(telefone)
            if not valido:
                QMessageBox.warning(self, "WhatsApp", msg_erro)
                return
            
            # Adicionar código do país (55) se ainda não tiver
            if not telefone_limpo.startswith('55'):
                telefone_limpo = '55' + telefone_limpo
            
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
            
            # Mensagem pré-formatada (tom mais humano e natural)
            mensagem = (
                f"Oi {cliente}, tudo bem?\n\n"
                f"Estou te enviando uma mensagem sobre a sua Ordem de Serviço nº {numero_os}. "
                f"Queria te atualizar brevemente sobre o andamento — se precisar de algo, é só falar comigo por aqui.\n\n"
            )
            
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
            
            # Buscar telefone atualizado do cliente no banco de dados
            telefone = self._buscar_telefone_atualizado_cliente(pedido)
            if not telefone:
                telefone = pedido.get('telefone_cliente', '').strip()
            
            numero_os = pedido.get('numero_os', pedido.get('id', 'N/A'))
            cliente = pedido.get('nome_cliente', 'Cliente')
            
            print(f"[DEBUG WhatsApp Direto] Telefone usado: '{telefone}'")
            
            if not telefone:
                QMessageBox.warning(self, "WhatsApp", "Telefone não informado para este cliente.")
                return
            
            # Validar telefone
            valido, telefone_limpo, msg_erro = self._validar_telefone_whatsapp(telefone)
            if not valido:
                QMessageBox.warning(self, "WhatsApp", msg_erro)
                return
            
            # Adicionar código do país (55) se ainda não tiver
            if not telefone_limpo.startswith('55'):
                telefone_limpo = '55' + telefone_limpo
            
            # Mensagem pré-formatada (tom mais humano e natural)
            mensagem = (
                f"Oi {cliente}, tudo bem?\n\n"
                f"Aqui é a merkava, e viemos te atualizar sobre o seu pedido. "
                f"Tenho uma atualização e, se quiser saber mais ou tiver qualquer dúvida, pode me responder aqui mesmo.\n\n"
                
            )
            
            # Codificar mensagem para URL
            mensagem_encoded = urllib.parse.quote(mensagem)
            
            # Criar URL do WhatsApp
            url = f"https://wa.me/{telefone_limpo}?text={mensagem_encoded}"
            
            # Abrir WhatsApp
            webbrowser.open(url)
            
            # Feedback visual de sucesso (não-bloqueante, fecha em 5 segundos)
            self._mostrar_mensagem_auto_close(
                "WhatsApp",
                f"WhatsApp aberto para {cliente}!\nTelefone: {telefone}",
                "success",
                5
            )
            
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Erro ao abrir WhatsApp: {str(e)}")
            print(f"Erro ao abrir WhatsApp: {e}")
