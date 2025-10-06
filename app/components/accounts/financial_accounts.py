from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox,
    QGroupBox, QFrame, QTableWidget, QTableWidgetItem, QSizePolicy
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QDate
from database import db_manager
from datetime import datetime, timedelta

# Matplotlib imports
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ContasFinanceiroWidget(QWidget):
    """Dashboard financeiro: mostra vendas, gastos e lucros usando apenas o DB."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._build_ui()
        self._connect()
        # default filter: mês atual
        self.filter_mode = 'mes'
        self.refresh()

    def _build_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(12)
        # Dark background to match app
        self.setStyleSheet("""
            QWidget { background: #2d2d2d; color: #e6e6e6 }
            QGroupBox { border: 1px solid #404040; border-radius: 8px; margin-top: 8px; padding: 8px; }
            QGroupBox:title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
        """)

        # Top controls: filter
        ctrl_row = QHBoxLayout()
        ctrl_row.addWidget(QLabel("Período:"))
        self.combo_period = QComboBox()
        self.combo_period.addItems(["Este Mês", "Últimos 3 Meses", "Este Ano"])
        ctrl_row.addWidget(self.combo_period)
        ctrl_row.addStretch()
        btn_refresh = QPushButton("Atualizar Dados")
        btn_refresh.clicked.connect(self.refresh)
        ctrl_row.addWidget(btn_refresh)
        self.layout().addLayout(ctrl_row)

        # Cards
        cards_row = QHBoxLayout()
        self.card_vendas = self._make_card("Total Vendas", "R$ 0.00", color="#00c48c")
        self.card_gasto = self._make_card("Gasto (mês)", "R$ 0.00", color="#ffaa33")
        self.card_lucro = self._make_card("Lucro Líquido", "R$ 0.00", color="#66d9ef")
        self.card_caixas = self._make_card("Caixas Vendidas", "0", color="#ff6b9d")
        cards_row.addWidget(self.card_vendas)
        cards_row.addWidget(self.card_gasto)
        cards_row.addWidget(self.card_lucro)
        cards_row.addWidget(self.card_caixas)
        self.layout().addLayout(cards_row)

        # Chart area
        chart_box = QGroupBox("Vendas")
        chart_layout = QVBoxLayout(chart_box)
        # Make figure dark to blend with UI
        self.figure = Figure(figsize=(8, 3), facecolor='#2d2d2d')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #2d2d2d;")
        chart_layout.addWidget(self.canvas)
        self.layout().addWidget(chart_box)

        # Expenses table
        gastos_box = QGroupBox("Gastos")
        gastos_layout = QVBoxLayout(gastos_box)
        self.table_gastos = QTableWidget(0, 3)
        self.table_gastos.setHorizontalHeaderLabels(["Tipo", "Descrição", "Valor (R$)"])
        self.table_gastos.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Styling for table: dark theme and alternating rows
        self.table_gastos.setAlternatingRowColors(True)
        self.table_gastos.setStyleSheet('''
            QTableWidget { background: #2f2f2f; color: #e6e6e6; gridline-color: #444444 }
            QHeaderView::section { background: #3a3a3a; color: #e6e6e6; padding: 4px; border: none }
        ''')
        # Ensure header stretches
        try:
            hdr = self.table_gastos.horizontalHeader()
            hdr.setSectionResizeMode(0, hdr.ResizeMode.Stretch)
            hdr.setSectionResizeMode(1, hdr.ResizeMode.Stretch)
            hdr.setSectionResizeMode(2, hdr.ResizeMode.ResizeToContents)
        except Exception:
            # fallback for PyQt versions
            try:
                from PyQt6.QtWidgets import QHeaderView
                self.table_gastos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            except Exception:
                pass

        gastos_layout.addWidget(self.table_gastos)
        self.layout().addWidget(gastos_box)

    def _make_card(self, title, value, color="#00ff88"):
        w = QGroupBox(title)
        w.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        w.setStyleSheet(f"QGroupBox {{ background: #333333; border: 1px solid {color}; border-radius: 8px; padding: 8px }}")
        w.setMinimumHeight(90)
        l = QVBoxLayout(w)
        lbl = QLabel(value)
        lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {color}")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addStretch()
        l.addWidget(lbl)
        l.addStretch()
        w.value_label = lbl
        return w

    def _connect(self):
        self.combo_period.currentIndexChanged.connect(lambda _: self.refresh())

    def refresh(self):
        idx = self.combo_period.currentIndex()
        if idx == 0:
            # Este mês
            hoje = datetime.now()
            inicio = hoje.replace(day=1).strftime('%Y-%m-%d')
            fim = hoje.strftime('%Y-%m-%d')
            mode = 'mes'
        elif idx == 1:
            # Últimos 3 meses (12 semanas)
            hoje = datetime.now()
            inicio_dt = hoje - timedelta(weeks=12)
            inicio = inicio_dt.strftime('%Y-%m-%d')
            fim = hoje.strftime('%Y-%m-%d')
            mode = '3meses'
        else:
            # Ano atual
            hoje = datetime.now()
            inicio = hoje.replace(month=1, day=1).strftime('%Y-%m-%d')
            fim = hoje.strftime('%Y-%m-%d')
            mode = 'ano'

        # Total vendas (somar valor_produto + frete) exceto pedidos cancelados
        vendas = self.db.calcular_resumo_vendas(inicio, fim) if hasattr(self.db, 'calcular_resumo_vendas') else self.db.calcular_resumo_vendas(inicio, fim)
        # calcular_resumo_vendas retorna (total_vendas, total_valor, total_entradas, ticket) or similar from ReportQueries
        total_vendas = float((vendas[1] or 0) if len(vendas) > 1 else (vendas or 0))

        # Gasto mensal (somar gastos na janela atual)
        gasto_total = float(self.db.soma_gastos_periodo(inicio, fim) if hasattr(self.db, 'soma_gastos_periodo') else 0.0)

        # Lucro líquido
        lucro = total_vendas - gasto_total

        # Caixas vendidas heurística
        caixas = int(self.db.contar_caixas_vendidas_periodo(inicio, fim))

        # Atualizar cartões
        self.card_vendas.value_label.setText(f"R$ {total_vendas:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        self.card_gasto.value_label.setText(f"R$ {gasto_total:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        self.card_lucro.value_label.setText(f"R$ {lucro:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        self.card_caixas.value_label.setText(str(caixas))

        # Atualizar gráfico
        self._plot_vendas(inicio, fim, mode)

        # Preencher tabela de gastos
        gastos = self.db.listar_gastos_periodo(inicio, fim) or []
        self.table_gastos.setRowCount(0)
        for row in gastos:
            # row may be (id, tipo, descricao, valor, data)
            try:
                _id, tipo, desc, val, data = row
            except Exception:
                # fallback for dict-style row
                tipo = row.get('tipo', '') if isinstance(row, dict) else ''
                desc = row.get('descricao', '') if isinstance(row, dict) else ''
                val = row.get('valor', 0) if isinstance(row, dict) else 0

            r = self.table_gastos.rowCount()
            self.table_gastos.insertRow(r)
            self.table_gastos.setItem(r, 0, QTableWidgetItem(str(tipo)))
            self.table_gastos.setItem(r, 1, QTableWidgetItem(str(desc)))
            self.table_gastos.setItem(r, 2, QTableWidgetItem(f"{float(val):.2f}"))

        if not gastos:
            # show empty placeholder row
            self.table_gastos.setRowCount(1)
            self.table_gastos.setItem(0, 0, QTableWidgetItem("-"))
            self.table_gastos.setItem(0, 1, QTableWidgetItem("Sem gastos no período"))
            self.table_gastos.setItem(0, 2, QTableWidgetItem("0.00"))

    def _plot_vendas(self, inicio, fim, mode):
        self.figure.clear()
        # make axes dark-themed
        ax = self.figure.add_subplot(111, facecolor='#2d2d2d')

        # Query vendas por dia/weeks/months
        valores = []
        labels = []

        if mode == 'mes':
            # agrupar por semana dentro do mês -> 4-5 barras
            data_inicio = datetime.strptime(inicio, '%Y-%m-%d')
            for w in range(0, 6):
                s0 = data_inicio + timedelta(weeks=w)
                s1 = s0 + timedelta(days=6)
                if s0.strftime('%Y-%m-%d') > fim:
                    break
                res = self.db.calcular_resumo_vendas(s0.strftime('%Y-%m-%d'), min(s1.strftime('%Y-%m-%d'), fim))
                total = float((res[1] or 0) if res else 0)
                labels.append(s0.strftime('%d %b'))
                valores.append(total)
            bars = ax.bar(labels, valores, color='#00c48c', alpha=0.95)
            ax.set_title('Vendas por Semana (mês)', color='#e6e6e6')

        elif mode == '3meses':
            # últimas 12 semanas
            hoje = datetime.now()
            for i in range(12):
                s0 = hoje - timedelta(weeks=11 - i)
                inicio_s = (s0 - timedelta(days=s0.weekday())).strftime('%Y-%m-%d')
                fim_s = (s0 + timedelta(days=6 - s0.weekday())).strftime('%Y-%m-%d')
                res = self.db.calcular_resumo_vendas(inicio_s, fim_s)
                total = float((res[1] or 0) if res else 0)
                labels.append(s0.strftime('%d %b'))
                valores.append(total)
            bars = ax.bar(labels, valores, color='#00c48c', alpha=0.95)
            ax.set_title('Vendas nas últimas 12 semanas', color='#e6e6e6')

        else:
            # ano -> 12 meses
            ano = datetime.now().year
            for m in range(1, 13):
                inicio_m = datetime(ano, m, 1).strftime('%Y-%m-%d')
                if m == 12:
                    fim_m = datetime(ano, m, 28).strftime('%Y-%m-%d')
                else:
                    fim_m = (datetime(ano, m+1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
                res = self.db.calcular_resumo_vendas(inicio_m, fim_m)
                total = float((res[1] or 0) if res else 0)
                labels.append(datetime(ano, m, 1).strftime('%b'))
                valores.append(total)
            bars = ax.bar(labels, valores, color='#00c48c', alpha=0.95)
            ax.set_title('Vendas por Mês (ano)', color='#e6e6e6')

        # annotate bars
        for b, v in zip(bars, valores):
            if v > 0:
                ax.text(b.get_x() + b.get_width() / 2, v * 1.01, f"R$ {v:,.0f}".replace(',', 'v').replace('.', ',').replace('v', '.'), ha='center', color='white', fontsize=9)

        ax.set_ylabel('Valor (R$)', color='#e6e6e6')
        ax.tick_params(colors='#e6e6e6')
        ax.grid(axis='y', color='#444444', linestyle='--', alpha=0.6)
        # style x labels
        for label in ax.get_xticklabels():
            label.set_color('#e6e6e6')
            label.set_rotation(0)

        # Empty state: if all zeros, show message
        if not valores or all(v == 0 for v in valores):
            ax.text(0.5, 0.5, 'Sem vendas no período', transform=ax.transAxes, ha='center', va='center', color='#bbbbbb', fontsize=12)

        self.figure.tight_layout()
        self.canvas.draw()
