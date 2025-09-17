"""
Módulo principal que inicia a aplicação de Ordem de Serviço (OS) usando PyQt6.

Este script inicializa a interface gráfica usando PyQt6 e
executa a aplicação principal modularizada.

"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from app.ui.theme import apply_app_theme, small_icon

# Garante que a raiz do projeto está no sys.path para imports como "app.components"
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Importações dos managers
# Importações dos managers serão feitas tardiamente após QApplication ser criada


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui(),
        
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
            # Prefer the PyQt6-specific Clientes manager (uses the Produtos-like UI)
            from app.components.clientes_manager_pyqt import ClientesManager
            self.clientes_manager = ClientesManager(clientes_widget)
            clientes_layout.addWidget(self.clientes_manager)
        except ModuleNotFoundError:
            # Fallback to the original clientes_manager if the PyQt file is missing
            try:
                from app.components.clientes_manager import ClientesManager
                self.clientes_manager = ClientesManager(clientes_widget)
                clientes_layout.addWidget(self.clientes_manager)
            except Exception as e:
                error_label = QLabel(f"Erro ao carregar Clientes: {e}")
                error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
                clientes_layout.addWidget(error_label)
        except Exception as e:
            error_label = QLabel(f"Erro ao carregar Clientes: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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

        # Aba Backup
        backup_widget = QWidget()
        backup_layout = QVBoxLayout(backup_widget)
        backup_layout.setContentsMargins(0, 0, 0, 0)
        try:
            from app.ui.backup_tab import BackupTab
            self.backup_tab = BackupTab()
            backup_layout.addWidget(self.backup_tab)
        except Exception as e:
            error_label = QLabel(f"Erro ao carregar Backup: {e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
            backup_layout.addWidget(error_label)

        self.tab_widget.addTab(backup_widget, "💾 Backup")

        # remember backup tab index and protect access
        try:
            self.backup_tab_index = self.tab_widget.indexOf(backup_widget)
        except Exception:
            self.backup_tab_index = None

        # connect tab change handler to enforce password on Backup tab
        try:
            self._last_tab_index = self.tab_widget.currentIndex()
            self._authenticating = False
            self.tab_widget.currentChanged.connect(self._on_tab_changed)
        except Exception:
            pass

    def _on_tab_changed(self, index: int):
        """Prompt for password when user tries to open the Backup tab."""
        # If no backup tab configured, ignore
        try:
            if self.backup_tab_index is None:
                self._last_tab_index = index
                return
        except Exception:
            self._last_tab_index = index
            return

        # Avoid recursive prompts
        if getattr(self, '_authenticating', False):
            self._last_tab_index = index
            return

        # If switching to the backup tab, prompt for password
        if index == self.backup_tab_index:
            self._authenticating = True
            ok = False
            try:
                pwd, accepted = QInputDialog.getText(self, 'Senha necessária', 'Digite a senha para acessar Backup:', echo=QInputDialog.EchoMode.Password)
                if accepted:
                    if pwd == '123':
                        ok = True
                    else:
                        QMessageBox.warning(self, 'Senha incorreta', 'Senha inválida. Acesso negado.')
                else:
                    ok = False
            except Exception:
                ok = False

            # revert to previous tab on failure
            if not ok:
                # block signal while reverting
                try:
                    self.tab_widget.blockSignals(True)
                    self.tab_widget.setCurrentIndex(self._last_tab_index)
                finally:
                    self.tab_widget.blockSignals(False)

            self._authenticating = False

        self._last_tab_index = index


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
    
    # Apply shared theme
    try:
        apply_app_theme(app)
    except Exception:
        pass

    # --- Ensure DB is initialized synchronously to avoid first-interaction delays ---
    try:
        # Importing the package will create the singleton DatabaseManager
        # and open the SQLite connection during startup rather than on first use.
        from database import db_manager as _db_init  # type: ignore
    except Exception:
        # ignore failures here; the prewarm will still attempt a lazy touch
        pass

    # Criar e mostrar a janela principal
    main_window = MainApp()
    # Pre-warm heavy resources that cause the first dialog to be slow.
    # Reason: first-time creation of QMessageBox, DB connection and icons can block
    # while loading theme resources or opening the SQLite connection. We do a
    # small, non-blocking warmup shortly after the event loop starts so the
    # visible first user dialog is fast.
    def _prewarm():
        try:
            # touch the database singleton to ensure connection / table setup done
            try:
                from database import db_manager as _db
                # small read to ensure any lazy initialization happens now
                try:
                    _ = _db.listar_pedidos_ordenados_por_prazo(1)
                except Exception:
                    pass
            except Exception:
                pass

            # create a transient, tool-window message box and close it quickly to
            # force Qt to load dialog resources (styles, icons, native widgets).
            try:
                m = QMessageBox()
                m.setWindowTitle("")
                m.setText("")
                m.setWindowFlag(Qt.WindowType.Tool)
                m.setModal(False)
                m.show()
                QTimer.singleShot(40, m.close)
            except Exception:
                pass

            # preload small icons used in BackupTab and other places (best-effort)
            try:
                for name in ('refresh', 'create', 'restore', 'replace', 'delete', 'add', 'edit'):
                    try:
                        _ = small_icon(app, name)
                    except Exception:
                        pass
            except Exception:
                pass

            # Preload font subsystem and any heavy font resources to avoid
            # the first-dialog font initialization penalty on some platforms.
            try:
                from PyQt6.QtGui import QFontDatabase, QPixmap
                QFontDatabase()  # touch font DB
                # Optional: create a small pixmap cache warmup for common icons
                for name in ('refresh', 'create', 'restore', 'replace'):
                    try:
                        p = small_icon(app, name)
                        if p is not None:
                            # small_icon may return QIcon; attempt to get pixmap
                            try:
                                pm = p.pixmap(16, 16)
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            pass

    # schedule warmup to run once the event loop starts
    QTimer.singleShot(200, _prewarm)
    # add small icons/tooltips to BackupTab buttons if present
    try:
        if hasattr(main_window, 'backup_tab'):
            icon = small_icon(app, 'refresh')
            if icon:
                main_window.backup_tab.btn_refresh.setIcon(icon)
            icon = small_icon(app, 'create')
            if icon:
                main_window.backup_tab.btn_create.setIcon(icon)
            icon = small_icon(app, 'restore')
            if icon:
                main_window.backup_tab.btn_restore.setIcon(icon)
            icon = small_icon(app, 'replace')
            if icon:
                main_window.backup_tab.btn_replace.setIcon(icon)
            # tooltips
            main_window.backup_tab.btn_refresh.setToolTip('Atualizar a lista de backups')
            main_window.backup_tab.btn_create.setToolTip('Criar um novo backup do banco de dados')
            main_window.backup_tab.btn_restore.setToolTip('Restaurar a partir de um arquivo .db')
            main_window.backup_tab.btn_replace.setToolTip('Substituir o DB atual por um arquivo')
    except Exception:
        pass
    main_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
