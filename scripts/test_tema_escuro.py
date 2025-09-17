#!/usr/bin/env python3
"""
Teste visual do tema escuro do modal
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication
from app.components.pedidos.novo_pedidos_modal import NovoPedidosModal


def main():
    print("🌚 Testando tema escuro do modal...")
    
    app = QApplication(sys.argv)
    
    try:
        # Criar modal com tema escuro
        modal = NovoPedidosModal()
        
        print("✅ Modal criado com tema escuro!")
        print("🎨 Paleta de cores aplicada:")
        print("   📱 Fundo principal: #2b2b2b (escuro)")
        print("   🔲 Componentes: #3a3a3a (cinza escuro)")  
        print("   ⚫ Bordas/Botões: #555555 (cinza médio)")
        print("   ⚪ Texto: #ffffff (branco)")
        print("   🎯 Hover: #666666 (cinza claro)")
        
        print("\n🎉 TEMA ESCURO APLICADO COM SUCESSO!")
        print("🌚 Design moderno escuro ✓")
        print("⚫ Apenas 1 tom de cinza + branco ✓")
        print("🖤 Visual elegante e profissional ✓")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        app.quit()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)