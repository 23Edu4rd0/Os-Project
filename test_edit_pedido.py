#!/usr/bin/env python3
"""
Teste específico para verificar se os botões de editar pedido funcionam
"""
import sys
import os
sys.path.append('/home/eduardo/Área de Trabalho/Os-Project')

from PyQt6.QtWidgets import QApplication
from app.components.pedidos.pedidos_interface import PedidosInterface
from app.components.clientes_manager_pyqt import ClienteDetailDialog

def test_pedidos_interface():
    """Testa o botão editar na aba de pedidos"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        interface = PedidosInterface(None)
        print("✅ PedidosInterface criada com sucesso")
        
        # Testar o método editar_pedido
        try:
            interface.editar_pedido(3)  # Testa com ID 3 que sabemos que existe
            print("✅ Método editar_pedido executou sem erros")
        except Exception as e:
            print(f"❌ Erro ao executar editar_pedido: {e}")
        
    except Exception as e:
        print(f"❌ Erro ao criar PedidosInterface: {e}")

def test_client_detail_dialog():
    """Testa o botão editar no dialog de detalhes do cliente"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # Dados de teste do cliente
        cliente_teste = {
            'id': 1,
            'nome': 'Eduardo Teste',
            'cpf': '12345678901',
            'telefone': '123456789'
        }
        
        dialog = ClienteDetailDialog(None, cliente_teste)
        print("✅ ClienteDetailDialog criado com sucesso")
        
        # Testar o método editar_pedido_selecionado
        try:
            dialog.editar_pedido_selecionado()
            print("✅ Método editar_pedido_selecionado executou (esperado mostrar mensagem de seleção)")
        except Exception as e:
            print(f"❌ Erro ao executar editar_pedido_selecionado: {e}")
            
    except Exception as e:
        print(f"❌ Erro ao criar ClienteDetailDialog: {e}")

if __name__ == "__main__":
    print("=== Testando Botões de Editar Pedido ===")
    print("\n1. Testando PedidosInterface...")
    test_pedidos_interface()
    
    print("\n2. Testando ClienteDetailDialog...")
    test_client_detail_dialog()
    
    print("\n=== Teste Concluído ===")