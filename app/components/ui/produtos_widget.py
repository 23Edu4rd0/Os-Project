from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt

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
        search_row.addWidget(self.btn_novo)
        layout.addLayout(search_row)

        # Table
        self.produtos_table = QTableWidget(0, 4)
        self.produtos_table.setHorizontalHeaderLabels(['Nome', 'Valor', 'Categoria', 'Observação'])
        self.produtos_table.setAlternatingRowColors(True)
        self.produtos_table.setStyleSheet('''
            QTableWidget {
                background-color: #23272e;
                color: #f8f8f2;
                border-radius: 10px;
                font-size: 15px;
                gridline-color: #44475a;
                selection-background-color: #44475a;
                alternate-background-color: #282a36;
            }
            QHeaderView::section {
                background-color: #44475a;
                color: #50fa7b;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                padding: 8px;
            }
            QTableWidget::item {
                padding: 8px;
            }
        ''')
        header = self.produtos_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.produtos_table)

        # Exemplo de preenchimento
        self.add_produto('Caixa sei la o que', 'R$ 5000.00', 'ai', 'Ui')
        self.add_produto('Cx7gvt60', 'R$ 830.00', 'Caixa Agro', '')

    def add_produto(self, nome, valor, categoria, obs):
        row = self.produtos_table.rowCount()
        self.produtos_table.insertRow(row)
        self.produtos_table.setItem(row, 0, QTableWidgetItem(nome))
        self.produtos_table.setItem(row, 1, QTableWidgetItem(valor))
        self.produtos_table.setItem(row, 2, QTableWidgetItem(categoria))
        self.produtos_table.setItem(row, 3, QTableWidgetItem(obs))
