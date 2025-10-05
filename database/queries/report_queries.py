"""
Module for queries and reports.
All user-facing messages are in Portuguese. All comments, docstrings, and logs are in English.
"""
import sqlite3
from datetime import datetime, timedelta

class ReportQueries:
    def __init__(self, cursor):
        self.cursor = cursor
    
    def buscar_todas_ordens(self):
        """Fetch all service orders."""
        try:
            query = '''
            SELECT id, numero_os, data_criacao, nome_cliente, cpf_cliente, 
                   telefone_cliente, detalhes_produto, valor_produto, 
                   valor_entrada, frete, forma_pagamento, prazo, dados_json
            FROM ordem_servico 
            ORDER BY data_criacao DESC
            '''
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar todas as ordens: {e}")  # User-facing message in Portuguese
            print(f"Error fetching all orders: {e}")  # Log in English
            return []
    
    def buscar_por_periodo(self, data_inicio, data_fim):
        """Fetch orders by period."""
        try:
            query = '''
            SELECT * FROM ordem_servico 
            WHERE date(data_criacao) BETWEEN ? AND ?
            AND deleted_at IS NULL
            ORDER BY data_criacao DESC
            '''
            self.cursor.execute(query, (data_inicio, data_fim))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar por período: {e}")  # User-facing message in Portuguese
            print(f"Error fetching by period: {e}")  # Log in English
            return []
    
    def buscar_por_cliente(self, nome_cliente):
        """Fetch orders by client name."""
        try:
            query = '''
            SELECT * FROM ordem_servico 
            WHERE nome_cliente LIKE ?
            AND deleted_at IS NULL
            ORDER BY data_criacao DESC
            '''
            self.cursor.execute(query, (f'%{nome_cliente}%',))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar por cliente: {e}")  # User-facing message in Portuguese
            print(f"Error fetching by client: {e}")  # Log in English
            return []

    def buscar_por_cpf(self, cpf_cliente):
        """Fetch orders by client CPF (exact match)."""
        try:
            # Normalize CPF to digits-only for comparison
            cpf = ''.join(ch for ch in str(cpf_cliente or '') if ch.isdigit())
            # Normalize stored cpf_cliente by removing common punctuation before comparing
            query = '''
            SELECT * FROM ordem_servico
            WHERE replace(replace(replace(cpf_cliente, '.', ''), '-', ''), ' ', '') = ?
            AND deleted_at IS NULL
            ORDER BY data_criacao DESC
            '''
            self.cursor.execute(query, (cpf,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar por cpf: {e}")  # User-facing message in Portuguese
            print(f"Error fetching by cpf: {e}")  # Log in English
            return []
    
    def calcular_vendas_periodo(self, data_inicio, data_fim):
        """Calculate sales by period."""
        try:
            query = '''
            SELECT 
                COUNT(*) as total_vendas,
                SUM(valor_produto + frete) as total_valor,
                SUM(valor_entrada) as total_entradas,
                AVG(valor_produto + frete) as ticket_medio
            FROM ordem_servico 
            WHERE date(data_criacao) BETWEEN ? AND ?
            '''
            self.cursor.execute(query, (data_inicio, data_fim))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao calcular vendas: {e}")  # User-facing message in Portuguese
            print(f"Error calculating sales: {e}")  # Log in English
            return (0, 0, 0, 0)
    
    def vendas_por_dia(self, dias=30):
        """Sales for the last N days."""
        try:
            data_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
            query = '''
            SELECT 
                date(data_criacao) as data,
                COUNT(*) as quantidade,
                SUM(valor_produto + frete) as total
            FROM ordem_servico 
            WHERE date(data_criacao) >= ?
            GROUP BY date(data_criacao)
            ORDER BY data
            '''
            self.cursor.execute(query, (data_limite,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao buscar vendas por dia: {e}")  # User-facing message in Portuguese
            print(f"Error fetching sales by day: {e}")  # Log in English
            return []

    def relatorio_top_clientes(self, limite=10):
        """Return clients with most purchases (top clients)."""
        try:
            query = '''
            SELECT nome_cliente, cpf_cliente, COUNT(*) as total_compras, SUM(valor_produto + frete) as total_gasto
            FROM ordem_servico
            WHERE deleted_at IS NULL
            GROUP BY nome_cliente, cpf_cliente
            ORDER BY total_compras DESC, total_gasto DESC
            LIMIT ?
            '''
            self.cursor.execute(query, (limite,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao gerar relatório de top clientes: {e}")  # User-facing message in Portuguese
            print(f"Error generating top clients report: {e}")  # Log in English
            return []

    def relatorio_pedidos_deletados(self, dias=30):
        """Return statistics of deleted orders in the last N days."""
        try:
            from datetime import datetime, timedelta
            data_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d %H:%M:%S')
            query = '''
            SELECT COUNT(*) as total_deletados, SUM(valor_produto + frete) as valor_deletado
            FROM ordem_servico
            WHERE deleted_at IS NOT NULL AND deleted_at >= ?
            '''
            self.cursor.execute(query, (data_limite,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao gerar relatório de pedidos deletados: {e}")  # User-facing message in Portuguese
            print(f"Error generating deleted orders report: {e}")  # Log in English
            return (0, 0)
