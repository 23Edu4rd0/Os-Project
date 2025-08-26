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
        self.tipo.addItems(["Despesa", "Serviço", "Compra", "Outro"])
        form.addRow("Tipo:", self.tipo)

        self.descricao = QLineEdit()
        self.descricao.setPlaceholderText("Descrição do gasto")
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
            db_manager.inserir_gasto(tipo, descricao, valor, data_py.strftime("%Y-%m-%d"))
            QMessageBox.information(self, "Sucesso", "Gasto salvo com sucesso.")
            self.gasto_adicionado.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar gasto: {e}")
