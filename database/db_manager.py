"""
Módulo de gerenciamento do banco de dados SQLite para armazenar ordens de serviço.
Refatorado para usar módulos especializados.
"""


import sqlite3
import json
from datetime import datetime

from database.db_setup import DatabaseSetup
from database.order_crud import OrderCRUD
from database.report_queries import ReportQueries
from database.products_crud import ProductsCRUD


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
            self.products = ProductsCRUD(self.cursor, self.conn)
            
            # Criar tabelas
            DatabaseSetup.criar_tabelas(self.cursor)
            self.conn.commit()
            
            self._inicializado = True

    def salvar_ordem(self, dados, nome_pdf=""):
        """Salva ordem de serviço usando módulo CRUD"""
        try:
            # Debug: log incoming payload summary
            produtos = dados.get('produtos') if isinstance(dados, dict) else None
            total_produtos = None
            if produtos and isinstance(produtos, (list, tuple)):
                try:
                    total_produtos = sum([float(p.get('valor', 0) or 0) for p in produtos])
                except Exception:
                    total_produtos = None
            print(f"[DB DEBUG] salvar_ordem: numero_os={dados.get('numero_os')}, nome_cliente={dados.get('nome_cliente')}, total_produtos={total_produtos}")
        except Exception:
            pass
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
            SELECT id, numero_os, nome_cliente, cpf_cliente, telefone_cliente, detalhes_produto, 
                   valor_produto, valor_entrada, frete, forma_pagamento,
                   prazo, data_criacao, dados_json
            FROM ordem_servico
            ORDER BY data_criacao DESC
            LIMIT ?
            '''
            self.cursor.execute(query, (limite,))
            resultados = self.cursor.fetchall()

            pedidos = []
            for row in resultados:
                # Expecting 13 columns
                if len(row) < 13:
                    continue
                (id_, numero_os, nome_cliente, cpf_cliente, telefone_cliente, detalhes_produto,
                 valor_produto, valor_entrada, frete, forma_pagamento,
                 prazo, data_criacao, dados_json) = row[:13]

                # Parse JSON fields and determine a sensible default status from persisted list
                try:
                    from app.utils.statuses import load_statuses
                    _sts = load_statuses()
                    default_status = _sts[0] if _sts else 'em produção'
                except Exception:
                    default_status = 'em produção'

                desconto = 0.0
                produtos = []
                status = default_status
                if dados_json:
                    try:
                        dados = json.loads(dados_json)
                        status = dados.get('status', default_status)
                        desconto = float(dados.get('desconto', 0) or 0)
                        produtos = dados.get('produtos', []) or []
                    except Exception:
                        produtos = []

                # If produtos structured present, compute valor_produto from it
                if produtos:
                    try:
                        valor_produto = sum([float(p.get('valor', 0) or 0) for p in produtos])
                    except Exception:
                        try:
                            valor_produto = float(valor_produto or 0)
                        except Exception:
                            valor_produto = 0.0

                # Calcular valor total (produtos + frete - desconto)
                try:
                    valor_total = (valor_produto or 0) + (frete or 0) - (desconto or 0)
                except Exception:
                    valor_total = 0.0

                # Attempt to assemble endereco from clientes table when cpf present
                endereco_cliente = ''
                try:
                    cpf_norm = ''.join(ch for ch in str(cpf_cliente or '') if ch.isdigit())
                    if cpf_norm:
                        self.cursor.execute(
                            "SELECT rua, numero, bairro, cidade, estado FROM clientes WHERE replace(replace(replace(cpf, '.', ''), '-', ''), ' ', '') = ? LIMIT 1",
                            (cpf_norm,)
                        )
                        cli_row = self.cursor.fetchone()
                        if cli_row:
                            rua, numero_c, bairro_c, cidade_c, estado_c = cli_row
                            endereco_cliente = f"{rua or ''} {numero_c or ''} - {bairro_c or ''} - {cidade_c or ''} / {estado_c or ''}".strip()
                except Exception:
                    endereco_cliente = ''

                pedido = {
                    'id': id_,
                    'numero_os': numero_os or 0,
                    'nome_cliente': nome_cliente or 'Cliente não informado',
                    'cpf_cliente': cpf_cliente or '',
                    'telefone_cliente': telefone_cliente or '',
                    'endereco_cliente': endereco_cliente,
                    'detalhes_produto': detalhes_produto or '',
                    'valor_produto': float(valor_produto or 0),
                    'valor_entrada': float(valor_entrada or 0),
                    'frete': float(frete or 0),
                    'forma_pagamento': forma_pagamento or '',
                    'valor_total': float(valor_total),
                    'prazo': int(prazo or 30),
                    'data_criacao': data_criacao or '',
                    'status': status,
                    'desconto': float(desconto or 0),
                    'cor': (dados.get('cor') if 'dados' in locals() else ''),
                    'reforco': bool(dados.get('reforco')) if 'dados' in locals() else False,
                    'produtos': produtos
                }
                pedidos.append(pedido)

            return pedidos
        except Exception as e:
            print(f"Erro ao listar pedidos: {e}")
            return []

    def atualizar_json_campos(self, pedido_id, updates: dict) -> bool:
        """Atualiza campos específicos dentro de dados_json da ordem."""
        try:
            self.cursor.execute('SELECT dados_json FROM ordem_servico WHERE id = ?', (pedido_id,))
            row = self.cursor.fetchone()
            dados = {}
            if row and row[0]:
                try:
                    dados = json.loads(row[0])
                except Exception:
                    dados = {}
            dados.update(updates or {})
            self.cursor.execute('UPDATE ordem_servico SET dados_json = ? WHERE id = ?', (json.dumps(dados), pedido_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar JSON da OS: {e}")
            return False

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

    def buscar_pedidos_por_cpf(self, cpf_cliente):
        """Busca pedidos por CPF do cliente"""
        return self.reports.buscar_por_cpf(cpf_cliente)

    def atualizar_pedido(self, pedido_id, campos_atualizacao):
        """Atualiza campos do pedido usando módulo CRUD"""
        return self.order_crud.atualizar_ordem(pedido_id, campos_atualizacao)

    def listar_clientes(self, limite=None):
        """Lista clientes da tabela de clientes separada"""
        try:
            if limite:
                query = '''
                SELECT id, nome, cpf, cnpj, inscricao_estadual, telefone, email, rua, numero, bairro, cidade, estado, referencia
                FROM clientes 
                ORDER BY nome 
                LIMIT ?
                '''
                self.cursor.execute(query, (limite,))
            else:
                query = '''
                SELECT id, nome, cpf, cnpj, inscricao_estadual, telefone, email, rua, numero, bairro, cidade, estado, referencia
                FROM clientes 
                ORDER BY nome
                '''
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar clientes: {e}")
            return []

    def atualizar_cliente(self, cliente_id, nome, cpf=None, telefone=None, email=None,
                          endereco=None, referencia=None, rua=None, numero=None,
                          bairro=None, cidade=None, estado=None):
        """Atualiza um cliente existente na tabela de clientes.
        Parâmetro 'endereco' mantido para compatibilidade e é ignorado, pois os campos estão normalizados.
        """
        try:
            self.cursor.execute(
                """
                UPDATE clientes
                SET nome = ?, cpf = ?, telefone = ?, email = ?,
                    rua = ?, numero = ?, bairro = ?, cidade = ?, estado = ?, referencia = ?
                WHERE id = ?
                """,
                (nome, cpf, telefone, email, rua, numero, bairro, cidade, estado, referencia, int(cliente_id))
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar cliente: {e}")
            return False

    def atualizar_cliente_completo(self, cliente_id, nome, cpf=None, cnpj=None, inscricao_estadual=None,
                                  telefone=None, email=None, cep=None, rua=None, numero=None,
                                  bairro=None, cidade=None, estado=None, referencia=None):
        """Atualiza um cliente existente com todos os campos, incluindo CNPJ, IE e CEP."""
        try:
            self.cursor.execute(
                """
                UPDATE clientes
                SET nome = ?, cpf = ?, cnpj = ?, inscricao_estadual = ?, telefone = ?, email = ?,
                    cep = ?, rua = ?, numero = ?, bairro = ?, cidade = ?, estado = ?, referencia = ?
                WHERE id = ?
                """,
                (nome, cpf, cnpj, inscricao_estadual, telefone, email, cep,
                 rua, numero, bairro, cidade, estado, referencia, int(cliente_id))
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar cliente completo: {e}")
            return False

    def criar_cliente_completo(self, nome, cpf=None, cnpj=None, inscricao_estadual=None,
                              telefone=None, email=None, cep=None, rua=None, numero=None,
                              bairro=None, cidade=None, estado=None, referencia=None):
        """Cria um novo cliente com todos os campos, incluindo CNPJ, IE e CEP."""
        try:
            from datetime import datetime
            data_atual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.cursor.execute(
                """
                INSERT INTO clientes (nome, cpf, cnpj, inscricao_estadual, telefone, email,
                                    cep, rua, numero, bairro, cidade, estado, referencia, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (nome, cpf, cnpj, inscricao_estadual, telefone, email, cep,
                 rua, numero, bairro, cidade, estado, referencia, data_atual)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao criar cliente completo: {e}")
            return False

    def deletar_cliente(self, cliente_id):
        """Exclui um cliente pelo ID."""
        try:
            self.cursor.execute("DELETE FROM clientes WHERE id = ?", (int(cliente_id),))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao deletar cliente: {e}")
            return False

    # ---------- Produtos (Catálogo) ----------
    def inserir_produto(self, nome, preco, descricao="", categoria="", codigo=None):
        return self.products.inserir_produto(nome, preco, descricao, categoria, codigo)

    def listar_produtos(self, busca="", limite=200):
        return self.products.listar_produtos(busca, limite)

    def atualizar_produto(self, produto_id, nome, preco, descricao="", categoria="", codigo=None):
        return self.products.atualizar_produto(produto_id, nome, preco, descricao, categoria, codigo)

    def deletar_produto(self, produto_id):
        return self.products.deletar_produto(produto_id)

    def listar_produtos_vendidos(self, busca: str = '', limite: int = 1000):
        """Extrai produtos reais das ordens (dados_json.produtos ou detalhes_produto).
        Retorna lista de dicts: {ordem_id, numero_os, data_criacao, descricao, valor, cor, reforco}
        """
        try:
            query = 'SELECT id, numero_os, data_criacao, detalhes_produto, dados_json FROM ordem_servico ORDER BY data_criacao DESC LIMIT ?'
            self.cursor.execute(query, (limite,))
            rows = self.cursor.fetchall()
            produtos = []
            for row in rows:
                ordem_id, numero_os, data_criacao, detalhes, dados_json = row
                # try JSON first
                parsed = []
                if dados_json:
                    try:
                        dj = json.loads(dados_json)
                        parsed = dj.get('produtos', []) or []
                    except Exception:
                        parsed = []
                if parsed:
                    for p in parsed:
                        try:
                            desc = str(p.get('descricao') or p.get('nome') or '').strip()
                            valor = float(p.get('valor') or p.get('preco') or 0)
                            cor = p.get('cor') if 'cor' in p else ''
                            reforco = bool(p.get('reforco')) if 'reforco' in p else False
                        except Exception:
                            desc = str(p.get('descricao') or '').strip()
                            try:
                                valor = float(str(p.get('valor') or '0').replace(',', '.'))
                            except Exception:
                                valor = 0.0
                            cor = p.get('cor') if 'cor' in p else ''
                            reforco = bool(p.get('reforco')) if 'reforco' in p else False
                        if busca and busca.lower() not in desc.lower():
                            continue
                        # try to find product code from catalog by exact or partial name match
                        codigo = ''
                        try:
                            self.cursor.execute("SELECT codigo FROM produtos WHERE nome = ? COLLATE NOCASE LIMIT 1", (desc,))
                            rowc = self.cursor.fetchone()
                            if rowc and rowc[0]:
                                codigo = rowc[0]
                            else:
                                self.cursor.execute("SELECT codigo FROM produtos WHERE nome LIKE ? COLLATE NOCASE LIMIT 1", (f"%{desc}%",))
                                rowc2 = self.cursor.fetchone()
                                if rowc2 and rowc2[0]:
                                    codigo = rowc2[0]
                        except Exception:
                            codigo = ''
                        produtos.append({'ordem_id': ordem_id, 'numero_os': numero_os, 'data_criacao': data_criacao, 'descricao': desc, 'valor': float(valor or 0), 'cor': cor, 'reforco': reforco, 'codigo': codigo or ''})
                else:
                    # fallback: parse detalhes_produto lines like '• desc - R$ 1.234,56'
                    if detalhes:
                        try:
                            linhas = [l.strip() for l in detalhes.replace('\r','\n').split('\n') if l.strip() and not l.strip().startswith('-')]
                            for linha in linhas:
                                if ' - R$ ' in linha:
                                    try:
                                        desc, valtxt = linha.rsplit(' - R$ ', 1)
                                        valconv = valtxt.replace('.', '').replace(',', '.') if ',' in valtxt else valtxt
                                        valor = float(valconv) if valconv else 0.0
                                    except Exception:
                                        valor = 0.0
                                        desc = linha
                                else:
                                    valor = 0.0
                                    desc = linha
                                desc = desc.strip('• ').strip()
                                if busca and busca.lower() not in desc.lower():
                                    continue
                                # try to find product code by matching description to catalog
                                codigo = ''
                                try:
                                    self.cursor.execute("SELECT codigo FROM produtos WHERE nome = ? COLLATE NOCASE LIMIT 1", (desc,))
                                    rowc = self.cursor.fetchone()
                                    if rowc and rowc[0]:
                                        codigo = rowc[0]
                                    else:
                                        self.cursor.execute("SELECT codigo FROM produtos WHERE nome LIKE ? COLLATE NOCASE LIMIT 1", (f"%{desc}%",))
                                        rowc2 = self.cursor.fetchone()
                                        if rowc2 and rowc2[0]:
                                            codigo = rowc2[0]
                                except Exception:
                                    codigo = ''
                                produtos.append({'ordem_id': ordem_id, 'numero_os': numero_os, 'data_criacao': data_criacao, 'descricao': desc, 'valor': float(valor or 0), 'cor': '', 'reforco': False, 'codigo': codigo or ''})
                        except Exception:
                            pass
            return produtos
        except Exception as e:
            print(f"Erro ao listar produtos vendidos: {e}")
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
            
            # Normalize CPF
            cpf_norm = ''.join(ch for ch in str(cpf or '') if ch.isdigit())
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
            
            cpf_norm = ''.join(ch for ch in str(cpf or '') if ch.isdigit())
            self.cursor.execute("""
                INSERT INTO clientes (nome, cpf, telefone, email, rua, numero, referencia, data_criacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (nome, cpf_norm, telefone, email, endereco, numero, referencia, data_atual))
            
            self.conn.commit()
            return self.cursor.lastrowid
            
        except Exception as e:
            print(f"Erro ao inserir cliente: {e}")
            return None

    def close(self):
        """Fecha conexão com o banco"""
        if hasattr(self, 'conn'):
            self.conn.close()

    # ---------- Gastos (Despesas) ----------
    def inserir_gasto(self, tipo, descricao, valor, data=None):
        try:
            if data:
                self.cursor.execute("INSERT INTO gastos (tipo, descricao, valor, data) VALUES (?, ?, ?, ?)", (tipo, descricao, float(valor), data))
            else:
                self.cursor.execute("INSERT INTO gastos (tipo, descricao, valor) VALUES (?, ?, ?)", (tipo, descricao, float(valor)))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Erro ao inserir gasto: {e}")
            return None

    def atualizar_gasto(self, gasto_id, tipo=None, descricao=None, valor=None, data=None):
        """Atualiza um gasto existente. Campos None serão preservados (não atualizados)."""
        try:
            # Buscar valores atuais
            self.cursor.execute('SELECT tipo, descricao, valor, data FROM gastos WHERE id = ?', (gasto_id,))
            row = self.cursor.fetchone()
            if not row:
                return False

            cur_tipo, cur_desc, cur_val, cur_data = row

            novo_tipo = tipo if tipo is not None else cur_tipo
            novo_desc = descricao if descricao is not None else cur_desc
            novo_val = float(valor) if valor is not None else float(cur_val or 0)
            novo_data = data if data is not None else cur_data

            self.cursor.execute(
                'UPDATE gastos SET tipo = ?, descricao = ?, valor = ?, data = ? WHERE id = ?',
                (novo_tipo, novo_desc, novo_val, novo_data, gasto_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar gasto: {e}")
            return False

    def deletar_gasto(self, gasto_id):
        """Exclui um gasto pelo seu ID."""
        try:
            self.cursor.execute('DELETE FROM gastos WHERE id = ?', (gasto_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao deletar gasto: {e}")
            return False

    def get_gasto(self, gasto_id):
        """Retorna um gasto pelo ID como tupla (id, tipo, descricao, valor, data) ou None."""
        try:
            self.cursor.execute('SELECT id, tipo, descricao, valor, data FROM gastos WHERE id = ?', (gasto_id,))
            row = self.cursor.fetchone()
            return row
        except Exception as e:
            print(f"Erro ao buscar gasto por id: {e}")
            return None

    def listar_gastos_periodo(self, data_inicio, data_fim):
        try:
            query = 'SELECT id, tipo, descricao, valor, data FROM gastos WHERE date(data) BETWEEN ? AND ? ORDER BY data DESC'
            self.cursor.execute(query, (data_inicio, data_fim))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar gastos por período: {e}")
            return []

    def soma_gastos_periodo(self, data_inicio, data_fim):
        try:
            query = 'SELECT SUM(valor) FROM gastos WHERE date(data) BETWEEN ? AND ?'
            self.cursor.execute(query, (data_inicio, data_fim))
            row = self.cursor.fetchone()
            return float(row[0] or 0.0)
        except Exception as e:
            print(f"Erro ao somar gastos por período: {e}")
            return 0.0

    def contar_caixas_vendidas_periodo(self, data_inicio, data_fim):
        """Conta ocorrências de 'caixa' em detalhes_produto no período (heurística simples)."""
        try:
            query = "SELECT detalhes_produto FROM ordem_servico WHERE date(data_criacao) BETWEEN ? AND ? AND (dados_json IS NULL OR instr(dados_json, 'cancelado') = 0)"
            self.cursor.execute(query, (data_inicio, data_fim))
            rows = self.cursor.fetchall()
            total = 0
            for (det,) in rows:
                if not det:
                    continue
                # contar a palavra 'caixa' e variações
                txt = det.lower()
                total += txt.count('caixa')
            return total
        except Exception as e:
            print(f"Erro ao contar caixas: {e}")
            return 0

    def get_pedido_por_id(self, pedido_id):
        """Busca um pedido específico por ID"""
        import json
        try:
            query = '''
            SELECT id, numero_os, data_criacao, nome_cliente, cpf_cliente, 
                   telefone_cliente, detalhes_produto, valor_produto, valor_entrada, 
                   frete, forma_pagamento, prazo, nome_pdf, dados_json, status
            FROM ordem_servico 
            WHERE id = ?
            '''
            self.cursor.execute(query, (pedido_id,))
            row = self.cursor.fetchone()
            
            if not row:
                return None
            
            # Converter para dicionário
            pedido = {
                'id': row[0],
                'numero_os': row[1],
                'data_criacao': row[2],
                'cliente_nome': row[3],
                'cpf_cliente': row[4],
                'telefone_cliente': row[5],
                'detalhes_produto': row[6],
                'valor_total': row[7] or 0.0,
                'entrada': row[8] or 0.0,
                'frete': row[9] or 0.0,
                'metodo_pagamento': row[10],
                'prazo': row[11],
                'nome_pdf': row[12],
                'dados_json': row[13],
                'status': row[14] or 'Pendente'
            }
            
            # Tentar extrair dados do JSON para campos adicionais
            if pedido['dados_json']:
                try:
                    json_data = json.loads(pedido['dados_json'])
                    pedido.update({
                        'desconto': json_data.get('desconto', 0.0),
                        'observacoes': json_data.get('observacoes', '')
                    })
                    # Sobrescrever status se houver no JSON
                    if 'status' in json_data:
                        pedido['status'] = json_data['status']
                except:
                    pass
            
            return pedido
            
        except Exception as e:
            print(f"Erro ao buscar pedido por ID: {e}")
            return None

    def get_produtos_do_pedido(self, pedido_id):
        """Extrai lista de produtos de um pedido"""
        try:
            pedido = self.get_pedido_por_id(pedido_id)
            if not pedido:
                return []
            
            produtos = []
            
            # Tentar extrair do JSON primeiro
            if pedido.get('dados_json'):
                try:
                    import json
                    json_data = json.loads(pedido['dados_json'])
                    produtos_json = json_data.get('produtos', [])
                    if produtos_json:
                        for i, p in enumerate(produtos_json):
                            print(f"Processando produto JSON {i}: {p}, tipo: {type(p)}")
                            if isinstance(p, dict):
                                produtos.append({
                                    'nome': p.get('descricao', p.get('nome', 'Produto')),
                                    'quantidade': p.get('quantidade', 1),
                                    'valor_unitario': p.get('valor', p.get('preco', 0.0))
                                })
                            else:
                                print(f"ERRO: Produto não é dict: {p}")
                                produtos.append({
                                    'nome': str(p),
                                    'quantidade': 1,
                                    'valor_unitario': 0.0
                                })
                        return produtos
                except Exception as e:
                    print(f"Erro ao processar JSON de produtos: {e}")
                    pass
            
            # Fallback: extrair do campo detalhes_produto (texto)
            detalhes = pedido.get('detalhes_produto', '')
            if detalhes:
                linhas = detalhes.replace('\r', '\n').split('\n')
                for linha in linhas:
                    linha = linha.strip()
                    if linha and not linha.startswith('-'):
                        if ' - R$ ' in linha:
                            try:
                                nome = linha.split(' - R$ ')[0].strip()
                                valor_str = linha.split(' - R$ ')[1].strip()
                                valor = float(valor_str.replace(',', '.'))
                                produtos.append({
                                    'nome': nome,
                                    'quantidade': 1,
                                    'valor_unitario': valor
                                })
                            except Exception as e:
                                print(f"Erro ao processar linha de produto: {linha}, erro: {e}")
                                pass
                        else:
                            # Produto sem valor especificado
                            produtos.append({
                                'nome': linha,
                                'quantidade': 1,
                                'valor_unitario': 0.0
                            })
            
            return produtos
            
        except Exception as e:
            print(f"Erro ao buscar produtos do pedido: {e}")
            import traceback
            traceback.print_exc()
            return []
