"""Theme manager simplificado: somente tema escuro."""

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    DARK_THEME = """
    QWidget { background-color: #1e1e1e; color: #e6e6e6; }
    QMainWindow { background-color: #1e1e1e; }
    QTabWidget::pane { border: none; background-color: #1e1e1e; }
    QTabBar::tab { background-color: #2d2d2d; color: #b0b0b0; border: none; padding: 8px 20px; margin: 0; margin-right: 2px; }
    QTabBar::tab:selected { background-color: #4a4a4a; color: #ffffff; }
    QTabBar::tab:hover:!selected { background-color: #3d3d3d; }
    QLabel { background-color: transparent; color: #e6e6e6; }
    QLabel#header { color: #ffffff; font-weight: 600; font-size: 16px; }
    QListWidget, QTableWidget { background-color: #2d2d2d; border: 1px solid #404040; border-radius: 8px; padding: 8px; color: #e6e6e6; }
    QTableWidget::item { padding: 8px; color: #e6e6e6; }
    QTableWidget::item:selected { background-color: #5a5a5a; }
    QHeaderView::section { background-color: #2d2d2d; color: #e6e6e6; padding: 4px; border: 1px solid #404040; }
    QPushButton { background-color: #2d2d2d; border: 1px solid #404040; border-radius: 6px; color: #e6e6e6; padding: 8px 16px; }
    QPushButton:hover { background-color: #3d3d3d; }
    QPushButton:pressed { background-color: #5a5a5a; }
    QPushButton:disabled { background-color: #252525; color: #666666; }
    QLineEdit, QTextEdit, QPlainTextEdit { background-color: #2d2d2d; border: 1px solid #404040; border-radius: 6px; padding: 8px; color: #e6e6e6; }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus { border: 2px solid #5a5a5a; }
    QComboBox, QSpinBox, QDoubleSpinBox { background-color: #2d2d2d; border: 1px solid #404040; border-radius: 6px; padding: 8px; color: #e6e6e6; }
    QScrollBar:vertical, QScrollBar:horizontal { background-color: #2d2d2d; border-radius: 6px; }
    QScrollBar:vertical { width: 12px; }
    QScrollBar:horizontal { height: 12px; }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background-color: #505050; border-radius: 6px; }
    QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover { background-color: #6a6a6a; }
    QMenuBar { background-color: #1e1e1e; color: #e6e6e6; }
    QMenu { background-color: #2d2d2d; color: #e6e6e6; border: 1px solid #404040; }
    QMenu::item:selected { background-color: #5a5a5a; }
    QMessageBox { background-color: #2d2d2d; }
    QGroupBox { background-color: #2d2d2d; border: 1px solid #404040; border-radius: 6px; margin-top: 6px; padding-top: 10px; }
    QGroupBox::title { color: #b0b0b0; left: 10px; }
    QCheckBox, QRadioButton { color: #e6e6e6; }
    QCheckBox::indicator, QRadioButton::indicator { width:16px; height:16px; border:1px solid #404040; background:#2d2d2d; }
    QCheckBox::indicator:checked, QRadioButton::indicator:checked { background:#5a5a5a; border-color:#5a5a5a; }
    QStatusBar { background:#2d2d2d; color:#e6e6e6; }
    QProgressBar { background:#2d2d2d; border:1px solid #404040; border-radius:4px; text-align:center; color:#e6e6e6; }
    QProgressBar::chunk { background:#5a5a5a; border-radius:4px; }
    """

    def __init__(self):
        self.settings = QSettings("OSProject", "App")
        self._current_theme = "dark"
        self.save_theme_preference("dark")

    def save_theme_preference(self, theme: str = "dark"):
        self.settings.setValue("theme", "dark")
        self._current_theme = "dark"

    def get_current_theme(self) -> str:
        return "dark"

    def is_dark_theme(self) -> bool:
        return True

    def is_light_theme(self) -> bool:
        return False

    def apply_theme(self, app: QApplication, theme: str = None):
        app.setStyleSheet(self.DARK_THEME)
        self._current_theme = "dark"

    def toggle_theme(self, app: QApplication):
        self.apply_theme(app, "dark")
        return "dark"


_theme_manager = None


def get_theme_manager() -> ThemeManager:
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
