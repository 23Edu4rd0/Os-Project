"""
app_runner.py - Application runner service

Main entry point logic for running the application.
"""

import sys
import logging
from PyQt6.QtWidgets import QDialog

from services.app_config import initialize_config
from services.app_setup import setup_application
from services.main_window import MainApp
from app.ui.login_dialog import LoginDialog
from app.ui.app_loader_thread import AppLoaderThread

logger = logging.getLogger(__name__)


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


def run_app() -> int:
    """
    Main entry point for the application.
    Initializes logging, exception handling, the interface, and runs the main event loop.
    
    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    try:
        # Initialize configuration
        global logger
        logger, root_dir = initialize_config()
        
        # Setup exception handler
        sys.excepthook = handle_exception
        logger.info("Iniciando Sistema de Ordem de Serviço...")

        # Setup QApplication
        app = setup_application(root_dir)

        # Simula processamento do app principal enquanto login está aberto
        loader_thread = AppLoaderThread()
        loader_thread.start()

        # Show login dialog
        login_dialog = LoginDialog()
        login_result = login_dialog.exec()
        loader_thread.wait()

        # If login successful, show main window
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
