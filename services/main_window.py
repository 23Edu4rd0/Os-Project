"""
main_window.py - Main application window

Contains the MainApp class with all UI logic.
"""

import sys
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMessageBox, QApplication
)
from PyQt6.QtCore import QTimer, QSettings

from app.ui.theme import apply_app_theme

logger = logging.getLogger(__name__)


class MainApp(QMainWindow):
    """
    Main application window for the Service Order System.
    Provides a tabbed interface for managing clients, service orders, products, and backup/restore operations.
    Handles window state persistence and logging.
    """

    APP_NAME = "Sistema de Ordem de Serviço"
    APP_VERSION = "2.0.0"

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
            }
            
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5a5a5a, stop: 0.1 #525252, 
                    stop: 0.5 #4a4a4a, stop: 0.9 #3e3e3e, stop: 1 #3a3a3a);
                border: 2px solid #666666;
                color: #f0f0f0;
            }
            
            QTabBar::tab:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #005588, stop: 0.5 #004466, stop: 1 #003344);
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
            
            from app.components.clients_manager import ClientesManager
            from app.components.orders import PedidosManager
            from app.components.products_manager import ProdutosManager
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
