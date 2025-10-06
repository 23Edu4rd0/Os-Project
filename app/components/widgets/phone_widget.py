"""
Widget customizado de telefone com formatação automática.
"""

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from app.validation.telefone_validator import TelefoneValidator


class TelefoneLineEdit(QLineEdit):
    """
    QLineEdit customizado para entrada de telefones com formatação automática.
    
    Funcionalidades:
    - Formatação automática enquanto digita
    - Aceita apenas números
    - Limita a 11 dígitos
    - Valida DDD
    """
    
    # Sinal emitido quando o telefone é válido
    telefone_valido = pyqtSignal(str)  # Emite telefone sem formatação
    telefone_invalido = pyqtSignal(str)  # Emite mensagem de erro
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("(00) 00000-0000")
        self.setMaxLength(15)  # (11) 98765-4321 = 15 caracteres
        
        # Conectar eventos
        self.textChanged.connect(self._on_text_changed)
        self.editingFinished.connect(self._on_editing_finished)
        
        # Estilo
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QLineEdit:focus {
                border: 2px solid #007ACC;
            }
            QLineEdit[valid="true"] {
                border: 2px solid #28a745;
            }
            QLineEdit[valid="false"] {
                border: 2px solid #dc3545;
            }
        """)
    
    def _on_text_changed(self, text):
        """Formata o texto enquanto o usuário digita"""
        if not text:
            return
        
        # Obter posição atual do cursor
        cursor_pos = self.cursorPosition()
        
        # Formatar
        texto_formatado, nova_pos = TelefoneValidator.formatar_enquanto_digita(text, cursor_pos)
        
        # Se o texto mudou, atualizar
        if texto_formatado != text:
            # Bloquear sinal temporariamente para evitar loop
            self.blockSignals(True)
            self.setText(texto_formatado)
            self.setCursorPosition(nova_pos)
            self.blockSignals(False)
    
    def _on_editing_finished(self):
        """Valida o telefone quando o campo perde o foco"""
        telefone = self.text()
        
        if not telefone:
            self.setProperty("valid", None)
            self.style().unpolish(self)
            self.style().polish(self)
            return
        
        valido, mensagem = TelefoneValidator.validar_telefone(telefone)
        
        if valido:
            self.setProperty("valid", "true")
            self.telefone_valido.emit(TelefoneValidator.limpar_telefone(telefone))
        else:
            self.setProperty("valid", "false")
            self.telefone_invalido.emit(mensagem)
        
        # Atualizar estilo
        self.style().unpolish(self)
        self.style().polish(self)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Aceita apenas números e teclas de controle"""
        key = event.key()
        
        # Permitir teclas de controle
        if key in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete, Qt.Key.Key_Left, 
                  Qt.Key.Key_Right, Qt.Key.Key_Home, Qt.Key.Key_End, 
                  Qt.Key.Key_Tab, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            super().keyPressEvent(event)
            return
        
        # Permitir Ctrl+C, Ctrl+V, Ctrl+X, Ctrl+A
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            super().keyPressEvent(event)
            return
        
        # Permitir apenas números
        text = event.text()
        if text.isdigit():
            super().keyPressEvent(event)
        else:
            event.ignore()
    
    def get_telefone_limpo(self) -> str:
        """
        Retorna o telefone sem formatação (apenas números).
        
        Returns:
            String contendo apenas números
        """
        return TelefoneValidator.limpar_telefone(self.text())
    
    def get_telefone_formatado(self) -> str:
        """
        Retorna o telefone formatado.
        
        Returns:
            Telefone no formato (11) 98765-4321
        """
        return TelefoneValidator.formatar_telefone(self.text())
    
    def set_telefone(self, telefone: str):
        """
        Define o telefone (com ou sem formatação).
        
        Args:
            telefone: Telefone a ser definido
        """
        formatado = TelefoneValidator.formatar_telefone(telefone)
        self.setText(formatado)
    
    def is_valido(self) -> bool:
        """
        Verifica se o telefone atual é válido.
        
        Returns:
            True se válido, False caso contrário
        """
        valido, _ = TelefoneValidator.validar_telefone(self.text())
        return valido
    
    def limpar(self):
        """Limpa o campo e reseta a validação"""
        self.clear()
        self.setProperty("valid", None)
        self.style().unpolish(self)
        self.style().polish(self)
