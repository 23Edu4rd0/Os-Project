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
    editar_clicked = pyqtSignal(int)  # pedido_id
    excluir_clicked = pyqtSignal(int)  # pedido_id
    status_changed = pyqtSignal(int, str)  # pedido_id, novo_status
    pedido_atualizado = pyqtSignal()  # Para refresh da lista
    
    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        
    def criar_card(self, pedido):
        """Cria um card completo com todas as informações do pedido"""
        # Frame principal
        card_widget = QFrame()
        # Aumentar o tamanho dos cards para melhorar leitura
        card_widget.setFixedWidth(380)
        card_widget.setFixedHeight(300)

        # Layout principal
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(5)

        # Extrair informações do pedido
        pedido_id = pedido.get('id', 'N/A')
        cliente_nome = pedido.get('nome_cliente', 'Cliente não informado')
        cliente_telefone = pedido.get('telefone_cliente', '')
        status = pedido.get('status', 'pendente')
        produtos = pedido.get('produtos', [])
        endereco = pedido.get('endereco_cliente', 'Endereço não informado')
        valor_total = pedido.get('valor_total', 0)

        # 1. Cliente e número
        cliente_info = f"{cliente_nome}"
        if cliente_telefone:
            cliente_info += f" - {cliente_telefone}"

        cliente_label = QLabel(cliente_info)
        cliente_label.setStyleSheet("font-weight: bold; font-size: 13px; color: white;")
        cliente_label.setWordWrap(True)
        card_layout.addWidget(cliente_label)

        # 2. Pedido e prazo
        dias_restantes = self._calcular_dias_restantes(pedido)
        prazo_info = f"Pedido #{pedido_id}"
        if dias_restantes is not None:
            if dias_restantes > 0:
                prazo_info += f" - Faltam {dias_restantes} dias"
            elif dias_restantes == 0:
                prazo_info += " - Entrega hoje!"
            else:
                prazo_info += f" - Atrasado {abs(dias_restantes)} dias"

        pedido_label = QLabel(prazo_info)
        pedido_label.setStyleSheet("font-size: 11px; color: #cccccc;")
        card_layout.addWidget(pedido_label)

        # 3. Produtos (nome, código e quantidade - até 3 linhas)
        if produtos and len(produtos) > 0:
            produto_info = []
            produtos_para_mostrar = produtos[:3]

            for i, produto in enumerate(produtos_para_mostrar):
                descricao = produto.get('descricao', '').strip()
                valor = produto.get('valor', 0)

                # Gerar quantidade baseada no valor (simulação)
                if valor >= 500:
                    quantidade = 1
                elif valor >= 200:
                    quantidade = 2
                else:
                    quantidade = 3

                if descricao:
                    # Gerar código mais curto e realista (usa _gerar_codigo_produto existente)
                    codigo_produto = self._gerar_codigo_produto(descricao, i)
                    # Formato: nome - código - quantidade
                    linha_produto = f"{descricao} - {codigo_produto} - {quantidade}x"
                else:
                    # Formato antigo como fallback (sem divisórias)
                    nome = produto.get('nome', 'Produto')
                    codigo = produto.get('codigo', f"{8000 + i:04d}")
                    linha_produto = f"{nome} - {codigo} - {quantidade}x"

                produto_info.append(linha_produto)

            if len(produtos) > 3:
                produto_info.append(f"... e mais {len(produtos) - 3}")

            produtos_text = "\n".join(produto_info)
        else:
            # Fallback para detalhes_produto se produtos[] estiver vazio
            detalhes_produto = pedido.get('detalhes_produto', '')
            if detalhes_produto:
                # Tentar extrair informações do texto
                linhas = detalhes_produto.split('\n')[:3]  # Máximo 3 linhas
                produto_info = []
                for i, linha in enumerate(linhas):
                    linha = linha.strip()
                    if linha:
                        codigo = f"{8250 + (i * 100):04d}"
                        linha_formatada = f"{linha} - {codigo} - 1x"
                        produto_info.append(linha_formatada)

                produtos_text = "\n".join(produto_info) if produto_info else "Nenhum produto"
            else:
                produtos_text = "Nenhum produto"

        produtos_label = QLabel(f"Produtos:\n{produtos_text}")
        produtos_label.setStyleSheet("font-size: 11px; color: #d0d0d0;")
        produtos_label.setWordWrap(True)
        card_layout.addWidget(produtos_label)

        # 4. Endereço
        endereco_label = QLabel(f"Endereço: {endereco}")
        endereco_label.setStyleSheet("font-size: 10px; color: #cccccc;")
        endereco_label.setWordWrap(True)
        card_layout.addWidget(endereco_label)

        # 5. Valor
        try:
            valor_formatado = f"R$ {float(valor_total):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            valor_formatado = f"R$ {valor_total}"

        valor_label = QLabel(f"Valor: {valor_formatado}")
        valor_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #90EE90;")
        card_layout.addWidget(valor_label)

        # Spacer para empurrar botões para baixo
        card_layout.addStretch()

        # 6. Botões (4 botões conforme solicitado)
        self._criar_botoes_completos(card_layout, pedido)

        # Aplicar estilo básico
        self._aplicar_estilo_basico(card_widget, status)

        return card_widget
    
    def _criar_botoes_completos(self, layout, pedido):
        """Cria os 4 botões: Editar, Status, WhatsApp e Deletar"""
        botoes_layout = QHBoxLayout()
        botoes_layout.setSpacing(5)
        
        pedido_id = pedido.get('id')
        telefone = pedido.get('telefone_cliente', '')
        
        # Botão Editar
        btn_editar = QPushButton("Editar")
        btn_editar.setFixedSize(70, 25)
        btn_editar.clicked.connect(lambda: self.editar_clicked.emit(pedido_id))
        botoes_layout.addWidget(btn_editar)
        
        # Botão Status
        btn_status = QPushButton("Status")
        btn_status.setFixedSize(70, 25)
        btn_status.clicked.connect(lambda: self._abrir_menu_status(pedido_id))
        botoes_layout.addWidget(btn_status)
        
        # Botão WhatsApp
        btn_whatsapp = QPushButton("WhatsApp")
        btn_whatsapp.setFixedSize(70, 25)
        if telefone:
            btn_whatsapp.clicked.connect(lambda: self._abrir_whatsapp(pedido))
        else:
            btn_whatsapp.setEnabled(False)
            btn_whatsapp.setStyleSheet("color: #666666;")
        botoes_layout.addWidget(btn_whatsapp)
        
        # Botão Deletar
        btn_deletar = QPushButton("Deletar")
        btn_deletar.setFixedSize(70, 25)
        btn_deletar.clicked.connect(lambda: self.excluir_clicked.emit(pedido_id))
        btn_deletar.setStyleSheet("""
            QPushButton {
                background-color: #cc4444;
                color: white;
                border: 1px solid #aa3333;
                border-radius: 3px;
                font-size: 9px;
            }
            QPushButton:hover {
                background-color: #dd5555;
            }
        """)
        botoes_layout.addWidget(btn_deletar)
        
        layout.addLayout(botoes_layout)
    
    # (Remove this entire duplicate block; keep only the most complete version of _calcular_dias_restantes)
    
    def _abrir_whatsapp(self, pedido):
        """Abre o WhatsApp com mensagem sobre o pedido"""
        try:
            import webbrowser
            import urllib.parse
            
            telefone = pedido.get('telefone_cliente', '')
            cliente_nome = pedido.get('nome_cliente', 'Cliente')  # Corrigido: era 'cliente_nome'
            pedido_id = pedido.get('id', '')
            
            # Remove caracteres não numéricos do telefone
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            if len(telefone_limpo) >= 10:
                # Adiciona código do país se necessário (Brasil)
                if len(telefone_limpo) == 10 or len(telefone_limpo) == 11:
                    telefone_limpo = '55' + telefone_limpo
                
                # Monta a mensagem
                mensagem = f"Olá {cliente_nome}! Referente ao pedido #{pedido_id}..."
                mensagem_encoded = urllib.parse.quote(mensagem)
                
                # Monta a URL do WhatsApp
                url = f"https://wa.me/{telefone_limpo}?text={mensagem_encoded}"
                webbrowser.open(url)
                
        except Exception as e:
            print(f"Erro ao abrir WhatsApp: {e}")
    
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
    
    def _abrir_whatsapp(self, pedido):
        """Abre WhatsApp para o cliente do pedido"""
        try:
            import webbrowser
            telefone = pedido.get('telefone_cliente', '')
            if telefone:
                # Remove caracteres não numéricos
                telefone_limpo = ''.join(filter(str.isdigit, telefone))
                if telefone_limpo:
                    url = f"https://wa.me/55{telefone_limpo}"
                    webbrowser.open(url)
        except Exception as e:
            print(f"Erro ao abrir WhatsApp: {e}")
            
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
    
    def _criar_botoes(self, layout, pedido):
        """Cria os botões do card com design melhorado"""
        botoes_frame = QFrame()
        botoes_frame.setStyleSheet("background: transparent; border: none;")
        botoes_layout = QHBoxLayout(botoes_frame)
        botoes_layout.setContentsMargins(0, 8, 0, 0)
        botoes_layout.setSpacing(12)
        
        pedido_id = pedido.get('id')
        
        # Adicionar stretch no início para centralizar botões
        botoes_layout.addStretch()
        
        # Botão Editar simples
        btn_editar = QPushButton("Editar")
        btn_editar.setMinimumWidth(70)
        btn_editar.clicked.connect(lambda: self.editar_clicked.emit(pedido_id))
        botoes_layout.addWidget(btn_editar)
        
        # Botão Excluir simples
        btn_excluir = QPushButton("Excluir")
        btn_excluir.setMinimumWidth(70)
        btn_excluir.clicked.connect(lambda: self.excluir_clicked.emit(pedido_id))
        btn_excluir.setStyleSheet("""
            QPushButton {
                background-color: #cc4444;
                color: white;
                border: 1px solid #aa3333;
                border-radius: 3px;
                padding: 6px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #dd5555;
            }
        """)
        botoes_layout.addWidget(btn_excluir)
        
        # Botão Status simples
        btn_status = QPushButton("Status")
        btn_status.setMinimumWidth(70)
        btn_status.clicked.connect(lambda: self._abrir_menu_status(pedido_id))
        botoes_layout.addWidget(btn_status)
        
        # Botão WhatsApp simples (se disponível)
        telefone = pedido.get('telefone_cliente', '')
        if telefone:
            btn_whatsapp = QPushButton("WhatsApp")
            btn_whatsapp.setMinimumWidth(80)
            btn_whatsapp.setStyleSheet("""
                QPushButton {
                    background-color: #25d366;
                    color: white;
                    border: 1px solid #1da851;
                    border-radius: 3px;
                    padding: 6px 10px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #1da851;
                }
            """)
            btn_whatsapp.clicked.connect(lambda: self._abrir_whatsapp(pedido))
            botoes_layout.addWidget(btn_whatsapp)
        
        # Adicionar stretch no final para centralizar botões
        botoes_layout.addStretch()
        
        # Aplicar estilo aos botões (exceto os que já têm estilo customizado)
        self._aplicar_estilo_botoes(botoes_frame)
        
        layout.addWidget(botoes_frame)
    
    def _abrir_whatsapp(self, pedido):
        """Abre WhatsApp com o cliente do pedido"""
        import webbrowser
        telefone = pedido.get('telefone_cliente', '').strip()
        if telefone:
            # Limpar telefone (manter apenas números)
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            if telefone_limpo:
                # Adicionar código do país se não tiver
                if len(telefone_limpo) == 11 and telefone_limpo.startswith('9'):
                    telefone_limpo = '55' + telefone_limpo
                elif len(telefone_limpo) == 10:
                    telefone_limpo = '5511' + telefone_limpo
                
                numero_os = pedido.get('numero_os', '')
                cliente = pedido.get('nome_cliente', 'Cliente')
                
                mensagem = f"Olá {cliente}! Sobre a OS #{numero_os}"
                url = f"https://wa.me/{telefone_limpo}?text={mensagem}"
                webbrowser.open(url)

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
