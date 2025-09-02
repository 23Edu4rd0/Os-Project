from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QDoubleSpinBox, QPushButton, QFormLayout, QMessageBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from database import db_manager
from datetime import datetime


class GastosDialog(QDialog):
    """Dialog estilizado para criar/editar um gasto.

    - foco inicial na descrição
    - Enter no campo descrição salva
    - botões com estilo, diálogo com largura fixa
    """
    gasto_adicionado = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._gasto_id = None
        self.setWindowTitle("Adicionar Gasto")
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setFixedWidth(380)
        self._build_ui()

    def _build_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(12)
        self.layout().setContentsMargins(12, 12, 12, 12)

        # Styling
        self.setStyleSheet('''
            QDialog { background: #2e2e2e; color: #e6e6e6 }
            QLabel { color: #e6e6e6 }
            QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox { background: #3a3a3a; color: #ffffff; border: 1px solid #444; padding: 4px; border-radius: 4px }
            QPushButton#cancel { background: transparent; color: #cccccc; padding: 6px 12px; border: 1px solid #444; border-radius: 6px }
            QPushButton#save { background: #0d7377; color: white; padding: 6px 12px; border-radius: 6px }
            QPushButton#save:hover { background: #139a9c }
        ''')

        # Form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.tipo = QComboBox()
        # Adicionar 'Salario' como tipo específico para simplificar descrição (nome da pessoa)
        self.tipo.addItems(["Despesa", "Salario", "Serviço", "Compra", "Outro"])
        form.addRow("Tipo:", self.tipo)

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Descrição do gasto (se 'Salario', informe o nome da pessoa)")
        self.descricao.setMinimumWidth(240)
        form.addRow("Descrição:", self.descricao)

        self.valor = QDoubleSpinBox()
        self.valor.setPrefix("R$ ")
        self.valor.setDecimals(2)
        self.valor.setMaximum(1_000_000.00)
        form.addRow("Valor:", self.valor)

        self.data = QDateEdit()
        self.data.setCalendarPopup(True)
        self.data.setDate(QDate.currentDate())
        form.addRow("Data:", self.data)

        self.layout().addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton("Salvar")
        btn_save.setObjectName("save")
        btn_save.clicked.connect(self._on_save)
        btn_save.setDefault(True)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(btn_save)

        # botão excluir (escondido em modo de criação)
        self.btn_delete = QPushButton("Excluir")
        self.btn_delete.setObjectName("delete")
        self.btn_delete.setStyleSheet('background: #c94b4b; color: white; border-radius:6px;')
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_delete.setVisible(False)
        btn_row.addWidget(self.btn_delete)

        self.layout().addLayout(btn_row)

        # Shortcuts and focus
        QShortcut(QKeySequence("Escape"), self, activated=self.reject)
        QShortcut(QKeySequence("Ctrl+S"), self, activated=self._on_save)
        # Enter in description saves
        self.descricao.returnPressed.connect(self._on_save)
        self.descricao.setFocus()

    def _on_save(self):
        descricao = self.descricao.text().strip()
        tipo = self.tipo.currentText()
        valor = float(self.valor.value())
        try:
            data_py = self.data.date().toPyDate()
        except Exception:
            data_py = datetime.now().date()

        if not descricao:
            QMessageBox.warning(self, "Validação", "Informe a descrição do gasto.")
            self.descricao.setFocus()
            return
        if valor <= 0:
            QMessageBox.warning(self, "Validação", "Informe um valor maior que zero.")
            self.valor.setFocus()
            return

        try:
            if self._gasto_id:
                ok = db_manager.atualizar_gasto(self._gasto_id, tipo=tipo, descricao=descricao, valor=valor, data=data_py.strftime("%Y-%m-%d"))
            else:
                ok = db_manager.inserir_gasto(tipo, descricao, valor, data_py.strftime("%Y-%m-%d"))

            if ok:
                QMessageBox.information(self, "Sucesso", "Gasto salvo com sucesso.")
                self.gasto_adicionado.emit()
                self.accept()
            else:
                QMessageBox.critical(self, "Erro", "Falha ao salvar gasto.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar gasto: {e}")

    def load_gasto(self, gasto_id):
        """Carrega dados de um gasto existente no diálogo para edição."""
        row = db_manager.get_gasto(gasto_id)
        if not row:
            QMessageBox.critical(self, "Erro", "Gasto não encontrado.")
            return False
        self._gasto_id, tipo, descricao, valor, data = row
        # preencher campos
        idx = self.tipo.findText(tipo)
        if idx >= 0:
            self.tipo.setCurrentIndex(idx)
        else:
            self.tipo.setCurrentIndex(0)
        self.descricao.setText(str(descricao or ""))
        try:
            self.valor.setValue(float(valor or 0))
        except Exception:
            self.valor.setValue(0.0)
        try:
            qd = QDate.fromString(data, 'yyyy-MM-dd')
            if qd.isValid():
                self.data.setDate(qd)
        except Exception:
            pass
        self.btn_delete.setVisible(True)
        return True

    def _on_delete(self):
        if not self._gasto_id:
            return
        # Passar os botões diretamente (PyQt6 usa StandardButton enums combinados)
        resp = QMessageBox.question(self, 'Confirmar', 'Deseja realmente excluir este gasto?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        try:
            # comparar de forma segura (pode ser enum ou int dependendo da binding)
            if int(resp) == int(QMessageBox.StandardButton.Yes):
                ok = db_manager.deletar_gasto(self._gasto_id)
                if ok:
                    QMessageBox.information(self, 'Sucesso', 'Gasto excluído.')
                    # sinalizar atualização e fechar
                    self.gasto_adicionado.emit()
                    # limpar id local
                    self._gasto_id = None
                    self.accept()
                else:
                    QMessageBox.critical(self, 'Erro', 'Falha ao excluir gasto.')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao confirmar/excluir: {e}')
