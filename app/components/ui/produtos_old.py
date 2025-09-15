"""
Sistema de Gestão de Produtos - Interface Corrigida
Substitui completamente a lógica antiga com sistema funcional
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QLabel, QDialog, QFormLayout, QComboBox, QTextEdit, 
    QMessageBox, QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor
import re
from database import db_manager


class CurrencyParser:
    """Parser robusto para valores monetários brasileiros"""
    
    @staticmethod
    def to_float(value_str):
        """
        Converte string monetária para float
        Aceita: '10,50', '10.50', '1.234,56', 'R$ 25,90'
        """
        if not value_str or not str(value_str).strip():
            raise ValueError("Valor não pode estar vazio")
            
        # Limpar entrada
        clean = str(value_str).strip().upper()
        clean = clean.replace('R$', '').replace(' ', '')
        
        if not clean:
            raise ValueError("Valor não pode estar vazio")
        
        # Verificar se há sinal negativo
        if clean.startswith('-'):
            raise ValueError("Valor não pode ser negativo")
        
        # Remover caracteres não numéricos exceto vírgula e ponto
        clean = re.sub(r'[^\d,.]', '', clean)
        
        if not clean:
            raise ValueError("Formato inválido")
        
        # Determinar separador decimal
        if ',' in clean and '.' in clean:
            # Ambos presentes - último é decimal
            last_comma = clean.rfind(',')
            last_dot = clean.rfind('.')
            
            if last_comma > last_dot:
                # Vírgula é decimal: 1.234,56
                clean = clean.replace('.', '').replace(',', '.')
            else:
                # Ponto é decimal: 1,234.56
                clean = clean.replace(',', '')
        elif ',' in clean:
            # Apenas vírgula - decimal brasileiro
            clean = clean.replace(',', '.')
        
        try:
            result = float(clean)
            if result <= 0:
                raise ValueError("Valor deve ser maior que zero")
            return result
        except ValueError:
            raise ValueError(f"Formato inválido: '{value_str}'")
    
    @staticmethod
    def to_brazilian(value):
        """Converte float para formato brasileiro"""
        try:
            return f"R$ {float(value):.2f}".replace('.', ',')
        except:
            return "R$ 0,00"


class ProdutoDialog(QDialog):
    """Dialog simples e funcional para produtos"""
    
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.is_editing = product_data is not None
        
        self.setWindowTitle("Editar Produto" if self.is_editing else "Novo Produto")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        self._create_ui()
        self._setup_styles()
        
        if self.is_editing:
            self._load_product_data()
    
    def _create_ui(self):
        """Criar interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("✏️ Editar Produto" if self.is_editing else "➕ Novo Produto")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2fa6a0;")
        layout.addWidget(title)
        
        # Separador
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #555;")
        layout.addWidget(line)
        
        # Formulário
        form = QFormLayout()
        form.setSpacing(12)
        
        # Campos
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome do produto...")
        
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Ex: 99,90 ou 1.234,56")
        
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self._load_categories()
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Código (opcional)")
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descrição (opcional)")
        self.desc_input.setMaximumHeight(60)
        
        # Adicionar ao formulário
        form.addRow("📝 Nome *:", self.name_input)
        form.addRow("💰 Preço *:", self.price_input)
        form.addRow("📂 Categoria:", self.category_input)
        form.addRow("🏷️ Código:", self.code_input)
        form.addRow("📄 Descrição:", self.desc_input)
        
        layout.addLayout(form)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.cancel_btn = QPushButton("❌ Cancelar")
        self.save_btn = QPushButton("💾 Salvar")
        
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self._save_product)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_categories(self):
        """Carregar categorias"""
        categories = ["", "Agro", "Ferramentas", "Peças", "Serviços", "Outros"]
        
        try:
            # Tentar carregar do arquivo de configuração
            from app.utils.categories import load_categories
            file_cats = load_categories()
            if file_cats:
                categories.extend([c for c in file_cats if c not in categories])
        except:
            pass
        
        for cat in categories:
            self.category_input.addItem(str(cat))
    
    def _load_product_data(self):
        """Carregar dados do produto para edição"""
        if not self.product_data:
            return
        
        try:
            # product_data: (id, nome, codigo, preco, descricao, categoria, criado_em)
            self.name_input.setText(str(self.product_data[1] or ""))
            self.code_input.setText(str(self.product_data[2] or ""))
            
            # Formatação do preço
            price = float(self.product_data[3] or 0)
            if price > 0:
                price_str = f"{price:.2f}".replace('.', ',')
                self.price_input.setText(price_str)
            
            self.desc_input.setPlainText(str(self.product_data[4] or ""))
            
            # Categoria
            category = str(self.product_data[5] or "")
            if category:
                index = self.category_input.findText(category)
                if index >= 0:
                    self.category_input.setCurrentIndex(index)
                else:
                    self.category_input.addItem(category)
                    self.category_input.setCurrentText(category)
        
        except Exception as e:
            print(f"[ERROR] Erro ao carregar dados: {e}")
    
    def _save_product(self):
        """Validar e salvar produto"""
        try:
            # Validar nome
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Erro", "Nome é obrigatório!")
                self.name_input.setFocus()
                return
            
            # Validar preço
            price_text = self.price_input.text().strip()
            try:
                price = CurrencyParser.to_float(price_text)
            except ValueError as e:
                QMessageBox.warning(self, "Erro de Preço", str(e))
                self.price_input.setFocus()
                return
            
            # Outros campos
            code = self.code_input.text().strip() or None
            category = self.category_input.currentText().strip()
            description = self.desc_input.toPlainText().strip()
            
            # Salvar dados
            self.result_data = {
                'name': name,
                'price': price,
                'code': code,
                'category': category,
                'description': description
            }
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {e}")
    
    def _setup_styles(self):
        """Aplicar estilos"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border-radius: 8px;
            }
            QLabel {
                color: #e6e6e6;
                font-weight: 600;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #3a3a3a;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
                color: #e6e6e6;
                font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #2fa6a0;
                background-color: #404040;
            }
            QPushButton {
                background-color: #2fa6a0;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: 600;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #28a399;
            }
            QPushButton:pressed {
                background-color: #1f7a75;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 3px solid transparent;
                border-top: 6px solid #e6e6e6;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                border: 1px solid #555;
                color: #e6e6e6;
                selection-background-color: #2fa6a0;
            }
        """)


class ProdutosWidget(QWidget):
    """Widget principal de produtos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_styles()
        self._load_products()
    
    def _setup_ui(self):
        """Configurar interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🛍️ Gestão de Produtos")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2fa6a0;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Busca
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar produtos...")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self._load_products)
        header_layout.addWidget(self.search_input)
        
        # Botões de ação
        self.new_btn = QPushButton("➕ Novo")
        self.edit_btn = QPushButton("✏️ Editar")
        self.delete_btn = QPushButton("🗑️ Excluir")
        
        self.new_btn.clicked.connect(self._new_product)
        self.edit_btn.clicked.connect(self._edit_product)
        self.delete_btn.clicked.connect(self._delete_product)
        
        header_layout.addWidget(self.new_btn)
        header_layout.addWidget(self.edit_btn)
        header_layout.addWidget(self.delete_btn)
        
        layout.addLayout(header_layout)
        
        # Tabela
        self._setup_table()
        layout.addWidget(self.table)
        
        # Info footer
        self.info_label = QLabel("Produtos carregados: 0")
        self.info_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.info_label)
    
    def _setup_table(self):
        """Configurar tabela"""
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nome", "Preço", "Categoria", "Código", "Criado"
        ])
        
        # Configurações básicas
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        
        # Larguras das colunas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)    # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Nome
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Preço
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Categoria
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Código
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Data
        
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 140)
        
        # Conectar duplo clique
        self.table.doubleClicked.connect(self._edit_product)
    
    def _load_products(self):
        """Carregar produtos na tabela"""
        try:
            search_text = self.search_input.text().strip()
            products = db_manager.listar_produtos(busca=search_text)
            
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                # product: (id, nome, codigo, preco, descricao, categoria, criado_em)
                
                # ID
                id_item = QTableWidgetItem(str(product[0]))
                id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 0, id_item)
                
                # Nome
                name_item = QTableWidgetItem(str(product[1] or ""))
                self.table.setItem(row, 1, name_item)
                
                # Preço formatado
                price_formatted = CurrencyParser.to_brazilian(product[3] or 0)
                price_item = QTableWidgetItem(price_formatted)
                price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                price_item.setData(Qt.ItemDataRole.UserRole, float(product[3] or 0))
                self.table.setItem(row, 2, price_item)
                
                # Categoria
                cat_item = QTableWidgetItem(str(product[5] or ""))
                self.table.setItem(row, 3, cat_item)
                
                # Código
                code_item = QTableWidgetItem(str(product[2] or ""))
                code_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, code_item)
                
                # Data
                date_str = str(product[6] or "")
                if date_str:
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        formatted_date = dt.strftime("%d/%m/%Y")
                    except:
                        formatted_date = date_str[:10] if len(date_str) >= 10 else date_str
                else:
                    formatted_date = ""
                
                date_item = QTableWidgetItem(formatted_date)
                date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 5, date_item)
            
            # Atualizar info
            self.info_label.setText(f"Produtos carregados: {len(products)}")
            
        except Exception as e:
            print(f"[ERROR] Erro ao carregar produtos: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produtos:\n{e}")
            self.info_label.setText("Erro ao carregar produtos")
    
    def _new_product(self):
        """Criar novo produto"""
        dialog = ProdutoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                data = dialog.result_data
                
                product_id = db_manager.inserir_produto(
                    nome=data['name'],
                    preco=data['price'],
                    descricao=data['description'],
                    categoria=data['category'],
                    codigo=data['code']
                )
                
                if product_id:
                    QMessageBox.information(self, "✅ Sucesso", 
                                          f"Produto '{data['name']}' criado com sucesso!")
                    self._load_products()
                else:
                    QMessageBox.warning(self, "❌ Erro", "Falha ao criar produto.")
                    
            except Exception as e:
                print(f"[ERROR] Erro ao criar produto: {e}")
                QMessageBox.critical(self, "❌ Erro", f"Erro ao criar produto:\n{e}")
    
    def _edit_product(self):
        """Editar produto selecionado"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "ℹ️ Info", "Selecione um produto para editar.")
            return
        
        try:
            # Obter ID do produto
            product_id = int(self.table.item(current_row, 0).text())
            
            # Buscar produto completo
            products = db_manager.listar_produtos()
            product = None
            for p in products:
                if p[0] == product_id:
                    product = p
                    break
            
            if not product:
                QMessageBox.warning(self, "❌ Erro", "Produto não encontrado.")
                return
            
            # Abrir dialog de edição
            dialog = ProdutoDialog(self, product)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.result_data
                
                success = db_manager.atualizar_produto(
                    produto_id=product_id,
                    nome=data['name'],
                    preco=data['price'],
                    descricao=data['description'],
                    categoria=data['category'],
                    codigo=data['code']
                )
                
                if success:
                    QMessageBox.information(self, "✅ Sucesso",
                                          f"Produto '{data['name']}' atualizado com sucesso!")
                    self._load_products()
                else:
                    QMessageBox.warning(self, "❌ Erro", "Falha ao atualizar produto.")
                    
        except Exception as e:
            print(f"[ERROR] Erro ao editar produto: {e}")
            QMessageBox.critical(self, "❌ Erro", f"Erro ao editar produto:\n{e}")
    
    def _delete_product(self):
        """Excluir produto selecionado"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "ℹ️ Info", "Selecione um produto para excluir.")
            return
        
        try:
            product_id = int(self.table.item(current_row, 0).text())
            product_name = self.table.item(current_row, 1).text()
            
            # Confirmar exclusão
            reply = QMessageBox.question(
                self, "⚠️ Confirmar Exclusão",
                f"Tem certeza que deseja excluir:\n\n'{product_name}'\n\nEsta ação não pode ser desfeita.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success = db_manager.deletar_produto(product_id)
                if success:
                    QMessageBox.information(self, "✅ Sucesso", "Produto excluído com sucesso!")
                    self._load_products()
                else:
                    QMessageBox.warning(self, "❌ Erro", "Falha ao excluir produto.")
                    
        except Exception as e:
            print(f"[ERROR] Erro ao excluir produto: {e}")
            QMessageBox.critical(self, "❌ Erro", f"Erro ao excluir produto:\n{e}")
    
    def _setup_styles(self):
        """Aplicar estilos"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                color: #e6e6e6;
            }
            QLineEdit {
                background-color: #3a3a3a;
                border: 2px solid #555;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e6e6e6;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #2fa6a0;
                background-color: #404040;
            }
            QPushButton {
                background-color: #2fa6a0;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
                font-size: 13px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #28a399;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #1f7a75;
                transform: translateY(1px);
            }
            QTableWidget {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 8px;
                gridline-color: #555;
                color: #e6e6e6;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #2fa6a0;
                color: white;
            }
            QTableWidget::item:alternate {
                background-color: #343434;
            }
            QHeaderView::section {
                background-color: #444;
                color: #e6e6e6;
                padding: 10px;
                border: none;
                border-right: 1px solid #555;
                border-bottom: 2px solid #2fa6a0;
                font-weight: 600;
                font-size: 13px;
            }
            QHeaderView::section:hover {
                background-color: #2fa6a0;
                color: white;
            }
        """)
            }
            QLineEdit:focus, QComboBox:focus { border: 1.6px solid #56c6bf; }
            QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 28px; }
            QComboBox QAbstractItemView { background: #242424; color: #e6e6e6; selection-background-color: #2fa6a0; }
            QDialogButtonBox { margin-top: 10px; }
            QDialogButtonBox QPushButton#save { background-color: #2fa6a0; color: #061214; font-weight:700; border-radius:8px; padding: 10px 20px; min-width:120px; }
            QDialogButtonBox QPushButton#cancel { background-color: #323232; color: #e6e6e6; border: 1px solid #3a3a3a; border-radius:8px; padding: 10px 20px; min-width:120px; }
            QDialogButtonBox QPushButton#save:hover { background-color: #28a399; }
            QDialogButtonBox QPushButton#cancel:hover { background-color: #3a3a3a; }
            /* subtle inner panel accent */
            QFrame#inner { background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #2a2a2a, stop:1 #252525); border-radius:8px; }
        ''')
        # Add a subtle shadow if available
        try:
            from PyQt6.QtWidgets import QGraphicsDropShadowEffect
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setOffset(0, 6)
            shadow.setColor(__import__('PyQt6').QtGui.QColor(0,0,0,160))
            self.setGraphicsEffect(shadow)
        except Exception:
            pass
        self.input_nome = QLineEdit()
        self.input_valor = QLineEdit()
        # Use a combo so users must pick existing categories
        self.input_categoria = QComboBox()
        # populate categories from the persisted file
        try:
            from app.utils.categories import load_categories
            cats = load_categories()
            if cats:
                self.input_categoria.addItems([str(c) for c in cats])
        except Exception:
            # fallback defaults
            self.input_categoria.addItems(['Agro', 'Normal', 'Outros'])
        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText('Código opcional')
        layout.addRow('Nome:', self.input_nome)
        layout.addRow('Valor:', self.input_valor)
        layout.addRow('Categoria:', self.input_categoria)
        layout.addRow('Código:', self.input_codigo)

        # Autocomplete de produtos
        self.sugestoes = QListWidget()
        self.sugestoes.setWindowFlags(self.sugestoes.windowFlags() | Qt.WindowType.Popup)
        self.sugestoes.setStyleSheet('''
            QListWidget { background: #23272e; color: #f8f8f2; border: 1.5px solid #50fa7b; font-size: 15px; }
            QListWidget::item:selected { background: #50fa7b; color: #23272e; }
        ''')

        self.sugestoes.hide()
        self.input_nome.textEdited.connect(self.buscar_sugestoes)
        self.sugestoes.itemClicked.connect(self.preencher_produto)

        # Botões de ação
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)

        # Improve save/cancel button appearance and sizes
        try:
            save_btn = self.button_box.button(QDialogButtonBox.StandardButton.Save)
            cancel_btn = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)
            if save_btn:
                save_btn.setObjectName('save')
                save_btn.setMinimumWidth(140)
                save_btn.setFixedHeight(44)
                save_btn.setStyleSheet('background-color: #2fa6a0; color: #061214; font-weight: 700; border-radius: 8px;')
            if cancel_btn:
                cancel_btn.setObjectName('cancel')
                cancel_btn.setMinimumWidth(140)
                cancel_btn.setFixedHeight(44)
                cancel_btn.setStyleSheet('background-color: #323232; color: #e6e6e6; border: 1px solid #3a3a3a; border-radius: 8px;')
        except Exception:
            pass

    # Preenche campos se for edição
        if produto:
            self.input_nome.setText(str(produto.get('nome', '')))
            valor = produto.get('valor', '')
            try:
                valor_f = float(str(valor).replace('R$', '').replace(',', '.'))
                if valor_f > 9999:
                    valor_f = valor_f / 100
                self.input_valor.setText(f"{valor_f:.2f}")
            except Exception:
                self.input_valor.setText(str(valor))
            try:
                self.input_categoria.setCurrentText(str(produto.get('categoria', '')))
            except Exception:
                # if value not present, add it then set
                val = str(produto.get('categoria', '')).strip()
                if val:
                    self.input_categoria.addItem(val)
                    self.input_categoria.setCurrentText(val)
            self.input_codigo.setText(str(produto.get('codigo', '')))
        # object names already applied above; keep compatibility
        try:
            save_btn = self.button_box.button(QDialogButtonBox.StandardButton.Save)
            cancel_btn = self.button_box.button(QDialogButtonBox.StandardButton.Cancel)
            if save_btn and not save_btn.objectName():
                save_btn.setObjectName('save')
            if cancel_btn and not cancel_btn.objectName():
                cancel_btn.setObjectName('cancel')
        except Exception:
            pass

    def buscar_sugestoes(self, texto):
        if not texto.strip():
            self.sugestoes.hide()
            return
        produtos = db_manager.listar_produtos(busca=texto, limite=8)
        self.sugestoes.clear()
        for prod in produtos:
            # ProductsCRUD returns: (id, nome, codigo, preco, descricao, categoria, criado_em)
            nome = prod[1]
            valor = prod[3]
            categoria = prod[5] if len(prod) > 5 else ''
            codigo = prod[2] if len(prod) > 2 else ''
            item = QListWidgetItem(f"{nome} | R$ {float(valor or 0):.2f} | {categoria} | {codigo}")
            item.setData(Qt.ItemDataRole.UserRole, prod)
            self.sugestoes.addItem(item)
        if produtos:
            self.sugestoes.setMinimumWidth(self.input_nome.width())
            self.sugestoes.move(self.input_nome.mapToGlobal(self.input_nome.rect().bottomLeft()))
            self.sugestoes.show()
        else:
            self.sugestoes.hide()

    def preencher_produto(self, item):
        prod = item.data(Qt.ItemDataRole.UserRole)
        self.input_nome.setText(str(prod[1]))
        # Corrige valor para reais se vier em centavos
        valor = float(prod[3] or 0)
        if valor > 9999:
            valor = valor / 100
        self.input_valor.setText(f"{valor:.2f}")
        try:
            self.input_categoria.setCurrentText(str(prod[5] if len(prod) > 5 else ''))
        except Exception:
            val = str(prod[5] if len(prod) > 5 else '').strip()
            if val:
                self.input_categoria.addItem(val)
                self.input_categoria.setCurrentText(val)
        self.input_codigo.setText(str(prod[2] if len(prod) > 2 else ''))

    def get_data(self):
        # Garante que o valor será salvo em reais
        valor_str = self.input_valor.text().replace('R$', '').replace(',', '.').strip()
        try:
            valor = float(valor_str)
        except Exception:
            valor = 0.0
        return {
            'nome': self.input_nome.text().strip(),
            'valor': valor,
            'categoria': self.input_categoria.currentText().strip(),
            'codigo': self.input_codigo.text().strip(),
        }
class ProdutosWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        # Header
        header = QLabel('Produtos')
        header.setObjectName('header')
        header.setStyleSheet('font-size: 22px; font-weight: bold; padding-bottom: 8px;')
        layout.addWidget(header)

        # Search bar and buttons
        search_row = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText('Buscar produto...')
        # neutral search box styling (matches BackupTab)
        self.input_busca.setStyleSheet('''
            QLineEdit { background-color: #1f1f1f; color: #e6e6e6; border: 1px solid #393939; border-radius: 6px; padding: 8px 12px; font-size: 14px; }
            QLineEdit:focus { border: 1px solid #5a5a5a; }
        ''')
        search_row.addWidget(self.input_busca, stretch=1)

        self.btn_buscar = QPushButton('Buscar')
        # flat, neutral buttons
        self.btn_buscar.setStyleSheet('''
            QPushButton { background-color: #323232; color: #eaeaea; border-radius: 6px; padding: 8px 14px; font-weight: 600; }
            QPushButton:hover { background-color: #3a3a3a; }
        ''')
        search_row.addWidget(self.btn_buscar)

        self.btn_novo = QPushButton('Novo')
        self.btn_novo.setStyleSheet('''
            QPushButton { background-color: #323232; color: #eaeaea; border-radius: 6px; padding: 8px 14px; font-weight: 600; }
            QPushButton:hover { background-color: #3a3a3a; }
        ''')
        self.btn_deletar = QPushButton('Deletar')
        self.btn_deletar.setStyleSheet('''
            QPushButton { background-color: #323232; color: #eaeaea; border-radius: 6px; padding: 8px 14px; font-weight: 600; }
            QPushButton:hover { background-color: #3a3a3a; }
        ''')
        # visual consistency
        for b in (self.btn_buscar, self.btn_novo, self.btn_deletar):
            b.setMinimumHeight(36)
            b.setCursor(Qt.CursorShape.PointingHandCursor)

        search_row.addWidget(self.btn_novo)
        search_row.addWidget(self.btn_deletar)
        layout.addLayout(search_row)

        # Table
        self.produtos_table = QTableWidget(0, 5)
        self.produtos_table.setHorizontalHeaderLabels(['ID', 'Nome', 'Valor', 'Categoria', 'Código'])
        self.produtos_table.verticalHeader().setVisible(False)
        self.produtos_table.setAlternatingRowColors(True)
        self.produtos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.produtos_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # neutral table styling similar to BackupTab
        self.produtos_table.setStyleSheet('''
            QTableWidget { background-color: #1f1f1f; color: #e6e6e6; border: 1px solid #393939; border-radius: 6px; font-size: 13px; gridline-color: #333333; selection-background-color: #2d2d2d; alternate-background-color: #232323; }
            QHeaderView::section { background-color: #1f1f1f; color: #e6e6e6; font-weight: bold; }
        ''')

        from PyQt6.QtGui import QPalette, QColor
        palette = self.produtos_table.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#1f1f1f"))
        palette.setColor(QPalette.ColorRole.Window, QColor("#1f1f1f"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#232323"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#e6e6e6"))
        self.produtos_table.setPalette(palette)
        header = self.produtos_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { background-color: #1f1f1f; color: #e6e6e6; font-weight: bold; font-size: 14px; }")
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.produtos_table)

        self.btn_novo.clicked.connect(self.novo_produto)
        self.btn_deletar.clicked.connect(self.deletar_produto)
        self.produtos_table.cellDoubleClicked.connect(self.editar_produto)

        self.load_produtos()

    def load_produtos(self):
        try:
            self.produtos_table.setRowCount(0)
            produtos = db_manager.listar_produtos()
            for produto in produtos:
                # produto: (id, nome, codigo, preco, descricao, categoria, criado_em)
                id = produto[0]
                nome = produto[1]
                valor = f"R$ {float(produto[3] or 0):.2f}"
                categoria = produto[5] or ""
                codigo = produto[2] or ""
                row = self.produtos_table.rowCount()
                self.produtos_table.insertRow(row)
                self.produtos_table.setItem(row, 0, QTableWidgetItem(str(id)))
                self.produtos_table.setItem(row, 1, QTableWidgetItem(nome))
                self.produtos_table.setItem(row, 2, QTableWidgetItem(valor))
                self.produtos_table.setItem(row, 3, QTableWidgetItem(categoria))
                self.produtos_table.setItem(row, 4, QTableWidgetItem(codigo))
        except Exception as e:
            import traceback
            print("Erro ao carregar Produtos:")
            traceback.print_exc()
            self.produtos_table.setRowCount(0)
            self.produtos_table.setColumnCount(1)
            self.produtos_table.setHorizontalHeaderLabels(["Erro"])
            self.produtos_table.insertRow(0)
            self.produtos_table.setItem(0, 0, QTableWidgetItem(f"Erro ao carregar Produtos: {e}"))

    def novo_produto(self):
        dialog = ProdutoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                valor = float(data['valor'].replace('R$', '').replace(',', '.'))
            except Exception:
                valor = 0.0
            ok = db_manager.inserir_produto(data['nome'], valor, data.get('categoria', ''), data.get('codigo') or None)
            if ok:
                self.load_produtos()
            else:
                QMessageBox.warning(self, 'Erro', 'Erro ao inserir produto.')

    def editar_produto(self, row, col):
        if row < 0:
            return
        id_item = self.produtos_table.item(row, 0)
        if not id_item:
            return
        produto_id = int(id_item.text())
        nome = self.produtos_table.item(row, 1).text()
        valor = self.produtos_table.item(row, 2).text().replace('R$', '').replace(',', '.')
        categoria = self.produtos_table.item(row, 3).text()
        codigo = self.produtos_table.item(row, 4).text()
        dialog = ProdutoDialog(self, produto={'nome': nome, 'valor': valor, 'categoria': categoria, 'codigo': codigo})
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                valor = float(data['valor'].replace('R$', '').replace(',', '.'))
            except Exception:
                valor = 0.0
            ok = db_manager.atualizar_produto(produto_id, data['nome'], valor, data.get('categoria', ''), data.get('codigo') or None)
            if ok:
                self.load_produtos()
            else:
                QMessageBox.warning(self, 'Erro', 'Erro ao atualizar produto.')

    def deletar_produto(self):
        try:
            row = self.produtos_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, 'Atenção', 'Selecione um produto para deletar.')
                return
            id_item = self.produtos_table.item(row, 0)
            if not id_item:
                return
            produto_id = int(id_item.text())
            nome = self.produtos_table.item(row, 1).text()
            resp = QMessageBox.question(self, 'Confirmar', f'Deseja deletar o produto "{nome}"?')
            if resp == QMessageBox.StandardButton.Yes:
                ok = db_manager.deletar_produto(produto_id)
                if ok:
                    self.load_produtos()
                else:
                    QMessageBox.warning(self, 'Erro', 'Erro ao deletar produto.')
        except Exception as e:
            import traceback
            print("Erro ao deletar Produto:")
            traceback.print_exc()
            self.produtos_table.setRowCount(0)
            self.produtos_table.setColumnCount(1)
            self.produtos_table.setHorizontalHeaderLabels(["Erro"])
            self.produtos_table.insertRow(0)
            self.produtos_table.setItem(0, 0, QTableWidgetItem(f"Erro ao deletar Produto: {e}"))

