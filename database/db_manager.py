"""
Módulo de gerenciamento do banco de dados SQLite para armazenar ordens de serviço.
Refatorado para usar módulos especializados.
"""

import sqlite3
import json
from datetime import datetime

from .db_setup import DatabaseSetup
from .order_crud import OrderCRUD
from .report_queries import ReportQueries


class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._inicializado = False
        return cls._instance

    def __init__(self):
        if not self._inicializado:
            self.db_path = DatabaseSetup.get_database_path()
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Inicializar módulos especializados
            self.order_crud = OrderCRUD(self.cursor, self.conn)
            self.reports = ReportQueries(self.cursor)
            
            # Criar tabelas
            DatabaseSetup.criar_tabelas(self.cursor)
            self.conn.commit()
            
            self._inicializado = True

    def salvar_ordem(self, dados, nome_pdf=""):
        """Salva ordem de serviço usando módulo CRUD"""
        return self.order_crud.criar_ordem(dados, nome_pdf)

    def deletar_pedido(self, pedido_id):
        """Deleta um pedido específico pelo ID"""
        return self.order_crud.deletar_ordem(pedido_id)

    def deletar_ordem(self, pedido_id):
        """Deleta ordem - mantido para compatibilidade"""
        return self.order_crud.deletar_ordem(pedido_id)

    def atualizar_status_pedido(self, pedido_id, novo_status):
        """Atualiza o status do pedido usando dados JSON"""
        try:
            self.cursor.execute('SELECT dados_json FROM ordem_servico WHERE id = ?', (pedido_id,))
            row = self.cursor.fetchone()
            if not row:
                return False
                
            dados_json = row[0] or '{}'
            try:
                dados = json.loads(dados_json)
            except:
                dados = {}
                
            dados['status'] = novo_status
            novo_json = json.dumps(dados)
            
            self.cursor.execute('UPDATE ordem_servico SET dados_json = ? WHERE id = ?', (novo_json, pedido_id))
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar status: {e}")
            return False

    def listar_pedidos_ordenados_por_prazo(self, limite=50):
        """Lista pedidos ordenados por prazo - INCLUINDO TODOS OS CAMPOS PARA EDIÇÃO"""
        try:
            # Query com todos os campos necessários para edição
            query = '''
            SELECT id, numero_os, nome_cliente, telefone_cliente, detalhes_produto, 
                   valor_produto, valor_entrada, frete, forma_pagamento,
                   prazo, data_criacao, dados_json
            FROM ordem_servico
            ORDER BY data_criacao DESC
            LIMIT ?
            '''
            self.cursor.execute(query, (limite,))
            resultados = self.cursor.fetchall()
            
            # Processamento otimizado
            pedidos = []
            for row in resultados:
                if len(row) >= 12:
                    (id_, numero_os, nome_cliente, telefone_cliente, detalhes_produto,
                     valor_produto, valor_entrada, frete, forma_pagamento,
                     prazo, data_criacao, dados_json) = row
                    
                    # Status do JSON (mais rápido)
                    status = 'em produção'
                    if dados_json:
                        try:
                            dados = json.loads(dados_json)
                            status = dados.get('status', 'em produção')
                        except:
                            pass  # Usar padrão se falhar
                    
                    # Calcular valor total
                    valor_total = (valor_produto or 0) + (frete or 0)
                    
                    # Objeto pedido completo para edição
                    pedido = {
                        'id': id_,
                        'numero_os': numero_os or 0,
                        'nome_cliente': nome_cliente or 'Cliente não informado',
                        'telefone_cliente': telefone_cliente or '',
                        'detalhes_produto': detalhes_produto or '',
                        'valor_produto': float(valor_produto or 0),
                        'valor_entrada': float(valor_entrada or 0),
                        'frete': float(frete or 0),
                        'forma_pagamento': forma_pagamento or '',
                        'valor_total': float(valor_total),
                        'prazo': int(prazo or 30),
                        'data_criacao': data_criacao or '',
                        'status': status
                    }
                    pedidos.append(pedido)
            
            return pedidos
            
        except Exception as e:
            print(f"Erro ao listar pedidos: {e}")
            return []

    def buscar_ordem_por_numero(self, numero_os):
        """Busca ordem por número usando módulo CRUD"""
        return self.order_crud.buscar_ordem(numero_os)

    def obter_vendas_por_periodo(self, data_inicio, data_fim):
        """Obtém vendas por período usando módulo de relatórios"""
        return self.reports.buscar_por_periodo(data_inicio, data_fim)

    def calcular_resumo_vendas(self, data_inicio, data_fim):
        """Calcula resumo de vendas usando módulo de relatórios"""
        return self.reports.calcular_vendas_periodo(data_inicio, data_fim)

    def obter_vendas_diarias(self, dias=30):
        """Obtém vendas diárias usando módulo de relatórios"""
        return self.reports.vendas_por_dia(dias)

    def buscar_pedidos_por_cliente(self, nome_cliente):
        """Busca pedidos por cliente usando módulo de relatórios"""
        return self.reports.buscar_por_cliente(nome_cliente)

    def atualizar_pedido(self, pedido_id, campos_atualizacao):
        """Atualiza campos do pedido usando módulo CRUD"""
        return self.order_crud.atualizar_ordem(pedido_id, campos_atualizacao)

    def listar_clientes(self, limite=None):
        """Lista clientes da tabela de clientes separada"""
        try:
            if limite:
                query = '''
                SELECT id, nome, cpf, telefone, email, rua, numero, bairro, cidade, estado, referencia
                FROM clientes 
                ORDER BY nome 
                LIMIT ?
                '''
                self.cursor.execute(query, (limite,))
            else:
                query = '''
                SELECT id, nome, cpf, telefone, email, rua, numero, bairro, cidade, estado, referencia
                FROM clientes 
                ORDER BY nome
                '''
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar clientes: {e}")
            return []

    def obter_resumo_mes(self, ano, mes):
        """Obtém resumo de vendas do mês"""
        try:
            query = '''
            SELECT 
                COUNT(*) as total_pedidos,
                SUM(valor_produto) as total_valor,
                SUM(valor_entrada) as total_entradas
            FROM ordem_servico 
            WHERE strftime('%Y', data_criacao) = ? AND strftime('%m', data_criacao) = ?
            '''
            self.cursor.execute(query, (str(ano), f"{mes:02d}"))
            resultado = self.cursor.fetchone()
            return resultado if resultado else (0, 0, 0)
        except Exception as e:
            print(f"Erro ao obter resumo do mês: {e}")
            return (0, 0, 0)

    def listar_pedidos_ordenados_prazo(self, limite=200):
        """Lista pedidos ordenados por prazo - compatibilidade"""
        return self.listar_pedidos_ordenados_por_prazo(limite)

    def obter_resumo_ano(self, ano):
        """Obtém resumo de vendas do ano"""
        try:
            query = '''
            SELECT 
                COUNT(*) as total_pedidos,
                SUM(valor_produto) as total_valor,
                SUM(valor_entrada) as total_entradas
            FROM ordem_servico 
            WHERE strftime('%Y', data_criacao) = ?
            '''
            self.cursor.execute(query, (str(ano),))
            resultado = self.cursor.fetchone()
            return resultado if resultado else (0, 0, 0)
        except Exception as e:
            print(f"Erro ao obter resumo do ano: {e}")
            return (0, 0, 0)

    def obter_resumo_total(self):
        """Obtém resumo total de vendas"""
        try:
            query = '''
            SELECT 
                COUNT(*) as total_pedidos,
                SUM(valor_produto) as total_valor,
                SUM(valor_entrada) as total_entradas
            FROM ordem_servico
            '''
            self.cursor.execute(query)
            resultado = self.cursor.fetchone()
            return resultado if resultado else (0, 0, 0)
        except Exception as e:
            print(f"Erro ao obter resumo total: {e}")
            return (0, 0, 0)

    def criar_dados_teste(self):
        """Cria dados de teste se a tabela estiver vazia"""
        try:
            # Verificar se já existem dados
            self.cursor.execute('SELECT COUNT(*) FROM ordem_servico')
            count = self.cursor.fetchone()[0]
            
            if count == 0:
                # Criar alguns dados de teste
                dados_teste = [
                    {
                        'numero_os': 1,
                        'nome_cliente': 'João Silva',
                        'cpf_cliente': '12345678901',
                        'telefone_cliente': '11999999999',
                        'detalhes_produto': 'Móvel sob medida - Cor: Branco - 3 gavetas',
                        'valor_produto': 500.0,
                        'valor_entrada': 100.0,
                        'frete': 50.0,
                        'forma_pagamento': 'Cartão',
                        'prazo': 30
                    },
                    {
                        'numero_os': 2,
                        'nome_cliente': 'Maria Santos',
                        'cpf_cliente': '98765432109',
                        'telefone_cliente': '11888888888',
                        'detalhes_produto': 'Guarda-roupa - Cor: Marrom - 2 gavetas',
                        'valor_produto': 800.0,
                        'valor_entrada': 200.0,
                        'frete': 75.0,
                        'forma_pagamento': 'PIX',
                        'prazo': 45
                    }
                ]
                
                for dados in dados_teste:
                    self.salvar_ordem(dados, "")
                
                print("Dados de teste criados!")
                return True
            
        except Exception as e:
            print(f"Erro ao criar dados de teste: {e}")
            return False

    def upsert_cliente_completo(self, nome, cpf=None, telefone=None, email=None, 
                               cliente_id=None, referencia=None, rua=None, numero=None, 
                               bairro=None, cidade=None, estado=None):
        """Insere ou atualiza um cliente com dados completos na tabela de clientes"""
        try:
            from datetime import datetime
            
            if cliente_id:
                # Atualizar cliente existente
                self.cursor.execute("""
                    UPDATE clientes 
                    SET nome = ?, cpf = ?, telefone = ?, email = ?, rua = ?, numero = ?,
                        bairro = ?, cidade = ?, estado = ?, referencia = ?
                    WHERE id = ?
                """, (nome, cpf, telefone, email, rua, numero, bairro, cidade, estado, referencia, cliente_id))
            else:
                # Criar novo cliente
                data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute("""
                    INSERT INTO clientes (nome, cpf, telefone, email, rua, numero, bairro, cidade, estado, referencia, data_criacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome, cpf, telefone, email, rua, numero, bairro, cidade, estado, referencia, data_atual))
                
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar cliente completo: {e}")
            return False

    def inserir_cliente(self, nome, cpf=None, telefone=None, email=None, endereco=None, referencia=None, numero=None):
        """Insere um novo cliente na tabela de clientes"""
        try:
            from datetime import datetime
            data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.cursor.execute("""
                INSERT INTO clientes (nome, cpf, telefone, email, rua, numero, referencia, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, cpf, telefone, email, endereco, numero, referencia, data_atual))
            
            self.conn.commit()
            return self.cursor.lastrowid
            
        except Exception as e:
            print(f"Erro ao inserir cliente: {e}")
            return None

    def close(self):
        """Fecha conexão com o banco"""
        if hasattr(self, 'conn'):
            self.conn.close()
