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
        background: #4a4a4a;
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
        color: #b0b0b0;
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
        background: #5a5a5a;
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
        border-color: #5a5a5a;
    }
    
    QPushButton:pressed {
        background: #5a5a5a;
    }

    /* Campos de texto */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 8px;
        selection-background-color: #5a5a5a;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #5a5a5a;
    }

    /* ComboBox e SpinBox */
    QComboBox, QSpinBox, QDoubleSpinBox {
        background: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 8px;
        color: #e6e6e6;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox QAbstractItemView {
        background: #2d2d2d;
        selection-background-color: #5a5a5a;
    }

    /* ScrollBars */
    QScrollBar:vertical {
        background: #2d2d2d;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background: #505050;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #6a6a6a;
    }
    
    QScrollBar:horizontal {
        background: #2d2d2d;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background: #505050;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background: #6a6a6a;
    }
    
    /* MessageBox */
    QMessageBox {
        background: #2d2d2d;
    }
    
    QMessageBox QLabel {
        color: #e6e6e6;
    }
    """
    
    # Tema claro
    LIGHT_THEME = """
    /* Cores e estilo base - TEMA CLARO */
    QWidget {
        background: #ffffff;
        color: #2c3e50;
    }

    /* Tabs principais */
    QTabWidget::pane {
        border: none;
        background: #ffffff;
    }
    
    QTabBar::tab {
        background: #ecf0f1;
        color: #7f8c8d;
        border: none;
        padding: 8px 20px;
        margin: 0;
        margin-right: 2px;
    }
    
    QTabBar::tab:selected {
        background: #95a5a6;
        color: white;
    }
    
    QTabBar::tab:hover:!selected {
        background: #bdc3c7;
    }

    /* Headers e labels */
    QLabel#header {
        color: #2c3e50;
        font-weight: 600;
        font-size: 16px;
    }
    
    QLabel#sectionLabel {
        color: #7f8c8d;
        font-weight: 500;
        font-size: 14px;
    }

    /* Listas e tabelas */
    QListWidget, QTableWidget {
        background: #f8f9fa;
        border: 1px solid #dce1e6;
        border-radius: 8px;
        padding: 8px;
    }
    
    QTableWidget::item {
        padding: 8px;
        color: #2c3e50;
    }
    
    QTableWidget::item:selected {
        background: #7f8c8d;
        color: white;
    }

    /* Botões */
    QPushButton {
        background: #ecf0f1;
        border: 1px solid #bdc3c7;
        border-radius: 6px;
        color: #2c3e50;
        padding: 8px 16px;
        font-weight: 500;
    }
    
    QPushButton:hover {
        background: #bdc3c7;
        border-color: #7f8c8d;
    }
    
    QPushButton:pressed {
        background: #7f8c8d;
        color: white;
    }

    /* Campos de texto */
    QLineEdit, QTextEdit, QPlainTextEdit {
        background: #ffffff;
        border: 1px solid #bdc3c7;
        border-radius: 6px;
        padding: 8px;
        color: #2c3e50;
        selection-background-color: #7f8c8d;
    }
    
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border-color: #7f8c8d;
    }

    /* ComboBox e SpinBox */
    QComboBox, QSpinBox, QDoubleSpinBox {
        background: #ffffff;
        border: 1px solid #bdc3c7;
        border-radius: 6px;
        padding: 8px;
        color: #2c3e50;
    }
    
    QComboBox::drop-down {
        border: none;
    }
    
    QComboBox QAbstractItemView {
        background: #ffffff;
        selection-background-color: #7f8c8d;
        color: #2c3e50;
    }

    /* ScrollBars */
    QScrollBar:vertical {
        background: #ecf0f1;
        width: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:vertical {
        background: #95a5a6;
        border-radius: 6px;
        min-height: 20px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: #7f8c8d;
    }
    
    QScrollBar:horizontal {
        background: #ecf0f1;
        height: 12px;
        border-radius: 6px;
    }
    
    QScrollBar::handle:horizontal {
        background: #95a5a6;
        border-radius: 6px;
        min-width: 20px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background: #7f8c8d;
    }
    
    /* MessageBox */
    QMessageBox {
        background: #ffffff;
    }
    
    QMessageBox QLabel {
        color: #2c3e50;
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
