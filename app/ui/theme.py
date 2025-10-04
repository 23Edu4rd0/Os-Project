from PyQt6.QtWidgets import QStyle, QApplication
from PyQt6.QtGui import QIcon
from app.ui.theme_manager import get_theme_manager


def apply_app_theme(app: QApplication):
    """
    Apply a compact, app-wide stylesheet for a consistent look.
    Usa o gerenciador de temas para aplicar tema salvo (claro/escuro).
    """
    theme_manager = get_theme_manager()
    theme_manager.apply_theme(app)
    return  # Retorna aqui, o tema já foi aplicado
    
    # Código antigo mantido para compatibilidade (não será executado)
    style = """
    /* Cores e estilo base */
    QWidget {
        background: #1e1e1e;
        color: #e6e6e6;
    }

    /* Tabs principais */
    QTabWidget::pane {
        border: none;
        background: #1e1e1e;
    }
    
    QTabBar::tab {
        background: #2d2d2d;
        color: #b0b0b0;
        border: none;
        padding: 8px 20px;
        margin: 0;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background: #0d7377;
        color: white;
    }
    
    QTabBar::tab:hover:!selected {
        background: #3d3d3d;
    }

    /* Headers e labels */
    QLabel#header {
        color: #ffffff;
        font-weight: 600;
        font-size: 16px;
    }
    
    QLabel#sectionLabel {
        color: #0d7377;
        font-weight: 500;
        font-size: 14px;
    }

    /* Listas e tabelas */
    QListWidget, QTableWidget {
        background: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 8px;
    }
    
    QTableWidget::item {
        padding: 8px;
    }
    
    QTableWidget::item:selected {
        background: #0d7377;
    }

    /* Botões */
    QPushButton {
        background: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 6px;
        color: #e6e6e6;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background: #3d3d3d;
        border-color: #0d7377;
    }
    
    QPushButton:pressed {
        background: #0d7377;
    }

    /* Campos de texto */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 8px;
        selection-background-color: #0d7377;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #0d7377;
    }

    /* Tooltips */
    QToolTip {
        background: #2d2d2d;
        color: #e6e6e6;
        border: 1px solid #404040;
        border-radius: 4px;
        padding: 6px;
    }

    /* Cards */
    QFrame#card {
        background: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 10px;
    }
    """
    app.setStyleSheet(style)


_STANDARD_MAP = {
    'refresh': QStyle.StandardPixmap.SP_BrowserReload,
    'create': QStyle.StandardPixmap.SP_DialogSaveButton,
    'restore': QStyle.StandardPixmap.SP_DialogOpenButton,
    'replace': QStyle.StandardPixmap.SP_FileDialogNewFolder,
    'delete': QStyle.StandardPixmap.SP_TrashIcon if hasattr(QStyle.StandardPixmap, 'SP_TrashIcon') else QStyle.StandardPixmap.SP_DialogCloseButton,
}


def small_icon(app: QApplication, name: str) -> QIcon | None:
    """Return a small QIcon for a logical name using the current style's standard pixmaps.

    Names: 'refresh','create','restore','replace','delete'
    """
    sp = _STANDARD_MAP.get(name)
    if sp is None:
        return None
    return app.style().standardIcon(sp)
