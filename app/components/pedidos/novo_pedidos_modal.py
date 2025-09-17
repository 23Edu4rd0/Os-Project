"""
Modal de Pedidos Simplificado
Design moderno em tons de cinza, sem camadas desnecessárias
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QComboBox, QGroupBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QWidget, QMessageBox, QCompleter, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt6.QtGui import QFont

from database import db_manager
from app.numero_os import Contador


class NovoPedidosModal(QDialog):
    pedido_salvo = pyqtSignal()
    
    def __init__(self, parent=None, dados_cliente=None, pedido_id=None):
        super().__init__(parent)
        self.produtos_dict = {}
        self.produtos_list = []
        self.cliente_selecionado = None
        self.dados_cliente_inicial = dados_cliente
        self.pedido_id = pedido_id
        
        if pedido_id:
            self.setWindowTitle(f"Editar Ordem de Serviço Nº {pedido_id:05d}")
        else:
            self.setWindowTitle("Nova Ordem de Serviço")
        self.setFixedSize(900, 700)
        self.setModal(True)
        
        # Carregar dados
        self._carregar_produtos()
        self._carregar_clientes()
        
        # Criar interface
        self._criar_interface()
        self._aplicar_estilo()
        
        # Preencher dados se fornecidos
        if dados_cliente:
            self._preencher_dados_cliente(dados_cliente)
        
    def _carregar_produtos(self):
        """Carrega produtos do banco de dados"""
        try:
            rows = db_manager.listar_produtos()
            self.produtos_dict = {}
            
            for row in rows:
                # (id, nome, codigo, preco, descricao, categoria, criado_em)
                nome = (row[1] or '').strip()
                codigo = (row[2] or '').strip()
                preco = float(row[3]) if row[3] is not None else 0.0
                categoria = (row[5] or '').strip()
                
                if nome:
                    produto_data = {
                        "id": row[0],
                        "nome": nome,
                        "codigo": codigo,
                        "preco": preco,
                        "categoria": categoria
                    }
                    # Indexar por nome
                    self.produtos_dict[nome] = produto_data
                    # Indexar por nome lowercase
                    self.produtos_dict[nome.lower()] = produto_data
                    
        except Exception as e:
            print(f"Erro ao carregar produtos: {e}")
            self.produtos_dict = {}
    
    def _carregar_clientes(self):
        """Carrega clientes do banco de dados"""
        try:
            rows = db_manager.listar_clientes()
            self.clientes_dict = {}
            clientes_lista = []
            
            for row in rows:
                nome = (row[1] or '').strip()
                if nome:
                    cliente_data = {
                        "id": row[0],
                        "nome": nome,
                        "cnpj": row[2] or '',
                        "telefone": row[3] or '',
                        "endereco": row[4] or ''
                    }
                    self.clientes_dict[nome] = cliente_data
                    clientes_lista.append(nome)
            
            # Configurar completer para cliente
            if hasattr(self, 'input_cliente'):
                completer = QCompleter(clientes_lista)
                completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
                self.input_cliente.setCompleter(completer)
                
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            self.clientes_dict = {}
    
    def _criar_interface(self):
        """Cria a interface do modal"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        self._criar_header(layout)
        
        # Seção Cliente
        self._criar_secao_cliente(layout)
        
        # Seção Produtos
        self._criar_secao_produtos(layout)
        
        # Botões
        self._criar_botoes(layout)
    
    def _criar_header(self, layout):
        """Cria o cabeçalho com número da OS"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Número da OS
        numero_os = Contador().get_proximo_numero()
        titulo = QLabel(f"Ordem de Serviço Nº {numero_os:05d}")
        titulo.setObjectName("titulo")
        
        header_layout.addWidget(titulo)
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
    
    def _criar_secao_cliente(self, layout):
        """Cria a seção de dados do cliente"""
        group = QGroupBox("Cliente")
        group_layout = QVBoxLayout(group)
        
        # Linha 1: Nome e CNPJ
        row1 = QHBoxLayout()
        
        # Nome
        nome_layout = QVBoxLayout()
        nome_layout.addWidget(QLabel("Nome:"))
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Digite o nome do cliente...")
        nome_layout.addWidget(self.input_cliente)
        row1.addLayout(nome_layout, 2)
        
        # CNPJ
        cnpj_layout = QVBoxLayout()
        cnpj_layout.addWidget(QLabel("CNPJ:"))
        self.input_cnpj = QLineEdit()
        self.input_cnpj.setPlaceholderText("00.000.000/0000-00")
        cnpj_layout.addWidget(self.input_cnpj)
        row1.addLayout(cnpj_layout, 1)
        
        group_layout.addLayout(row1)
        
        # Linha 2: Telefone e Endereço
        row2 = QHBoxLayout()
        
        # Telefone
        tel_layout = QVBoxLayout()
        tel_layout.addWidget(QLabel("Telefone:"))
        self.input_telefone = QLineEdit()
        self.input_telefone.setPlaceholderText("(11) 99999-9999")
        tel_layout.addWidget(self.input_telefone)
        row2.addLayout(tel_layout, 1)
        
        # Endereço
        end_layout = QVBoxLayout()
        end_layout.addWidget(QLabel("Endereço:"))
        self.input_endereco = QLineEdit()
        self.input_endereco.setPlaceholderText("Endereço completo...")
        end_layout.addWidget(self.input_endereco)
        row2.addLayout(end_layout, 2)
        
        group_layout.addLayout(row2)
        
        # Conectar evento do cliente
        self.input_cliente.textChanged.connect(self._on_cliente_changed)
        
        layout.addWidget(group)
    
    def _criar_secao_produtos(self, layout):
        """Cria a seção de produtos"""
        group = QGroupBox("Produtos")
        group_layout = QVBoxLayout(group)
        
        # Formulário de adição
        form_layout = QHBoxLayout()
        
        # Produto
        produto_layout = QVBoxLayout()
        produto_layout.addWidget(QLabel("Produto:"))
        self.input_produto = QLineEdit()
        self.input_produto.setPlaceholderText("Digite o nome do produto...")
        produto_layout.addWidget(self.input_produto)
        form_layout.addLayout(produto_layout, 2)
        
        # Valor
        valor_layout = QVBoxLayout()
        valor_layout.addWidget(QLabel("Valor (R$):"))
        self.input_valor = QLineEdit()
        self.input_valor.setPlaceholderText("0,00")
        valor_layout.addWidget(self.input_valor)
        form_layout.addLayout(valor_layout, 1)
        
        # Cor
        cor_layout = QVBoxLayout()
        cor_layout.addWidget(QLabel("Cor:"))
        self.combo_cor = QComboBox()
        self.combo_cor.addItems(['', 'Branco', 'Preto', 'Azul', 'Verde', 'Vermelho', 'Amarelo', 'Personalizado'])
        cor_layout.addWidget(self.combo_cor)
        form_layout.addLayout(cor_layout, 1)
        
        # Botão adicionar
        btn_add = QPushButton("+ Adicionar")
        btn_add.setFixedHeight(35)
        btn_add.setObjectName("btnAdd")
        btn_add.clicked.connect(self._adicionar_produto)
        form_layout.addWidget(btn_add)
        
        group_layout.addLayout(form_layout)
        
        # Tabela de produtos
        self.table_produtos = QTableWidget(0, 5)
        self.table_produtos.setHorizontalHeaderLabels(['Nome', 'Código', 'Valor (R$)', 'Cor', 'Ações'])
        
        # Configurar colunas
        header = self.table_produtos.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Nome
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)    # Código
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Valor
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Cor
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Ações
        
        # Larguras das colunas
        self.table_produtos.setColumnWidth(1, 100)  # Código
        self.table_produtos.setColumnWidth(2, 120)  # Valor
        self.table_produtos.setColumnWidth(3, 100)  # Cor
        self.table_produtos.setColumnWidth(4, 200)  # Ações
        
        # Altura das linhas
        self.table_produtos.verticalHeader().setDefaultSectionSize(50)
        self.table_produtos.verticalHeader().setVisible(False)
        
        group_layout.addWidget(self.table_produtos)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("Valor Total (R$):"))
        self.label_total = QLabel("R$ 0,00")
        self.label_total.setObjectName("total")
        total_layout.addWidget(self.label_total)
        
        group_layout.addLayout(total_layout)
        
        # Configurar completer para produtos
        self._configurar_completer_produtos()
        
        # Conectar eventos
        self.input_produto.textChanged.connect(self._on_produto_changed)
        self.input_valor.returnPressed.connect(self._adicionar_produto)
        self.input_produto.returnPressed.connect(self._adicionar_produto)
        
        layout.addWidget(group)
    
    def _configurar_completer_produtos(self):
        """Configura autocomplete para produtos"""
        produtos_nomes = [produto['nome'] for produto in self.produtos_dict.values() if 'nome' in produto]
        # Remove duplicatas mantendo ordem
        produtos_unicos = list(dict.fromkeys(produtos_nomes))
        
        completer = QCompleter(produtos_unicos)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.activated.connect(self._on_produto_selecionado)
        self.input_produto.setCompleter(completer)
    
    def _criar_botoes(self, layout):
        """Cria os botões do modal"""
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        # Cancelar
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancelar)
        
        # Salvar
        btn_salvar = QPushButton("Salvar Pedido")
        btn_salvar.setObjectName("btnSalvar")
        btn_salvar.clicked.connect(self._salvar_pedido)
        btn_layout.addWidget(btn_salvar)
        
        layout.addLayout(btn_layout)
    
    def _on_cliente_changed(self, texto):
        """Evento quando o texto do cliente muda"""
        if texto in self.clientes_dict:
            cliente = self.clientes_dict[texto]
            self.input_cnpj.setText(cliente['cnpj'])
            self.input_telefone.setText(cliente['telefone'])
            self.input_endereco.setText(cliente['endereco'])
            self.cliente_selecionado = cliente
        else:
            self.cliente_selecionado = None
    
    def _on_produto_changed(self, texto):
        """Evento quando o texto do produto muda"""
        if texto in self.produtos_dict:
            produto = self.produtos_dict[texto]
            self.input_valor.setText(f"{produto['preco']:.2f}")
    
    def _on_produto_selecionado(self, texto):
        """Evento quando um produto é selecionado no completer"""
        if texto in self.produtos_dict:
            produto = self.produtos_dict[texto]
            self.input_valor.setText(f"{produto['preco']:.2f}")
    
    def _adicionar_produto(self):
        """Adiciona um produto à lista"""
        nome = self.input_produto.text().strip()
        valor_texto = self.input_valor.text().strip()
        cor = self.combo_cor.currentText()
        
        # Validações
        if not nome:
            QMessageBox.warning(self, "Aviso", "Digite o nome do produto!")
            return
        
        if not valor_texto or valor_texto in ['0', '0,00', '0.00']:
            QMessageBox.warning(self, "Aviso", "Digite um valor válido!")
            return
        
        # Converter valor
        try:
            valor = float(valor_texto.replace(',', '.'))
        except ValueError:
            QMessageBox.warning(self, "Aviso", "Valor inválido!")
            return
        
        # Buscar código no catálogo
        codigo = ''
        if nome in self.produtos_dict:
            produto_cat = self.produtos_dict[nome]
            codigo = produto_cat.get('codigo', '')
            # Usar preço do catálogo se disponível
            if produto_cat.get('preco', 0) > 0:
                valor = produto_cat['preco']
        
        # Adicionar à lista
        produto = {
            'nome': nome,
            'codigo': codigo,
            'valor': valor,
            'cor': cor
        }
        self.produtos_list.append(produto)
        
        # Atualizar tabela
        self._atualizar_tabela_produtos()
        
        # Limpar campos
        self.input_produto.clear()
        self.input_valor.clear()
        self.combo_cor.setCurrentIndex(0)
        
        # Focar no campo produto
        self.input_produto.setFocus()
    
    def _atualizar_tabela_produtos(self):
        """Atualiza a tabela de produtos"""
        self.table_produtos.setRowCount(len(self.produtos_list))
        total = 0
        
        for row, produto in enumerate(self.produtos_list):
            # Nome
            self.table_produtos.setItem(row, 0, QTableWidgetItem(produto['nome']))
            
            # Código
            codigo = produto.get('codigo', '')
            self.table_produtos.setItem(row, 1, QTableWidgetItem(codigo if codigo else '-'))
            
            # Valor
            valor = produto['valor']
            self.table_produtos.setItem(row, 2, QTableWidgetItem(f"R$ {valor:.2f}"))
            total += valor
            
            # Cor
            cor = produto.get('cor', '')
            self.table_produtos.setItem(row, 3, QTableWidgetItem(cor if cor else '-'))
            
            # Ações
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(5, 5, 5, 5)
            
            btn_remover = QPushButton("Remover")
            btn_remover.setObjectName("btnRemover")
            btn_remover.clicked.connect(lambda checked, idx=row: self._remover_produto(idx))
            btn_layout.addWidget(btn_remover)
            
            self.table_produtos.setCellWidget(row, 4, btn_widget)
            
            # Altura da linha
            self.table_produtos.setRowHeight(row, 50)
        
        # Atualizar total
        self.label_total.setText(f"R$ {total:.2f}")
    
    def _remover_produto(self, index):
        """Remove um produto da lista"""
        if 0 <= index < len(self.produtos_list):
            self.produtos_list.pop(index)
            self._atualizar_tabela_produtos()
    
    def _salvar_pedido(self):
        """Salva o pedido no banco de dados"""
        # Validações
        if not self.input_cliente.text().strip():
            QMessageBox.warning(self, "Aviso", "Digite o nome do cliente!")
            return
        
        if not self.produtos_list:
            QMessageBox.warning(self, "Aviso", "Adicione pelo menos um produto!")
            return
        
        try:
            # Dados do cliente
            cliente_data = {
                'nome': self.input_cliente.text().strip(),
                'cnpj': self.input_cnpj.text().strip(),
                'telefone': self.input_telefone.text().strip(),
                'endereco': self.input_endereco.text().strip()
            }
            
            # Salvar cliente se não existir
            if self.cliente_selecionado:
                cliente_id = self.cliente_selecionado['id']
            else:
                cliente_id = db_manager.salvar_cliente(
                    cliente_data['nome'],
                    cliente_data['cnpj'],
                    cliente_data['telefone'],
                    cliente_data['endereco']
                )
            
            # Calcular total
            valor_total = sum(p['valor'] for p in self.produtos_list)
            
            # Dados do pedido
            numero_os = Contador().get_proximo_numero()
            pedido_data = {
                'numero_os': numero_os,
                'cliente_id': cliente_id,
                'cliente_nome': cliente_data['nome'],
                'valor_total': valor_total,
                'status': 'Pendente',
                'produtos': self.produtos_list
            }
            
            # Salvar pedido
            pedido_id = db_manager.salvar_pedido(pedido_data)
            
            QMessageBox.information(self, "Sucesso", f"Pedido #{numero_os:05d} salvo com sucesso!")
            
            # Emitir sinal e fechar
            self.pedido_salvo.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar pedido:\n{e}")
    
    def _aplicar_estilo(self):
        """Aplica o estilo moderno em tema escuro com cinza e branco"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #3a3a3a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #ffffff;
            }
            
            QLabel {
                color: #ffffff;
                font-weight: 500;
                font-size: 12px;
            }
            
            #titulo {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                padding: 10px 0;
            }
            
            #total {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
            }
            
            QLineEdit, QComboBox {
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: #3a3a3a;
                color: #ffffff;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #888888;
            }
            
            QTableWidget {
                border: 1px solid #555555;
                border-radius: 6px;
                background-color: #3a3a3a;
                gridline-color: #555555;
                font-size: 12px;
                color: #ffffff;
            }
            
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            
            QHeaderView::section {
                background-color: #555555;
                color: #ffffff;
                padding: 10px 8px;
                font-weight: bold;
                border: none;
                border-right: 1px solid #2b2b2b;
            }
            
            QPushButton {
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
                min-height: 20px;
            }
            
            #btnAdd {
                background-color: #555555;
                color: #ffffff;
            }
            
            #btnAdd:hover {
                background-color: #666666;
            }
            
            #btnSalvar {
                background-color: #555555;
                color: #ffffff;
            }
            
            #btnSalvar:hover {
                background-color: #666666;
            }
            
            #btnCancelar {
                background-color: #555555;
                color: #ffffff;
            }
            
            #btnCancelar:hover {
                background-color: #666666;
            }
            
            #btnRemover {
                background-color: #555555;
                color: #ffffff;
                padding: 5px 10px;
                font-size: 11px;
            }
            
            #btnRemover:hover {
                background-color: #666666;
            }
        """)
    
    def _preencher_dados_cliente(self, dados):
        """Preenche os campos do cliente com os dados fornecidos"""
        try:
            if 'nome' in dados and dados['nome']:
                self.nome_input.setText(dados['nome'])
            if 'cpf' in dados and dados['cpf']:
                self.cpf_input.setText(dados['cpf'])
            if 'telefone' in dados and dados['telefone']:
                self.telefone_input.setText(dados['telefone'])
            if 'email' in dados and dados['email']:
                self.email_input.setText(dados['email'])
            
            # Endereço combinado
            endereco_parts = []
            if 'rua' in dados and dados['rua']:
                endereco_parts.append(dados['rua'])
            if 'numero' in dados and dados['numero']:
                endereco_parts.append(dados['numero'])
            if 'cidade' in dados and dados['cidade']:
                endereco_parts.append(dados['cidade'])
            
            if endereco_parts:
                self.endereco_input.setText(', '.join(endereco_parts))
                
        except Exception as e:
            print(f"Erro ao preencher dados do cliente: {e}")


def abrir_novo_pedido(parent=None):
    """Função para abrir o modal de novo pedido"""
    modal = NovoPedidosModal(parent)
    return modal.exec()