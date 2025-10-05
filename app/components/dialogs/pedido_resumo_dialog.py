"""
Dialog para mostrar resumo de um pedido ao fazer duplo clique
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFrame, QScrollArea, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database import db_manager


class PedidoResumoDialog(QDialog):
    """Dialog que mostra resumo completo de um pedido"""
    
    def __init__(self, pedido_id, parent=None):
        super().__init__(parent)
        self.pedido_id = pedido_id
        self.setWindowTitle("Resumo do Pedido")
        self.setModal(True)
        self.resize(650, 500)
        
        # Estilo dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2d;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QFrame {
                background-color: #3a3a3a;
                border: 1px solid #cccccc;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton {
                background-color: #cccccc;
                color: #2b2b2d;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #999999;
            }
            QScrollArea {
                border: none;
                background-color: #2b2b2d;
            }
        """)
        
        self._setup_ui()
        self._carregar_dados()
    
    
    def _setup_ui(self):
        """Configura a interface do dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel(f"Resumo do Pedido #{self.pedido_id}")
        titulo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #ffffff; font-size: 18px; margin-bottom: 10px;")
        layout.addWidget(titulo)
        
        # Área com scroll para o conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Widget principal do conteúdo
        content_widget = QFrame()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setSpacing(15)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Botões
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_editar = QPushButton("Editar Pedido")
        btn_editar.clicked.connect(self._editar_pedido)
        btn_layout.addWidget(btn_editar)
        
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.close)
        btn_layout.addWidget(btn_fechar)
        
        layout.addLayout(btn_layout)
    
    def _carregar_dados(self):
        """Carrega os dados do pedido do banco"""
        try:
            # Buscar dados do pedido
            pedido = db_manager.get_pedido_por_id(self.pedido_id)
            if not pedido:
                QMessageBox.warning(self, "Erro", "Pedido não encontrado!")
                self.close()
                return
            
            # Buscar produtos do pedido
            produtos = db_manager.get_produtos_do_pedido(self.pedido_id)
            
            self._mostrar_dados_pedido(pedido, produtos)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados do pedido: {e}")
            self.close()
    
    def _mostrar_dados_pedido(self, pedido, produtos):
        """Mostra os dados do pedido na interface"""
        
        try:
            # Seção de informações gerais
            frame_geral = QFrame()
            layout_geral = QVBoxLayout(frame_geral)
            
            titulo_geral = QLabel("📋 Informações Gerais")
            titulo_geral.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            titulo_geral.setStyleSheet("color: #ffffff; font-size: 16px; margin-bottom: 10px;")
            layout_geral.addWidget(titulo_geral)
            
            # Número da OS
            if pedido.get('numero_os'):
                label_os = QLabel(f"• Número da OS: {pedido['numero_os']}")
                layout_geral.addWidget(label_os)
            
            # Cliente e informações completas
            if pedido.get('cliente_nome'):
                label_cliente = QLabel(f"• Cliente: {pedido['cliente_nome']}")
                layout_geral.addWidget(label_cliente)
                
                # Buscar dados completos do cliente se houver CPF/CNPJ
                cliente_completo = None
                if pedido.get('cpf_cliente'):
                    from database.core.db_manager import DatabaseManager
                    db = DatabaseManager()
                    
                    # Normalizar documento (remover pontuação)
                    documento_norm = ''.join(ch for ch in str(pedido['cpf_cliente']) if ch.isdigit())
                    
                    # Buscar por CPF ou CNPJ
                    if documento_norm:
                        # Tentar buscar por CPF primeiro
                        cliente_completo = db.buscar_cliente_por_cpf(documento_norm)
                        
                        # Se não encontrou, tentar buscar por CNPJ
                        if not cliente_completo:
                            try:
                                db.cursor.execute(
                                    """SELECT id, nome, cpf, cnpj, inscricao_estadual, telefone, email, 
                                       cep, rua, numero, bairro, cidade, estado, referencia
                                       FROM clientes 
                                       WHERE replace(replace(replace(replace(cnpj, '.', ''), '/', ''), '-', ''), ' ', '') = ?
                                       LIMIT 1""",
                                    (documento_norm,)
                                )
                                row = db.cursor.fetchone()
                                if row:
                                    cliente_completo = {
                                        'id': row[0], 'nome': row[1], 'cpf': row[2], 'cnpj': row[3],
                                        'inscricao_estadual': row[4], 'telefone': row[5], 'email': row[6],
                                        'cep': row[7], 'rua': row[8], 'numero': row[9], 'bairro': row[10],
                                        'cidade': row[11], 'estado': row[12], 'referencia': row[13]
                                    }
                            except Exception as e:
                                print(f"Erro ao buscar cliente por CNPJ: {e}")
                    
                    if cliente_completo:
                        # Determinar se é CPF ou CNPJ
                        tem_cpf = cliente_completo.get('cpf') and str(cliente_completo.get('cpf')).strip() not in ['', 'None']
                        tem_cnpj = cliente_completo.get('cnpj') and str(cliente_completo.get('cnpj')).strip() not in ['', 'None']
                        
                        # Mostrar CPF se tiver
                        if tem_cpf:
                            label_cpf = QLabel(f"  - CPF: {cliente_completo['cpf']}")
                            layout_geral.addWidget(label_cpf)
                        
                        # Mostrar CNPJ e Inscrição Estadual se tiver
                        if tem_cnpj:
                            label_cnpj = QLabel(f"  - CNPJ: {cliente_completo['cnpj']}")
                            layout_geral.addWidget(label_cnpj)
                            
                            # Inscrição Estadual (só mostrar se tiver CNPJ)
                            if cliente_completo.get('inscricao_estadual'):
                                label_ie = QLabel(f"  - Inscrição Estadual: {cliente_completo['inscricao_estadual']}")
                                layout_geral.addWidget(label_ie)
                        
                        # Telefone
                        if cliente_completo.get('telefone'):
                            label_tel = QLabel(f"  - Telefone: {cliente_completo['telefone']}")
                            layout_geral.addWidget(label_tel)
                        
                        # Endereço completo
                        endereco_partes = []
                        if cliente_completo.get('rua'):
                            endereco_partes.append(cliente_completo['rua'])
                        if cliente_completo.get('numero'):
                            endereco_partes.append(f"nº {cliente_completo['numero']}")
                        if cliente_completo.get('bairro'):
                            endereco_partes.append(cliente_completo['bairro'])
                        if cliente_completo.get('cidade'):
                            endereco_partes.append(cliente_completo['cidade'])
                        if cliente_completo.get('estado'):
                            endereco_partes.append(cliente_completo['estado'])
                        if cliente_completo.get('cep'):
                            endereco_partes.append(f"CEP: {cliente_completo['cep']}")
                        
                        if endereco_partes:
                            endereco_completo = ', '.join(endereco_partes)
                            label_endereco = QLabel(f"  - Endereço: {endereco_completo}")
                            label_endereco.setWordWrap(True)
                            layout_geral.addWidget(label_endereco)
                        
                        # Email (opcional)
                        if cliente_completo.get('email'):
                            label_email = QLabel(f"  - Email: {cliente_completo['email']}")
                            layout_geral.addWidget(label_email)
                        
                        # Referência (opcional)
                        if cliente_completo.get('referencia'):
                            label_ref = QLabel(f"  - Referência: {cliente_completo['referencia']}")
                            layout_geral.addWidget(label_ref)
                    else:
                        # Se não encontrou o cliente completo, mostrar dados básicos do pedido
                        if pedido.get('cpf_cliente'):
                            label_cpf_basico = QLabel(f"  - CPF/CNPJ: {pedido['cpf_cliente']}")
                            layout_geral.addWidget(label_cpf_basico)
                        
                        if pedido.get('telefone_cliente'):
                            label_tel_basico = QLabel(f"  - Telefone: {pedido['telefone_cliente']}")
                            layout_geral.addWidget(label_tel_basico)
                else:
                    # Se não há CPF/CNPJ, mostrar apenas telefone do pedido se disponível
                    if pedido.get('telefone_cliente'):
                        label_tel_basico = QLabel(f"  - Telefone: {pedido['telefone_cliente']}")
                        layout_geral.addWidget(label_tel_basico)
            
            # Status
            if pedido.get('status'):
                label_status = QLabel(f"• Status: {pedido['status']}")
                layout_geral.addWidget(label_status)
            
            # Prazo
            if pedido.get('prazo'):
                # Calcular data final baseada na data de criação + prazo em dias
                try:
                    from datetime import datetime, timedelta
                    
                    # Converter data_criacao string para datetime
                    data_criacao_str = pedido.get('data_criacao', '')
                    if data_criacao_str:
                        # Assumindo formato YYYY-MM-DD HH:MM:SS ou YYYY-MM-DD
                        if ' ' in data_criacao_str:
                            data_criacao = datetime.strptime(data_criacao_str.split(' ')[0], '%Y-%m-%d')
                        else:
                            data_criacao = datetime.strptime(data_criacao_str, '%Y-%m-%d')
                        
                        # Calcular data final
                        prazo_dias = int(pedido['prazo'])
                        data_final = data_criacao + timedelta(days=prazo_dias)
                        data_final_str = data_final.strftime('%d/%m/%y')
                        
                        label_prazo = QLabel(f"• Prazo: {data_final_str} ({pedido['prazo']} dias)")
                    else:
                        # Fallback se não houver data_criacao
                        label_prazo = QLabel(f"• Prazo: {pedido['prazo']} dias")
                        
                except (ValueError, TypeError) as e:
                    # Fallback para formato original
                    label_prazo = QLabel(f"• Prazo: {pedido['prazo']} dias")
                
                layout_geral.addWidget(label_prazo)
            
            self.content_layout.addWidget(frame_geral)
            
            # Seção de produtos
            frame_produtos = QFrame()
            layout_produtos = QVBoxLayout(frame_produtos)
            
            titulo_produtos = QLabel("🛍️ Produtos")
            titulo_produtos.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            titulo_produtos.setStyleSheet("color: #ffffff; font-size: 16px; margin-bottom: 10px;")
            layout_produtos.addWidget(titulo_produtos)
            
            
            if produtos:
                for i, produto in enumerate(produtos):
                    try:
                        # Debug: verificar estrutura do produto
                        if isinstance(produto, dict):
                            nome = produto.get('nome', 'Produto sem nome')
                            codigo = produto.get('codigo', 'S/Código')
                            quantidade = produto.get('quantidade', 1)
                            valor_unitario = produto.get('valor_unitario', 0.0)
                            valor_total = quantidade * valor_unitario
                            
                            # Processar informações de cor com debug
                            cor_info = ""
                            print(f"Processando cores do produto {nome}:")
                            print(f"  - cor_data: {produto.get('cor_data')}")
                            print(f"  - cor: {produto.get('cor')}")
                            
                            if 'cor_data' in produto and produto['cor_data']:
                                cor_data = produto['cor_data']
                                if cor_data.get('tipo') == 'separadas':
                                    tampa = cor_data.get('tampa', '')
                                    corpo = cor_data.get('corpo', '')
                                    if tampa or corpo:
                                        cor_info = f" — Tampa: {tampa}, Corpo: {corpo}"
                                elif cor_data.get('tipo') == 'unica':
                                    cor_unica = cor_data.get('cor', '')
                                    if cor_unica:
                                        cor_info = f" — Cor: {cor_unica}"
                            elif 'cor' in produto and produto['cor']:
                                cor_antiga = produto['cor']
                                cor_info = f" — Cor: {cor_antiga}"
                            
                            print(f"  - cor_info final: '{cor_info}'")
                            
                            # Primeira linha: informações do produto
                            produto_text = f"• {nome} (Código: {codigo}) - Qtd: {quantidade} - R$ {valor_total:.2f}"
                            label_produto = QLabel(produto_text)
                            label_produto.setStyleSheet("color: #ffffff; font-size: 14px; margin-bottom: 2px;")
                            layout_produtos.addWidget(label_produto)
                            
                            # Segunda linha: informações de cor (apenas se houver cores)
                            if cor_info:
                                cor_text = f"  {cor_info.lstrip(' — ')}"  # Remove o "—" inicial e adiciona indentação
                                label_cor = QLabel(cor_text)
                                label_cor.setStyleSheet("color: #cccccc; font-size: 12px; margin-left: 20px; margin-bottom: 5px; font-style: italic;")
                                layout_produtos.addWidget(label_cor)
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        # Adicionar linha de erro para o usuário ver
                        label_erro = QLabel(f"• Erro ao carregar produto {i+1}")
                        layout_produtos.addWidget(label_erro)
            else:
                label_sem_produtos = QLabel("• Nenhum produto cadastrado")
                layout_produtos.addWidget(label_sem_produtos)
            
            self.content_layout.addWidget(frame_produtos)
            
            # Seção financeira
            frame_financeiro = QFrame()
            layout_financeiro = QVBoxLayout(frame_financeiro)
            
            titulo_financeiro = QLabel("💰 Informações Financeiras")
            titulo_financeiro.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            titulo_financeiro.setStyleSheet("color: #ffffff; font-size: 16px; margin-bottom: 10px;")
            layout_financeiro.addWidget(titulo_financeiro)
            
            # Valor base (produto)
            valor_produto = float(pedido.get('valor_total', 0.0))
            label_produto = QLabel(f"• Valor do Produto: R$ {valor_produto:.2f}")
            layout_financeiro.addWidget(label_produto)
            
            # Frete
            frete = float(pedido.get('frete', 0.0))
            label_frete = QLabel(f"• Frete: R$ {frete:.2f}")
            layout_financeiro.addWidget(label_frete)
            
            # Desconto
            desconto = float(pedido.get('desconto', 0.0))
            label_desconto = QLabel(f"• Desconto: R$ {desconto:.2f}")
            layout_financeiro.addWidget(label_desconto)
            
            # Valor total final (produto + frete - desconto)
            valor_total_final = round(valor_produto + frete - desconto, 2)
            label_total = QLabel(f"• Valor Total Final: R$ {valor_total_final:.2f}")
            label_total.setStyleSheet("font-weight: bold; font-size: 16px; color: #90EE90;")
            layout_financeiro.addWidget(label_total)
            
            # Entrada paga (sempre mostrar)
            entrada = float(pedido.get('entrada', 0.0))
            label_entrada = QLabel(f"• Entrada Paga: R$ {entrada:.2f}")
            layout_financeiro.addWidget(label_entrada)
            
            # Método de pagamento
            metodo_pagamento = pedido.get('metodo_pagamento')
            if metodo_pagamento:
                label_metodo = QLabel(f"• Método de Pagamento: {metodo_pagamento}")
                layout_financeiro.addWidget(label_metodo)
            
            # Valor restante (baseado no valor total final)
            valor_restante = round(valor_total_final - entrada, 2)
            label_restante = QLabel(f"• Valor Restante: R$ {valor_restante:.2f}")
            if valor_restante > 0:
                label_restante.setStyleSheet("font-weight: bold; color: #ffcccc;")
            else:
                label_restante.setStyleSheet("font-weight: bold; color: #90EE90;")
            layout_financeiro.addWidget(label_restante)
            
            self.content_layout.addWidget(frame_financeiro)
            
            # Seção de observações
            observacoes = pedido.get('observacoes')
            if observacoes:
                frame_obs = QFrame()
                layout_obs = QVBoxLayout(frame_obs)
                
                titulo_obs = QLabel("📝 Observações")
                titulo_obs.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                titulo_obs.setStyleSheet("color: #ffffff; font-size: 16px; margin-bottom: 10px;")
                layout_obs.addWidget(titulo_obs)
                
                label_obs = QLabel(observacoes)
                label_obs.setWordWrap(True)
                layout_obs.addWidget(label_obs)
                
                self.content_layout.addWidget(frame_obs)
            
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e
    
    def _editar_pedido(self):
        """Abre o modal de edição do pedido"""
        try:
            from app.components.pedidos.novo_pedidos_modal import NovoPedidosModal
            modal = NovoPedidosModal(self.parent())
            modal.abrir_modal_edicao(self.pedido_id)
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir editor: {e}")