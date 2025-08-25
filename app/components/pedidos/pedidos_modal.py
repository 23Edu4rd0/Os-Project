# -*- coding: utf-8 -*-
"""
Modal de pedidos em PyQt6
"""


# Refatoração: importa funções da pasta pedidosModal
from .pedidosModal import (
    abrir_modal_novo, abrir_modal_edicao, _carregar_clientes, _criar_modal_completo, _criar_header,
    _criar_secao_cliente, _criar_secao_produtos, _carregar_produtos, _montar_produtos_completer,
    _filtrar_produtos_por_categoria, _on_produto_completer_activated, _on_produto_text_changed,
    _criar_secao_pagamento, _criar_secao_resumo, _criar_botoes, _format_phone, _on_cliente_completer_activated,
    _refresh_produtos_ui, _add_produto, _limpar_campos_cliente, _remove_produto, _recalcular_total,
    _on_cliente_selecionado, _preencher_dados_cliente, _resolver_cliente, _gerar_pdf, _aplicar_estilo
)
from .pedidosModal import PedidosModal

# O resto do arquivo pode ser removido, pois a classe e métodos agora estão na pasta pedidosModal


class PedidosModal(QDialog):
    """Gerencia os modais de pedidos"""
    
    # Sinal para notificar quando um pedido foi salvo
    pedido_salvo = pyqtSignal()
    
    def __init__(self, interface):
        super().__init__()
        self.interface = interface
        self.model = PedidoFormModel()
        self.clientes_dict = {}
        self.produtos_dict = {}
        
    def abrir_modal_novo(self):
        """Abre modal para novo pedido"""
        self._carregar_clientes()
        self._criar_modal_completo()
        
    def abrir_modal_edicao(self, pedido_id):
        """Abre modal para editar pedido"""
        # Buscar dados do pedido
        try:
            pedidos = db_manager.listar_pedidos_ordenados_por_prazo()
            pedido_data = None
            for pedido in pedidos:
                if pedido.get('id') == pedido_id:
                    pedido_data = pedido
                    break
            
            if pedido_data:
                self._carregar_clientes()
                self._criar_modal_completo(pedido_data)
            else:
                QMessageBox.warning(self, "Erro", "Pedido não encontrado!")
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar pedido: {e}")
    
    def _carregar_clientes(self):
        """Carrega lista de clientes do banco de dados"""
        try:
            clientes = db_manager.listar_clientes()
            self.clientes_dict = {}
            
            for cliente in clientes:
                if len(cliente) >= 7:
                    cliente_id = cliente[0]
                    nome = cliente[1] or ''
                    cpf = cliente[2] or ''
                    telefone = cliente[3] or ''
                    email = cliente[4] or ''
                    rua = cliente[5] or ''
                    numero = cliente[6] or ''
                    
                    if nome:
                        # Exibir como: Nome | (Telefone)
                        telefone_fmt = self._format_phone(telefone)
                        nome_exibicao = f"{nome} | {telefone_fmt}" if telefone_fmt else nome
                        
                        self.clientes_dict[nome_exibicao] = {
                            'id': cliente_id,
                            'nome': nome,
                            'cpf': cpf,
                            'telefone': telefone,
                            'email': email,
                            'rua': rua,
                            'numero': numero
                        }
                        
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            self.clientes_dict = {}
    
    def _criar_modal_completo(self, pedido_data=None):
        """Cria modal completo para pedido"""
        is_edit = pedido_data is not None
        if is_edit:
            self.model.reset()
            self.model.preencher(pedido_data)
        else:
            self.model.reset()
        numero_os = pedido_data.get('numero_os') if pedido_data else None
        titulo = f"Editar OS #{numero_os}" if is_edit else "Nova Ordem de Serviço"
        self.setWindowTitle(titulo)
        self.setFixedSize(900, 700)

        # Layout principal com scroll
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Área de scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Configurar scroll suave para modal
        scroll_area.verticalScrollBar().setSingleStep(15)
        scroll_area.verticalScrollBar().setPageStep(60)

        # Widget de conteúdo
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Header
        self._criar_header(content_layout, numero_os, is_edit)

        # Formulário
        self.campos = self.model.campos
        self.produtos_list = self.model.produtos_list
        self._criar_secao_cliente(content_layout, pedido_data)
        self._criar_secao_produtos(content_layout, pedido_data)
        self._criar_secao_pagamento(content_layout, pedido_data)
        self._criar_secao_resumo(content_layout)

        # Botões finais
        self._criar_botoes(content_layout, numero_os, pedido_data)

        # Configurar scroll
        try:
            scroll_area.setStyleSheet("QScrollArea{background:#2d2d2d;border:none;} QScrollArea > QWidget > QWidget {background:#2d2d2d;}")
            scroll_area.viewport().setStyleSheet("background:#2d2d2d;")
            content_widget.setStyleSheet("background:#2d2d2d;")
        except Exception:
            pass
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Aplicar estilo
        self._aplicar_estilo()

        # Executar modal
        self.exec()
    
    def _criar_header(self, layout, numero_os, is_edit):
        """Cria header do modal"""
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        if is_edit and numero_os is not None:
            titulo = f"Editar Ordem de Serviço #{numero_os:05d}"
        elif is_edit:
            titulo = "Editar Ordem de Serviço"
        else:
            titulo = f"Nova Ordem de Serviço" if numero_os is None else f"Nova Ordem de Serviço #{numero_os:05d}"
            
        titulo_label = QLabel(titulo)
        titulo_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_label.setStyleSheet("color: #ffffff; padding: 10px;")
        header_layout.addWidget(titulo_label)
        
        layout.addWidget(header_frame)
    
    def _criar_secao_cliente(self, layout, pedido_data):
        """Cria seção de dados do cliente"""
        if _criar_secao_cliente_part:
            _criar_secao_cliente_part(self, layout, pedido_data)
            return
        from PyQt6.QtWidgets import QLineEdit
        cliente_group = QGroupBox("👤 Dados do Cliente")
        cliente_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        cliente_layout = QFormLayout(cliente_group)

        # Nome do cliente com autocomplete + botão limpar
        self.campos['nome_cliente'] = QLineEdit()
        self.campos['nome_cliente'].setPlaceholderText("Digite o nome do cliente...")

        # Configurar autocomplete
        if self.clientes_dict:
            self.clientes_completer = QCompleter(list(self.clientes_dict.keys()))
            self.clientes_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.clientes_completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.campos['nome_cliente'].setCompleter(self.clientes_completer)
            # Preenche campos ao escolher opção do autocomplete
            try:
                self.clientes_completer.activated[str].connect(self._on_cliente_completer_activated)
            except Exception:
                pass
            # Atualiza endereço conforme digita/nome bate uma chave
            self.campos['nome_cliente'].textChanged.connect(self._on_cliente_selecionado)
            # Também tentar preencher ao terminar a edição
            try:
                self.campos['nome_cliente'].editingFinished.connect(lambda: self._on_cliente_selecionado(self.campos['nome_cliente'].text()))
            except Exception:
                pass

        # Adicionar botão de limpar ao lado do campo de nome
        nome_row = QHBoxLayout()
        nome_row.addWidget(self.campos['nome_cliente'])
        btn_limpar_cli = QPushButton("🧹 Limpar")
        btn_limpar_cli.setMaximumWidth(90)
        btn_limpar_cli.setToolTip("Limpar dados do cliente")
        btn_limpar_cli.clicked.connect(self._limpar_campos_cliente)
        nome_row.addWidget(btn_limpar_cli)
        nome_row_w = QWidget()
        nome_row_w.setLayout(nome_row)
        cliente_layout.addRow("Nome do Cliente:", nome_row_w)

        # Telefone
        self.campos['telefone_cliente'] = QLineEdit()
        self.campos['telefone_cliente'].setPlaceholderText("(11) 99999-9999")
        try:
            self.campos['telefone_cliente'].setInputMask("(00) 00000-0000;_")
        except Exception:
            pass
        cliente_layout.addRow("Telefone:", self.campos['telefone_cliente'])

        # CPF
        self.campos['cpf_cliente'] = QLineEdit()
        self.campos['cpf_cliente'].setPlaceholderText("000.000.000-00")
        try:
            self.campos['cpf_cliente'].setInputMask("000.000.000-00;_")
        except Exception:
            pass
        cliente_layout.addRow("CPF:", self.campos['cpf_cliente'])

        # Endereço
        self.campos['endereco_cliente'] = QLineEdit()
        self.campos['endereco_cliente'].setPlaceholderText("Rua, número, bairro, cidade")
        cliente_layout.addRow("Endereço:", self.campos['endereco_cliente'])

    # Preencher dados se for edição
    # (Removido: agora só a função modular faz isso para evitar conflito de tipos)

        layout.addWidget(cliente_group)
    
    def _criar_secao_produtos(self, layout, pedido_data):
        """Cria seção de produtos com adição múltipla"""
        if _criar_secao_produtos_part:
            _criar_secao_produtos_part(self, layout, pedido_data)
            return
        produtos_group = QGroupBox("📦 Produtos")
        produtos_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        produtos_vbox = QVBoxLayout(produtos_group)

        # Linha de inputs (categoria + descrição + valor + botão adicionar)
        linha_inputs = QHBoxLayout()
        self.input_categoria = QComboBox()
        self.input_categoria.setMinimumWidth(140)
        self.input_categoria.addItem("Todas")
        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Produto (catálogo)")
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("Valor (R$)")
        self.input_valor.setMaximumWidth(120)
        btn_add = QPushButton("+ Adicionar")
        btn_add.clicked.connect(self._add_produto)

        # Enter adiciona quando foco está no campo valor
        try:
            self.input_valor.returnPressed.connect(self._add_produto)
            self.input_desc.returnPressed.connect(self._add_produto)
        except Exception:
            pass
        # Autocomplete de produtos do catálogo
        try:
            self._carregar_produtos()
            # categorias
            if hasattr(self, '_produtos_categorias'):
                self.input_categoria.addItems(sorted(self._produtos_categorias))
                self.input_categoria.currentTextChanged.connect(self._filtrar_produtos_por_categoria)
            self._montar_produtos_completer()
        except Exception as _e:
            pass

        # Preencher automaticamente valor ao digitar nome de produto do catálogo
        try:
            self.input_desc.textChanged.connect(self._on_produto_text_changed)
        except Exception:
            pass

        linha_inputs.addWidget(self.input_categoria)
        linha_inputs.addWidget(self.input_desc, stretch=1)
        linha_inputs.addWidget(self.input_valor)
        linha_inputs.addWidget(btn_add)
        produtos_vbox.addLayout(linha_inputs)

        # Opções gerais do pedido: Cor e Reforço
        opcoes_row = QHBoxLayout()
        lbl_cor = QLabel("Cor:")
        self.campos['cor'] = QComboBox()
        self.campos['cor'].addItems([
            "",
            "Preto","Branco","Azul","Vermelho","Verde",
            "Amarelo","Cinza","Marrom","Rosa","Roxo",
        ])
        lbl_ref = QLabel("Reforço:")
        self.campos['reforco'] = QComboBox()
        self.campos['reforco'].addItems(["não", "sim"])
        opcoes_row.addWidget(lbl_cor)
        opcoes_row.addWidget(self.campos['cor'])
        opcoes_row.addSpacing(16)
        opcoes_row.addWidget(lbl_ref)
        opcoes_row.addWidget(self.campos['reforco'])
        opcoes_row.addStretch()
        produtos_vbox.addLayout(opcoes_row)

        # Lista de produtos inseridos
        self.lista_produtos_container = QVBoxLayout()
        self.lista_produtos_container.setSpacing(6)
        produtos_vbox.addLayout(self.lista_produtos_container)

        # Observações removidas conforme solicitado

        # Valor total (somado automaticamente)
        self.campos['valor_total'] = QLineEdit()
        self.campos['valor_total'].setReadOnly(True)
        self.campos['valor_total'].setPlaceholderText("0.00")
        total_row = QHBoxLayout()
        total_row.addWidget(QLabel("Valor Total (R$):"))
        total_row.addWidget(self.campos['valor_total'])
        produtos_vbox.addLayout(total_row)

        # Se for edição, tentar reconstruir lista a partir do texto/valor e preencher cor/reforço
        if pedido_data:
            # Tenta ler itens do campo 'detalhes_produto'
            detalhes = pedido_data.get('detalhes_produto', '') or ''
            for linha in [l.strip() for l in detalhes.replace('\\n', '\n').split('\n') if l.strip() and not l.strip().startswith('-')]:
                # Heurística simples: separador " - R$ "
                if ' - R$ ' in linha:
                    try:
                        desc, valtxt = linha.rsplit(' - R$ ', 1)
                        valor = float(valtxt.replace('.', '').replace(',', '.')) if valtxt else 0.0
                        self.produtos_list.append({"descricao": desc.strip('• ').strip(), "valor": valor})
                    except Exception:
                        self.produtos_list.append({"descricao": linha.strip('• ').strip(), "valor": 0.0})
                else:
                    self.produtos_list.append({"descricao": linha.strip('• ').strip(), "valor": 0.0})
            self._refresh_produtos_ui()
            valor = pedido_data.get('valor_total', pedido_data.get('valor_produto', 0))
            try:
                self.campos['valor_total'].setText(str(f"{float(valor or 0):.2f}"))
            except Exception:
                self.campos['valor_total'].setText(str("0.00"))
            # Prefill cor/reforço
            try:
                cor = pedido_data.get('cor', '') or ''
                if cor:
                    idx = self.campos['cor'].findText(cor)
                    if idx >= 0:
                        self.campos['cor'].setCurrentIndex(idx)
            except Exception:
                pass
            try:
                reforco_val = pedido_data.get('reforco', False)
                reforco_txt = 'sim' if (str(reforco_val).lower() in ('1','true','sim','yes')) else 'não'
                idx = self.campos['reforco'].findText(reforco_txt)
                if idx >= 0:
                    self.campos['reforco'].setCurrentIndex(idx)
            except Exception:
                pass

        layout.addWidget(produtos_group)

    def _carregar_produtos(self):
        """Carrega produtos do catálogo e prepara dicionário para autocomplete"""
        try:
            rows = db_manager.listar_produtos()
            self._produtos_rows = rows
            self._produtos_categorias = set([r[4] for r in rows if r[4]])
            self.produtos_dict = {}
            for r in rows:
                # r: (id, nome, preco, descricao, categoria, criado_em)
                nome = (r[1] or '').strip()
                preco = float(r[2] or 0)
                display = f"{nome} | R$ {preco:.2f}"
                self.produtos_dict[display] = {"id": r[0], "nome": nome, "preco": preco, "categoria": (r[4] or '')}
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
            self.produtos_dict = {}

    def _montar_produtos_completer(self, categoria: str | None = None):
        try:
            dic = {}
            source = getattr(self, '_produtos_rows', [])
            for r in source:
                if categoria and categoria != "Todas" and (r[4] or "") != categoria:
                    continue
                nome = (r[1] or '').strip()
                preco = float(r[2] or 0)
                display = f"{nome} | R$ {preco:.2f}"
                dic[display] = {"id": r[0], "nome": nome, "preco": preco, "categoria": (r[4] or '')}
            self.produtos_dict = dic
            if dic:
                self.produtos_completer = QCompleter(list(dic.keys()))
                self.produtos_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                self.produtos_completer.setFilterMode(Qt.MatchFlag.MatchContains)
                self.input_desc.setCompleter(self.produtos_completer)
                try:
                    self.produtos_completer.activated[str].disconnect()
                except Exception:
                    pass
                self.produtos_completer.activated[str].connect(self._on_produto_completer_activated)
        except Exception:
            pass

    def _filtrar_produtos_por_categoria(self, cat: str):
        self._montar_produtos_completer(cat)

    def _on_produto_completer_activated(self, texto: str):
        if texto in self.produtos_dict:
            p = self.produtos_dict[texto]
            # Preenche descrição com o nome e valor com o preço
            self.input_desc.setText(str(p.get('nome', '')))
            self.input_valor.setText(str(f"{float(p.get('preco', 0)):.2f}"))
            # Ajusta categoria, se houver
            try:
                cat = p.get('categoria') or 'Todas'
                idx = self.input_categoria.findText(cat)
                if idx >= 0:
                    self.input_categoria.setCurrentIndex(idx)
            except Exception:
                pass
    
    def _on_produto_text_changed(self, texto: str):
        """Ao digitar, se corresponder a um produto do catálogo, preencher valor."""
        if not texto:
            return
        # 0) Se texto já contém preço estilo " ... | R$ 123,45 " ou "R$ 123,45", extrair
        try:
            if 'R$' in texto:
                parte = texto.split('R$')[-1]
                num = ''.join(ch for ch in parte if ch.isdigit() or ch in ',.')
                if num:
                    num = num.replace('.', '').replace(',', '.')
                    self.input_valor.setText(str(f"{float(num):.2f}"))
        except Exception:
            self.input_valor.setText("")
        # 1) Match direto por display text do catálogo
        if texto in self.produtos_dict:
            p = self.produtos_dict.get(texto, {})
            preco = p.get('preco', 0)
            try:
                preco_float = float(preco)
            except Exception:
                preco_float = 0.0
            self.input_valor.setText(str(f"{preco_float:.2f}"))
            # também normaliza descrição para apenas o nome
            try:
                self.input_desc.setText(str(p.get('nome', texto)))
            except Exception:
                pass
            return
        # 2) Match por nome (case-insensitive)
        try:
            low = texto.strip().lower()
            best = None
            for _, pdata in self.produtos_dict.items():
                nome = pdata.get('nome', '').strip()
                nlow = nome.lower()
                if nlow == low:
                    best = pdata
                    break
                if best is None and nlow.startswith(low):
                    best = pdata
            if best is None:
                for _, pdata in self.produtos_dict.items():
                    if low in pdata.get('nome', '').strip().lower():
                        best = pdata
                        break
            if best:
                preco = best.get('preco', 0)
                try:
                    preco_float = float(preco)
                except Exception:
                    preco_float = 0.0
                self.input_valor.setText(str(f"{preco_float:.2f}"))
                try:
                    cat = best.get('categoria') or 'Todas'
                    idx = self.input_categoria.findText(cat)
                    if idx >= 0:
                        self.input_categoria.setCurrentIndex(idx)
                except Exception:
                    pass
                # normaliza descrição para o nome
                try:
                    self.input_desc.setText(str(best.get('nome', texto)))
                except Exception:
                    pass
        except Exception:
            self.input_valor.setText("")
    
    def _criar_secao_pagamento(self, layout, pedido_data):
        """Cria seção de pagamento"""
        # Se existir parte modular, delega
        if _criar_secao_pagamento_part:
            _criar_secao_pagamento_part(self, layout, pedido_data)
            return
        pagamento_group = QGroupBox("💳 Dados de Pagamento")
        pagamento_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        pagamento_layout = QFormLayout(pagamento_group)

        # Entrada (R$)
        self.campos['entrada'] = QLineEdit()
        self.campos['entrada'].setPlaceholderText("0.00")
        self.campos['entrada'].setMaximumWidth(150)
        pagamento_layout.addRow("Entrada (R$):", self.campos['entrada'])

        # Frete (R$)
        self.campos['frete'] = QLineEdit()
        self.campos['frete'].setPlaceholderText("0.00")
        self.campos['frete'].setMaximumWidth(150)
        pagamento_layout.addRow("Frete (R$):", self.campos['frete'])

        # Desconto (R$)
        self.campos['desconto'] = QLineEdit()
        self.campos['desconto'].setPlaceholderText("0.00")
        self.campos['desconto'].setMaximumWidth(150)
        pagamento_layout.addRow("Desconto (R$):", self.campos['desconto'])

        # Status
        self.campos['status'] = QComboBox()
        self.campos['status'].addItems(["em produção", "enviado", "entregue", "cancelado"])
        pagamento_layout.addRow("Status:", self.campos['status'])

        # Forma de pagamento
        self.campos['forma_pagamento'] = QComboBox()
        self.campos['forma_pagamento'].addItems(["pix", "cartão de crédito", "cartão de débito", "dinheiro", "transferência", "boleto"])
        pagamento_layout.addRow("Forma de Pagamento:", self.campos['forma_pagamento'])

        # Prazo (em dias)
        self.campos['prazo_entrega'] = QLineEdit()
        self.campos['prazo_entrega'].setPlaceholderText("dias (ex: 30)")
        pagamento_layout.addRow("Prazo (dias):", self.campos['prazo_entrega'])

        # (Cor e Reforço movidos para seção de Produtos)

        # Preencher dados se for edição
        if pedido_data:
            # Valores financeiros
            try:
                self.campos['entrada'].setText(f"{float(pedido_data.get('valor_entrada', 0) or 0):.2f}")
            except Exception:
                pass
            try:
                self.campos['frete'].setText(f"{float(pedido_data.get('frete', 0) or 0):.2f}")
            except Exception:
                pass
            try:
                self.campos['desconto'].setText(f"{float(pedido_data.get('desconto', 0) or 0):.2f}")
            except Exception:
                pass
            status = pedido_data.get('status', 'em produção')
            index = self.campos['status'].findText(status)
            if index >= 0:
                self.campos['status'].setCurrentIndex(index)

            forma_pag = pedido_data.get('forma_pagamento', 'pix')
            index = self.campos['forma_pagamento'].findText(forma_pag)
            if index >= 0:
                self.campos['forma_pagamento'].setCurrentIndex(index)

            # Mostrar prazo em dias quando editar
            try:
                self.campos['prazo_entrega'].setText(str(int(pedido_data.get('prazo', 0) or 0)))
            except Exception:
                self.campos['prazo_entrega'].setText("")
            # (cor/reforço já preenchidos na seção Produtos)

        # Sempre que mudar, recalcula total
        try:
            self.campos['entrada'].textChanged.connect(self._recalcular_total)
            self.campos['frete'].textChanged.connect(self._recalcular_total)
            self.campos['desconto'].textChanged.connect(self._recalcular_total)
        except Exception:
            pass

    
    def _criar_secao_resumo(self, layout):
        """Cria seção de resumo financeiro"""
        if _criar_secao_resumo_part:
            _criar_secao_resumo_part(self, layout)
            return
        resumo_group = QGroupBox("💰 Resumo Financeiro")
        resumo_group.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        resumo_layout = QHBoxLayout(resumo_group)
        
        self.label_resumo = QLabel("Valor Total: R$ 0,00")
        self.label_resumo.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.label_resumo.setStyleSheet("color: #00ff88;")
        resumo_layout.addWidget(self.label_resumo)
        
        # Conectar eventos para atualizar resumo
        self.campos['valor_total'].textChanged.connect(self._atualizar_resumo)
        
        layout.addWidget(resumo_group)
    
    def _criar_botoes(self, layout, numero_os, pedido_data):
        """Cria botões do modal"""
        if '_criar_botoes_part' in globals() and _criar_botoes_part:
            _criar_botoes_part(self, layout, numero_os, pedido_data)
            return
        botoes_frame = QFrame()
        botoes_layout = QHBoxLayout(botoes_frame)
        botoes_layout.setContentsMargins(0, 10, 0, 0)

        # Botão Cancelar
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.setMinimumWidth(120)
        btn_cancelar.clicked.connect(self.reject)
        botoes_layout.addWidget(btn_cancelar)

        botoes_layout.addStretch()

        # Botão Salvar
        btn_salvar = QPushButton("💾 Salvar")
        btn_salvar.setMinimumWidth(120)
        btn_salvar.clicked.connect(lambda: self._salvar_pedido(numero_os, pedido_data))
        botoes_layout.addWidget(btn_salvar)

        # Botão Gerar PDF (apenas para edição)
        if pedido_data:
            btn_pdf = QPushButton("📄 Gerar PDF")
            btn_pdf.setMinimumWidth(120)
            btn_pdf.clicked.connect(lambda: self._gerar_pdf(pedido_data))
            botoes_layout.addWidget(btn_pdf)

        layout.addWidget(botoes_frame)
    
    # === Clientes: helpers ===
    def _format_phone(self, telefone: str) -> str:
        if not telefone:
            return ""
        dig = ''.join(filter(str.isdigit, str(telefone)))
        # Formatos simples: 11 dígitos -> (11) 9xxxx-xxxx, 10 -> (xx) xxxx-xxxx
        if len(dig) == 11:
            return f"({dig[:2]}) {dig[2:7]}-{dig[7:]}"
        if len(dig) == 10:
            return f"({dig[:2]}) {dig[2:6]}-{dig[6:]}"
        return telefone

    def _on_cliente_completer_activated(self, texto: str):
        # Após selecionar no autocomplete, preencher CPF/telefone e endereço
        key_cli = self._resolver_cliente(texto)
        if key_cli:
            key, cli = key_cli
            # Ajusta campo do nome para o formato "Nome | (Telefone)"
            try:
                telefone_fmt = self._format_phone(cli.get('telefone', ''))
                display = f"{cli.get('nome','')} | {telefone_fmt}" if telefone_fmt else cli.get('nome','')
                self.campos['nome_cliente'].setText(display)
            except Exception:
                pass
            self._preencher_dados_cliente(cli)

    # === Produtos: UI e lógica ===
    def _refresh_produtos_ui(self):
        # Limpar UI
        while self.lista_produtos_container.count():
            item = self.lista_produtos_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        # Recriar linhas
        for idx, prod in enumerate(self.produtos_list):
            row = QHBoxLayout()
            cor_txt = prod.get('cor') or ''
            reforco_txt = 'sim' if prod.get('reforco') else 'não'
            extras = []
            if cor_txt:
                extras.append(f"Cor: {cor_txt}")
            if 'reforco' in prod:
                extras.append(f"Reforço: {reforco_txt}")
            extras_txt = ("  —  " + "  |  ".join(extras)) if extras else ""
            lbl = QLabel(f"• {prod['descricao']}{extras_txt}")
            lbl.setStyleSheet("color: #cccccc")
            # Formatação brasileira: milhar com ponto, centavos com vírgula
            valor = prod.get('valor', 0.0)
            valor_fmt = f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
            val = QLabel(valor_fmt)
            val.setStyleSheet("color: #00ff88; font-weight: bold;")
            btn_rem = QPushButton("Remover")
            btn_rem.setMaximumWidth(90)
            btn_rem.clicked.connect(lambda _, i=idx: self._remove_produto(i))
            row.addWidget(lbl, stretch=1)
            row.addWidget(val)
            row.addWidget(btn_rem)
            row_w = QWidget()
            row_w.setLayout(row)
            row_w.setStyleSheet("QWidget { background: #3a3a3a; border: 1px solid #505050; border-radius: 6px; padding: 6px; }")
            self.lista_produtos_container.addWidget(row_w)
        self.lista_produtos_container.addStretch()
        self._recalcular_total()

    def _add_produto(self):
        desc = (self.input_desc.text() or '').strip()
        val_text_raw = (self.input_valor.text() or '').strip()
        # Se descrição vier no formato "Nome | R$ 123,45", separa o nome e extrai preço se necessário
        if '|' in desc and 'R$' in desc:
            try:
                nome_parte, resto = desc.split('|', 1)
                desc = nome_parte.strip()
                if not val_text_raw:
                    parte = resto.split('R$')[-1]
                    num = ''.join(ch for ch in parte if ch.isdigit() or ch in ',.')
                    if num:
                        val_text_raw = num
            except Exception:
                pass
        # Se descrição igual a display do catálogo, normaliza e pega preço
        if desc in self.produtos_dict:
            try:
                p = self.produtos_dict[desc]
                if not val_text_raw:
                    val_text_raw = f"{float(p.get('preco', 0)):.2f}"
                desc = p.get('nome', desc)
            except Exception:
                pass
        # Normalizar número
        # Corrige: não remover ponto decimal, só vírgula vira ponto
        val_text = val_text_raw.replace('R$', '').replace(' ', '').replace(',', '.')
        # Se descrição coincide com um item do catálogo (por nome), e não há valor, usar preço do catálogo
        if (not val_text) and self.produtos_dict:
            # procurar por nome exato entre valores do dict
            try:
                for display, pdata in self.produtos_dict.items():
                    if pdata.get('nome', '').lower() == desc.lower():
                        val_text = str(pdata.get('preco', 0.0))
                        break
            except Exception:
                pass
        if not desc:
            return
        try:
            valor = float(val_text) if val_text else 0.0
        except Exception:
            valor = 0.0
    # Capturar cor/reforço atuais (por item)
    try:
        cor_sel = (self.campos.get('cor').currentText() if 'cor' in self.campos else '').strip()
    except Exception:
        cor_sel = ''
    try:
        reforco_widget = self.campos.get('reforco')
        if reforco_widget is None:
            reforco_sel = False
        elif hasattr(reforco_widget, 'isChecked'):
            reforco_sel = bool(reforco_widget.isChecked())
        else:
            reforco_sel = (reforco_widget.currentText() if hasattr(reforco_widget, 'currentText') else '').strip().lower() == 'sim'
    except Exception:
        reforco_sel = False
    # Aplicar acréscimo de R$15,00 se reforço
    try:
        if reforco_sel:
            valor += 15.0
    except Exception:
        pass
    self.produtos_list.append({"descricao": desc, "valor": valor, "cor": cor_sel, "reforco": reforco_sel})
    self.input_desc.clear()
    self.input_valor.clear()
    self._refresh_produtos_ui()

    def _limpar_campos_cliente(self):
        """Limpa os campos do cliente e foca no nome."""
        try:
            self.campos['nome_cliente'].clear()
        except Exception:
            pass
        try:
            self.campos['telefone_cliente'].clear()
        except Exception:
            pass
        try:
            self.campos['cpf_cliente'].clear()
        except Exception:
            pass
        try:
            self.campos['endereco_cliente'].clear()
        except Exception:
            pass
        try:
            self.campos['nome_cliente'].setFocus()
        except Exception:
            pass

    def _remove_produto(self, index: int):
        if 0 <= index < len(self.produtos_list):
            self.produtos_list.pop(index)
            self._refresh_produtos_ui()

    def _recalcular_total(self):
        if _recalcular_total_part:
            _recalcular_total_part(self)
            return
        total_produtos = sum([p.get('valor', 0.0) for p in self.produtos_list])
        def _f(txt):
            try:
                return float((txt or '').replace(',', '.'))
            except Exception:
                return 0.0
        def safe_text(campo):
            try:
                if campo is not None and hasattr(campo, 'text'):
                    return campo.text()
            except Exception:
                pass
            return ''
        frete = _f(safe_text(self.campos.get('frete'))) if 'frete' in self.campos else 0.0
        desconto = _f(safe_text(self.campos.get('desconto'))) if 'desconto' in self.campos else 0.0
        total = total_produtos + frete - desconto
        if total < 0:
            total = 0.0
        self.campos['valor_total'].setText(str(f"{total:.2f}"))
        try:
            self.label_resumo.setText(str(f"Valor Total: R$ {total:.2f}"))
        except Exception:
            pass

    def _on_cliente_selecionado(self, texto):
        """Callback quando cliente é selecionado no autocomplete ou ao finalizar edição."""
        key_cli = self._resolver_cliente(texto)
        if not key_cli:
            return
        key, cliente = key_cli
        # Padroniza exibição do campo
        try:
            telefone_fmt = self._format_phone(cliente.get('telefone', ''))
            display = f"{cliente.get('nome','')} | {telefone_fmt}" if telefone_fmt else cliente.get('nome','')
            self.campos['nome_cliente'].setText(str(display))
        except Exception:
            pass
        self._preencher_dados_cliente(cliente)

    def _preencher_dados_cliente(self, cli: dict):
        """Preenche telefone, CPF e endereço com base no dict do cliente."""
        try:
            self.campos['telefone_cliente'].setText(str(cli.get('telefone', '')))
        except Exception:
            pass
        try:
            self.campos['cpf_cliente'].setText(str(cli.get('cpf', '')))
        except Exception:
            pass
        try:
            rua = cli.get('rua', '')
            numero = cli.get('numero', '')
            endereco = f"{rua}, {numero}" if rua and numero else (rua or numero or '')
            self.campos['endereco_cliente'].setText(str(endereco))
        except Exception:
            pass

    def _resolver_cliente(self, texto: str):
        """Tenta resolver o cliente a partir do texto digitado (nome, telefone, ou chave exata)."""
        if not texto:
            return None
        # Match exato da chave
        if texto in self.clientes_dict:
            cli = self.clientes_dict[texto]
            return (texto, cli)
        low = texto.strip().lower()
        # Se contiver só o nome (antes de "|")
        nome_parte = low.split('|')[0].strip()
        # Telefone (apenas dígitos)
        digitos = ''.join(ch for ch in texto if ch.isdigit())
        candidatos = []
        for k, v in self.clientes_dict.items():
            k_low = k.lower()
            if k_low == low:
                return (k, v)
            # por nome
            nome_cli = (v.get('nome') or '').lower()
            if nome_parte and (nome_cli == nome_parte or nome_cli.startswith(nome_parte)):
                candidatos.append((k, v))
                continue
            # por telefone
            if digitos and ''.join(ch for ch in str(v.get('telefone','')) if ch.isdigit()).endswith(digitos):
                candidatos.append((k, v))
        if len(candidatos) == 1:
            return candidatos[0]
        # tentar contains por nome
        if not candidatos and nome_parte:
            for k, v in self.clientes_dict.items():
                if nome_parte in (v.get('nome') or '').lower():
                    candidatos.append((k, v))
        if len(candidatos) == 1:
            return candidatos[0]
        return None
    
    def _add_produto(self):
        desc = (self.input_desc.text() or '').strip()
        val_text_raw = (self.input_valor.text() or '').strip()
        # Se descrição vier no formato "Nome | R$ 123,45", separa o nome e extrai preço se necessário
        if '|' in desc and 'R$' in desc:
            try:
                nome_parte, resto = desc.split('|', 1)
                desc = nome_parte.strip()
                if not val_text_raw:
                    parte = resto.split('R$')[-1]
                    num = ''.join(ch for ch in parte if ch.isdigit() or ch in ',.')
                    if num:
                        val_text_raw = num
            except Exception:
                pass
        # Se descrição igual a display do catálogo, normaliza e pega preço
        if desc in self.produtos_dict:
            try:
                p = self.produtos_dict[desc]
                if not val_text_raw:
                    val_text_raw = f"{float(p.get('preco', 0)):.2f}"
                desc = p.get('nome', desc)
            except Exception:
                pass
        # Normalizar número
        # Corrige: não remover ponto decimal, só vírgula vira ponto
        val_text = val_text_raw.replace('R$', '').replace(' ', '').replace(',', '.')
        # Se descrição coincide com um item do catálogo (por nome), e não há valor, usar preço do catálogo
        if (not val_text) and self.produtos_dict:
            # procurar por nome exato entre valores do dict
            try:
                for display, pdata in self.produtos_dict.items():
                    if pdata.get('nome', '').lower() == desc.lower():
                        val_text = str(pdata.get('preco', 0.0))
                        break
            except Exception:
                pass
        if not desc:
            return
        try:
            valor = float(val_text) if val_text else 0.0
        except Exception:
            valor = 0.0
        # Capturar cor/reforço atuais (por item)
        try:
            cor_sel = (self.campos.get('cor').currentText() if 'cor' in self.campos else '').strip()
        except Exception:
            cor_sel = ''
        try:
            reforco_sel = (self.campos.get('reforco').currentText() if 'reforco' in self.campos else '').strip().lower() == 'sim'
        except Exception:
            reforco_sel = False
    self.produtos_list.append({"descricao": desc, "valor": valor, "cor": cor_sel, "reforco": reforco_sel})
    self.input_desc.clear()
    self.input_valor.clear()
    self._refresh_produtos_ui()
    
    def _gerar_pdf(self, pedido_data):
        """Gera PDF da ordem de serviço"""
        try:
            pdf_generator = OrdemServicoPDF()
            pdf_path = pdf_generator.gerar_pdf(pedido_data)
            QMessageBox.information(self, "PDF Gerado", f"PDF salvo em: {pdf_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {e}")
    
    def _aplicar_estilo(self):
        """Aplica estilo moderno ao modal"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            /* Garante que todos os widgets filhos mantenham o fundo escuro */
            QDialog QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            /* Viewport do scroll escura (evita fundo branco) */
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: #2d2d2d; }
            QFrame { background: transparent; }
            
            QGroupBox {
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #353535;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #ffffff;
                background-color: #353535;
            }
            
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            
            QLineEdit, QTextEdit {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #0d7377;
            }
            
            QComboBox {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            
            QComboBox::drop-down {
                border: none;
                background-color: #505050;
            }
            
            QComboBox QAbstractItemView {
                background-color: #404040;
                color: #ffffff;
                border: 1px solid #606060;
                selection-background-color: #0d7377;
            }
            
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: 500;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #0a5d61;
            }
            
            QPushButton:pressed {
                background-color: #084a4d;
            }
            
            QScrollBar:vertical {
                background-color: #404040;
                width: 14px;
                border-radius: 7px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 7px;
                min-height: 30px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #707070;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #808080;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
