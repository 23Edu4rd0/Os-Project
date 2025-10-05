from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont, QPixmap
from pathlib import Path

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Login')
        self.setModal(True)
        self.setFixedSize(420, 320)
        self.username = ''
        self.password = ''
        # Ícone customizado se existir
        icon_path = Path(__file__).parent.parent.parent / 'assets' / 'logo.ico'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self._build_ui()
        self.setStyleSheet(self._modern_style())
        self.user_input.setFocus()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 16, 20, 16)

        # Logo (opcional)
        logo_path = Path(__file__).parent.parent.parent / 'assets' / 'logo.png'
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path)).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            layout.addWidget(logo_label)

        # Texto
        info = QLabel('Digite usuário e senha para acessar o sistema:')
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet('color: #ddd; font-size: 14px;')
        layout.addWidget(info)

        # Usuário
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText('Usuário')
        self.user_input.setMinimumHeight(34)
        layout.addWidget(self.user_input)

        # Senha
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText('Senha')
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setMinimumHeight(34)
        self.pass_input.returnPressed.connect(self.try_login)
        layout.addWidget(self.pass_input)

        # Botão
        self.login_btn = QPushButton('Entrar')
        self.login_btn.setMinimumHeight(36)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.try_login)
        layout.addWidget(self.login_btn)

    def _modern_style(self):
        return """
        QDialog {
            background-color: #2b2b2b;
        }
        QLabel { color: #e6e6e6; }
        QLineEdit {
            background-color: #1f1f1f;
            border: 1px solid #4b5563;
            border-radius: 6px;
            padding: 8px 10px;
            color: #e6e6e6;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #007ACC;
            background-color: #242424;
        }
        QPushButton {
            background-color: #0d6efd;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            font-size: 15px;
            font-weight: 600;
            padding: 8px 12px;
            margin-top: 8px;
        }
        QPushButton:hover { background-color: #0b5ed7; }
        QPushButton:pressed { background-color: #0a58ca; }
        """

    def try_login(self):
        user = self.user_input.text().strip()
        pwd = self.pass_input.text()
        
        # Validações
        if not user:
            self._show_error("Por favor, digite seu usuário.")
            self.user_input.setFocus()
            return
        
        if not pwd:
            self._show_error("Por favor, digite sua senha.")
            self.pass_input.setFocus()
            return
        
        # Usuário e senha fixos para exemplo
        if user == 'admin' and pwd == '1234':
            self.username = user
            self.password = pwd
            self.accept()
        else:
            self._show_error("Usuário ou senha incorretos!")
            self.pass_input.clear()
            self.pass_input.setFocus()
            self._shake_animation()
    
    def _show_error(self, message):
        """Exibe mensagem de erro com estilo moderno"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Erro de autenticação")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1f2937;
            }
            QMessageBox QLabel {
                color: #f3f4f6;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        msg.exec()
    
    def _shake_animation(self):
        """Animação de shake para erro de login"""
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(500)
        animation.setLoopCount(1)
        
        pos = self.pos()
        animation.setStartValue(pos)
        animation.setKeyValueAt(0.1, pos + Qt.QPoint(-10, 0))
        animation.setKeyValueAt(0.2, pos + Qt.QPoint(10, 0))
        animation.setKeyValueAt(0.3, pos + Qt.QPoint(-10, 0))
        animation.setKeyValueAt(0.4, pos + Qt.QPoint(10, 0))
        animation.setKeyValueAt(0.5, pos + Qt.QPoint(-10, 0))
        animation.setEndValue(pos)
        animation.setEasingCurve(QEasingCurve.Type.InOutElastic)
        animation.start()
        self.animation = animation  # Manter referência
