"""
Gerenciador de cores para produtos
"""

import json
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, 
    QLineEdit, QLabel, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt


class ColorManagerDialog(QDialog):
    """Dialog para gerenciar cores dos produtos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'colors.json')
        self.setWindowTitle("Gerenciar Cores")
        self.setModal(True)
        self.resize(400, 500)
        self._setup_ui()
        self._load_colors()
        self._apply_styles()
    
    def _setup_ui(self):
        """Configura a interface do dialog"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Gerenciamento de Cores")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Lista de cores
        self.colors_list = QListWidget()
        self.colors_list.setMinimumHeight(300)
        layout.addWidget(self.colors_list)
        
        # Entrada para nova cor
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Nova cor:"))
        
        self.new_color_input = QLineEdit()
        self.new_color_input.setPlaceholderText("Digite o nome da cor...")
        self.new_color_input.returnPressed.connect(self._add_color)
        input_layout.addWidget(self.new_color_input)
        
        layout.addLayout(input_layout)
        
        # Botões de ação
        actions_layout = QHBoxLayout()
        
        btn_add = QPushButton("Adicionar")
        btn_add.clicked.connect(self._add_color)
        actions_layout.addWidget(btn_add)
        
        btn_edit = QPushButton("Editar")
        btn_edit.clicked.connect(self._edit_color)
        actions_layout.addWidget(btn_edit)
        
        btn_remove = QPushButton("Remover")
        btn_remove.clicked.connect(self._remove_color)
        actions_layout.addWidget(btn_remove)
        
        layout.addLayout(actions_layout)
        
        # Botões de controle
        control_layout = QHBoxLayout()
        control_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        control_layout.addWidget(btn_cancel)
        
        btn_save = QPushButton("Salvar")
        btn_save.clicked.connect(self._save_colors)
        btn_save.setDefault(True)
        control_layout.addWidget(btn_save)
        
        layout.addLayout(control_layout)
    
    def _load_colors(self):
        """Carrega cores do arquivo JSON"""
        try:
            if os.path.exists(self.colors_file):
                with open(self.colors_file, 'r', encoding='utf-8') as f:
                    self.colors = json.load(f)
            else:
                # Cores padrão se o arquivo não existir
                self.colors = [
                    "Branco", "Preto", "Azul", "Verde", "Vermelho", 
                    "Amarelo", "Personalizado"
                ]
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar cores: {e}")
            self.colors = ["Branco", "Preto", "Personalizado"]
        
        self._refresh_list()
    
    def _refresh_list(self):
        """Atualiza a lista na interface"""
        self.colors_list.clear()
        for color in self.colors:
            self.colors_list.addItem(color)
    
    def _add_color(self):
        """Adiciona uma nova cor"""
        color_name = self.new_color_input.text().strip()
        if not color_name:
            QMessageBox.warning(self, "Atenção", "Digite o nome da cor!")
            return
        
        if color_name in self.colors:
            QMessageBox.warning(self, "Atenção", "Esta cor já existe!")
            return
        
        self.colors.append(color_name)
        self._refresh_list()
        self.new_color_input.clear()
    
    def _edit_color(self):
        """Edita a cor selecionada"""
        current_row = self.colors_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Atenção", "Selecione uma cor para editar!")
            return
        
        current_color = self.colors[current_row]
        new_name, ok = QInputDialog.getText(
            self, "Editar Cor", "Nome da cor:", 
            text=current_color
        )
        
        if ok and new_name.strip():
            new_name = new_name.strip()
            if new_name != current_color and new_name in self.colors:
                QMessageBox.warning(self, "Atenção", "Esta cor já existe!")
                return
            
            self.colors[current_row] = new_name
            self._refresh_list()
            self.colors_list.setCurrentRow(current_row)
    
    def _remove_color(self):
        """Remove a cor selecionada"""
        current_row = self.colors_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Atenção", "Selecione uma cor para remover!")
            return
        
        color_name = self.colors[current_row]
        
        # Confirmar remoção
        reply = QMessageBox.question(
            self, "Confirmar", 
            f"Deseja realmente remover a cor '{color_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.colors[current_row]
            self._refresh_list()
    
    def _save_colors(self):
        """Salva as cores no arquivo JSON"""
        try:
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(self.colors_file), exist_ok=True)
            
            with open(self.colors_file, 'w', encoding='utf-8') as f:
                json.dump(self.colors, f, indent=2, ensure_ascii=False)
            
            # Emitir sinal para atualizar outras interfaces
            try:
                from app.signals import get_signals
                signals = get_signals()
                signals.cores_atualizadas.emit()
            except Exception:
                pass
            
            QMessageBox.information(self, "Sucesso", "Cores salvas com sucesso!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar cores: {e}")
    
    def _apply_styles(self):
        """Aplica estilos ao dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
            QLineEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #0d7377;
            }
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5d60;
            }
        """)


def load_colors():
    """Carrega cores do arquivo JSON"""
    colors_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'colors.json')
    try:
        if os.path.exists(colors_file):
            with open(colors_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Cores padrão
            return [
                "Branco", "Preto", "Azul", "Verde", "Vermelho", 
                "Amarelo", "Personalizado"
            ]
    except Exception:
        return ["Branco", "Preto", "Personalizado"]