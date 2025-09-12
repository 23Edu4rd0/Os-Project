import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.components.pedidos.pedidosModal.__init__ import PedidosModal
from database import db_manager

pm = PedidosModal(None)
# Simulate ClientesManager prefill
pm.model.preencher({'nome_cliente': 'Alexandre Test', 'cpf_cliente': '11122233344', 'telefone_cliente': '99999-0000'})
# Ensure produtos_list has one product so totals are computed
pm.produtos_list = [{'descricao':'Item X','valor':200.0}]
# Directly call salvar (simulate pressing save) using the internal function
res = pm._salvar_pedido()
print('save result:', res)
# Check last inserted
rows = db_manager.listar_pedidos_ordenados_por_prazo(5)
print('recent rows count:', len(rows))
for r in rows[:5]:
    print('row:', r.get('id'), r.get('numero_os'), r.get('nome_cliente'))
