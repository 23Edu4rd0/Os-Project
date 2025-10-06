"""
Módulo de estilos dinâmicos que se adaptam ao tema atual (claro/escuro).
Fornece funções helper para retornar estilos CSS baseados no tema ativo.
"""

from app.ui.theme_manager import get_theme_manager


def get_info_frame_style():
    """Retorna o estilo para frames de informação"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QFrame { 
                background: #1f232b; 
                border-radius: 12px; 
                padding: 12px;
            }
        """
    else:
        return """
            QFrame { 
                background: #ffffff; 
                border: 1px solid #dfe4ea;
                border-radius: 12px; 
                padding: 12px;
            }
        """


def get_label_color():
    """Retorna a cor do texto para labels"""
    theme_manager = get_theme_manager()
    return "#2c3e50" if theme_manager.is_light_theme() else "#c0c0c0"


def get_accent_color():
    """Retorna a cor de destaque"""
    theme_manager = get_theme_manager()
    return "#4A90E2" if theme_manager.is_light_theme() else "#50fa7b"


def get_header_label_style():
    """Retorna o estilo para labels de cabeçalho"""
    theme_manager = get_theme_manager()
    color = "#2c3e50" if theme_manager.is_light_theme() else "#e0e0e0"
    return f"font-size: 16px; font-weight: bold; color: {color}; margin-bottom: 6px;"


def get_small_label_style():
    """Retorna o estilo para labels pequenos"""
    theme_manager = get_theme_manager()
    color = "#57606f" if theme_manager.is_light_theme() else "#c0c0c0"
    return f"font-size: 11px; color: {color}; margin-top: 4px;"


def get_address_label_style():
    """Retorna o estilo para labels de endereço"""
    return "font-size: 12px; line-height: 1.4;"


def get_purchases_label_style():
    """Retorna o estilo para labels de compras"""
    accent = get_accent_color()
    return f"font-size: 13px; color: {accent}; font-weight: bold; margin-top: 8px;"


def get_table_style():
    """Retorna o estilo para tabelas"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QTableWidget {
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 8px;
                gridline-color: #404040;
            }
            QTableWidget::item {
                padding: 8px;
                color: #e6e6e6;
                border-bottom: 1px solid #2d2d2d;
            }
            QTableWidget::item:selected {
                background-color: #5a5a5a;
                color: white;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #e6e6e6;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #404040;
                font-weight: bold;
                font-size: 13px;
            }
        """
    else:
        return """
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #dfe4ea;
                border-radius: 8px;
                gridline-color: #dfe4ea;
            }
            QTableWidget::item {
                padding: 8px;
                color: #2c3e50;
                border-bottom: 1px solid #f5f6fa;
            }
            QTableWidget::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                color: #2c3e50;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #dfe4ea;
                font-weight: bold;
                font-size: 13px;
            }
        """


def get_button_primary_style():
    """Retorna o estilo para botões primários (ações principais)"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5c5f;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2868A8;
            }
        """


def get_button_secondary_style():
    """Retorna o estilo para botões secundários"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QPushButton {
                background-color: #3d3d3d;
                color: #e6e6e6;
                border: 1px solid #505050;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #606060;
            }
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #dfe4ea;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #f5f6fa;
                border-color: #4A90E2;
            }
            QPushButton:pressed {
                background-color: #e8e9ed;
            }
        """


def get_button_success_style():
    """Retorna o estilo para botões de sucesso (WhatsApp, etc)"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QPushButton {
                background-color: #25d366;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1fa855;
            }
            QPushButton:pressed {
                background-color: #1a8e47;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #25d366;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1fa855;
            }
            QPushButton:pressed {
                background-color: #1a8e47;
            }
        """


def get_button_danger_style():
    """Retorna o estilo para botões de perigo (deletar, etc)"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QPushButton {
                background-color: #ff5555;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
            }
            QPushButton:pressed {
                background-color: #ee4444;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """


def get_button_close_style():
    """Retorna o estilo para botões de fechar"""
    return get_button_secondary_style()


def get_button_action_style():
    """Retorna o estilo para botões de ação em tabelas"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QPushButton {
                background-color: #2d2d2d;
                color: #e6e6e6;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0d7377;
                border-color: #0d7377;
                color: white;
            }
            QPushButton:pressed {
                background-color: #0a5c5f;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #dfe4ea;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #4A90E2;
                border-color: #4A90E2;
                color: white;
            }
            QPushButton:pressed {
                background-color: #357ABD;
            }
        """


def get_search_input_style():
    """Retorna o estilo para campos de busca"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 10px 15px;
                color: #e6e6e6;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0d7377;
            }
        """
    else:
        return """
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #dfe4ea;
                border-radius: 8px;
                padding: 10px 15px;
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
        """


def get_results_label_style():
    """Retorna o estilo para labels de resultados"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QLabel {
                color: #50fa7b;
                font-size: 14px;
                font-weight: 600;
                padding: 8px;
                background: transparent;
            }
        """
    else:
        return """
            QLabel {
                color: #27ae60;
                font-size: 14px;
                font-weight: 600;
                padding: 8px;
                background: transparent;
            }
        """


def get_menu_style():
    """Retorna o estilo para menus contextuais"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QMenu {
                background-color: #2d2d2d;
                color: #e6e6e6;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #0d7377;
            }
            QMenu::separator {
                height: 1px;
                background: #404040;
                margin: 5px 10px;
            }
        """
    else:
        return """
            QMenu {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #dfe4ea;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #4A90E2;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #dfe4ea;
                margin: 5px 10px;
            }
        """


def get_message_box_style():
    """Retorna o estilo para caixas de mensagem"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return """
            QMessageBox {
                background-color: #2d2d2d;
            }
            QMessageBox QLabel {
                color: #e6e6e6;
                font-size: 13px;
            }
            QMessageBox QPushButton {
                background-color: #3d3d3d;
                color: #e6e6e6;
                border: 1px solid #505050;
                border-radius: 6px;
                padding: 8px 20px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4d4d4d;
            }
        """
    else:
        return """
            QMessageBox {
                background-color: #f5f6fa;
            }
            QMessageBox QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QMessageBox QPushButton {
                background-color: #ffffff;
                color: #2c3e50;
                border: 1px solid #dfe4ea;
                border-radius: 6px;
                padding: 8px 20px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4A90E2;
                color: white;
            }
        """


def get_header_style():
    """Retorna o estilo para cabeçalhos de tabela"""
    theme_manager = get_theme_manager()
    
    if theme_manager.is_dark_theme():
        return "QHeaderView::section { background-color: #1f1f1f; color: #e6e6e6; font-weight: bold; font-size: 14px; }"
    else:
        return "QHeaderView::section { background-color: #f5f6fa; color: #2c3e50; font-weight: bold; font-size: 14px; border: 1px solid #dfe4ea; }"
