from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QDialog, QFormLayout, QDialogButtonBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from database import db_manager


class ProdutoDialog(QDialog):
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)
        self.setWindowTitle('Produto')
        self.setMinimumWidth(380)
        layout = QFormLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)
        self.setStyleSheet('''
            QDialog {
                background-color: #23272e;
                border-radius: 12px;
            }
            QLabel {
                color: #50fa7b;
                font-size: 15px;
                font-weight: bold;
                padding-bottom: 2px;
            }
            QLineEdit {
                background-color: #282a36;
                color: #f8f8f2;
                border: 1.5px solid #50fa7b;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 15px;
                margin-bottom: 2px;
            }
            QLineEdit:focus {
                border: 2px solid #8be9fd;
                background-color: #23272e;
            }
            QDialogButtonBox QPushButton {
                background-color: #50fa7b;
                color: #23272e;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: bold;
                font-size: 15px;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                background-color: #40c97b;
            }
        ''')
        self.input_nome = QLineEdit()
        self.input_valor = QLineEdit()
        self.input_categoria = QLineEdit()
        self.input_reforco = QCheckBox('Sim')
        layout.addRow('Nome:', self.input_nome)
        layout.addRow('Valor:', self.input_valor)
        layout.addRow('Categoria:', self.input_categoria)
        layout.addRow('Reforço:', self.input_reforco)

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
            self.input_categoria.setText(str(produto.get('categoria', '')))
            self.input_reforco.setChecked(str(produto.get('reforco', '')).lower() in ['sim', 'true', '1'])

    def buscar_sugestoes(self, texto):
        if not texto.strip():
            self.sugestoes.hide()
            return
        produtos = db_manager.listar_produtos(busca=texto, limite=8)
        self.sugestoes.clear()
        for prod in produtos:
            nome = prod[1]
            valor = prod[2]
            categoria = prod[4]
            reforco = prod[3]
            item = QListWidgetItem(f"{nome} | R$ {float(valor or 0):.2f} | {categoria}")
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
        valor = float(prod[2] or 0)
        if valor > 9999:
            valor = valor / 100
        self.input_valor.setText(f"{valor:.2f}")
        self.input_categoria.setText(str(prod[4] or ''))
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
            'categoria': self.input_categoria.text().strip(),
            'reforco': 'Sim' if self.input_reforco.isChecked() else 'Não'
        }
        self.input_reforco.setChecked(prod[3] in [1, True, '1', 'Sim', 'sim', 'True', 'true'])
        self.sugestoes.hide()
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)
        if produto:
            self.input_nome.setText(str(produto.get('nome', '')))
            self.input_valor.setText(str(produto.get('valor', '')))
            self.input_categoria.setText(str(produto.get('categoria', '')))
            # Considera reforco True/1/'Sim' como marcado
            reforco_val = produto.get('reforco', False)
            if str(reforco_val).lower() in ['1', 'true', 'sim', 'yes']:
                self.input_reforco.setChecked(True)
            else:
                self.input_reforco.setChecked(False)
    def get_data(self):
        return {
            'nome': self.input_nome.text().strip(),
            'valor': self.input_valor.text().strip(),
            'categoria': self.input_categoria.text().strip(),
            'reforco': 1 if self.input_reforco.isChecked() else 0,
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
        header.setStyleSheet('font-size: 22px; font-weight: bold; color: #50fa7b; padding-bottom: 8px;')
        layout.addWidget(header)

        # Search bar and buttons
        search_row = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText('Buscar produto...')
        self.input_busca.setStyleSheet('''
            QLineEdit {
                background-color: #282a36;
                color: #f8f8f2;
                border: 1.5px solid #50fa7b;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
            }
        ''')
        search_row.addWidget(self.input_busca, stretch=1)

        self.btn_buscar = QPushButton('Buscar')
        self.btn_buscar.setStyleSheet('''
            QPushButton {
                background-color: #50fa7b;
                color: #23272e;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #40c97b;
            }
        ''')
        search_row.addWidget(self.btn_buscar)

        self.btn_novo = QPushButton('Novo')
        self.btn_novo.setStyleSheet('''
            QPushButton {
                background-color: #6272a4;
                color: #fff;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7082c4;
            }
        ''')
        self.btn_deletar = QPushButton('Deletar')
        self.btn_deletar.setStyleSheet('''
            QPushButton {
                background-color: #ff5555;
                color: #fff;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ff8888;
            }
        ''')
        search_row.addWidget(self.btn_novo)
        search_row.addWidget(self.btn_deletar)
        layout.addLayout(search_row)

        # Table
        self.produtos_table = QTableWidget(0, 5)
        self.produtos_table.setHorizontalHeaderLabels(['ID', 'Nome', 'Valor', 'Categoria', 'Reforço'])
        self.produtos_table.verticalHeader().setVisible(False)
        self.produtos_table.setAlternatingRowColors(True)
        self.produtos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.produtos_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.produtos_table.setStyleSheet('''
            QTableWidget {
                background-color: #23272e;
                color: #f8f8f2;
                 border-radius: 10px;
                font-size: 15px;
                gridline-color: #44475a;
                selection-background-color: #353535;
                alternate-background-color: #282a36;
            }
        ''')

        # Set table palette and header style
        from PyQt6.QtGui import QPalette, QColor
        palette = self.produtos_table.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#23272e"))
        palette.setColor(QPalette.ColorRole.Window, QColor("#23272e"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#282a36"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#f8f8f2"))
        self.produtos_table.setPalette(palette)
        header = self.produtos_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { background-color: #000; color: #fff; font-weight: bold; font-size: 16px; }")
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
                # produto: (id, nome, preco, descricao, categoria, criado_em)
                id = produto[0]
                nome = produto[1]
                valor = f"R$ {float(produto[2] or 0):.2f}"
                categoria = produto[4] or ""
                reforco = "Sim" if produto[3] in [1, True, '1', 'Sim', 'sim', 'True', 'true'] else "Não"
                row = self.produtos_table.rowCount()
                self.produtos_table.insertRow(row)
                self.produtos_table.setItem(row, 0, QTableWidgetItem(str(id)))
                self.produtos_table.setItem(row, 1, QTableWidgetItem(nome))
                self.produtos_table.setItem(row, 2, QTableWidgetItem(valor))
                self.produtos_table.setItem(row, 3, QTableWidgetItem(categoria))
                self.produtos_table.setItem(row, 4, QTableWidgetItem(reforco))
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
            ok = db_manager.inserir_produto(data['nome'], valor, data['reforco'], data['categoria'])
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
        reforco = self.produtos_table.item(row, 4).text()
        dialog = ProdutoDialog(self, produto={'nome': nome, 'valor': valor, 'categoria': categoria, 'reforco': reforco})
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                valor = float(data['valor'].replace('R$', '').replace(',', '.'))
            except Exception:
                valor = 0.0
            ok = db_manager.atualizar_produto(produto_id, data['nome'], valor, data['reforco'], data['categoria'])
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
