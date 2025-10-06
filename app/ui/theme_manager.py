"""
Sistema de temas claro/escuro com persistência de preferências.
"""

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication


class ThemeManager:
    """Gerenciador de temas da aplicação"""
    
    # Tema escuro (padrão atual)
    DARK_THEME = """
    /* Cores e estilo base - TEMA ESCURO */
    QWidget {
        background-color: #1e1e1e;
        color: #e6e6e6;
    }
    
    QMainWindow {
        background-color: #1e1e1e;
    }

    /* Tabs principais */
    QTabWidget::pane {
        border: none;
        background-color: #1e1e1e;
    }
    
    QTabBar::tab {
        background-color: #2d2d2d;
        color: #b0b0b0;
        border: none;
        padding: 8px 20px;
        margin: 0;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #4a4a4a;
        color: white;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #3d3d3d;
    }

    /* Headers e labels */
    QLabel {
        background-color: transparent;
        color: #e6e6e6;
    }
    
    QLabel#header {
        color: #ffffff;
        font-weight: 600;
        font-size: 16px;
    }
    
    QLabel#sectionLabel {
        color: #b0b0b0;
        font-weight: 500;
        font-size: 14px;
    }

    /* Listas e tabelas */
    QListWidget, QTableWidget {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 8px;
        padding: 8px;
        color: #e6e6e6;
    }
    
    QTableWidget::item {
        padding: 8px;
        color: #e6e6e6;
        background-color: transparent;
    }
    
    QTableWidget::item:selected {
        background-color: #5a5a5a;
    }

    QHeaderView::section {
        background-color: #2d2d2d;
        color: #e6e6e6;
        padding: 4px;
        border: 1px solid #404040;
    }

    /* Botões */
    QPushButton {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 6px;
        color: #e6e6e6;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #3d3d3d;
        border-color: #5a5a5a;
    }
    
    QPushButton:pressed {
        background-color: #5a5a5a;
    }
    
    QPushButton:disabled {
        background-color: #252525;
        color: #666666;
        border-color: #404040;
    }

    /* Campos de texto */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 8px;
        color: #e6e6e6;
        selection-background-color: #5a5a5a;
        selection-color: white;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #5a5a5a;
        border-width: 2px;
    }

    /* ComboBox e SpinBox */
    QComboBox, QSpinBox, QDoubleSpinBox {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 8px;
        color: #e6e6e6;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox QAbstractItemView {
        background-color: #2d2d2d;
        selection-background-color: #5a5a5a;
        selection-color: white;
        color: #e6e6e6;
        border: 1px solid #404040;
    }

    /* ScrollBars */
    QScrollBar:vertical {
        background-color: #2d2d2d;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #505050;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #6a6a6a;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    
    QScrollBar:horizontal {
        background-color: #2d2d2d;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #505050;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #6a6a6a;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
    }
    
    /* MenuBar */
    QMenuBar {
        background-color: #1e1e1e;
        color: #e6e6e6;
    }
    
    QMenuBar::item:selected {
        background-color: #2d2d2d;
    }
    
    QMenu {
        background-color: #2d2d2d;
        color: #e6e6e6;
        border: 1px solid #404040;
    }
    
    QMenu::item:selected {
        background-color: #5a5a5a;
    }
    
    /* MessageBox */
    QMessageBox {
        background-color: #2d2d2d;
    }
    
    QMessageBox QLabel {
        color: #e6e6e6;
        background-color: transparent;
    }
    
    QMessageBox QPushButton {
        min-width: 80px;
    }
    
    /* GroupBox */
    QGroupBox {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 6px;
        margin-top: 6px;
        padding-top: 10px;
        color: #e6e6e6;
    }
    
    QGroupBox::title {
        color: #b0b0b0;
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    
    /* CheckBox e RadioButton */
    QCheckBox, QRadioButton {
        color: #e6e6e6;
        background-color: transparent;
    }
    
    QCheckBox::indicator, QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #404040;
        background-color: #2d2d2d;
    }
    
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #5a5a5a;
        border-color: #5a5a5a;
    }
    
    /* StatusBar */
    QStatusBar {
        background-color: #2d2d2d;
        color: #e6e6e6;
    }
    
    /* ProgressBar */
    QProgressBar {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 4px;
        text-align: center;
        color: #e6e6e6;
    }
    
    QProgressBar::chunk {
        background-color: #5a5a5a;
        border-radius: 4px;
    }
    """
    
    # Tema claro
    LIGHT_THEME = """
    /* Cores e estilo base - TEMA CLARO */
    QWidget {
        background-color: #f5f6fa;
        color: #2c3e50;
    }
    
    QMainWindow {
        background-color: #f5f6fa;
    }

    /* Tabs principais */
    QTabWidget::pane {
        border: none;
        background-color: #f5f6fa;
    }
    
    QTabBar::tab {
        background-color: #dfe4ea;
        color: #57606f;
        border: none;
        padding: 8px 20px;
        margin: 0;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background-color: #4A90E2;
        color: white;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #ced6e0;
    }

    /* Headers e labels */
    QLabel {
        background-color: transparent;
        color: #2c3e50;
    }
    
    QLabel#header {
        color: #2c3e50;
        font-weight: 600;
        font-size: 16px;
    }
    
    QLabel#sectionLabel {
        color: #4A90E2;
        font-weight: 500;
        font-size: 14px;
    }

    /* Listas e tabelas */
    QListWidget, QTableWidget {
        background-color: #ffffff;
        border: 1px solid #dfe4ea;
        border-radius: 8px;
        padding: 8px;
        color: #2c3e50;
    }
    
    QTableWidget::item {
        padding: 8px;
        color: #2c3e50;
        background-color: transparent;
    }
    
    QTableWidget::item:selected {
        background-color: #4A90E2;
        color: white;
    }
    
    QHeaderView::section {
        background-color: #dfe4ea;
        color: #2c3e50;
        padding: 4px;
        border: 1px solid #ced6e0;
    }

    /* Botões */
    QPushButton {
        background-color: #ffffff;
        border: 1px solid #dfe4ea;
        border-radius: 6px;
        color: #2c3e50;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background-color: #dfe4ea;
        border-color: #4A90E2;
    }
    
    QPushButton:pressed {
        background-color: #4A90E2;
        color: white;
    }
    
    QPushButton:disabled {
        background-color: #ecf0f1;
        color: #95a5a6;
        border-color: #dfe4ea;
    }

    /* Campos de texto */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #ffffff;
        border: 1px solid #dfe4ea;
        border-radius: 6px;
        padding: 8px;
        color: #2c3e50;
        selection-background-color: #4A90E2;
        selection-color: white;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #4A90E2;
        border-width: 2px;
    }

    /* ComboBox e SpinBox */
    QComboBox, QSpinBox, QDoubleSpinBox {
        background-color: #ffffff;
        border: 1px solid #dfe4ea;
        border-radius: 6px;
        padding: 8px;
        color: #2c3e50;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        selection-background-color: #4A90E2;
        selection-color: white;
        color: #2c3e50;
        border: 1px solid #dfe4ea;
    }

    /* ScrollBars */
    QScrollBar:vertical {
        background-color: #f5f6fa;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background-color: #a4b0be;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background-color: #57606f;
    }
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        border: none;
        background: none;
    }
    
    QScrollBar:horizontal {
        background-color: #f5f6fa;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background-color: #a4b0be;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background-color: #57606f;
    }
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        border: none;
        background: none;
    }
    
    /* MenuBar */
    QMenuBar {
        background-color: #f5f6fa;
        color: #2c3e50;
    }
    
    QMenuBar::item:selected {
        background-color: #dfe4ea;
    }
    
    QMenu {
        background-color: #ffffff;
        color: #2c3e50;
        border: 1px solid #dfe4ea;
    }
    
    QMenu::item:selected {
        background-color: #4A90E2;
        color: white;
    }
    
    /* MessageBox */
    QMessageBox {
        background-color: #f5f6fa;
    }
    
    QMessageBox QLabel {
        color: #2c3e50;
        background-color: transparent;
    }
    
    QMessageBox QPushButton {
        min-width: 80px;
    }
    
    /* GroupBox */
    QGroupBox {
        background-color: #ffffff;
        border: 1px solid #dfe4ea;
        border-radius: 6px;
        margin-top: 6px;
        padding-top: 10px;
        color: #2c3e50;
    }
    
    QGroupBox::title {
        color: #4A90E2;
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }
    
    /* CheckBox e RadioButton */
    QCheckBox, QRadioButton {
        color: #2c3e50;
        background-color: transparent;
    }
    
    QCheckBox::indicator, QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #dfe4ea;
        background-color: #ffffff;
    }
    
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #4A90E2;
        border-color: #4A90E2;
    }
    
    /* StatusBar */
    QStatusBar {
        background-color: #dfe4ea;
        color: #2c3e50;
    }
    
    /* ProgressBar */
    QProgressBar {
        background-color: #dfe4ea;
        border: 1px solid #ced6e0;
        border-radius: 4px;
        text-align: center;
        color: #2c3e50;
    }
    
    QProgressBar::chunk {
        background-color: #4A90E2;
        border-radius: 4px;
    }
    """
    
    def __init__(self):
        """Inicializa o gerenciador de temas"""
        self.settings = QSettings("SOS", "OrdemServico")
        self._current_theme = self.load_theme_preference()
    
    def load_theme_preference(self) -> str:
        """
        Carrega a preferência de tema salva.
        
        Returns:
            "dark" ou "light"
        """
        return self.settings.value("theme", "dark")
    
    def save_theme_preference(self, theme: str):
        """
        Salva a preferência de tema.
        
        Args:
            theme: "dark" ou "light"
        """
        self.settings.setValue("theme", theme)
        self._current_theme = theme
    
    def get_current_theme(self) -> str:
        """Retorna o tema atual ("dark" ou "light")"""
        return self._current_theme
    
    def is_dark_theme(self) -> bool:
        """Verifica se o tema atual é escuro"""
        return self._current_theme == "dark"
    
    def is_light_theme(self) -> bool:
        """Verifica se o tema atual é claro"""
        return self._current_theme == "light"
    
    def apply_theme(self, app: QApplication, theme: str = None):
        """
        Aplica um tema à aplicação.
        
        Args:
            app: Instância do QApplication
            theme: "dark" ou "light". Se None, usa o tema salvo.
        """
        if theme is None:
            theme = self._current_theme
        
        if theme == "light":
            app.setStyleSheet(self.LIGHT_THEME)
        else:
            app.setStyleSheet(self.DARK_THEME)
        
        self._current_theme = theme
    
    def toggle_theme(self, app: QApplication):
        """
        Alterna entre tema claro e escuro.
        
        Args:
            app: Instância do QApplication
        """
        new_theme = "light" if self._current_theme == "dark" else "dark"
        self.apply_theme(app, new_theme)
        self.save_theme_preference(new_theme)
        return new_theme


# Instância global do gerenciador de temas
_theme_manager = None

def get_theme_manager() -> ThemeManager:
    """Retorna a instância global do gerenciador de temas"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
