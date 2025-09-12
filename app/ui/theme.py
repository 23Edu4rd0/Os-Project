from PyQt6.QtWidgets import QStyle, QApplication
from PyQt6.QtGui import QIcon


def apply_app_theme(app: QApplication):
    """Apply a compact, app-wide stylesheet for a consistent look."""
    style = """
    QWidget { background: #262626; color: #e6e6e6; }
    QTabWidget::pane { border: none; }
    QLabel#header { color: #ffffff; font-weight: 600; font-size: 16px; }
    QListWidget { background: #1f1f1f; border: 1px solid #393939; border-radius: 6px; padding: 6px; }
    QPushButton { background: #323232; border: 1px solid #444444; border-radius: 6px; color: #eaeaea; }
    QPushButton:hover { background: #3d3d3d; }
    QPlainTextEdit { background: #141414; border: 1px solid #333333; border-radius: 6px; }
    QToolTip { background: #111111; color: #eaeaea; border: 1px solid #333333; }
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
