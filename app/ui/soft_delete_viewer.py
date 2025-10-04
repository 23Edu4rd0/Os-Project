"""
Visualizador e Restaurador de Registros Deletados (Soft Delete).
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt


class SoftDeleteViewer(QDialog):
    """Diálogo para visualizar e restaurar registros deletados"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 Registros Deletados (Lixeira)")
        self.setMinimumSize(900, 600)
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Configura a interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🗑️ Lixeira - Registros Deletados")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        info = QLabel("Registros deletados podem ser restaurados. "
                     "Após 30 dias, serão removidos permanentemente.")
        info.setStyleSheet("color: #888888; padding: 5px 10px;")
        layout.addWidget(info)
        
        # Tabs para cada tipo de registro
        self.tabs = QTabWidget()
        
        # Tab Pedidos
        self.pedidos_tab = self._create_tab("Pedidos")
        self.tabs.addTab(self.pedidos_tab, "📋 Pedidos")
        
        # Tab Clientes
        self.clientes_tab = self._create_tab("Clientes")
        self.tabs.addTab(self.clientes_tab, "👥 Clientes")
        
        # Tab Produtos
        self.produtos_tab = self._create_tab("Produtos")
        self.tabs.addTab(self.produtos_tab, "📦 Produtos")
        
        # Tab Gastos
        self.gastos_tab = self._create_tab("Gastos")
        self.tabs.addTab(self.gastos_tab, "💰 Gastos")
        
        layout.addWidget(self.tabs)
        
        # Botões
        buttons = QHBoxLayout()
        
        self.btn_restore = QPushButton("♻️ Restaurar Selecionado")
        self.btn_restore.clicked.connect(self._restore_selected)
        self.btn_restore.setStyleSheet("background-color: #28a745; color: white; padding: 8px 16px;")
        buttons.addWidget(self.btn_restore)
        
        self.btn_refresh = QPushButton("🔄 Atualizar")
        self.btn_refresh.clicked.connect(self._load_data)
        self.btn_refresh.setStyleSheet("padding: 8px 16px;")
        buttons.addWidget(self.btn_refresh)
        
        buttons.addStretch()
        
        self.btn_close = QPushButton("✖ Fechar")
        self.btn_close.clicked.connect(self.accept)
        self.btn_close.setStyleSheet("padding: 8px 16px;")
        buttons.addWidget(self.btn_close)
        
        layout.addLayout(buttons)
        
        # Estilo
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QTableWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                gridline-color: #404040;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0d7377;
            }
            QHeaderView::section {
                background-color: #323232;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #404040;
            }
        """)
    
    def _create_tab(self, tipo):
        """Cria uma tab com tabela"""
        from PyQt6.QtWidgets import QWidget
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Label com contador
        label = QLabel(f"{tipo}: 0 registros deletados")
        label.setObjectName(f"label_{tipo}")
        layout.addWidget(label)
        
        # Tabela
        table = QTableWidget()
        table.setObjectName(f"table_{tipo}")
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(table)
        
        return widget
    
    def _load_data(self):
        """Carrega dados deletados de todas as tabelas"""
        from app.utils.soft_delete import SoftDeleteManager
        
        # Carregar Pedidos
        pedidos = SoftDeleteManager.list_deleted_pedidos()
        self._populate_table(
            self.pedidos_tab.findChild(QTableWidget),
            pedidos,
            ["ID", "Nº OS", "Cliente", "Status", "Deletado em"]
        )
        label = self.pedidos_tab.findChild(QLabel)
        label.setText(f"Pedidos: {len(pedidos)} registros deletados")
        
        # Carregar Clientes
        clientes = SoftDeleteManager.list_deleted_clientes()
        self._populate_table(
            self.clientes_tab.findChild(QTableWidget),
            clientes,
            ["ID", "Nome", "CPF", "CNPJ", "Telefone", "Deletado em"]
        )
        label = self.clientes_tab.findChild(QLabel)
        label.setText(f"Clientes: {len(clientes)} registros deletados")
        
        # Carregar Produtos
        produtos = SoftDeleteManager.list_deleted_produtos()
        self._populate_table(
            self.produtos_tab.findChild(QTableWidget),
            produtos,
            ["ID", "Nome", "Código", "Preço", "Categoria", "Deletado em"]
        )
        label = self.produtos_tab.findChild(QLabel)
        label.setText(f"Produtos: {len(produtos)} registros deletados")
        
        # Carregar Gastos
        gastos = SoftDeleteManager.list_deleted_gastos()
        self._populate_table(
            self.gastos_tab.findChild(QTableWidget),
            gastos,
            ["ID", "Tipo", "Descrição", "Valor", "Data", "Deletado em"]
        )
        label = self.gastos_tab.findChild(QLabel)
        label.setText(f"Gastos: {len(gastos)} registros deletados")
    
    def _populate_table(self, table, data, headers):
        """Popula tabela com dados"""
        table.clear()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            # Pegar apenas as colunas necessárias (limitado pelo header)
            display_data = row_data[:len(headers)]
            
            for col_idx, value in enumerate(display_data):
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, col_idx, item)
        
        table.resizeColumnsToContents()
    
    def _restore_selected(self):
        """Restaura o registro selecionado"""
        from app.utils.soft_delete import SoftDeleteManager
        
        # Descobrir qual tab está ativa
        current_tab = self.tabs.currentWidget()
        current_index = self.tabs.currentIndex()
        table = current_tab.findChild(QTableWidget)
        
        # Verificar se há seleção
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um registro para restaurar")
            return
        
        # Pegar ID do registro
        row = selected_rows[0].row()
        id_item = table.item(row, 0)  # Primeira coluna é sempre ID
        if not id_item:
            QMessageBox.warning(self, "Erro", "ID não encontrado")
            return
        
        record_id = int(id_item.text())
        
        # Confirmar
        reply = QMessageBox.question(
            self,
            "Confirmar Restauração",
            f"Deseja restaurar o registro ID {record_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Restaurar baseado na tab
        sucesso = False
        mensagem = ""
        
        if current_index == 0:  # Pedidos
            sucesso, mensagem = SoftDeleteManager.restore_pedido(record_id)
        elif current_index == 1:  # Clientes
            sucesso, mensagem = SoftDeleteManager.restore_cliente(record_id)
        elif current_index == 2:  # Produtos
            sucesso, mensagem = SoftDeleteManager.restore_produto(record_id)
        elif current_index == 3:  # Gastos
            sucesso, mensagem = SoftDeleteManager.restore_gasto(record_id)
        
        if sucesso:
            QMessageBox.information(self, "Sucesso", f"✅ {mensagem}")
            self._load_data()  # Recarregar
        else:
            QMessageBox.warning(self, "Erro", f"❌ {mensagem}")
