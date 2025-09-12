
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget, QTableWidgetItem
from .__init__ import PedidosModal

def _refresh_produtos_ui(self):
    # Use QTableWidget lista_produtos_table
    try:
        table = getattr(self, 'lista_produtos_table', None)
        if table is None:
            return
        table.setRowCount(0)
        for idx, prod in enumerate(self.produtos_list):
            table.insertRow(idx)
            desc = prod.get('descricao') or ''
            valor = prod.get('valor') or 0.0
            cor = prod.get('cor') or ''
            divisorias = prod.get('divisorias', 0)  # Novo campo divisórias
            db_marker = '' if prod.get('_source') != 'db' else '[DB] '
            
            # Preencher células da tabela com estilo consistente
            desc_item = QTableWidgetItem(f"{db_marker}{desc}")
            desc_item.setBackground(table.palette().base())
            table.setItem(idx, 0, desc_item)
            
            valor_item = QTableWidgetItem(f"{float(valor):.2f}")
            valor_item.setBackground(table.palette().base())
            table.setItem(idx, 1, valor_item)
            
            cor_item = QTableWidgetItem(cor if cor else "")
            cor_item.setBackground(table.palette().base())
            table.setItem(idx, 2, cor_item)
            
            div_item = QTableWidgetItem(str(divisorias))
            div_item.setBackground(table.palette().base())
            table.setItem(idx, 3, div_item)
            
            # Botões de ação
            from PyQt6.QtWidgets import QWidget, QHBoxLayout
            btn_widget = QWidget()
            btn_widget.setStyleSheet('''
                QWidget {
                    background-color: #2d2d2d;
                    border: none;
                }
            ''')
            layout = QHBoxLayout(btn_widget)
            layout.setContentsMargins(6, 4, 6, 4)
            layout.setSpacing(8)
            
            # Botão Editar
            btn_edit = QPushButton('Editar')
            btn_edit.setFixedSize(70, 28)
            btn_edit.setStyleSheet('''
                QPushButton {
                    background-color: #0d7377;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0a5d61;
                }
            ''')
            btn_edit.clicked.connect(lambda _, i=idx: self._editar_produto(i))
            
            # Botão Remover
            btn_rem = QPushButton('Remover')
            btn_rem.setFixedSize(70, 28)
            btn_rem.setStyleSheet('''
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            ''')
            btn_rem.clicked.connect(lambda _, i=idx: self._remove_produto(i))
            
            layout.addWidget(btn_edit)
            layout.addWidget(btn_rem)
            table.setCellWidget(idx, 4, btn_widget)  # Coluna 4 para ações (5 colunas no total)
        # Recalcular total
        try:
            if hasattr(self, '_recalcular_total'):
                self._recalcular_total()
        except Exception:
            pass
    except Exception:
        pass
