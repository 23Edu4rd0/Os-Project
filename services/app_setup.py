"""
app_setup.py - QApplication setup and configuration

Handles QApplication initialization, fonts, icons, and styles.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon

from services.tooltip_service import install_tooltip_fix


def setup_application(root_dir: Path) -> QApplication:
    """
    Initialize and configure the QApplication instance.
    
    Args:
        root_dir: Project root directory
        
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
    
    # Configurar ícone da aplicação
    icon_path = root_dir / "assets" / "logo.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app
