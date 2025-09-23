"""
Sistema de Gestão de Produtos - Versão Completamente Reescrita
Focado em simplicidade e funcionamento garantido
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QLabel, QDialog, QFormLayout, QComboBox, QTextEdit, 
    QMessageBox, QHeaderView, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPointF
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QPixmap, QPolygonF, QBrush
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


class SimpleProdutoDialog(QDialog):
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
        
        # Combobox de categoria: colocamos dentro de um widget com uma seta separada
        # para evitar problemas de renderização do glifo em algumas fontes/sistemas.
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.setPlaceholderText("Selecione ou digite uma categoria...")

        # Container que segura a combobox e a seta clicável
        self.category_widget = QWidget()
        cw_layout = QHBoxLayout(self.category_widget)
        cw_layout.setContentsMargins(0, 0, 0, 0)
        cw_layout.setSpacing(6)
        cw_layout.addWidget(self.category_input)

        # Label da seta (usamos um caractere mais simples e confiável)
        self.category_arrow = QLabel('▾')
        self.category_arrow.setStyleSheet("""
            QLabel { color: #cccccc; font-size: 14px; background: transparent; }
        """)
        self.category_arrow.setFixedWidth(18)
        self.category_arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # clicar na seta abre o popup da combobox
        self.category_arrow.mousePressEvent = lambda event: self.category_input.showPopup()

        cw_layout.addWidget(self.category_arrow)

        # Estilo simples e limpo aplicado à combobox (sem tentar customizar a seta nativa)
        self.category_input.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                color: #ffffff;
                min-height: 20px;
            }
            QComboBox:hover {
                border-color: #777;
                background-color: #404040;
            }
            QComboBox:focus {
                border-color: #0078d4;
                background-color: #404040;
            }
            QComboBox::drop-down { border: none; width: 0; }
            QComboBox::down-arrow { image: none; width: 0; height: 0; }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a;
                border: 2px solid #555;
                border-radius: 6px;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                color: #ffffff;
                padding: 4px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px;
                min-height: 20px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #4a4a4a;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #0078d4;
            }
        """)
        
        self._load_categories()
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Código (opcional)")
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descrição (opcional)")
        self.desc_input.setMaximumHeight(60)
        
        # Adicionar ao formulário
        form.addRow("📝 Nome *:", self.name_input)
        form.addRow("💰 Preço *:", self.price_input)
        form.addRow("📂 Categoria:", self.category_widget)
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


class ProdutosManager(QWidget):
    """Manager de produtos completamente reescrito"""
    
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
        dialog = SimpleProdutoDialog(self)
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
            dialog = SimpleProdutoDialog(self, product)
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
