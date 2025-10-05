
"""
DatabaseManager: Singleton for centralized access to the SQLite database.
Handles orders, clients, products, reports, and migrations.
All user-facing messages are in Portuguese. All comments, docstrings, and logs are in English.
"""


import sqlite3
import json
from datetime import datetime

# Specialized modules
from database.core.db_setup import DatabaseSetup
from database.crud.order_crud import OrderCRUD
from database.queries.report_queries import ReportQueries
from database.crud.products_crud import ProductsCRUD



class DatabaseManager:
    """Singleton for centralized database access and main operations."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.db_path = DatabaseSetup.get_database_path()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        # Specialized modules
        self.order_crud = OrderCRUD(self.cursor, self.conn)
        self.reports = ReportQueries(self.cursor)
        self.products = ProductsCRUD(self.cursor, self.conn)
        # Database initialization
        DatabaseSetup.criar_tabelas(self.cursor)
        self.conn.commit()
        self._migrate_soft_delete()
        self._migrate_numero_compras()
        self._initialized = True
    
    def _migrate_soft_delete(self):
        """Run Soft Delete migration if needed."""
        try:
            from app.utils.soft_delete import SoftDeleteManager
            success, message = SoftDeleteManager.migrate_add_deleted_at_columns()
            # Log migration result in English
            print(f"Soft Delete migration: {message}" if success else f"Soft Delete migration warning: {message}")
        except Exception as e:
            print(f"Soft Delete migration error: {e}")
    
    def _migrate_numero_compras(self):
        """Run numero_compras migration and sync if needed."""
        try:
            print("Starting numero_compras migration/sync...")
            from database.migrations import migrate_add_numero_compras
            migrate_add_numero_compras(self.conn)
        except Exception as e:
            print(f"numero_compras migration error: {e}")

    def salvar_ordem(self, dados, nome_pdf=""):
        """Save service order using CRUD module."""
        try:
            # Log incoming payload summary (for debugging)
            produtos = dados.get('produtos') if isinstance(dados, dict) else None
            total_produtos = None
            if produtos and isinstance(produtos, (list, tuple)):
                try:
                    total_produtos = sum([float(p.get('valor', 0) or 0) for p in produtos])
                except Exception:
                    total_produtos = None
        except Exception:
            pass
        return self.order_crud.criar_ordem(dados, nome_pdf)

    def deletar_pedido(self, pedido_id):
        """Delete a specific order by ID."""
        return self.order_crud.deletar_ordem(pedido_id)

    def deletar_ordem(self, pedido_id):
        """Delete order - kept for compatibility."""
        return self.order_crud.deletar_ordem(pedido_id)

    def atualizar_status_pedido(self, pedido_id, novo_status):
        """Update order status using JSON data."""
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
            print(f"Error updating status: {e}")
            return False

    def listar_pedidos_ordenados_por_prazo(self, limite=50):
        """List orders sorted by deadline - INCLUDING ALL FIELDS FOR EDITING."""
        try:
            # Query com todos os campos necessários para edição (APENAS PEDIDOS NÃO DELETADOS)
            query = '''
            SELECT id, numero_os, data_criacao, nome_cliente, cpf_cliente, telefone_cliente, 
                   detalhes_produto, valor_produto, valor_entrada, frete, forma_pagamento,
                   prazo, nome_pdf, dados_json, status
            FROM ordem_servico
            WHERE deleted_at IS NULL
            ORDER BY data_criacao DESC
            LIMIT ?
            '''
            self.cursor.execute(query, (limite,))
            resultados = self.cursor.fetchall()

            pedidos = []
            for row in resultados:
                # Expecting 15 columns
                if len(row) < 15:
                    continue
                (id_, numero_os, data_criacao, nome_cliente, cpf_cliente, telefone_cliente,
                 detalhes_produto, valor_produto, valor_entrada, frete, forma_pagamento,
                 prazo, nome_pdf, dados_json, status) = row[:15]

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

                # Buscar dados completos do endereço da tabela clientes
                endereco_cliente = ''
                cep_cliente = ''
                rua_cliente = ''
                numero_cliente = ''
                bairro_cliente = ''
                cidade_cliente = ''
                estado_cliente = ''
                
                try:
                    # Normalizar CPF/CNPJ (remover pontuação)
                    documento_norm = ''.join(ch for ch in str(cpf_cliente or '') if ch.isdigit())
                    if documento_norm:
                        # Buscar por CPF ou CNPJ (ambos armazenados sem pontuação)
                        self.cursor.execute(
                            """SELECT cep, rua, numero, bairro, cidade, estado 
                               FROM clientes 
                               WHERE replace(replace(replace(cpf, '.', ''), '-', ''), ' ', '') = ? 
                                  OR replace(replace(replace(replace(cnpj, '.', ''), '/', ''), '-', ''), ' ', '') = ?
                               LIMIT 1""",
                            (documento_norm, documento_norm)
                        )
                        cli_row = self.cursor.fetchone()
                        if cli_row:
                            cep_cliente, rua_cliente, numero_cliente, bairro_cliente, cidade_cliente, estado_cliente = cli_row
                            cep_cliente = cep_cliente or ''
                            rua_cliente = rua_cliente or ''
                            numero_cliente = numero_cliente or ''
                            bairro_cliente = bairro_cliente or ''
                            cidade_cliente = cidade_cliente or ''
                            estado_cliente = estado_cliente or ''
                            # Montar endereço completo para compatibilidade
                            endereco_cliente = f"{rua_cliente} {numero_cliente} - {bairro_cliente} - {cidade_cliente} / {estado_cliente}".strip()
                except Exception as e:
                    print(f"Error fetching client address: {e}")
                    endereco_cliente = ''

                pedido = {
                    'id': id_,
                    'numero_os': numero_os or 0,
                    'nome_cliente': nome_cliente or 'Cliente não informado',
                    'cpf_cliente': cpf_cliente or '',
                    'telefone_cliente': telefone_cliente or '',
                    'endereco_cliente': endereco_cliente,
                    # Dados detalhados do endereço para o PDF
                    'cep_cliente': cep_cliente,
                    'rua_cliente': rua_cliente,
                    'numero_cliente': numero_cliente,
                    'bairro_cliente': bairro_cliente,
                    'cidade_cliente': cidade_cliente,
                    'estado_cliente': estado_cliente,
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
            print(f"Error listing orders: {e}")
            return []

    def atualizar_json_campos(self, pedido_id, updates: dict) -> bool:
        """Update specific fields inside order's dados_json."""
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
            print(f"Error updating order JSON: {e}")
            return False

    def buscar_ordem_por_numero(self, numero_os):
        """Search order by number using CRUD module."""
        return self.order_crud.buscar_ordem(numero_os)

    def obter_vendas_por_periodo(self, data_inicio, data_fim):
        """Get sales by period using reports module."""
        return self.reports.buscar_por_periodo(data_inicio, data_fim)

    def calcular_resumo_vendas(self, data_inicio, data_fim):
        """Calculate sales summary using reports module."""
        return self.reports.calcular_vendas_periodo(data_inicio, data_fim)

    def obter_vendas_diarias(self, dias=30):
        """Get daily sales using reports module."""
        return self.reports.vendas_por_dia(dias)

    def buscar_pedidos_por_cliente(self, nome_cliente):
        """Search orders by client using reports module."""
        return self.reports.buscar_por_cliente(nome_cliente)

    def buscar_pedidos_por_cpf(self, cpf_cliente):
        """Search orders by client CPF."""
        return self.reports.buscar_por_cpf(cpf_cliente)

    def atualizar_pedido(self, pedido_id, campos_atualizacao):
        """Update order fields using CRUD module."""
        return self.order_crud.atualizar_ordem(pedido_id, campos_atualizacao)

    def listar_clientes(self, limite=None):
        """List clients from the separate clients table."""
        try:
            if limite:
                query = '''
                SELECT id, nome, cpf, cnpj, inscricao_estadual, telefone, email, cep, rua, numero, bairro, cidade, estado, referencia, numero_compras
                FROM clientes 
                ORDER BY nome 
                LIMIT ?
                '''
                self.cursor.execute(query, (limite,))
            else:
                query = '''
                SELECT id, nome, cpf, cnpj, inscricao_estadual, telefone, email, cep, rua, numero, bairro, cidade, estado, referencia, numero_compras
                FROM clientes 
                ORDER BY nome
                '''
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error listing clients: {e}")
            return []
    
    def buscar_cliente_por_cpf(self, cpf):
        """Search full client data by CPF."""
        try:
            if not cpf:
                return None
            
            cpf_normalizado = ''.join(ch for ch in str(cpf) if ch.isdigit())
            if not cpf_normalizado:
                return None
                
            query = '''
            SELECT id, nome, cpf, cnpj, inscricao_estadual, telefone, email, 
                   cep, rua, numero, bairro, cidade, estado, referencia
            FROM clientes 
            WHERE replace(replace(replace(cpf, '.', ''), '-', ''), ' ', '') = ?
            LIMIT 1
            '''
            self.cursor.execute(query, (cpf_normalizado,))
            row = self.cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'nome': row[1],
                    'cpf': row[2],
                    'cnpj': row[3],
                    'inscricao_estadual': row[4],
                    'telefone': row[5],
                    'email': row[6],
                    'cep': row[7],
                    'rua': row[8],
                    'numero': row[9],
                    'bairro': row[10],
                    'cidade': row[11],
                    'estado': row[12],
                    'referencia': row[13]
                }
            return None
            
        except Exception as e:
            print(f"Error searching client by CPF: {e}")
            return None

    def atualizar_cliente(self, cliente_id, nome, cpf=None, telefone=None, email=None,
                          endereco=None, referencia=None, rua=None, numero=None,
                          bairro=None, cidade=None, estado=None):
        """Update an existing client in the clients table.
        Parameter 'endereco' kept for compatibility and is ignored, as fields are normalized.
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
            print(f"Error updating client: {e}")
            return False

    def atualizar_cliente_completo(self, cliente_id, nome, cpf=None, cnpj=None, inscricao_estadual=None,
                                  telefone=None, email=None, cep=None, rua=None, numero=None,
                                  bairro=None, cidade=None, estado=None, referencia=None):
        """Update an existing client with all fields, including CNPJ, IE, and CEP."""
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
            print(f"Error updating full client: {e}")
            return False

    def criar_cliente_completo(self, nome, cpf=None, cnpj=None, inscricao_estadual=None,
                              telefone=None, email=None, cep=None, rua=None, numero=None,
                              bairro=None, cidade=None, estado=None, referencia=None):
        """Create a new client with all fields, including CNPJ, IE, and CEP."""
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
            print(f"Error creating full client: {e}")
            return False

    def deletar_cliente(self, cliente_id):
        """Delete a client by ID."""
        try:
            self.cursor.execute("DELETE FROM clientes WHERE id = ?", (int(cliente_id),))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting client: {e}")
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
        """Extracts real products from orders (dados_json.produtos or detalhes_produto).
        Returns a list of dicts: {ordem_id, numero_os, data_criacao, descricao, valor, cor, reforco}
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
            print(f"Error listing sold products: {e}")
            return []

    def obter_resumo_mes(self, ano, mes):
        """Get sales summary for the month."""
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
            print(f"Error getting month summary: {e}")
            return (0, 0, 0)

    def listar_pedidos_ordenados_prazo(self, limite=200):
        """List orders sorted by deadline - compatibility."""
        return self.listar_pedidos_ordenados_por_prazo(limite)

    def obter_resumo_ano(self, ano):
        """Get sales summary for the year."""
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
            print(f"Error getting year summary: {e}")
            return (0, 0, 0)

    def obter_resumo_total(self):
        """Get total sales summary."""
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
            print(f"Error getting total summary: {e}")
            return (0, 0, 0)

    def criar_dados_teste(self):
        """Create test data if the table is empty."""
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
                
                print("Dados de teste criados!")  # User-facing message in Portuguese
                return True
            
        except Exception as e:
            print(f"Error creating test data: {e}")
            return False

    def upsert_cliente_completo(self, nome, cpf=None, telefone=None, email=None, 
                               cliente_id=None, referencia=None, rua=None, numero=None, 
                               bairro=None, cidade=None, estado=None):
        """Insert or update a client with full data in the clients table."""
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
            print(f"Error saving full client: {e}")
            return False

    def inserir_cliente(self, nome, cpf=None, telefone=None, email=None, endereco=None, referencia=None, numero=None):
        """Insert a new client in the clients table."""
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
            print(f"Error inserting client: {e}")
            return None

    def close(self):
        """Close database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()

    # ---------- Gastos (Despesas) ----------
    def inserir_gasto(self, tipo, descricao, valor, data=None):
        """Insert an expense record."""
        try:
            if data:
                self.cursor.execute("INSERT INTO gastos (tipo, descricao, valor, data) VALUES (?, ?, ?, ?)", (tipo, descricao, float(valor), data))
            else:
                self.cursor.execute("INSERT INTO gastos (tipo, descricao, valor) VALUES (?, ?, ?)", (tipo, descricao, float(valor)))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error inserting expense: {e}")
            return None

    def atualizar_gasto(self, gasto_id, tipo=None, descricao=None, valor=None, data=None):
        """Update an existing expense. None fields will be preserved (not updated)."""
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
            print(f"Error updating expense: {e}")
            return False

    def deletar_gasto(self, gasto_id):
        """Delete an expense by its ID."""
        try:
            self.cursor.execute('DELETE FROM gastos WHERE id = ?', (gasto_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False

    def get_gasto(self, gasto_id):
        """Return an expense by ID as a tuple (id, tipo, descricao, valor, data) or None."""
        try:
            self.cursor.execute('SELECT id, tipo, descricao, valor, data FROM gastos WHERE id = ?', (gasto_id,))
            row = self.cursor.fetchone()
            return row
        except Exception as e:
            print(f"Error fetching expense by id: {e}")
            return None

    def listar_gastos_periodo(self, data_inicio, data_fim):
        """List expenses for a given period."""
        try:
            query = 'SELECT id, tipo, descricao, valor, data FROM gastos WHERE date(data) BETWEEN ? AND ? ORDER BY data DESC'
            self.cursor.execute(query, (data_inicio, data_fim))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error listing expenses by period: {e}")
            return []

    def soma_gastos_periodo(self, data_inicio, data_fim):
        """Sum expenses for a given period."""
        try:
            query = 'SELECT SUM(valor) FROM gastos WHERE date(data) BETWEEN ? AND ?'
            self.cursor.execute(query, (data_inicio, data_fim))
            row = self.cursor.fetchone()
            return float(row[0] or 0.0)
        except Exception as e:
            print(f"Error summing expenses by period: {e}")
            return 0.0

    def contar_caixas_vendidas_periodo(self, data_inicio, data_fim):
        """Count occurrences of 'caixa' in detalhes_produto in the period (simple heuristic)."""
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
            print(f"Error counting 'caixa': {e}")
            return 0

    def get_pedido_por_id(self, pedido_id):
        """Fetch a specific order by ID."""
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
            print(f"Error fetching order by ID: {e}")
            return None

    def get_produtos_do_pedido(self, pedido_id):
        """Extract product list from an order."""
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
                            # Log processing of each product in JSON (debug)
                            print(f"Processing JSON product {i}: {p}, type: {type(p)}")
                            if isinstance(p, dict):
                                produto = {
                                    'nome': p.get('descricao', p.get('nome', 'Produto')),
                                    'codigo': p.get('codigo', 'S/Código'),
                                    'quantidade': p.get('quantidade', 1),
                                    'valor_unitario': p.get('valor', p.get('preco', 0.0))
                                }
                                
                                # Adicionar informações de cor (estrutura completa)
                                if 'cor_data' in p:
                                    produto['cor_data'] = p['cor_data']
                                elif 'cor' in p:
                                    produto['cor'] = p['cor']
                                
                                # Debug: verificar se as cores estão sendo preservadas
                                print(f"Product {produto['nome']}: cor_data={produto.get('cor_data')}, cor={produto.get('cor')}")
                                
                                produtos.append(produto)
                            else:
                                print(f"ERROR: Product is not dict: {p}")
                                produtos.append({
                                    'nome': str(p),
                                    'quantidade': 1,
                                    'valor_unitario': 0.0
                                })
                        return produtos
                except Exception as e:
                    print(f"Error processing product JSON: {e}")
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
                                print(f"Error processing product line: {linha}, error: {e}")
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
            print(f"Error fetching order products: {e}")
            import traceback
            traceback.print_exc()
            return []

    def excluir_pedido(self, pedido_id):
        """Compatibility: calls deletar_pedido."""
        return self.deletar_pedido(pedido_id)

DBManager = DatabaseManager()
