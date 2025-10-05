
"""
main.py - Entry point for Merkava Service Order System

Features:
 - Tabbed interface for clients, orders, products, and backup
 - Window state and active tab persistence
 - Structured logging and global exception handling

Author: Eduardo Viana Chaves
License: MIT
"""


import sys
import logging
import warnings
from pathlib import Path

# --- Suppress warnings for cleaner output ---
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# --- PyQt6 Imports ---
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QTimer, QSettings

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Project Root ---
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))



# --- App Imports ---
from app.ui.theme import apply_app_theme
from app.ui.login_dialog import LoginDialog
from app.ui.app_loader_thread import AppLoaderThread


# --- Helper para Tooltips ---
def install_tooltip_fix(app):
    """
    Instala um filtro de eventos global para corrigir o posicionamento dos tooltips.
    Os tooltips aparecerão sempre próximos ao cursor do mouse.
    """
    from PyQt6.QtCore import QObject, QEvent, Qt
    from PyQt6.QtWidgets import QToolTip
    from PyQt6.QtGui import QCursor
    
    class ToolTipEventFilter(QObject):
        def eventFilter(self, obj, event):
            # Quando um tooltip está prestes a ser mostrado, reposicioná-lo
            if event.type() == QEvent.Type.ToolTip:
                # Obter posição do cursor
                cursor_pos = QCursor.pos()
                # Offset para não cobrir o cursor (10 pixels abaixo e 5 à direita)
                tooltip_pos = cursor_pos + type(cursor_pos)(5, 10)
                
                # Se o widget tem tooltip definido, mostrá-lo na posição do cursor
                if obj.toolTip():
                    QToolTip.showText(tooltip_pos, obj.toolTip(), obj)
                    return True  # Evento tratado, não propagar
            
            return super().eventFilter(obj, event)
    
    # Instalar filtro global
    tooltip_filter = ToolTipEventFilter(app)
    app.installEventFilter(tooltip_filter)
    # Manter referência para não ser coletado pelo garbage collector
    app._tooltip_filter = tooltip_filter


class MainApp(QMainWindow):
    """
    Main application window for the Service Order System.
    Provides a tabbed interface for managing clients, service orders, products, and backup/restore operations.
    Handles window state persistence and logging.
    """

    APP_NAME = "Sistema de Ordem de Serviço"
    APP_VERSION = "1.0.0"

    def __init__(self):
        super().__init__()
        logger.info(f"Initializing {self.APP_NAME} v{self.APP_VERSION}")
        self.settings = QSettings("SOS", "OrdemServico")
        self._setup_ui()
        self._apply_global_styles()
        self._restore_window_state()
        self._init_auto_backup()
        logger.info("Application initialized successfully")
    
    def _apply_global_styles(self) -> None:
        """
        Apply global application styles, such as custom tooltips.
        This method sets a consistent tooltip style for the entire application.
        """
        app = QApplication.instance()
        if app:
            # Configurar tooltips para aparecerem mais rápido e próximo ao cursor
            from PyQt6.QtWidgets import QToolTip
            from PyQt6.QtGui import QFont
            
            # Configurar fonte menor para tooltips
            tooltip_font = QFont()
            tooltip_font.setPointSize(9)
            QToolTip.setFont(tooltip_font)
            
            global_style = """
                QToolTip {
                    background: #2a2a2a;
                    color: #e0e0e0;
                    border: 1px solid #4a4a4a;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: normal;
                }
            """
            app.setStyleSheet(global_style)
        
    def _setup_ui(self) -> None:
        """
        Configure the main user interface, layout, tabs, and visual theme.
        Sets up the main window, central widget, tab widget, and applies the application theme.
        """
        self.setWindowTitle(f"{self.APP_NAME} v{self.APP_VERSION}")
        self.setMinimumSize(1000, 700)
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        layout.addWidget(self.tab_widget)
        
        # Aplicar estilo moderno às abas
        self._apply_modern_tab_style()
        apply_app_theme(self)
        QTimer.singleShot(100, self._init_tabs)
    
    def _apply_modern_tab_style(self) -> None:
        """
        Aplica um estilo moderno e atrativo às abas da aplicação.
        """
        modern_style = """
            QTabWidget::pane {
                border: 2px solid #3a3a3a;
                border-radius: 10px;
                background-color: #2b2b2b;
                margin-top: -1px;
            }
            
            QTabBar {
                qproperty-drawBase: 0;
                border-radius: 3px;
                margin: 0px;
                padding: 2px;
                background-color: transparent;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4a4a4a, stop: 0.1 #424242, 
                    stop: 0.5 #3a3a3a, stop: 0.9 #2e2e2e, stop: 1 #2a2a2a);
                border: 2px solid #555555;
                border-bottom: none;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                color: #e0e0e0;
                font-weight: 600;
                font-size: 13px;
                padding: 12px 20px;
                margin-right: 5px;
                margin-left: 5px;
                margin-top: 5px;
                min-width: 120px;
                text-align: center;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #007ACC, stop: 0.1 #0066BB, 
                    stop: 0.5 #005AA0, stop: 0.9 #004E88, stop: 1 #004477);
                border: 2px solid #007ACC;
                color: #ffffff;
                font-weight: bold;
                transform: translateY(-2px);
            }
            
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5a5a5a, stop: 0.1 #525252, 
                    stop: 0.5 #4a4a4a, stop: 0.9 #3e3e3e, stop: 1 #3a3a3a);
                border: 2px solid #666666;
                color: #f0f0f0;
                transform: translateY(-1px);
            }
            
            QTabBar::tab:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #005588, stop: 0.5 #004466, stop: 1 #003344);
            }
            
            /* Adicionar sombra às abas */
            QTabBar::tab:selected {
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }
            
            /* Estilo para o botão de fechar aba */
            QTabBar::close-button {
                image: url(close.png);
                subcontrol-position: right;
                background: transparent;
                border-radius: 2px;
                margin: 2px;
            }
            
            QTabBar::close-button:hover {
                background: #ff4444;
                border-radius: 4px;
            }
        """
        self.tab_widget.setStyleSheet(modern_style)
        
    def _init_tabs(self) -> None:
        """
        Initialize and add all functional tabs to the application.
        Each tab is loaded with individual error handling and informative tooltips.
        Logs the loading process and handles import or initialization errors gracefully.
        """
        try:
            logger.info("Loading application modules...")
            
            from app.components.clientes_manager_pyqt import ClientesManager
            from app.components.pedidos import PedidosManager
            from app.components.produtos_manager import ProdutosManager
            from app.ui.backup_tab import BackupTab
            
            tabs_config = [
                ("👥 Clientes", ClientesManager, "Gestão completa de clientes e cadastros"),
                ("📋 Pedidos", PedidosManager, "Ordens de serviço e acompanhamento"),
                ("📦 Produtos", ProdutosManager, "Catálogo de produtos e preços"),
                ("💾 Backup", BackupTab, "Backup e restauração de dados")
            ]
            
            for tab_name, manager_class, tooltip in tabs_config:
                try:
                    if manager_class == BackupTab:
                        manager = manager_class()
                        tab_index = self.tab_widget.addTab(manager, tab_name)
                    else:
                        widget = QWidget()
                        layout = QVBoxLayout(widget)
                        layout.setContentsMargins(0, 0, 0, 0)
                        manager = manager_class(widget)
                        layout.addWidget(manager)
                        tab_index = self.tab_widget.addTab(widget, tab_name)
                    
                    self.tab_widget.setTabToolTip(tab_index, tooltip)
                    logger.info(f"Tab '{tab_name}' loaded successfully")
                    
                except Exception as tab_error:
                    logger.error(f"Error loading tab '{tab_name}': {tab_error}")
                    continue
            
            self.tab_widget.setCurrentIndex(0)
            logger.info("All tabs initialized")
            
        except ImportError as import_error:
            logger.error(f"Import error: {import_error}")
            self._show_error("Erro de Módulo", f"Falha ao importar módulos necessários:\n{import_error}")
        except Exception as e:
            logger.error(f"Critical error initializing tabs: {e}")
            self._show_error("Erro Crítico", f"Falha crítica na inicialização:\n{e}")
    
    def _show_error(self, title: str, message: str) -> None:
        """
        Display a critical error message to the user and exit the application.
        Args:
            title (str): The title of the error dialog.
            message (str): The error message to display.
        """
        QMessageBox.critical(self, title, message)
        sys.exit(1)
    
    def _restore_window_state(self) -> None:
        """
        Restore window geometry, state, and last selected tab from saved settings.
        Attempts to retrieve and apply the saved window geometry, window state,
        and the index of the last selected tab from the application's settings.
        Logs a warning if restoration fails.
        """
        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
                
            window_state = self.settings.value("windowState")
            if window_state:
                self.restoreState(window_state)
                
            last_tab = self.settings.value("lastTab", 0, type=int)
            if 0 <= last_tab < self.tab_widget.count():
                self.tab_widget.setCurrentIndex(last_tab)
                
        except Exception as e:
            logger.warning(f"Failed to restore window state: {e}")
    
    def _save_window_state(self) -> None:
        """
        Save current window geometry, state, and selected tab to application settings.
        Logs a warning if saving fails.
        """
        try:
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            self.settings.setValue("lastTab", self.tab_widget.currentIndex())
        except Exception as e:
            logger.warning(f"Failed to save window state: {e}")
    
    def _init_auto_backup(self):
        """Inicializa o sistema de backup automático"""
        try:
            from app.utils.auto_backup import get_auto_backup_scheduler
            
            self.auto_backup = get_auto_backup_scheduler(self)
            self.auto_backup.start()
            
            logger.info("Sistema de backup automático iniciado (diário às 23h)")
        except Exception as e:
            logger.error(f"Erro ao iniciar backup automático: {e}")
    
    def closeEvent(self, event) -> None:
        """
        Handle the window close event by saving the current window state and logging the process.
        Args:
            event: The close event object.
        Attempts to save the window state and logs the closing process. If an exception occurs during the process, it logs the error. In both cases, it accepts the close event to proceed with closing the application.
        """
        try:
            logger.info("Closing application...")
            
            # Remover event filter de tooltip para evitar segfault
            app = QApplication.instance()
            if app and hasattr(app, '_tooltip_filter'):
                try:
                    app.removeEventFilter(app._tooltip_filter)
                    delattr(app, '_tooltip_filter')
                except:
                    pass
            
            # Parar backup automático
            if hasattr(self, 'auto_backup'):
                self.auto_backup.stop()
                logger.info("Backup automático parado")
            
            self._save_window_state()
            event.accept()
            logger.info("Application closed successfully")
        except Exception as e:
            logger.error(f"Error closing application: {e}")
            event.accept()


def setup_application() -> QApplication:
    """
    Initialize and configure the QApplication instance.
    Sets application name, version, organization, and icon if available.
    Returns:
        QApplication: The configured QApplication instance.
    """
    app = QApplication(sys.argv)
    
    app.setApplicationName("Sistema de Ordem de Serviço")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SOS")
    app.setOrganizationDomain("sos.local")
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Configurar tooltips para serem menores e mais discretos
    # Os tooltips do PyQt6 seguem automaticamente o cursor
    app.setStyleSheet("""
        QToolTip {
            background: #2a2a2a;
            color: #e0e0e0;
            border: 1px solid #4a4a4a;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
        }
    """)
    
    # Instalar correção de posicionamento de tooltips
    install_tooltip_fix(app)
    
    icon_path = ROOT_DIR / "assets" / "logo.ico"  # ou logo.ico se for .ico
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app


def handle_exception(exc_type, exc_value, exc_traceback) -> None:
    """
    Global handler for uncaught exceptions.
    Logs critical exceptions and allows KeyboardInterrupt to propagate normally.
    Args:
        exc_type: Exception type.
        exc_value: Exception value.
        exc_traceback: Exception traceback.
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def main() -> int:
    """
    Main entry point for the application.
    Initializes logging, exception handling, the interface, and runs the main event loop.
    Returns:
        int: Exit code (0 for success, 1 for failure).
    Handles:
        ImportError: Logs and prints an error if a required module is missing.
        Exception: Logs and prints any other critical errors during startup.
    """


    try:
        sys.excepthook = handle_exception
        logger.info("Iniciando Sistema de Ordem de Serviço...")

        app = setup_application()

        # Simula processamento do app principal enquanto login está aberto
        loader_thread = AppLoaderThread()
        loader_thread.start()

        login_dialog = LoginDialog()
        login_result = login_dialog.exec()
        loader_thread.wait()

        from PyQt6.QtWidgets import QDialog
        if login_result == QDialog.DialogCode.Accepted:
            window = MainApp()
            window.show()
            logger.info("Sistema iniciado com sucesso")
            return app.exec()
        logger.info("Login cancelado ou falhou. Encerrando aplicação.")
        return 0

    except ImportError as import_error:
        error_msg = f"Módulo necessário não encontrado: {import_error}"
        logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        return 1

    except Exception as e:
        error_msg = f"Erro crítico ao iniciar aplicação: {e}"
        logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        return 1



if __name__ == "__main__":
    sys.exit(main())