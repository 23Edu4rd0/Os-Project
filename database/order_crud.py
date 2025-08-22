"""
Módulo para operações CRUD de ordens de serviço
"""
import sqlite3
import json
from datetime import datetime

class OrderCRUD:
    def __init__(self, cursor, conn):
        self.cursor = cursor
        self.conn = conn
    
    def criar_ordem(self, dados, nome_pdf=""):
        """Cria nova ordem de serviço"""
        try:
            query = '''
            INSERT INTO ordem_servico (numero_os, data_criacao, nome_cliente, cpf_cliente, 
                                     telefone_cliente, detalhes_produto, valor_produto, 
                                     valor_entrada, frete, forma_pagamento, prazo, 
                                     nome_pdf, dados_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            dados_json = json.dumps({
                'status': dados.get('status', 'em produção'),
                'data_entrega': None,
                'desconto': float(dados.get('desconto', 0) or 0),
                'cor': dados.get('cor', ''),
                'reforco': bool(dados.get('reforco', False))
            })
            
            valores = (
                dados['numero_os'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                dados['nome_cliente'],
                dados['cpf_cliente'],
                dados['telefone_cliente'],
                dados['detalhes_produto'],
                dados['valor_produto'],
                dados['valor_entrada'],
                dados['frete'],
                dados['forma_pagamento'],
                dados['prazo'],
                nome_pdf,
                dados_json
            )
            
            self.cursor.execute(query, valores)
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao criar ordem: {e}")
            return False
    
    def buscar_ordem(self, numero_os):
        """Busca ordem por número"""
        try:
            query = 'SELECT * FROM ordem_servico WHERE numero_os = ?'
            self.cursor.execute(query, (numero_os,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao buscar ordem: {e}")
            return None
    
    def atualizar_ordem(self, pedido_id, campos):
        """Atualiza campos específicos da ordem"""
        try:
            print(f"=== ATUALIZANDO ORDEM ===")
            print(f"Pedido ID: {pedido_id}")
            print(f"Campos: {campos}")
            
            set_clause = ', '.join([f'{campo} = ?' for campo in campos.keys()])
            query = f'UPDATE ordem_servico SET {set_clause} WHERE id = ?'
            
            print(f"Query: {query}")
            
            valores = list(campos.values()) + [pedido_id]
            print(f"Valores: {valores}")
            
            self.cursor.execute(query, valores)
            self.conn.commit()
            
            print("Atualização realizada com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar ordem: {e}")
            return False
    
    def deletar_ordem(self, pedido_id):
        """Deleta ordem por ID"""
        try:
            self.cursor.execute('DELETE FROM ordem_servico WHERE id = ?', (pedido_id,))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao deletar ordem: {e}")
            return False
