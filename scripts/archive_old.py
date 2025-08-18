"""
Script para arquivar pedidos antigos (> N anos) exportando para CSV (gzip opcional)
e removendo-os do banco de dados de produção.

Uso:
    python scripts/archive_old.py --years 3 --out archives/old_orders_3y.csv.gz

Ele usa o mesmo DatabaseManager do projeto.
"""
import os
import argparse
import csv
import gzip
from datetime import datetime, timedelta

from database.db_manager import DatabaseManager


def export_and_delete(years: int, out_path: str, compress: bool = True):
    db = DatabaseManager()
    cutoff = datetime.now() - timedelta(days=365 * years)
    cutoff_str = cutoff.strftime('%Y-%m-%d')

    # Buscar pedidos antigos
    cur = db.cursor
    cur.execute("SELECT id, numero_os, nome_cliente, data_emissao, valor_produto, frete, dados_json, caminho_pdf FROM ordem_servico WHERE date(data_emissao) < date(?)", (cutoff_str,))
    rows = cur.fetchall()

    if not rows:
        print('Nenhum pedido antigo encontrado para arquivar.')
        return

    # Garantir pasta de saída
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    fieldnames = ['id','numero_os','nome_cliente','data_emissao','valor_produto','frete','dados_json','caminho_pdf']

    if compress:
        with gzip.open(out_path, 'wt', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            for r in rows:
                writer.writerow(r)
    else:
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            for r in rows:
                writer.writerow(r)

    # Depois de exportar, deletar itens e ordens
    ids = [str(r[0]) for r in rows]
    ids_placeholders = ','.join(['?'] * len(ids))
    try:
        cur.execute(f"DELETE FROM itens_pedido WHERE pedido_id IN ({ids_placeholders})", ids)
        cur.execute(f"DELETE FROM ordem_servico WHERE id IN ({ids_placeholders})", ids)
        db.conn.commit()
        print(f"Arquivados e deletados {len(ids)} pedidos. Arquivo: {out_path}")
    except Exception as e:
        print('Erro ao deletar pedidos arquivados:', e)
        db.conn.rollback()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--years', type=int, default=3, help='Arquivar pedidos mais antigos que X anos')
    p.add_argument('--out', type=str, default='archives/old_orders.csv.gz', help='Caminho do arquivo de saída')
    p.add_argument('--no-compress', dest='compress', action='store_false')
    args = p.parse_args()
    export_and_delete(args.years, args.out, compress=args.compress)
