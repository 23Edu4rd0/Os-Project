from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QDialog, QFormLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database import db_manager


class ProdutoDialog(QDialog):
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)
        self.setWindowTitle("Produto")
        self.setFixedSize(400, 260)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.nome = QLineEdit()
        self.nome.setPlaceholderText("Nome do produto")
        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Código opcional")
        self.preco = QLineEdit()
        self.preco.setPlaceholderText("Ex: 99.90")
        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Descrição opcional")

        from PyQt6.QtWidgets import QComboBox
        self.categoria = QComboBox()
        self.categoria.setEditable(False)
        # placeholder: an empty first item
        self.categoria.addItem("")
        try:
            from app.utils.categories import load_categories
            cats = load_categories()
            if cats:
                # only add non-empty categories
                for c in cats:
                    if str(c).strip():
                        self.categoria.addItem(str(c))
        except Exception:
            self.categoria.addItems(['Agro', 'Normal', 'Outros'])

        form.addRow("<b>Nome:</b>", self.nome)
        form.addRow("<b>Valor:</b>", self.preco)
        form.addRow("<b>Categoria:</b>", self.categoria)
        form.addRow("<b>Código:</b>", self.codigo)
        form.addRow("<b>Descrição:</b>", self.descricao)
        lay.addLayout(form)

        btns = QHBoxLayout()
        bsave = QPushButton("Save")
        bcancel = QPushButton("Cancel")
        bsave.setObjectName('save')
        bcancel.setObjectName('cancel')
        bcancel.clicked.connect(self.reject)

        def try_accept():
            preco_str = self.preco.text().replace(',', '.').strip()
            try:
                preco = float(preco_str)
                if preco <= 0:
                    raise ValueError()
            except Exception:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Erro", "Digite um valor válido e maior que zero para o produto!")
                return
            self.accept()

        bsave.clicked.connect(try_accept)
        btns.addStretch(); btns.addWidget(bsave); btns.addWidget(bcancel)
        lay.addLayout(btns)

        # Apply consistent app palette and input styles
        self.setStyleSheet('''
            QDialog { background-color: #2b2b2b; border-radius: 10px; }
            QLabel { color: #7fd2c9; font-weight: 700; font-size: 13px; }
            QLineEdit, QComboBox {
                background-color: #242424; color: #e6e6e6;
                border: 1px solid #2fa6a0; border-radius: 8px; padding: 8px 10px;
                min-height: 36px; font-size: 14px;
            }
            QLineEdit:focus, QComboBox:focus { border: 1.4px solid #56c6bf; }
            QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 28px; }
            QComboBox QAbstractItemView { background: #232323; color: #e6e6e6; selection-background-color: #2fa6a0; }
            QPushButton#save { background-color: #2fa6a0; color: #061214; border-radius: 8px; padding: 8px 18px; font-weight:700; }
            QPushButton#cancel { background-color: #323232; color: #e6e6e6; border: 1px solid #3a3a3a; border-radius:8px; padding: 8px 18px; }
            QPushButton#save:hover { background-color: #28a399; }
            QPushButton#cancel:hover { background-color: #3a3a3a; }
        ''')

        # Make Save/Cancel buttons look prominent
        try:
            bsave.setMinimumWidth(140); bsave.setFixedHeight(44)
            bcancel.setMinimumWidth(140); bcancel.setFixedHeight(44)
            bsave.setStyleSheet('background-color: #2fa6a0; color: #061214; font-weight:700; border-radius:8px;')
            bcancel.setStyleSheet('background-color: #323232; color: #e6e6e6; border:1px solid #3a3a3a; border-radius:8px;')
        except Exception:
            pass

        if produto:
            self.nome.setText(produto[1] or "")
            self.codigo.setText(produto[2] or "")
            self.preco.setText(str(produto[3] or ""))
            self.descricao.setText(produto[4] or "")
            # try to select existing category; if missing, append it
            try:
                if produto[5]:
                    val = produto[5] or ""
                    if val and self.categoria.findText(val) < 0:
                        self.categoria.addItem(val)
                    self.categoria.setCurrentText(val)
            except Exception:
                pass

    def get_values(self):
        nome = self.nome.text().strip()
        codigo = self.codigo.text().strip()
        preco_str = self.preco.text().replace(',', '.').strip()
        try:
            preco = float(preco_str)
        except Exception:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Valor inválido: '{self.preco.text()}'\nDigite um número válido.")
            print(f"[DEBUG] Valor inválido para preço: '{self.preco.text()}' (convertido: '{preco_str}')")
            preco = 0.0
        print(f"[DEBUG] get_values() -> nome: {nome}, codigo: {codigo}, preco: {preco}, desc: {self.descricao.text().strip()}, cat: {self.categoria.currentText().strip()}")
        return nome, codigo, preco, self.descricao.text().strip(), self.categoria.currentText().strip()


class ProdutosManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup()
        self._load()

    def _setup(self):
        lay = QVBoxLayout(self)
        top = QHBoxLayout()
        self.busca = QLineEdit(); self.busca.setPlaceholderText("Buscar produto...")
        btn_buscar = QPushButton("Buscar"); btn_novo = QPushButton("Novo")
        btn_buscar.clicked.connect(self._load)
        btn_novo.clicked.connect(self._novo)
        top.addWidget(QLabel("Produtos")); top.addStretch()
        top.addWidget(self.busca); top.addWidget(btn_buscar); top.addWidget(btn_novo)
        lay.addLayout(top)

        # Default table shows "produtos vendidos" from orders
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["OS", "Descrição", "Valor", "Cor", "Código", "Data"])
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        # Ensure columns are visible and properly sized
        self.table.resizeColumnsToContents()
        self.table.setColumnWidth(0, 80)   # OS
        self.table.setColumnWidth(1, 300)  # Descrição
        self.table.setColumnWidth(2, 100)  # Valor
        self.table.setColumnWidth(3, 100)  # Cor
        self.table.setColumnWidth(4, 80)   # Código
        self.table.setColumnWidth(5, 160)  # Data
        lay.addWidget(self.table)

        actions = QHBoxLayout()
        self.btn_edit = QPushButton("Editar"); self.btn_del = QPushButton("Excluir")
        self.btn_toggle = QPushButton("Mostrar Catálogo")
        self.btn_toggle.setToolTip('Alterna entre catálogo de produtos e produtos vendidos nas ordens')
        self.btn_toggle.clicked.connect(self._toggle_view)
        self.btn_edit.clicked.connect(self._editar)
        self.btn_del.clicked.connect(self._excluir)
        actions.addStretch(); actions.addWidget(self.btn_toggle); actions.addWidget(self.btn_edit); actions.addWidget(self.btn_del)
        lay.addLayout(actions)

        self.setStyleSheet("""
            QWidget { background-color: #2d2d2d; color: #fff; }
            QLineEdit { background: #404040; border: 1px solid #606060; border-radius: 5px; padding: 6px; }
            QPushButton { background: #0d7377; color:#fff; border:none; border-radius:6px; padding:8px 12px; }
            QPushButton:hover { background:#0a5d61; }
            QTableWidget { background:#303030; color: #fff; gridline-color: #555; }
            QHeaderView::section { background: #404040; color: #fff; padding: 4px; border: none; }
            QTableWidget::item { padding: 4px; }
        """)

    def _load(self):
        busca = self.busca.text().strip()
        # if view is vendas, show products extracted from orders
        try:
            if getattr(self, '_view_vendas', True):
                rows = db_manager.listar_produtos_vendidos(busca=busca)
                mode = 'vendas'
            else:
                rows = db_manager.listar_produtos(busca=busca)
                mode = 'catalogo'
        except Exception:
            rows = []
            mode = 'vendas'
        # DEBUG: mostrar todos os registros reais do banco
        import sqlite3
        from database.db_setup import DatabaseSetup
        db_path = DatabaseSetup.get_database_path()
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        print("[DEBUG] REGISTROS REAIS DA TABELA produtos:")
        try:
            for row in cur.execute("SELECT id, nome, preco, codigo, descricao, categoria FROM produtos"):
                print("  ", row)
        except Exception as e:
            print("[DEBUG] Erro ao ler tabela produtos:", e)
        conn.close()
        # Fim debug
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount(); self.table.insertRow(i)
            if mode == 'vendas':
                # row dict: {'ordem_id','numero_os','data_criacao','descricao','valor','cor','reforco'}
                os_num = str(r.get('numero_os') or '')
                desc = r.get('descricao') or ''
                valor = f"R$ {float(r.get('valor') or 0):.2f}"
                cor = r.get('cor') or ''
                reforco = 'Sim' if r.get('reforco') else 'Não'
                codigo = r.get('codigo') or ''
                data = str(r.get('data_criacao') or '')
                self.table.setItem(i, 0, QTableWidgetItem(os_num))
                self.table.setItem(i, 1, QTableWidgetItem(desc))
                self.table.setItem(i, 2, QTableWidgetItem(valor))
                self.table.setItem(i, 3, QTableWidgetItem(cor))
                self.table.setItem(i, 4, QTableWidgetItem(codigo))
                self.table.setItem(i, 5, QTableWidgetItem(data))
                # store ordem_id in header
                self.table.setVerticalHeaderItem(i, QTableWidgetItem(str(r.get('ordem_id'))))
            else:
                # catalog mode uses existing schema (id, nome, codigo, preco, descricao, categoria)
                nome = r[1] or ""
                codigo = r[2] or ""
                preco = f"R$ {float(r[3] or 0):.2f}"
                categoria = r[5] or ""
                descricao = r[4] or ""
                self.table.setItem(i, 0, QTableWidgetItem(str(r[0] or '')))
                self.table.setItem(i, 1, QTableWidgetItem(nome))
                self.table.setItem(i, 2, QTableWidgetItem(preco))
                self.table.setItem(i, 3, QTableWidgetItem(categoria))
                self.table.setItem(i, 4, QTableWidgetItem(descricao))
                self.table.setItem(i, 5, QTableWidgetItem(str(r[6] if len(r) > 6 else '')))
        
        # Ensure columns are properly sized after loading data
        self.table.resizeColumnsToContents()
        self.table.update()

    def _toggle_view(self):
        self._view_vendas = not getattr(self, '_view_vendas', True)
        if self._view_vendas:
            self.btn_toggle.setText('Mostrar Catálogo')
        else:
            self.btn_toggle.setText('Mostrar Vendidos')
        self._load()

    def _get_selected_id(self):
        idx = self.table.currentRow()
        if idx < 0:
            return None
        header_item = self.table.verticalHeaderItem(idx)
        return int(header_item.text()) if header_item else None

    def _novo(self):
        dlg = ProdutoDialog(self)
        if dlg.exec():
            nome, codigo, preco, desc, cat = dlg.get_values()
            print(f"[DEBUG] _novo() -> nome: {nome}, codigo: {codigo}, preco: {preco}, desc: {desc}, cat: {cat}")
            if nome:
                try:
                    res = db_manager.inserir_produto(nome, preco, desc, cat, codigo or None)
                except TypeError:
                    res = db_manager.inserir_produto(nome, preco, desc, cat)
                print(f"[DEBUG] Produto inserido, retorno do DB: {res}")
                self._load()

    def _editar(self):
        pid = self._get_selected_id()
        if pid is None:
            return
        # Buscar linha
        for i in range(self.table.rowCount()):
            if int(self.table.verticalHeaderItem(i).text()) == pid:
                nome = self.table.item(i,0).text()
                codigo = self.table.item(i,1).text()
                preco_str = self.table.item(i,2).text().replace('R$','').replace(',','.').strip()
                try:
                    preco = float(preco_str)
                except Exception:
                    preco = 0.0
                cat = self.table.item(i,3).text()
                desc = self.table.item(i,4).text()
                produto = (pid, nome, codigo, preco, desc, cat)
                break
        else:
            return
        dlg = ProdutoDialog(self, produto=produto)
        if dlg.exec():
            nome, codigo, preco, desc, cat = dlg.get_values()
            print(f"[DEBUG] _editar() -> pid: {pid}, nome: {nome}, codigo: {codigo}, preco: {preco}, desc: {desc}, cat: {cat}")
            try:
                res = db_manager.atualizar_produto(pid, nome, preco, desc, cat, codigo or None)
            except Exception:
                res = db_manager.atualizar_produto(pid, nome, preco, desc, cat)
            print(f"[DEBUG] Produto atualizado, retorno do DB: {res}")
            self._load()

    def _excluir(self):
        pid = self._get_selected_id()
        if pid is None:
            return
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Confirmar", "Tem certeza que deseja excluir este produto?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            res = db_manager.deletar_produto(pid)
            print(f"[DEBUG] Produto excluído, retorno do DB: {res}")
            self._load()
