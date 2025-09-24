"""
Módulo principal que inicia a aplicação de Ordem de Serviço (OS) usando PyQt6.

Este script inicializa a interface gráfica usando PyQt6 e
executa a aplicação principal modularizada.
"""

import sys
import os
import warnings
from pathlib import Path

# Suppress PyQt6 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QDate  # Added QDate import
from PyQt6.QtGui import QFont, QIcon
from app.ui.theme import apply_app_theme, small_icon

# Garante que a raiz do projeto está no sys.path para imports como "app.components"
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Sistema de Ordem de Serviço - PyQt6")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tab Widget principal
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        layout.addWidget(self.tab_widget)
        
        # Aplicar estilo moderno
        apply_app_theme(self)
        
        # Inicializar as abas
        self.init_tabs()
        
        self.show()
        
    def init_tabs(self):
        """Inicializa as abas do sistema"""
        try:
            # Importar módulos sob demanda para melhorar startup time
            from app.components.clientes_manager_pyqt import ClientesManager
            from app.components.pedidos.pedidos_interface import PedidosInterface
            from app.components.contas_manager import ContasManager  
            from app.components.produtos_manager import ProdutosManager
            from app.ui.backup_tab import BackupTab
            
            # Criar widgets para cada aba
            clientes_widget = QWidget()
            pedidos_widget = QWidget()
            contas_widget = QWidget()
            produtos_widget = QWidget()
            
            # Aba de Clientes
            clientes = ClientesManager(clientes_widget)  # Passar widget como parent
            clientes_layout = QVBoxLayout(clientes_widget)
            clientes_layout.addWidget(clientes)
            self.tab_widget.addTab(clientes_widget, "👥 Clientes")
            
            # Aba de Pedidos
            pedidos = PedidosInterface(pedidos_widget)  # Passar widget como parent
            pedidos_layout = QVBoxLayout(pedidos_widget)
            pedidos_layout.addWidget(pedidos)
            self.tab_widget.addTab(pedidos_widget, "📋 Pedidos")
            
            # Aba de Contas
            contas = ContasManager(contas_widget)  # Passar widget como parent
            contas_layout = QVBoxLayout(contas_widget)
            contas_layout.addWidget(contas)
            self.tab_widget.addTab(contas_widget, "💰 Contas")
            
            # Aba de Produtos
            produtos = ProdutosManager(produtos_widget)  # Passar widget como parent
            produtos_layout = QVBoxLayout(produtos_widget)
            produtos_layout.addWidget(produtos)
            self.tab_widget.addTab(produtos_widget, "📦 Produtos")
            
            # Aba de Backup
            backup = BackupTab()
            self.tab_widget.addTab(backup, "💾 Backup")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao inicializar módulos: {e}")
            sys.exit(1)


def main():
    try:
        # Criar aplicação
        app = QApplication(sys.argv)
        
        # Configurar fonte padrão
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        # Criar e mostrar janela principal
        window = MainApp()
        window.show()
        
        # Executar loop principal
        sys.exit(app.exec())
    except Exception as e:
        print(f"Erro ao iniciar aplicação: {str(e)}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()