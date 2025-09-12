from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt

from app.utils.categories import load_categories, save_categories


class CategoryManagerDialog(QDialog):
    """Small dialog to add/remove product categories persisted in app/data/categories.json."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Gerenciar categorias')
        self.setLayout(QVBoxLayout())
        self.list = QListWidget()
        self.list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.layout().addWidget(self.list)

        btn_row = QHBoxLayout()
        self.btn_add = QPushButton('Adicionar')
        self.btn_remove = QPushButton('Remover selecionado')
        self.btn_save = QPushButton('Salvar e fechar')
        self.btn_cancel = QPushButton('Cancelar')

        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_remove)
        btn_row.addWidget(self.btn_save)
        btn_row.addWidget(self.btn_cancel)
        self.layout().addLayout(btn_row)

        self.btn_add.clicked.connect(self.on_add)
        self.btn_remove.clicked.connect(self.on_remove)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_cancel.clicked.connect(self.reject)

        # load existing categories
        self._load()

    def _load(self):
        cats = load_categories()
        self.list.clear()
        for c in cats:
            self.list.addItem(str(c))

    def on_add(self):
        text, ok = QInputDialog.getText(self, 'Adicionar categoria', 'Nome da categoria:')
        if not ok:
            return
        name = text.strip()
        if not name:
            QMessageBox.information(self, 'Inválido', 'Nome vazio não permitido')
            return
        # prevent duplicates
        for i in range(self.list.count()):
            if self.list.item(i).text() == name:
                QMessageBox.information(self, 'Existente', 'Categoria já existe')
                return
        self.list.addItem(name)

    def on_remove(self):
        sel = self.list.currentRow()
        if sel < 0:
            QMessageBox.information(self, 'Nada selecionado', 'Selecione uma categoria para remover')
            return
        item_text = self.list.item(sel).text()
        resp = QMessageBox.question(self, 'Confirmar remoção', f'Remover "{item_text}"?')
        if int(resp) != int(QMessageBox.StandardButton.Yes):
            return
        self.list.takeItem(sel)

    def on_save(self):
        cats = [self.list.item(i).text() for i in range(self.list.count())]
        if not cats:
            QMessageBox.information(self, 'Inválido', 'Pelo menos uma categoria é necessária')
            return
        ok = save_categories(cats)
        if ok:
            QMessageBox.information(self, 'Salvo', 'Categorias salvas com sucesso')
            self.accept()
        else:
            QMessageBox.critical(self, 'Erro', 'Falha ao salvar categorias')
