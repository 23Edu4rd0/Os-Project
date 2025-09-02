import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from database import db_manager

p = db_manager.listar_pedidos_ordenados_por_prazo(50)
print('count=', len(p))
if p:
    print('sample id:', p[0].get('id'), 'status:', p[0].get('status'))
else:
    print('no pedidos returned')
