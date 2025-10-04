"""
Módulo de atalhos de teclado globais para o sistema.

Atalhos disponíveis:
- Ctrl+N: Novo registro
- Ctrl+S: Salvar
- Ctrl+F: Focar na busca
- F5: Recarregar dados
- Delete: Deletar item selecionado
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)


class KeyboardShortcutManager:
    """Gerenciador de atalhos de teclado para widgets"""
    
    def __init__(self, widget: QWidget):
        """
        Inicializa o gerenciador de atalhos.
        
        Args:
            widget: Widget onde os atalhos serão aplicados
        """
        self.widget = widget
        self.shortcuts = {}
        logger.debug(f"KeyboardShortcutManager inicializado para {widget.__class__.__name__}")
    
    def add_shortcut(self, key_sequence: str, callback, description: str = ""):
        """
        Adiciona um atalho de teclado.
        
        Args:
            key_sequence: Sequência de teclas (ex: "Ctrl+N", "F5")
            callback: Função a ser executada
            description: Descrição do atalho (para logs)
        """
        try:
            shortcut = QShortcut(QKeySequence(key_sequence), self.widget)
            shortcut.activated.connect(callback)
            self.shortcuts[key_sequence] = {
                'shortcut': shortcut,
                'callback': callback,
                'description': description
            }
            logger.debug(f"Atalho '{key_sequence}' adicionado: {description}")
        except Exception as e:
            logger.error(f"Erro ao adicionar atalho '{key_sequence}': {e}")
    
    def remove_shortcut(self, key_sequence: str):
        """Remove um atalho de teclado"""
        if key_sequence in self.shortcuts:
            self.shortcuts[key_sequence]['shortcut'].setEnabled(False)
            del self.shortcuts[key_sequence]
            logger.debug(f"Atalho '{key_sequence}' removido")
    
    def enable_shortcut(self, key_sequence: str, enabled: bool = True):
        """Habilita ou desabilita um atalho"""
        if key_sequence in self.shortcuts:
            self.shortcuts[key_sequence]['shortcut'].setEnabled(enabled)
    
    def get_shortcuts_info(self) -> dict:
        """Retorna informações sobre todos os atalhos registrados"""
        return {
            key: {
                'description': info['description'],
                'enabled': info['shortcut'].isEnabled()
            }
            for key, info in self.shortcuts.items()
        }


def setup_standard_shortcuts(widget: QWidget, callbacks: dict) -> KeyboardShortcutManager:
    """
    Configura atalhos padrão para um widget.
    
    Args:
        widget: Widget onde os atalhos serão aplicados
        callbacks: Dicionário com callbacks para cada ação:
            - 'new': Callback para Ctrl+N (criar novo)
            - 'save': Callback para Ctrl+S (salvar)
            - 'search': Callback para Ctrl+F (focar busca)
            - 'reload': Callback para F5 (recarregar)
            - 'delete': Callback para Delete (deletar)
    
    Returns:
        Instância do KeyboardShortcutManager
    """
    manager = KeyboardShortcutManager(widget)
    
    shortcuts_config = [
        ('Ctrl+N', 'new', 'Criar novo registro'),
        ('Ctrl+S', 'save', 'Salvar alterações'),
        ('Ctrl+F', 'search', 'Focar no campo de busca'),
        ('F5', 'reload', 'Recarregar dados'),
        ('Delete', 'delete', 'Deletar item selecionado'),
    ]
    
    for key_seq, action, description in shortcuts_config:
        if action in callbacks and callbacks[action] is not None:
            manager.add_shortcut(key_seq, callbacks[action], description)
    
    logger.info(f"Atalhos padrão configurados para {widget.__class__.__name__}")
    return manager
