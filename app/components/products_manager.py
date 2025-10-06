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
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QPixmap, QPolygonF, QBrush, QShortcut, QKeySequence
import re
from database import db_manager
from app.utils.currency_parser import CurrencyParser
from app.utils.keyboard_shortcuts import setup_standard_shortcuts



class SimpleProdutoDialog(QDialog):
    """Dialog simples e funcional para produtos"""
    
    def __init__(self, parent=None, product_data=None):
        super().__init__(parent)
        self.product_data = product_data
        self.is_editing = product_data is not None
        
        self.setWindowTitle("Editar Produto" if self.is_editing else "Novo Produto")
        self.setFixedSize(550, 480)  # Janela maior para mais espaçamento
        self.setModal(True)
        
        self._create_ui()
        self._setup_styles()
        self._setup_enter_navigation()
        self._connect_signals()
        
        if self.is_editing:
            self._load_product_data()
    
    def _connect_signals(self):
        """Conecta aos sinais para atualização automática"""
        try:
            from app.signals import get_signals
            signals = get_signals()
            signals.categorias_atualizadas.connect(self._on_categories_updated)
        except Exception as e:
            print(f"Erro ao conectar sinais no diálogo: {e}")
    
    def _on_categories_updated(self):
        """Callback quando categorias são atualizadas"""
        current_text = self.category_input.currentText()
        self._load_categories()
        # Tentar manter a categoria selecionada
        index = self.category_input.findText(current_text)
        if index >= 0:
            self.category_input.setCurrentIndex(index)
        else:
            self.category_input.setCurrentText(current_text)
    
    def _setup_enter_navigation(self):
        """Configurar navegação com Enter entre os campos"""
        # Instalar filtro de eventos para cada campo de entrada
        fields = [self.name_input, self.price_input, self.category_input, self.code_input]
        for field in fields:
            field.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Filtro de eventos para capturar Enter antes que feche o dialog"""
        if event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                # Determinar próximo campo baseado no objeto atual
                if obj == self.name_input:
                    self.price_input.setFocus()
                    return True  # Consumir evento
                elif obj == self.price_input:
                    self.category_input.setFocus()
                    return True
                elif obj == self.category_input:
                    self.code_input.setFocus()
                    return True
                elif obj == self.code_input:
                    self.desc_input.setFocus()
                    return True
        
        # Para outros eventos, comportamento padrão
        return super().eventFilter(obj, event)
    
    def _create_ui(self):
        """Criar interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(25)  # Mais espaço entre seções
        layout.setContentsMargins(30, 30, 30, 30)  # Mais margem geral
        
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
        form.setSpacing(22)  # Ainda mais espaço entre os campos
        form.setContentsMargins(10, 10, 10, 10)  # Margem interna do formulário
        
        # Campos
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome do produto...")
        self.name_input.setMinimumHeight(32)
        self.name_input.setFixedHeight(35)
        
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Ex: 99,90 ou 1.234,56")
        self.price_input.setMinimumHeight(32)
        self.price_input.setFixedHeight(35)
        
        # Combobox de categoria simples
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.setPlaceholderText("Selecione ou digite uma categoria...")
        self.category_input.setMinimumHeight(32)
        self.category_input.setFixedHeight(35)
        
        # Make the entire combobox clickable to open dropdown
        def show_popup():
            self.category_input.showPopup()
        
        # Override mouse press to always open popup
        original_mousePressEvent = self.category_input.mousePressEvent
        def new_mousePressEvent(event):
            show_popup()
            original_mousePressEvent(event)
        
        self.category_input.mousePressEvent = new_mousePressEvent
        
        self._load_categories()
        
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Código (opcional)")
        self.code_input.setMinimumHeight(32)
        self.code_input.setFixedHeight(35)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Descrição (opcional)")
        self.desc_input.setMinimumHeight(50)
        self.desc_input.setMaximumHeight(65)
        
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
        
        # Garantir que os botões não sejam padrão (não ativados por Enter)
        self.cancel_btn.setDefault(False)
        self.cancel_btn.setAutoDefault(False)
        self.save_btn.setDefault(False)
        self.save_btn.setAutoDefault(False)
        
        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self._save_product)
        
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)

    def keyPressEvent(self, event):
        """Handle Enter key para botões e campo de descrição"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            focused = self.focusWidget()
            
            # Apenas para botões e campo de descrição
            if focused == self.desc_input:
                # No campo de descrição, permite Enter para quebra de linha
                super().keyPressEvent(event)
                return
            elif focused == self.save_btn:
                self._save_product()
                return
            elif focused == self.cancel_btn:
                self.reject()
                return
            else:
                # Para outros widgets, consumir o evento para não fechar dialog
                event.accept()
                return
        
        # Para outras teclas, comportamento padrão
        super().keyPressEvent(event)
    
    def _load_categories(self):
        """Carregar categorias do arquivo de configuração"""
        self.category_input.clear()
        
        # Adicionar item vazio
        self.category_input.addItem("")
        
        try:
            from app.utils.categories import load_categories
            file_cats = load_categories()
            for cat in file_cats:
                self.category_input.addItem(str(cat))
        except Exception as e:
            print(f"Erro ao carregar categorias: {e}")
            # Fallback para categorias padrão
            default_cats = ["Agro", "Normal", "Outros"]
            for cat in default_cats:
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
                padding: 8px 12px;
                color: #e6e6e6;
                font-size: 13px;
                min-height: 35px;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #2fa6a0;
                background-color: #404040;
                border-width: 3px;
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
        self._animation_in_progress = False  # Flag para evitar animações múltiplas
        self._last_selected_row = -1  # Última linha selecionada
        self._conectar_sinais()
        self._setup_ui()
        self._setup_styles()
        self._load_products()
        self._setup_keyboard_shortcuts()
    
    def _mostrar_mensagem_auto_close(self, titulo, mensagem, icone="information", segundos=5):
        """Mostra uma mensagem não-bloqueante que fecha automaticamente após X segundos com contador"""
        from PyQt6.QtCore import QTimer
        
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
    
    def _conectar_sinais(self):
        """Conecta os sinais globais para atualização em tempo real"""
        try:
            from app.signals import get_signals
            signals = get_signals()
            signals.produto_criado.connect(self._on_produto_atualizado)
            signals.produto_editado.connect(self._on_produto_atualizado)
            signals.produto_excluido.connect(self._on_produto_atualizado)
            signals.produtos_atualizados.connect(self._on_produtos_atualizados)
            signals.categorias_atualizadas.connect(self._on_categorias_atualizadas)
        except Exception as e:
            print(f"Erro ao conectar sinais de produtos: {e}")
    
    def _on_categorias_atualizadas(self):
        """Atualiza categorias quando há mudanças no gerenciador"""
        # Recarrega as categorias no filtro se existir
        if hasattr(self, 'category_filter') and self.category_filter:
            current_text = self.category_filter.currentText()
            self.category_filter.clear()
            self.category_filter.addItem("Todas")
            try:
                from app.utils.categories import load_categories
                cats = load_categories()
                for cat in cats:
                    self.category_filter.addItem(cat)
                # Restaura seleção se ainda existir
                index = self.category_filter.findText(current_text)
                if index >= 0:
                    self.category_filter.setCurrentIndex(index)
            except Exception as e:
                print(f"Erro ao atualizar categorias: {e}")
        
        # Recarrega produtos para refletir mudanças
        self._load_products()
    
    def _on_produto_atualizado(self, produto_id: int = None):
        """Atualiza a lista quando um produto é modificado"""
        self._load_products()
    
    def _on_produtos_atualizados(self):
        """Atualiza a lista quando há mudança geral nos produtos"""
        self._load_products()
    
    def _setup_ui(self):
        """Configurar interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("Gestão de Produtos")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff; background: transparent;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Busca
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar produtos...")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self._load_products)
        header_layout.addWidget(self.search_input)
        
        # Contador de resultados
        self.label_resultados = QLabel("")
        self.label_resultados.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 12px;
                font-weight: 500;
                padding: 0px 10px;
            }
        """)
        header_layout.addWidget(self.label_resultados)
        
        # Botões de ação
        self.new_btn = QPushButton("➕ Novo")
        self.edit_btn = QPushButton("✏️ Editar")
        self.delete_btn = QPushButton("🗑️ Excluir")
        self.refresh_btn = QPushButton("🔄 Recarregar")
        
        self.new_btn.clicked.connect(self._new_product)
        self.edit_btn.clicked.connect(self._edit_product)
        self.delete_btn.clicked.connect(self._delete_product)
        self.refresh_btn.clicked.connect(self._load_products)
        
        # Aplicar cores intuitivas aos botões
        self.new_btn.setProperty("btnClass", "success")  # Verde
        self.edit_btn.setProperty("btnClass", "primary")  # Azul
        self.delete_btn.setProperty("btnClass", "danger")  # Vermelho
        self.refresh_btn.setProperty("btnClass", "success")  # Verde
        
        header_layout.addWidget(self.new_btn)
        header_layout.addWidget(self.edit_btn)
        header_layout.addWidget(self.delete_btn)
        header_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Tabela com scroll
        self._setup_table()
        
        # Criar scroll area para a tabela
        from PyQt6.QtWidgets import QScrollArea
        self.scroll_area = QScrollArea()
        scroll_area = self.scroll_area
        scroll_area.setWidget(self.table)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QScrollArea.Shape.NoFrame)
        
        # DEBUG: Adicionar logs de scroll
        
        # Conectar eventos de scroll para debug
        scroll_bar = scroll_area.verticalScrollBar()
        
        # Verificar se scroll é necessário
        def check_scroll_needed():
            table_height = self.table.sizeHint().height()
            scroll_height = scroll_area.height()
            needs_scroll = table_height > scroll_height
            return needs_scroll
        
        # Timer para verificar tamanhos após carregamento
        from PyQt6.QtCore import QTimer
        debug_timer = QTimer()
        debug_timer.timeout.connect(check_scroll_needed)
        debug_timer.setSingleShot(True)
        debug_timer.start(1000)  # Verificar após 1 segundo
        
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #2b2b2b;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        layout.addWidget(scroll_area)
        
        # Info footer
        self.info_label = QLabel("Produtos carregados: 0")
        self.info_label.setStyleSheet("color: #888; font-size: 12px; background: transparent;")
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
        self.table.setAlternatingRowColors(False)  # Desabilitar para não conflitar com animação
        self.table.setSortingEnabled(True)
        
        # Ocultar cabeçalho vertical (números das linhas)
        self.table.verticalHeader().setVisible(False)
        
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
        
        # Conectar seleção para efeito visual
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _on_selection_changed(self):
        """Efeito visual ao selecionar uma linha com flash animado"""
        # Evitar múltiplas animações ao mesmo tempo
        if self._animation_in_progress:
            return
        
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        
        # Se é a mesma linha, não animar novamente
        if row == self._last_selected_row:
            return
        
        self._last_selected_row = row
        self._animation_in_progress = True
        
        from PyQt6.QtCore import QTimer
        from PyQt6.QtGui import QColor, QFont
        
        # Criar efeito de "flash" com múltiplas etapas
        colors = [
            QColor("#00D4FF"),  # Ciano brilhante
            QColor("#00B8E6"),  # Ciano médio
            QColor("#3a5a7a"),  # Azul escuro (cor final)
        ]
        
        def apply_flash(step=0):
            if step < len(colors):
                # Pintar TODAS as células da linha
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    # Se não existe item, criar um vazio
                    if not item:
                        item = QTableWidgetItem("")
                        self.table.setItem(row, col, item)
                    
                    # Aplicar cor de fundo
                    item.setBackground(colors[step])
                    
                    # No primeiro flash, destacar o texto
                    if step == 0:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                        item.setForeground(QColor("#FFFFFF"))
                
                # Forçar atualização visual
                self.table.viewport().update()
                
                # Próxima etapa
                QTimer.singleShot(150, lambda: apply_flash(step + 1))
            else:
                # Finalizar animação
                self._animation_in_progress = False
                # Limpar e reselecionar para aplicar estilo padrão
                self.table.clearSelection()
                self.table.selectRow(row)
                self.table.viewport().update()
        
        apply_flash()
    
    def _setup_keyboard_shortcuts(self):
        """Configura os atalhos de teclado para a tela de produtos"""
        try:
            callbacks = {
                'new': self._new_product,  # Ctrl+N
                'save': None,  # Não aplicável nesta tela
                'search': lambda: self.search_input.setFocus(),  # Ctrl+F
                'reload': self._load_products,  # F5
                'delete': self._delete_selected_product,  # Delete
            }
            self.shortcut_manager = setup_standard_shortcuts(self, callbacks)
            
            # Atualizar tooltips dos botões com atalhos
            self.new_btn.setToolTip("Adicionar novo produto (Ctrl+N)")
            self.search_input.setToolTip("Buscar produto (Ctrl+F)")
            self.refresh_btn.setToolTip("Recarregar lista de produtos (F5)")
        except Exception as e:
            print(f"Erro ao configurar atalhos: {e}")
    
    def _delete_selected_product(self):
        """Deleta o produto selecionado"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self._delete_product(current_row)
    
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
            
            # Atualizar contador de resultados
            if hasattr(self, 'label_resultados'):
                total = len(products)
                if total == 0:
                    self.label_resultados.setText("Nenhum produto encontrado")
                elif total == 1:
                    self.label_resultados.setText("1 produto encontrado")
                else:
                    self.label_resultados.setText(f"{total} produtos encontrados")
            
            # DEBUG: Verificar scroll após carregamento
            
            # Verificar se scroll bar está visível
            if hasattr(self, 'scroll_area'):
                scroll_bar = self.scroll_area.verticalScrollBar()
        
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
                    self._mostrar_mensagem_auto_close("✅ Sucesso", 
                                          f"Produto '{data['name']}' criado com sucesso!", "success", 5)
                    # Emitir sinal de produto criado
                    from app.signals import get_signals
                    signals = get_signals()
                    signals.produto_criado.emit(product_id)
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
                    self._mostrar_mensagem_auto_close("✅ Sucesso",
                                          f"Produto '{data['name']}' atualizado com sucesso!", "success", 5)
                    # Emitir sinal de produto editado
                    from app.signals import get_signals
                    signals = get_signals()
                    signals.produto_editado.emit(product_id)
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
            msgbox = QMessageBox(self)
            msgbox.setWindowTitle("⚠️ Confirmar Exclusão")
            msgbox.setText(f"Tem certeza que deseja excluir:\n\n'{product_name}'\n\n⚠️ O produto será movido para a lixeira!\nVocê poderá recuperá-lo dentro de 30 dias.")
            msgbox.setIcon(QMessageBox.Icon.Question)
            msgbox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msgbox.setDefaultButton(QMessageBox.StandardButton.No)
            
            # Aplicar estilo escuro
            from app.ui.theme import apply_dark_messagebox_style
            apply_dark_messagebox_style(msgbox)
            
            reply = msgbox.exec()
            
            if reply == QMessageBox.StandardButton.Yes:
                # Usar soft delete em vez de exclusão permanente
                from app.utils.soft_delete import SoftDeleteManager
                success, mensagem = SoftDeleteManager.soft_delete_produto(product_id)
                
                if success:
                    self._mostrar_mensagem_auto_close("✅ Sucesso", "Produto movido para a lixeira! Você pode recuperá-lo em até 30 dias.", "success", 5)
                    # Emitir sinal de produto excluído
                    from app.signals import get_signals
                    signals = get_signals()
                    signals.produto_excluido.emit(product_id)
                else:
                    QMessageBox.warning(self, "❌ Erro", mensagem)
                    
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
            }
            QPushButton:pressed {
                background-color: #1f7a75;
            }
            
            /* Botão Verde - Sucesso (Novo, Recarregar) */
            QPushButton[btnClass="success"] {
                background-color: #28a745;
            }
            QPushButton[btnClass="success"]:hover {
                background-color: #218838;
            }
            QPushButton[btnClass="success"]:pressed {
                background-color: #1e7e34;
            }
            
            /* Botão Azul - Primário (Editar) */
            QPushButton[btnClass="primary"] {
                background-color: #007bff;
            }
            QPushButton[btnClass="primary"]:hover {
                background-color: #0069d9;
            }
            QPushButton[btnClass="primary"]:pressed {
                background-color: #0056b3;
            }
            
            /* Botão Vermelho - Perigo (Excluir) */
            QPushButton[btnClass="danger"] {
                background-color: #dc3545;
            }
            QPushButton[btnClass="danger"]:hover {
                background-color: #c82333;
            }
            QPushButton[btnClass="danger"]:pressed {
                background-color: #bd2130;
            }
            QTableWidget {
                background-color: transparent;
                border: none;
                border-radius: 0px;
                gridline-color: #333333;
                color: #e6e6e6;
                font-size: 13px;
                selection-background-color: #2d2d2d;
                alternate-background-color: transparent;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #3a5a7a;
                color: #ffffff;
                font-weight: bold;
            }
            QTableWidget::item:selected:hover {
                background-color: #4a6a8a;
            }
            QTableWidget::item:hover {
                background-color: #3a3a3a;
            }
            QHeaderView::section {
                background-color: transparent;
                color: #e6e6e6;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #393939;
                font-weight: bold;
                font-size: 14px;
            }
            QHeaderView::section:hover {
                background-color: transparent;
                color: #2fa6a0;
            }
        """)

