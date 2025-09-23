#!/usr/bin/env python3
"""
Script para testar funcionalidade de edição nos managers
"""

import sys
import os
sys.path.append('/home/eduardo/Área de Trabalho/Os-Project')

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

def test_edit_functions():
    """Testa as funções de edição"""
    print("=== Testando funcionalidades de edição ===")
    
    # Teste 1: ClientesManager
    try:
        from app.components.clientes_manager_pyqt import ClientesManager, ClienteModal
        print("✅ ClientesManager e ClienteModal importados com sucesso")
        
        # Verificar se o método existe
        if hasattr(ClientesManager, 'editar_cliente'):
            print("✅ Método editar_cliente existe")
        else:
            print("❌ Método editar_cliente NÃO existe")
            
    except Exception as e:
        print(f"❌ Erro ao importar ClientesManager: {e}")
    
    # Teste 2: ProdutosManager
    try:
        from app.components.produtos_manager import ProdutosManager
        print("✅ ProdutosManager importado com sucesso")
        
        # Verificar se o método existe
        if hasattr(ProdutosManager, '_edit_product'):
            print("✅ Método _edit_product existe")
        else:
            print("❌ Método _edit_product NÃO existe")
            
    except Exception as e:
        print(f"❌ Erro ao importar ProdutosManager: {e}")
    
    # Teste 3: PedidosManager
    try:
        from app.components.pedidos import PedidosManager
        print("✅ PedidosManager importado com sucesso")
        
        # Verificar se o método existe
        if hasattr(PedidosManager, 'editar_pedido'):
            print("✅ Método editar_pedido existe")
        else:
            print("❌ Método editar_pedido NÃO existe")
            
    except Exception as e:
        print(f"❌ Erro ao importar PedidosManager: {e}")

    # Teste 4: Verificar se há problemas com imports internos
    try:
        from database import db_manager
        print("✅ db_manager importado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao importar db_manager: {e}")

if __name__ == '__main__':
    # Criar aplicação mínima para testar PyQt
    app = QApplication([])
    
    # Executar testes
    test_edit_functions()
    
    # Encerrar aplicação
    QTimer.singleShot(100, app.quit)
    app.exec()