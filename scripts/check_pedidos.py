import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import db_manager

p = db_manager.listar_pedidos_ordenados_por_prazo(5)
print('Pedidos listed:')
for ped in p:
    print('OS', ped.get('numero_os'), 'valor_produto', ped.get('valor_produto'), 'produtos=', ped.get('produtos'))

if p:
    b = db_manager.buscar_ordem_por_numero(p[0].get('numero_os'))
    print('\nbuscar_ordem_por_numero sample:')
    print(b)
