#!/usr/bin/env python3
"""
Script para testar clique nos botões de editar
"""

import sys
import os
sys.path.append('/home/eduardo/Área de Trabalho/Os-Project')

from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt6.QtCore import QTimer

def test_edit_button_clicks():
    """Testa cliques nos botões de edição"""
    print("=== Testando cliques nos botões de edição ===")
    
    app = QApplication([])
    
    # Teste 1: ClientesManager
    try:
        from app.components.clientes_manager_pyqt import ClientesManager
        
        main_window = QMainWindow()
        tab_widget = QTabWidget()
        
        clientes_manager = ClientesManager(tab_widget)
        print("✅ ClientesManager criado com sucesso")
        
        # Verificar se o botão existe
        if hasattr(clientes_manager, 'btn_editar'):
            print("✅ Botão btn_editar existe")
            
            # Verificar se está conectado
            connections = clientes_manager.btn_editar.receivers(clientes_manager.btn_editar.clicked)
            print(f"📊 Número de conexões no botão: {connections}")
            
            # Simular clique (sem seleção)
            try:
                clientes_manager.editar_cliente()
                print("✅ Método editar_cliente executou (sem seleção)")
            except Exception as e:
                print(f"❌ Erro ao executar editar_cliente: {e}")
        else:
            print("❌ Botão btn_editar NÃO existe")
            
    except Exception as e:
        print(f"❌ Erro ao testar ClientesManager: {e}")
    
    # Teste 2: ProdutosManager
    try:
        from app.components.produtos_manager import ProdutosManager
        
        produtos_manager = ProdutosManager()
        print("✅ ProdutosManager criado com sucesso")
        
        # Verificar se o botão existe
        if hasattr(produtos_manager, 'edit_btn'):
            print("✅ Botão edit_btn existe")
            
            # Verificar se está conectado
            connections = produtos_manager.edit_btn.receivers(produtos_manager.edit_btn.clicked)
            print(f"📊 Número de conexões no botão: {connections}")
            
            # Simular clique (sem seleção)
            try:
                produtos_manager._edit_product()
                print("✅ Método _edit_product executou (sem seleção)")
            except Exception as e:
                print(f"❌ Erro ao executar _edit_product: {e}")
        else:
            print("❌ Botão edit_btn NÃO existe")
            
    except Exception as e:
        print(f"❌ Erro ao testar ProdutosManager: {e}")
    
    # Encerrar aplicação
    QTimer.singleShot(100, app.quit)
    return app.exec()

if __name__ == '__main__':
    test_edit_button_clicks()