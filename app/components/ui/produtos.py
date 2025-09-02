from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QDialog, QFormLayout, QDialogButtonBox, QMessageBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt
from database import db_manager


class ProdutoDialog(QDialog):
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)
        self.setWindowTitle('Produto')
        self.setMinimumWidth(420)
        layout = QFormLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        # Align labels to the right so inputs line up nicely
        try:
            layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        except Exception:
            # PyQt6 compatibility fallback
            layout.setLabelAlignment(Qt.Alignment.AlignRight)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        # Use the app's dark-gray + teal-accent palette for consistency
        self.setStyleSheet('''
            QDialog { background-color: #2b2b2b; border-radius: 10px; }
            QLabel { color: #7fd2c9; font-size: 14px; font-weight: 700; padding-right: 8px; }
            QLineEdit, QComboBox {
                background-color: #242424; color: #e6e6e6;
                border: 1px solid #2fa6a0; border-radius: 8px; padding: 10px 12px; font-size: 14px; min-height: 38px;
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

