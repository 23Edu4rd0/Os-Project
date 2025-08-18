"""
Script de teste para verificar se as correções funcionam
"""

try:
    # Testar importação do db_manager
    from database import db_manager
    print("✓ db_manager importado com sucesso")
    
    # Testar criação de dados de teste
    result = db_manager.criar_dados_teste()
    print(f"✓ Dados de teste: {result}")
    
    # Testar listar_clientes
    clientes = db_manager.listar_clientes(5)
    print(f"✓ Clientes encontrados: {len(clientes)}")
    if clientes:
        print(f"  Primeiro cliente: {clientes[0]}")
    
    # Testar listar_pedidos
    pedidos = db_manager.listar_pedidos_ordenados_por_prazo(5)
    print(f"✓ Pedidos encontrados: {len(pedidos)}")
    if pedidos:
        print(f"  Primeiro pedido: {pedidos[0].get('numero_os', 'N/A')}")
    
    print("\n🎉 Todos os testes passaram!")
    
except Exception as e:
    print(f"❌ Erro nos testes: {e}")
    import traceback
    traceback.print_exc()
