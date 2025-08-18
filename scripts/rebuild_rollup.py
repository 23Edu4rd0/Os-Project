"""Rebuild monthly rollup resumo_vendas_mensal from existing ordem_servico rows.
Run with the project's virtualenv python: .venv\Scripts\python.exe scripts\rebuild_rollup.py
"""
import sys
from datetime import datetime
sys.path.insert(0, '.')
from database.db_manager import db_manager

print('DB_PATH:', db_manager.db_path)

# Clear existing rollup
try:
    db_manager.cursor.execute('DELETE FROM resumo_vendas_mensal')
    db_manager.conn.commit()
    print('Cleared resumo_vendas_mensal')
except Exception as e:
    print('Error clearing resumo_vendas_mensal:', e)

vendas = db_manager.listar_pedidos_ordenados_por_prazo(100000)
print('Orders found:', len(vendas))
processed = 0
for v in vendas:
    status = (v.get('status') or '').strip().lower()
    if status in ('cancelado','cancelada','excluido','excluida','deletado'):
        continue
    de = v.get('data_emissao')
    if not de:
        continue
    try:
        if isinstance(de, str):
            dt = datetime.strptime(de[:19], '%Y-%m-%d %H:%M:%S')
        else:
            dt = de
    except Exception:
        dt = datetime.now()
    ano, mes = dt.year, dt.month
    total = float(v.get('valor_produto') or 0) + float(v.get('frete') or 0)
    frete = float(v.get('frete') or 0)
    ok = db_manager.atualizar_resumo_mensal(ano, mes, total, frete, 1)
    if ok:
        processed += 1

print('Processed (rollup entries added/updated):', processed)

# Show resumo for current month
now = datetime.now()
res = db_manager.obter_resumo_mes(now.year, now.month)
print('Resumo for', now.year, now.month, res)
