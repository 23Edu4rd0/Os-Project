"""
Módulo principal que inicia a aplicação de Ordem de Serviço (OS) usando PyQt6.

Este script inicializa a interface gráfica usando PyQt6 e
executa a aplicação principal modularizada.

"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

# Garante que a raiz do projeto está no sys.path para imports como "app.components"
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Importações dos managers
# Importações dos managers serão feitas tardiamente após QApplication ser criada


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
        self.apply_modern_style()
        
        # Criar abas
        self.create_tabs()
        
    def apply_modern_style(self):
        """Aplica estilo moderno ao aplicativo"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2d2d2d;
                border-radius: 8px;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                font-size: 14px;
            }
            
            QTabBar::tab:selected {
                background-color: #0d7377;
                color: #ffffff;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #505050;
            }
            
            QWidget {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QToolTip {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #505050;
                padding: 6px 8px;
                border-radius: 6px;
            }
        """)
        
    def create_tabs(self):
        """Cria as abas da aplicação"""
        
        # Aba Clientes
        clientes_widget = QWidget()
        clientes_layout = QVBoxLayout(clientes_widget)
        clientes_layout.setContentsMargins(0, 0, 0, 0)
        
        try:
            from app.components.clientes_manager import ClientesManager
            if hasattr(ClientesManager, "__init__"):
                self.clientes_manager = ClientesManager(clientes_widget)
                clientes_layout.addWidget(self.clientes_manager)
            else:
                raise ImportError("ClientesManager não possui construtor esperado.")
        except ModuleNotFoundError as e:
            error_label = QLabel(f"Erro ao carregar Clientes: Módulo não encontrado: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
            clientes_layout.addWidg.et(error_label)
        except Exception as e:
            error_label = QLabel(f"Erro ao carregar Clientes: {e}")
            error_label.setAli,gnment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
            clientes_layout.addWidget(error_label)
        
        self.tab_widget.addTab(clientes_widget, "👥 Clientes")
        
        # Aba Pedidos
        pedidos_widget = QWidget()
        pedidos_layout = QVBoxLayout(pedidos_widget)
        pedidos_layout.setContentsMargins(0, 0, 0, 0)
        
        try:
            from app.components.pedidos import PedidosManager
            self.pedidos_manager = PedidosManager(pedidos_widget)
            pedidos_layout.addWidget(self.pedidos_manager)
            try:
                self.pedidos_manager._build_cards()
            except Exception:
                pass
        except ModuleNotFoundError as e:
            error_label = QLabel(f"Erro ao carregar Pedidos: Módulo não encontrado: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
            pedidos_layout.addWidget(error_label)
        except Exception as e:
            error_label = QLabel(f"Erro ao carregar Pedidos: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
            pedidos_layout.addWidget(error_label)
        
        self.tab_widget.addTab(pedidos_widget, "📋 Pedidos")
 
        # Aba Contas (Financeiro)
        contas_widget = QWidget()
        contas_layout = QVBoxLayout(contas_widget)
        contas_layout.setContentsMargins(0, 0, 0, 0)
        
        try:
            from app.components.contas_manager import ContasManager
            self.contas_manager = ContasManager(contas_widget)
            contas_layout.addWidget(self.contas_manager)
        except Exception as e:
            error_label = QLabel(f"Erro ao carregar Contas: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
            contas_layout.addWidget(error_label)
        
        self.tab_widget.addTab(contas_widget, "💼 Contas")

        # Aba Produtos (Catálogo)
        try:
            from app.components.ui.produtos import ProdutosWidget
            produtos_widget = ProdutosWidget()
        except Exception as e:
            produtos_widget = QWidget()
            produtos_layout = QVBoxLayout(produtos_widget)
            produtos_layout.setContentsMargins(0, 0, 0, 0)
            error_label = QLabel(f"Erro ao carregar Produtos: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
            produtos_layout.addWidget(error_label)
        
        self.tab_widget.addTab(produtos_widget, "🛍️ Produtos")


def main():
    """Função principal"""
    app = QApplication(sys.argv)
    
    # Configurar fonte padrão
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Garantir estilo do tooltip global (evita bloco preto opaco)
    try:
        app.setStyleSheet(
            (app.styleSheet() or "")
            + "\nQToolTip { background-color: #333333; color: #ffffff; border: 1px solid #505050; padding: 6px 8px; border-radius: 6px; }\n"
        )
    except Exception:
        pass
    
    # Criar e mostrar a janela principal
    main_window = MainApp()
    main_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
