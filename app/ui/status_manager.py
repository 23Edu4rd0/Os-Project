from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QInputDialog, QMessageBox
)

from app.utils.statuses import load_statuses, save_statuses
from app.signals import get_signals


class StatusManagerDialog(QDialog):
    """Dialog para gerenciar os status de pedidos persistidos em app/data/statuses.json."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Gerenciar status')
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

        self._load()

    def _load(self):
        sts = load_statuses()
        self.list.clear()
        for s in sts:
            self.list.addItem(str(s))

    def on_add(self):
        text, ok = QInputDialog.getText(self, 'Adicionar status', 'Nome do status:')
        if not ok:
            return
        name = text.strip()
        if not name:
            QMessageBox.information(self, 'Inválido', 'Nome vazio não permitido')
            return
        # prevent duplicates
        for i in range(self.list.count()):
            if self.list.item(i).text() == name:
                QMessageBox.information(self, 'Existente', 'Status já existe')
                return
        self.list.addItem(name)

    def on_remove(self):
        sel = self.list.currentRow()
        if sel < 0:
            QMessageBox.information(self, 'Nada selecionado', 'Selecione um status para remover')
            return
        item_text = self.list.item(sel).text()
        resp = QMessageBox.question(self, 'Confirmar remoção', f'Remover "{item_text}"?')
        if int(resp) != int(QMessageBox.StandardButton.Yes):
            return
        self.list.takeItem(sel)

    def on_save(self):
        sts = [self.list.item(i).text() for i in range(self.list.count())]
        if not sts:
            QMessageBox.information(self, 'Inválido', 'Pelo menos um status é necessário')
            return
        ok = save_statuses(sts)
        if ok:
            QMessageBox.information(self, 'Salvo', 'Status salvos com sucesso')
            # notify app that statuses changed
            try:
                sig = get_signals()
                sig.statuses_updated.emit()
            except Exception:
                pass
            self.accept()
        else:
            QMessageBox.critical(self, 'Erro', 'Falha ao salvar status')
