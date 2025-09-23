#!/usr/bin/env python3
"""
Teste específico para debugging do botão editar
"""

import sys
sys.path.append('/home/eduardo/Área de Trabalho/Os-Project')

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

def debug_edit_cliente():
    """Debug específico do método editar_cliente"""
    print("=== Debug do método editar_cliente ===")
    
    app = QApplication([])
    
    try:
        from app.components.clientes_manager_pyqt import ClientesManager
        
        # Criar janela principal
        main_window = QMainWindow()
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Criar clientes manager
        clientes_manager = ClientesManager(central_widget)
        layout.addWidget(clientes_manager)
        
        main_window.setCentralWidget(central_widget)
        main_window.show()
        
        print("✅ Interface criada")
        
        # Aguardar carregar dados
        QTimer.singleShot(1000, lambda: debug_table_state(clientes_manager))
        QTimer.singleShot(3000, app.quit)
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1

def debug_table_state(clientes_manager):
    """Debug do estado da tabela"""
    print("\n=== Debug do estado da tabela ===")
    
    try:
        table = clientes_manager.table
        print(f"📊 Número de linhas: {table.rowCount()}")
        print(f"📊 Linha atual: {table.currentRow()}")
        print(f"📊 Linha selecionada: {table.currentRow()}")
        
        # Tentar selecionar primeira linha
        if table.rowCount() > 0:
            table.selectRow(0)
            print(f"📊 Após selecionar linha 0: {table.currentRow()}")
            
            # Agora testar editar_cliente
            print("\n--- Testando editar_cliente com seleção ---")
            try:
                clientes_manager.editar_cliente()
                print("✅ editar_cliente executado com seleção")
            except Exception as e:
                print(f"❌ Erro em editar_cliente: {e}")
        else:
            print("❌ Tabela vazia")
            
    except Exception as e:
        print(f"❌ Erro no debug: {e}")

if __name__ == '__main__':
    sys.exit(debug_edit_cliente())