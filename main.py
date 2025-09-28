import sys
import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont, QIcon
from app.ui.theme import apply_app_theme, small_icon

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Define o estilo global para tooltips
        app = QApplication.instance()
        tooltip_style = """
            QToolTip {
                background-color: rgb(0, 0, 0) !important;
                color: #ffffff !important;
                border: 2px solid #555555 !important;
                padding: 10px !important;
                font-size: 14px !important;
                font-weight: bold !important;
                border-radius: 5px !important;
            }
        """
        app.setStyleSheet(tooltip_style)
        
    def init_ui(self):
        self.setWindowTitle("Sistema de Ordem de Serviço")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        layout.addWidget(self.tab_widget)
        
        apply_app_theme(self)
        self.init_tabs()
        self.show()
        
    def init_tabs(self):
        try:
            from app.components.clientes_manager_pyqt import ClientesManager
            from app.components.pedidos import PedidosManager
            from app.components.contas_manager import ContasManager  
            from app.components.produtos_manager import ProdutosManager
            from app.ui.backup_tab import BackupTab
            
            clientes_widget = QWidget()
            pedidos_widget = QWidget()
            contas_widget = QWidget()
            produtos_widget = QWidget()
            
            clientes = ClientesManager(clientes_widget)
            clientes_layout = QVBoxLayout(clientes_widget)
            clientes_layout.addWidget(clientes)
            self.tab_widget.addTab(clientes_widget, "👥 Clientes")
            
            pedidos = PedidosManager(pedidos_widget)
            pedidos_layout = QVBoxLayout(pedidos_widget)
            pedidos_layout.addWidget(pedidos)
            self.tab_widget.addTab(pedidos_widget, "📋 Pedidos")
            
            contas = ContasManager(contas_widget)
            contas_layout = QVBoxLayout(contas_widget)
            contas_layout.addWidget(contas)
            self.tab_widget.addTab(contas_widget, "💰 Contas")
            
            produtos = ProdutosManager(produtos_widget)
            produtos_layout = QVBoxLayout(produtos_widget)
            produtos_layout.addWidget(produtos)
            self.tab_widget.addTab(produtos_widget, "📦 Produtos")
            
            backup = BackupTab()
            self.tab_widget.addTab(backup, "💾 Backup")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao inicializar módulos: {e}")
            sys.exit(1)


def main():
    try:
        app = QApplication(sys.argv)
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        window = MainApp()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {str(e)}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()