
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
from .__init__ import PedidosModal

def _refresh_produtos_ui(self):
    # Limpar UI
    try:
        # if using a QVBoxLayout as container
        while self.lista_produtos_container.count():
            item = self.lista_produtos_container.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
    except Exception:
        pass
    # Recriar linhas
    try:
        for idx, prod in enumerate(self.produtos_list):
            row = QHBoxLayout()
            cor_txt = prod.get('cor') or ''
            reforco_txt = 'sim' if prod.get('reforco') else 'não'
            extras = []
            if cor_txt:
                extras.append(f"Cor: {cor_txt}")
            if 'reforco' in prod:
                extras.append(f"Reforço: {reforco_txt}")
            extras_txt = ("  —  " + "  |  ".join(extras)) if extras else ""
            lbl = QLabel(f"• {prod['descricao']}{extras_txt}")
            lbl.setStyleSheet("color: #cccccc")
            # Formatação brasileira: milhar com ponto, centavos com vírgula
            valor = prod.get('valor', 0.0)
            valor_fmt = f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
            val = QLabel(valor_fmt)
            val.setStyleSheet("color: #00ff88; font-weight: bold;")
            btn_rem = QPushButton("Remover")
            btn_rem.setMaximumWidth(90)
            try:
                btn_rem.clicked.connect(lambda _, i=idx: self._remove_produto(i))
            except Exception:
                pass
            row.addWidget(lbl, stretch=1)
            row.addWidget(val)
            row.addWidget(btn_rem)
            row_w = QWidget()
            row_w.setLayout(row)
            try:
                row_w.setStyleSheet("QWidget { background: #3a3a3a; border: 1px solid #505050; border-radius: 6px; padding: 6px; }")
            except Exception:
                pass
            try:
                self.lista_produtos_container.addWidget(row_w)
            except Exception:
                pass
        try:
            self.lista_produtos_container.addStretch()
        except Exception:
            pass
    except Exception:
        pass
    try:
        # Reusar recalculo delegado
        if hasattr(self, '_recalcular_total'):
            self._recalcular_total()
    except Exception:
        pass
