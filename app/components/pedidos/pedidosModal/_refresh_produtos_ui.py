
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
            reforco = 'Sim' if prod.get('reforco') else 'Não'
            db_marker = '' if prod.get('_source') != 'db' else '[DB] '
            table.setItem(idx, 0, QTableWidgetItem(f"{db_marker}{desc}"))
            table.setItem(idx, 1, QTableWidgetItem(f"{float(valor):.2f}"))
            table.setItem(idx, 2, QTableWidgetItem(cor))
            table.setItem(idx, 3, QTableWidgetItem(reforco))
            # actions: place Edit and Remove buttons
            from PyQt6.QtWidgets import QWidget, QHBoxLayout
            btn_widget = QWidget()
            layout = QHBoxLayout(btn_widget)
            layout.setContentsMargins(0,0,0,0)
            btn_edit = QPushButton('Editar')
            btn_edit.setMaximumWidth(70)
            btn_edit.clicked.connect(lambda _, i=idx: self._editar_produto(i))
            btn_rem = QPushButton('Remover')
            btn_rem.setMaximumWidth(70)
            btn_rem.clicked.connect(lambda _, i=idx: self._remove_produto(i))
            layout.addWidget(btn_edit)
            layout.addWidget(btn_rem)
            table.setCellWidget(idx, 4, btn_widget)
        # Recalcular total
        try:
            if hasattr(self, '_recalcular_total'):
                self._recalcular_total()
        except Exception:
            pass
    except Exception:
        pass
