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
        print(f"=== INIT PedidoResumoDialog: ID={pedido_id}, parent={type(parent)} ===")
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
        
        print("Chamando _setup_ui...")
        self._setup_ui()
        print("Chamando _carregar_dados...")
        self._carregar_dados()
        print("=== INIT PedidoResumoDialog CONCLUÍDO ===")
    
    
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
            print(f"=== DEBUG INICIO: Carregando pedido ID: {self.pedido_id} ===")
            pedido = db_manager.get_pedido_por_id(self.pedido_id)
            if not pedido:
                print("ERRO: Pedido retornou None")
                QMessageBox.warning(self, "Erro", "Pedido não encontrado!")
                self.close()
                return
            
            print(f"Pedido encontrado: {type(pedido)}")
            print(f"Chaves do pedido: {list(pedido.keys()) if isinstance(pedido, dict) else 'NÃO É DICT'}")
            print(f"Cliente nome: {pedido.get('cliente_nome', 'CHAVE AUSENTE')}")
            
            # Buscar produtos do pedido
            print(f"Buscando produtos para pedido {self.pedido_id}...")
            produtos = db_manager.get_produtos_do_pedido(self.pedido_id)
            print(f"Produtos retornados: {type(produtos)}, tamanho: {len(produtos) if produtos else 'None/Vazio'}")
            
            if produtos:
                for i, prod in enumerate(produtos):
                    print(f"  Produto[{i}]: {type(prod)} = {prod}")
            
            print("Chamando _mostrar_dados_pedido...")
            self._mostrar_dados_pedido(pedido, produtos)
            print("=== DEBUG FIM: Sucesso ===")
            
        except Exception as e:
            print(f"=== DEBUG ERRO: {e} ===")
            import traceback
            print("Stack trace completo:")
            traceback.print_exc()
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados do pedido: {e}")
            self.close()
    
    def _mostrar_dados_pedido(self, pedido, produtos):
        """Mostra os dados do pedido na interface"""
        print(f"=== _mostrar_dados_pedido INICIO ===")
        print(f"Pedido recebido: {type(pedido)} com chaves: {list(pedido.keys()) if isinstance(pedido, dict) else 'NÃO É DICT'}")
        print(f"Produtos recebidos: {type(produtos)} com {len(produtos) if produtos else 0} itens")
        
        try:
            # Seção de informações gerais
            print("Criando seção de informações gerais...")
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
            
            # Cliente
            if pedido.get('cliente_nome'):
                label_cliente = QLabel(f"• Cliente: {pedido['cliente_nome']}")
                layout_geral.addWidget(label_cliente)
            
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
                    print(f"Erro ao calcular data do prazo: {e}")
                    # Fallback para formato original
                    label_prazo = QLabel(f"• Prazo: {pedido['prazo']} dias")
                
                layout_geral.addWidget(label_prazo)
            
            self.content_layout.addWidget(frame_geral)
            print("Seção geral criada com sucesso")
            
            # Seção de produtos
            print("Criando seção de produtos...")
            frame_produtos = QFrame()
            layout_produtos = QVBoxLayout(frame_produtos)
            
            titulo_produtos = QLabel("🛍️ Produtos")
            titulo_produtos.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            titulo_produtos.setStyleSheet("color: #ffffff; font-size: 16px; margin-bottom: 10px;")
            layout_produtos.addWidget(titulo_produtos)
            
            print(f"Processando {len(produtos) if produtos else 0} produtos...")
            
            if produtos:
                for i, produto in enumerate(produtos):
                    try:
                        # Debug: verificar estrutura do produto
                        print(f"=== Produto {i} ===")
                        print(f"  Tipo: {type(produto)}")
                        print(f"  Valor: {produto}")
                        if isinstance(produto, dict):
                            print(f"  Chaves: {list(produto.keys())}")
                        
                        nome = produto.get('nome', 'Produto sem nome')
                        quantidade = produto.get('quantidade', 1)
                        valor_unitario = produto.get('valor_unitario', 0.0)
                        valor_total = quantidade * valor_unitario
                        
                        print(f"  Nome extraído: '{nome}'")
                        print(f"  Quantidade: {quantidade}")
                        print(f"  Valor unitário: {valor_unitario}")
                        
                        produto_text = f"• {nome} (Qtd: {quantidade}) - R$ {valor_unitario:.2f} = R$ {valor_total:.2f}"
                        label_produto = QLabel(produto_text)
                        layout_produtos.addWidget(label_produto)
                        print(f"  Label criado: {produto_text}")
                    except Exception as e:
                        print(f"=== ERRO no produto {i}: {e} ===")
                        import traceback
                        traceback.print_exc()
                        # Adicionar linha de erro para o usuário ver
                        label_erro = QLabel(f"• Erro ao carregar produto {i+1}")
                        layout_produtos.addWidget(label_erro)
            else:
                label_sem_produtos = QLabel("• Nenhum produto cadastrado")
                layout_produtos.addWidget(label_sem_produtos)
                print("Nenhum produto encontrado")
            
            self.content_layout.addWidget(frame_produtos)
            print("Seção de produtos criada com sucesso")
            
            # Seção financeira
            print("Criando seção financeira...")
            frame_financeiro = QFrame()
            layout_financeiro = QVBoxLayout(frame_financeiro)
            
            titulo_financeiro = QLabel("💰 Informações Financeiras")
            titulo_financeiro.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            titulo_financeiro.setStyleSheet("color: #ffffff; font-size: 16px; margin-bottom: 10px;")
            layout_financeiro.addWidget(titulo_financeiro)
            
            # Valor base (produto)
            valor_produto = float(pedido.get('valor_total', 0.0))
            print(f"DEBUG CÁLCULO - Valor produto: {valor_produto}")
            label_produto = QLabel(f"• Valor do Produto: R$ {valor_produto:.2f}")
            layout_financeiro.addWidget(label_produto)
            
            # Frete
            frete = float(pedido.get('frete', 0.0))
            print(f"DEBUG CÁLCULO - Frete: {frete}")
            label_frete = QLabel(f"• Frete: R$ {frete:.2f}")
            layout_financeiro.addWidget(label_frete)
            
            # Desconto
            desconto = float(pedido.get('desconto', 0.0))
            print(f"DEBUG CÁLCULO - Desconto: {desconto}")
            label_desconto = QLabel(f"• Desconto: R$ {desconto:.2f}")
            layout_financeiro.addWidget(label_desconto)
            
            # Valor total final (produto + frete - desconto)
            valor_total_final = round(valor_produto + frete - desconto, 2)
            print(f"DEBUG CÁLCULO - Total final: {valor_produto} + {frete} - {desconto} = {valor_total_final}")
            label_total = QLabel(f"• Valor Total Final: R$ {valor_total_final:.2f}")
            label_total.setStyleSheet("font-weight: bold; font-size: 16px; color: #90EE90;")
            layout_financeiro.addWidget(label_total)
            
            # Entrada paga (sempre mostrar)
            entrada = float(pedido.get('entrada', 0.0))
            print(f"DEBUG CÁLCULO - Entrada: {entrada}")
            label_entrada = QLabel(f"• Entrada Paga: R$ {entrada:.2f}")
            layout_financeiro.addWidget(label_entrada)
            
            # Método de pagamento
            metodo_pagamento = pedido.get('metodo_pagamento')
            if metodo_pagamento:
                label_metodo = QLabel(f"• Método de Pagamento: {metodo_pagamento}")
                layout_financeiro.addWidget(label_metodo)
            
            # Valor restante (baseado no valor total final)
            valor_restante = round(valor_total_final - entrada, 2)
            print(f"DEBUG CÁLCULO - Valor restante: {valor_total_final} - {entrada} = {valor_restante}")
            label_restante = QLabel(f"• Valor Restante: R$ {valor_restante:.2f}")
            if valor_restante > 0:
                label_restante.setStyleSheet("font-weight: bold; color: #ffcccc;")
            else:
                label_restante.setStyleSheet("font-weight: bold; color: #90EE90;")
            layout_financeiro.addWidget(label_restante)
            
            self.content_layout.addWidget(frame_financeiro)
            print("Seção financeira criada com sucesso")
            
            # Seção de observações
            observacoes = pedido.get('observacoes')
            if observacoes:
                print("Criando seção de observações...")
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
                print("Seção de observações criada com sucesso")
            
            print("=== _mostrar_dados_pedido FIM ===")
            
        except Exception as e:
            print(f"=== ERRO GERAL em _mostrar_dados_pedido: {e} ===")
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