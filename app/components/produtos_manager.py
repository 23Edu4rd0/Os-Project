from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QLabel, QDialog, QFormLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from database import db_manager


class ProdutoDialog(QDialog):
    def __init__(self, parent=None, produto=None):
        super().__init__(parent)
        self.setWindowTitle("Produto")
        self.setFixedSize(420, 240)
        lay = QVBoxLayout(self)
        form = QFormLayout()
        self.nome = QLineEdit()
        self.preco = QLineEdit()
        self.descricao = QLineEdit()
        self.categoria = QLineEdit()
        form.addRow("Nome:", self.nome)
        form.addRow("Preço (R$):", self.preco)
        form.addRow("Descrição:", self.descricao)
        form.addRow("Categoria:", self.categoria)
        lay.addLayout(form)
        btns = QHBoxLayout()
        bcancel = QPushButton("Cancelar"); bsave = QPushButton("Salvar")
        bcancel.clicked.connect(self.reject); bsave.clicked.connect(self.accept)
        btns.addStretch(); btns.addWidget(bcancel); btns.addWidget(bsave)
        lay.addLayout(btns)
        if produto:
            self.nome.setText(produto[1] or "")
            self.preco.setText(str(produto[2] or 0))
            self.descricao.setText(produto[3] or "")
            self.categoria.setText(produto[4] or "")

    def get_values(self):
        nome = self.nome.text().strip()
        try:
            preco = float((self.preco.text() or "0").replace(',', '.'))
        except Exception:
            preco = 0.0
        return nome, preco, self.descricao.text().strip(), self.categoria.text().strip()


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

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Nome", "Preço", "Categoria", "Descrição"])
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        lay.addWidget(self.table)

        actions = QHBoxLayout()
        self.btn_edit = QPushButton("Editar"); self.btn_del = QPushButton("Excluir")
        self.btn_edit.clicked.connect(self._editar)
        self.btn_del.clicked.connect(self._excluir)
        actions.addStretch(); actions.addWidget(self.btn_edit); actions.addWidget(self.btn_del)
        lay.addLayout(actions)

        self.setStyleSheet("""
            QWidget { background-color: #2d2d2d; color: #fff; }
            QLineEdit { background: #404040; border: 1px solid #606060; border-radius: 5px; padding: 6px; }
            QPushButton { background: #0d7377; color:#fff; border:none; border-radius:6px; padding:8px 12px; }
            QPushButton:hover { background:#0a5d61; }
            QTableWidget { background:#303030; }
        """)

    def _load(self):
        busca = self.busca.text().strip()
        rows = db_manager.listar_produtos(busca=busca)
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount(); self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(r[1] or ""))
            self.table.setItem(i, 1, QTableWidgetItem(f"R$ {float(r[2] or 0):.2f}"))
            self.table.setItem(i, 2, QTableWidgetItem(r[4] or ""))
            self.table.setItem(i, 3, QTableWidgetItem(r[3] or ""))
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(str(r[0])))  # store id in header

    def _get_selected_id(self):
        idx = self.table.currentRow()
        if idx < 0:
            return None
        header_item = self.table.verticalHeaderItem(idx)
        return int(header_item.text()) if header_item else None

    def _novo(self):
        dlg = ProdutoDialog(self)
        if dlg.exec():
            nome, preco, desc, cat = dlg.get_values()
            if nome:
                db_manager.inserir_produto(nome, preco, desc, cat)
                self._load()

    def _editar(self):
        pid = self._get_selected_id()
        if pid is None:
            return
        # Buscar linha
        for i in range(self.table.rowCount()):
            if int(self.table.verticalHeaderItem(i).text()) == pid:
                nome = self.table.item(i,0).text()
                preco = self.table.item(i,1).text().replace('R$','').strip()
                cat = self.table.item(i,2).text()
                desc = self.table.item(i,3).text()
                produto = (pid, nome, float(preco.replace(',','.')), desc, cat)
                break
        else:
            return
        dlg = ProdutoDialog(self, produto=produto)
        if dlg.exec():
            nome, preco, desc, cat = dlg.get_values()
            db_manager.atualizar_produto(pid, nome, preco, desc, cat)
            self._load()

    def _excluir(self):
        pid = self._get_selected_id()
        if pid is None:
            return
        db_manager.deletar_produto(pid)
        self._load()
