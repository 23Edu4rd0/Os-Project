"""
Script para adicionar suporte a temas dinâmicos nos componentes existentes.
Adiciona método para atualizar estilos quando o tema é alterado.
"""

import os
import re

# Adicionar método de atualização de tema em cada componente
THEME_UPDATE_METHOD = '''
    def update_theme(self):
        """Atualiza os estilos do componente baseado no tema atual"""
        from app.ui.dynamic_styles import (
            get_info_frame_style, get_header_label_style, get_table_style,
            get_button_primary_style, get_button_secondary_style, 
            get_button_success_style, get_button_danger_style,
            get_button_close_style, get_button_action_style,
            get_search_input_style, get_results_label_style,
            get_menu_style, get_message_box_style, get_header_style
        )
        
        # Atualizar estilos de todos os componentes
        if hasattr(self, 'search_entry'):
            self.search_entry.setStyleSheet(get_search_input_style())
        
        if hasattr(self, 'btn_pesquisar'):
            self.btn_pesquisar.setStyleSheet(get_button_primary_style())
        
        if hasattr(self, 'btn_limpar'):
            self.btn_limpar.setStyleSheet(get_button_secondary_style())
        
        if hasattr(self, 'label_resultados'):
            self.label_resultados.setStyleSheet(get_results_label_style())
        
        if hasattr(self, 'table'):
            self.table.setStyleSheet(get_table_style())
            header = self.table.horizontalHeader()
            if header:
                header.setStyleSheet(get_header_style())
        
        # Força atualização visual
        self.update()
'''

print("Script criado para adicionar suporte a temas dinâmicos.")
print("Este é um template. A implementação manual é necessária para cada componente.")
