#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Teste final do modal de pedidos - validação da funcionalidade de preços
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from app.components.pedidos.novo_pedidos_modal import NovoPedidoModal

def main():
    app = QApplication(sys.argv)
    
    # Criar modal
    modal = NovoPedidoModal()
    modal.show()
    
    print("✅ Modal carregado com sucesso!")
    print("🔍 Para testar:")
    print("   1. Digite 'caixa teste' no campo produto")
    print("   2. Verifique se o valor aparece como '99.99'")
    print("   3. Clique em 'Adicionar' para validar")
    print("   4. Feche o modal para sair")
    
    result = app.exec()
    return result

if __name__ == "__main__":
    main()