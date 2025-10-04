"""
Módulo para operações CRUD de ordens de serviço
"""
import sqlite3
import json
from datetime import datetime


def _normalize_cpf(cpf):
    """Return only digits from cpf (normalize format)."""
    try:
        return ''.join(ch for ch in str(cpf or '') if ch.isdigit())
    except Exception:
        return ''

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
            
            # Build structured produtos list: prefer dados['produtos'] (list), else parse detalhes_produto text
            produtos_struct = []
            if isinstance(dados.get('produtos'), (list, tuple)) and len(dados.get('produtos')) > 0:
                for p in dados.get('produtos'):
                    try:
                        descricao = str(p.get('descricao') or p.get('nome') or '').strip()
                        valor = float(p.get('valor') or p.get('preco') or 0)
                        quantidade = int(p.get('quantidade', 1))
                    except Exception:
                        descricao = str(p.get('descricao') or '').strip()
                        try:
                            valor = float(str(p.get('valor') or '0').replace(',', '.'))
                        except Exception:
                            valor = 0.0
                        quantidade = int(p.get('quantidade', 1))
                    
                    # Preservar estrutura completa do produto, incluindo cor_data
                    produto_completo = {
                        'descricao': descricao,
                        'valor': valor,
                        'quantidade': quantidade
                    }
                    
                    # Preservar cor_data se existir
                    if 'cor_data' in p:
                        produto_completo['cor_data'] = p['cor_data']
                    elif 'cor' in p:  # Compatibilidade com formato antigo
                        produto_completo['cor'] = p['cor']
                    
                    # Preservar outros campos importantes
                    for campo in ['nome', 'codigo']:
                        if campo in p:
                            produto_completo[campo] = p[campo]
                    
                    produtos_struct.append(produto_completo)
            else:
                detalhes = dados.get('detalhes_produto', '') or ''
                for linha in [l.strip() for l in detalhes.replace('\r', '\n').split('\n') if l.strip() and not l.strip().startswith('-')]:
                    if ' - R$ ' in linha:
                        try:
                            desc, valtxt = linha.rsplit(' - R$ ', 1)
                            valtxt_original = valtxt.strip()
                            valconv = valtxt_original.replace('.', '').replace(',', '.') if ',' in valtxt_original else valtxt_original
                            valor = float(valconv) if valconv else 0.0
                            produtos_struct.append({'descricao': desc.strip('\u2022 ').strip(), 'valor': valor})
                        except Exception:
                            produtos_struct.append({'descricao': linha.strip('\u2022 ').strip(), 'valor': 0.0})
                    else:
                        produtos_struct.append({'descricao': linha.strip('\u2022 ').strip(), 'valor': 0.0})

            desconto = float(dados.get('desconto', 0) or 0)
            valor_produto = sum([float(p.get('valor', 0) or 0) for p in produtos_struct])

            dados_json = json.dumps({
                'status': dados.get('status', 'em produção'),
                'data_entrega': None,
                'desconto': desconto,
                'cor': dados.get('cor', ''),
                'reforco': bool(dados.get('reforco', False)),
                'produtos': produtos_struct,
            })

            # Normalize CPF to digits-only for consistent storage
            cpf_norm = _normalize_cpf(dados.get('cpf_cliente', ''))
            
            # Verificar campos obrigatórios
            nome_cliente = dados.get('nome_cliente')
            if not nome_cliente:
                raise ValueError("Campo 'nome_cliente' é obrigatório")
            
            valores = (
                dados.get('numero_os', 1),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                nome_cliente,
                cpf_norm,
                dados.get('telefone_cliente', ''),
                dados.get('detalhes_produto', ''),
                valor_produto,
                float(dados.get('valor_entrada') or 0),
                float(dados.get('frete') or 0),
                dados.get('forma_pagamento', ''),
                int(dados.get('prazo') or 0),
                nome_pdf,
                dados_json
            )
            
            self.cursor.execute(query, valores)
            self.conn.commit()
            
            # Incrementar contador de compras do cliente
            try:
                if cpf_norm:
                    self.cursor.execute("""
                        UPDATE clientes 
                        SET numero_compras = numero_compras + 1
                        WHERE cpf = ? OR cnpj = ?
                    """, (cpf_norm, cpf_norm))
                    self.conn.commit()
            except Exception as e:
                print(f"Aviso: não foi possível atualizar contador de compras: {e}")
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar ordem: {e}")
            return False
    
    def buscar_ordem(self, numero_os):
        """Busca ordem por número"""
        try:
            query = 'SELECT * FROM ordem_servico WHERE numero_os = ?'
            self.cursor.execute(query, (numero_os,))
            row = self.cursor.fetchone()
            if not row:
                return None
            cols = [d[0] for d in self.cursor.description]
            mapped = dict(zip(cols, row))
            try:
                dadosj = json.loads(mapped.get('dados_json') or '{}')
                mapped['produtos'] = dadosj.get('produtos', [])
            except Exception:
                mapped['produtos'] = []
            return mapped
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
        """Marca ordem como deletada (soft delete) - fica na lixeira por 30 dias"""
        try:
            from datetime import datetime
            deleted_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Soft delete: marcar como deletado em vez de remover
            self.cursor.execute(
                'UPDATE ordem_servico SET deleted_at = ? WHERE id = ?',
                (deleted_at, pedido_id)
            )
            self.conn.commit()
            print(f"✅ Pedido {pedido_id} movido para lixeira (recuperável por 30 dias)")
            return True
            
        except Exception as e:
            print(f"Erro ao deletar ordem: {e}")
            return False
