#!/usr/bin/env python3
"""
Service Order System v1.0.0

Desktop application for managing service orders, clients, products, and reports.

Main features:
- Tabbed interface for clients, orders, financial dashboard, products, and backup.
- Window state and active tab persistence.
- Structured logging and global exception handling.

Author: Eduardo Viana Chaves
License: MIT
"""

import sys
import logging
import warnings
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QTimer, QSettings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ui.theme import apply_app_theme


class MainApp(QMainWindow):
    """
    Main application window for the Service Order System.

    Provides a tabbed interface for managing clients, service orders, financial dashboard,
    products, and backup/restore operations. Handles window state persistence and logging.
    """
    
    APP_NAME = "Sistema de Ordem de Serviço"
    APP_VERSION = "1.0.0"
    
    def __init__(self):
        """
        Initialize the main window, configure the UI, apply global styles, and restore previous window state.
        Logs the initialization process.
        """
        super().__init__()
        logger.info(f"Initializing {self.APP_NAME} v{self.APP_VERSION}")
        
        self.settings = QSettings("SOS", "OrdemServico")
        
        self._setup_ui()
        self._apply_global_styles()
        self._restore_window_state()
        
        logger.info("Application initialized successfully")
    
    def _apply_global_styles(self) -> None:
        """
        Apply global application styles, such as custom tooltips.
        This method sets a consistent tooltip style for the entire application.
        """
        app = QApplication.instance()
        if app:
            tooltip_style = """
                QToolTip {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 2px solid #555555;
                    padding: 8px;
                    font-size: 12px;
                    font-weight: normal;
                    border-radius: 4px;
                }
            """
            app.setStyleSheet(tooltip_style)
        
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
        layout.addWidget(self.tab_widget)
        
        apply_app_theme(self)
        QTimer.singleShot(100, self._init_tabs)
        
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
            from app.components.contas_manager import ContasManager
            from app.components.produtos_manager import ProdutosManager
            from app.ui.backup_tab import BackupTab
            
            tabs_config = [
                ("👥 Clientes", ClientesManager, "Gestão de clientes"),
                ("📋 Pedidos", PedidosManager, "Ordens de serviço"),
                ("💰 Dashboard", ContasManager, "Relatórios financeiros"),
                ("📦 Produtos", ProdutosManager, "Catálogo de produtos"),
                ("💾 Backup", BackupTab, "Backup e restauração")
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
    
    def closeEvent(self, event) -> None:
        """
        Handle the window close event by saving the current window state and logging the process.
        Args:
            event: The close event object.
        Attempts to save the window state and logs the closing process. If an exception occurs during the process, it logs the error. In both cases, it accepts the close event to proceed with closing the application.
        """
        try:
            logger.info("Closing application...")
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
    
    icon_path = ROOT_DIR / "assets" / "icon.ico"
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
        window = MainApp()
        window.show()
        
        logger.info("Sistema iniciado com sucesso")
        return app.exec()
        
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
    exit_code = main()
    sys.exit(exit_code)