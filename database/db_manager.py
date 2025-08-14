"""
Módulo de gerenciamento do banco de dados SQLite para armazenar ordens de serviço.
"""

import sqlite3
import os
import platform
import json
from datetime import datetime, timedelta


class DatabaseManager:

    def atualizar_status_pedido(self, pedido_id, novo_status):
        """
        Atualiza o status do pedido (ordem de serviço) no campo dados_json.
        """
        try:
            # Busca o JSON atual
            self.cursor.execute('SELECT dados_json FROM ordem_servico WHERE id = ?', (pedido_id,))
            row = self.cursor.fetchone()
            if not row:
                raise Exception('Pedido não encontrado')
            dados_json = row[0] or '{}'
            try:
                dados = json.loads(dados_json)
            except Exception:
                dados = {}
            dados['status'] = novo_status
            novo_json = json.dumps(dados)
            self.cursor.execute('UPDATE ordem_servico SET dados_json = ? WHERE id = ?', (novo_json, pedido_id))
            self.conn.commit()
        except Exception as e:
            print(f"Erro ao atualizar status do pedido: {e}")
            raise

    def listar_pedidos_ordenados_por_prazo(self, limite=200):
        """
        Lista pedidos ordenados por prazo.
        USA APENAS O CAMPO PRAZO (dias) - NÃO USA data_entrega.
        """
        try:
            self.cursor.execute('''
                SELECT id, numero_os, nome_cliente, detalhes_produto, valor_produto, 
                       frete, data_emissao, prazo
                FROM ordem_servico
                ORDER BY data_emissao DESC
                LIMIT ?
            ''', (limite,))
            resultados = self.cursor.fetchall()
            pedidos = []
            for row in resultados:
                id_, numero_os, nome_cliente, detalhes_produto, valor_produto, frete, data_emissao, prazo = row
                
                pedidos.append({
                    'id': id_,
                    'numero_os': numero_os,
                    'nome_cliente': nome_cliente,
                    'descricao': detalhes_produto,
                    'detalhes_produto': detalhes_produto,
                    'valor_produto': valor_produto or 0.0,
                    'frete': frete or 0.0,
                    'valor_total': (valor_produto or 0.0) + (frete or 0.0),  # SEMPRE SOMAR
                    'data_emissao': data_emissao,
                    'prazo_dias': prazo,  # USAR APENAS ESTE CAMPO
                    'status': 'em produção'
                })
            
            # Ordenar por prazo (menor prazo primeiro = mais urgente)
            def get_prazo_for_sort(pedido):
                prazo = pedido.get('prazo_dias')
                if prazo is not None:
                    return int(prazo)
                return 999  # Se não tem prazo, colocar no final
            
            pedidos.sort(key=get_prazo_for_sort)
            return pedidos
        except sqlite3.Error as e:
            print(f"Erro ao listar pedidos ordenados por prazo: {e}")
            return []
    """
    Gerencia o banco de dados das ordens de serviço, permitindo
    salvar, recuperar e pesquisar ordens anteriores.
    """
    NOME_ARQUIVO_DB = "ordens_servico.db"
    NOME_PASTA_APP = "ProjetoOs"  # Mesmo nome usado no Contador

    def __init__(self):
        """Inicializa a conexão com o banco de dados."""
        self.db_path = self._get_db_path()
        self.conn = None
        self.cursor = None
        self._conectar()
        self._criar_tabelas()

    def _get_db_path(self):
        """Retorna o caminho para o banco de dados."""
        system = platform.system()
        if system == "Windows":
            pasta = os.path.join(
                os.getenv("APPDATA"), self.NOME_PASTA_APP
            )
        elif system == "Linux":
            pasta = os.path.join(
                os.path.expanduser("~/.local/share"), self.NOME_PASTA_APP
            )
        else:
            pasta = os.path.join(
                os.path.expanduser("~"), "." + self.NOME_PASTA_APP
            )

        if not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)
        
        return os.path.join(pasta, self.NOME_ARQUIVO_DB)

    def _conectar(self):
        """Estabelece a conexão com o banco de dados."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def _criar_tabelas(self):
        """Cria as tabelas necessárias se não existirem."""
        try:
            # Tabela de clientes (cadastro)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cpf TEXT UNIQUE,
                    telefone TEXT,
                    email TEXT,
                    created_at TEXT NOT NULL
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ordem_servico (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_os INTEGER NOT NULL,
                    nome_cliente TEXT NOT NULL,
                    cpf_cliente TEXT,
                    telefone_cliente TEXT,
                    detalhes_produto TEXT,
                    valor_produto REAL,
                    valor_entrada REAL,
                    frete REAL,
                    forma_pagamento TEXT,
                    prazo INTEGER,
                    data_emissao TEXT NOT NULL,
                    data_entrega TEXT,
                    caminho_pdf TEXT NOT NULL,
                    dados_json TEXT
                )
            ''')
            # Tentativa opcional de adicionar coluna de vínculo com cliente (id)
            try:
                self.cursor.execute('ALTER TABLE ordem_servico ADD COLUMN cliente_id INTEGER')
            except Exception:
                pass
            
            # Adicionar colunas endereco e referencia na tabela clientes se não existirem
            try:
                self.cursor.execute('ALTER TABLE clientes ADD COLUMN endereco TEXT')
            except Exception:
                pass
            try:
                self.cursor.execute('ALTER TABLE clientes ADD COLUMN referencia TEXT')
            except Exception:
                pass
            # Tabela para controle de prazos (para uso futuro e relatórios)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS prazos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_os INTEGER NOT NULL,
                    nome_cliente TEXT NOT NULL,
                    prazo INTEGER,
                    data_emissao TEXT NOT NULL,
                    data_entrega TEXT,
                    status TEXT DEFAULT 'pendente',
                    observacoes TEXT
                )
            ''')
            # Tabela para itens/produtos (cada linha dos detalhes)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_os INTEGER NOT NULL,
                    nome_cliente TEXT,
                    descricao TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            ''')
            # Opcional: itens_pedido estruturado (para evoluções futuras)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS itens_pedido (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id INTEGER,
                    descricao TEXT NOT NULL,
                    quantidade REAL DEFAULT 1,
                    valor REAL,
                    created_at TEXT NOT NULL
                )
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")
            raise

    def salvar_ordem(self, dados, caminho_pdf):
        """
        Salva uma ordem de serviço no banco de dados.
        SEMPRE calcula e salva o campo prazo em dias.
        
        Args:
            dados (dict): Dicionário com dados da ordem de serviço
            caminho_pdf (str): Caminho onde o PDF foi salvo
        
        Returns:
            int: ID da ordem inserida no banco
        """
        try:
            data_emissao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # GARANTIR que sempre temos o campo prazo em dias
            prazo_dias = dados.get("prazo")
            if not prazo_dias:
                # Se não tem prazo, definir padrão de 30 dias
                prazo_dias = 30
                dados["prazo"] = prazo_dias
            else:
                # Garantir que é um número inteiro
                try:
                    prazo_dias = int(prazo_dias)
                    dados["prazo"] = prazo_dias
                except:
                    prazo_dias = 30
                    dados["prazo"] = prazo_dias
            
            # Calcular data_entrega baseada no prazo (apenas para referência)
            data_entrega = dados.get('data_entrega')
            if not data_entrega:
                data_entrega = (datetime.now() + timedelta(days=prazo_dias)).strftime('%Y-%m-%d')
                dados['data_entrega'] = data_entrega
            
            # Serializa dados completos para recuperação futura
            dados_json = json.dumps(dados)
            
            self.cursor.execute('''
                INSERT INTO ordem_servico (
                    numero_os, nome_cliente, cpf_cliente, 
                    telefone_cliente, detalhes_produto, valor_produto,
                    valor_entrada, frete, forma_pagamento, prazo,
                    data_emissao, data_entrega, caminho_pdf, dados_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados["numero_os"], dados["nome_cliente"], dados.get("cpf_cliente"),
                dados.get("telefone_cliente"), dados.get("detalhes_produto"),
                dados.get("valor_produto"), dados.get("valor_entrada"),
                dados.get("frete"), dados.get("forma_pagamento"),
                prazo_dias, data_emissao, data_entrega, caminho_pdf,
                dados_json
            ))
            self.conn.commit()
            ordem_id = self.cursor.lastrowid
            print(f"Ordem salva com ID: {ordem_id}")  # Debug
            
            # Vincula/atualiza cliente
            try:
                cliente_id = self.upsert_cliente(
                    nome=dados.get("nome_cliente"),
                    cpf=dados.get("cpf_cliente"),
                    telefone=dados.get("telefone_cliente"),
                    email=None,
                    endereco=None,
                    referencia=None
                )
                if cliente_id:
                    try:
                        self.cursor.execute('UPDATE ordem_servico SET cliente_id = ? WHERE id = ?', (cliente_id, ordem_id))
                        self.conn.commit()
                    except Exception:
                        pass
            except Exception:
                pass
            
            return ordem_id
            # Também salvamos/atualizamos o registro em 'prazos' para consultas futuras
            try:
                self.salvar_prazo(dados)
            except Exception as _:
                # Não impedir a OS por falha no registro de prazos
                pass
            # Salvar produtos (linhas dos detalhes)
            try:
                self.salvar_produtos(dados)
            except Exception as _:
                pass
            return ordem_id
        except sqlite3.Error as e:
            print(f"Erro ao salvar ordem: {e}")
            self.conn.rollback()
            raise

    # ===== CRUD de Clientes =====
    def upsert_cliente(self, nome: str, cpf: str | None = None, telefone: str | None = None, email: str | None = None, endereco: str | None = None, referencia: str | None = None):
        """Cria ou atualiza cliente por CPF (preferencial) ou por par nome+telefone.
        Retorna o id do cliente.
        """
        if not nome:
            return None
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            if cpf:
                self.cursor.execute('SELECT id FROM clientes WHERE cpf = ?', (cpf,))
                row = self.cursor.fetchone()
                if row:
                    cid = row[0]
                    self.cursor.execute('''UPDATE clientes SET nome = ?, telefone = ?, email = ?, endereco = ?, referencia = ? WHERE id = ?''', 
                                      (nome, telefone, email, endereco, referencia, cid))
                    self.conn.commit()
                    return cid
                else:
                    self.cursor.execute('''INSERT INTO clientes (nome, cpf, telefone, email, endereco, referencia, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                                      (nome, cpf, telefone, email, endereco, referencia, now))
                    self.conn.commit()
                    return self.cursor.lastrowid
            # Sem CPF: tenta pelo par nome+telefone
            self.cursor.execute('SELECT id FROM clientes WHERE nome = ? AND ifnull(telefone,"") = ifnull(?,"")', (nome, telefone))
            row = self.cursor.fetchone()
            if row:
                cid = row[0]
                self.cursor.execute('''UPDATE clientes SET email = ?, cpf = ifnull(cpf, ?), endereco = ?, referencia = ? WHERE id = ?''', 
                                  (email, cpf, endereco, referencia, cid))
                self.conn.commit()
                return cid
            self.cursor.execute('''INSERT INTO clientes (nome, cpf, telefone, email, endereco, referencia, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                              (nome, cpf, telefone, email, endereco, referencia, now))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Erro upsert cliente: {e}")
            self.conn.rollback()
            return None

    def listar_clientes(self, limite=300):
        try:
            self.cursor.execute('SELECT id, nome, cpf, telefone, email, created_at FROM clientes ORDER BY created_at DESC LIMIT ?', (limite,))
            rows = self.cursor.fetchall()
            cols = ['id','nome','cpf','telefone','email','created_at']
            return [dict(zip(cols, r)) for r in rows]
        except sqlite3.Error as e:
            print(f"Erro ao listar clientes: {e}")
            return []

    def atualizar_cliente(self, cliente_id: int, nome: str, cpf: str | None, telefone: str | None, email: str | None):
        try:
            self.cursor.execute('UPDATE clientes SET nome = ?, cpf = ?, telefone = ?, email = ? WHERE id = ?', (nome, cpf, telefone, email, cliente_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar cliente: {e}")
            self.conn.rollback()
            return False

    def deletar_cliente(self, cliente_id: int):
        """Exclui cliente. Não deleta ordens existentes (para segurança)."""
        try:
            self.cursor.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao deletar cliente: {e}")
            self.conn.rollback()
            return False

    # ===== CRUD de Ordens/Pedidos =====
    def atualizar_ordem(self, ordem_id: int, campos: dict):
        """Atualiza campos de uma ordem de serviço por id."""
        if not campos:
            return False
        keys = []
        vals = []
        for k, v in campos.items():
            keys.append(f"{k} = ?")
            vals.append(v)
        vals.append(ordem_id)
        sql = f"UPDATE ordem_servico SET {', '.join(keys)} WHERE id = ?"
        try:
            self.cursor.execute(sql, tuple(vals))
            self.conn.commit()
            # Se mudou nome_cliente/prazo, atualiza prazos também
            try:
                self.cursor.execute('SELECT numero_os, nome_cliente, prazo FROM ordem_servico WHERE id = ?', (ordem_id,))
                row = self.cursor.fetchone()
                if row:
                    numero_os, nome_cliente, prazo = row
                    self.salvar_prazo({'numero_os': numero_os, 'nome_cliente': nome_cliente, 'prazo': prazo})
            except Exception:
                pass
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar ordem: {e}")
            self.conn.rollback()
            return False

    def deletar_ordem(self, ordem_id: int):
        """Apaga ordem e registros vinculados (prazos, produtos)."""
        try:
            # Buscar numero_os para limpar correlatos
            self.cursor.execute('SELECT numero_os FROM ordem_servico WHERE id = ?', (ordem_id,))
            row = self.cursor.fetchone()
            numero_os = row[0] if row else None
            if numero_os is not None:
                self.cursor.execute('DELETE FROM prazos WHERE numero_os = ?', (numero_os,))
                self.cursor.execute('DELETE FROM produtos WHERE numero_os = ?', (numero_os,))
            self.cursor.execute('DELETE FROM ordem_servico WHERE id = ?', (ordem_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao deletar ordem: {e}")
            self.conn.rollback()
            return False

    # ===== CRUD de Produtos (linhas) =====
    def atualizar_produto(self, produto_id: int, descricao: str):
        try:
            self.cursor.execute('UPDATE produtos SET descricao = ? WHERE id = ?', (descricao, produto_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao atualizar produto: {e}")
            self.conn.rollback()
            return False

    def deletar_produto(self, produto_id: int):
        try:
            self.cursor.execute('DELETE FROM produtos WHERE id = ?', (produto_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao deletar produto: {e}")
            self.conn.rollback()
            return False

    def salvar_prazo(self, dados):
        """
        Registra ou atualiza um prazo referente a uma OS.

        Args:
            dados (dict): Deve conter numero_os, nome_cliente e prazo (dias).
        """
        try:
            numero_os = int(dados.get('numero_os')) if dados.get('numero_os') is not None else None
            nome_cliente = dados.get('nome_cliente')
            prazo = dados.get('prazo')
            data_emissao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            data_entrega = None
            if prazo:
                data_entrega = (datetime.now() + timedelta(days=int(prazo))).strftime('%Y-%m-%d')

            if numero_os is None or not nome_cliente:
                return

            # Upsert simples: remove registro antigo do mesmo numero_os e insere novamente
            self.cursor.execute('DELETE FROM prazos WHERE numero_os = ?', (numero_os,))
            self.cursor.execute('''
                INSERT INTO prazos (
                    numero_os, nome_cliente, prazo, data_emissao, data_entrega, status, observacoes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                numero_os, nome_cliente, prazo, data_emissao, data_entrega, 'pendente', None
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Erro ao salvar prazo: {e}")
            self.conn.rollback()

    def listar_prazos(self, limite=200):
        """
        Lista prazos registrados, ordenando pela data de entrega (os sem data por último).
        """
        try:
            self.cursor.execute('''
                SELECT id, numero_os, nome_cliente, prazo, data_emissao, data_entrega, status, observacoes
                FROM prazos
                ORDER BY (data_entrega IS NULL) ASC, data_entrega ASC
                LIMIT ?
            ''', (limite,))
            rows = self.cursor.fetchall()
            colunas = [
                'id', 'numero_os', 'nome_cliente', 'prazo', 'data_emissao', 'data_entrega', 'status', 'observacoes'
            ]
            return [dict(zip(colunas, r)) for r in rows]
        except sqlite3.Error as e:
            print(f"Erro ao listar prazos: {e}")
            return []

    def salvar_produtos(self, dados):
        """Salva as linhas de detalhes como produtos vinculados à OS."""
        try:
            numero_os = int(dados.get('numero_os')) if dados.get('numero_os') is not None else None
            nome_cliente = dados.get('nome_cliente')
            detalhes = dados.get('detalhes_produto') or ''
            if numero_os is None:
                return
            linhas = [l.strip() for l in str(detalhes).splitlines() if l.strip()]
            # Limpa anteriores e insere atuais
            self.cursor.execute('DELETE FROM produtos WHERE numero_os = ?', (numero_os,))
            agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for desc in linhas:
                self.cursor.execute(
                    'INSERT INTO produtos (numero_os, nome_cliente, descricao, created_at) VALUES (?, ?, ?, ?)',
                    (numero_os, nome_cliente, desc, agora)
                )
            self.conn.commit()
        except Exception as e:
            print(f"Erro ao salvar produtos: {e}")
            self.conn.rollback()

    def listar_produtos(self, limite=300):
        """Lista produtos (linhas de detalhes) das últimas OS."""
        try:
            self.cursor.execute(
                'SELECT id, numero_os, nome_cliente, descricao, created_at FROM produtos ORDER BY created_at DESC LIMIT ?',
                (limite,)
            )
            rows = self.cursor.fetchall()
            colunas = ['id','numero_os','nome_cliente','descricao','created_at']
            return [dict(zip(colunas, r)) for r in rows]
        except sqlite3.Error as e:
            print(f"Erro ao listar produtos: {e}")
            return []

    def buscar_ordem_por_numero(self, numero_os):
        """
        Busca uma ordem de serviço pelo número.
        
        Args:
            numero_os (int): Número da OS a buscar
        
        Returns:
            dict: Dados da ordem de serviço ou None se não encontrada
        """
        try:
            self.cursor.execute('''
                SELECT * FROM ordem_servico 
                WHERE numero_os = ?
                ORDER BY data_emissao DESC
            ''', (numero_os,))
            
            resultado = self.cursor.fetchone()
            if not resultado:
                return None
                
            return self._converter_resultado_para_dict(resultado)
        except sqlite3.Error as e:
            print(f"Erro ao buscar ordem por número: {e}")
            return None

    def buscar_ordem_por_cliente(self, nome_cliente):
        """
        Busca ordens de serviço pelo nome do cliente.
        
        Args:
            nome_cliente (str): Nome do cliente (parcial)
        
        Returns:
            list: Lista de dicionários com as ordens encontradas
        """
        try:
            self.cursor.execute('''
                SELECT * FROM ordem_servico 
                WHERE nome_cliente LIKE ?
                ORDER BY data_emissao DESC
            ''', (f'%{nome_cliente}%',))
            
            resultados = self.cursor.fetchall()
            return [self._converter_resultado_para_dict(resultado) 
                    for resultado in resultados]
        except sqlite3.Error as e:
            print(f"Erro ao buscar ordem por cliente: {e}")
            return []

    def listar_ultimas_ordens(self, limite=10):
        """
        Lista as últimas ordens de serviço criadas.
        
        Args:
            limite (int): Número máximo de resultados
        
        Returns:
            list: Lista de dicionários com as ordens encontradas
        """
        try:
            self.cursor.execute('''
                SELECT * FROM ordem_servico 
                ORDER BY data_emissao DESC
                LIMIT ?
            ''', (limite,))
            
            resultados = self.cursor.fetchall()
            return [self._converter_resultado_para_dict(resultado) 
                    for resultado in resultados]
        except sqlite3.Error as e:
            print(f"Erro ao listar últimas ordens: {e}")
            return []

    def _converter_resultado_para_dict(self, resultado):
        """
        Converte uma linha do banco de dados em um dicionário.
        
        Args:
            resultado (tuple): Resultado da consulta SQL
        
        Returns:
            dict: Dicionário com os dados da ordem
        """
        colunas = [
            'id', 'numero_os', 'nome_cliente', 'cpf_cliente',
            'telefone_cliente', 'detalhes_produto', 'valor_produto',
            'valor_entrada', 'frete', 'forma_pagamento', 'prazo',
            'data_emissao', 'data_entrega', 'caminho_pdf', 'dados_json'
        ]
        
        ordem_dict = dict(zip(colunas, resultado))
        
        # Carregar dados completos do JSON se disponível
        if ordem_dict.get('dados_json'):
            try:
                dados_completos = json.loads(ordem_dict['dados_json'])
                # Mesclar dados_completos com ordem_dict
                ordem_dict.update(dados_completos)
            except json.JSONDecodeError:
                pass
                
        return ordem_dict

    def fechar(self):
        """Fecha a conexão com o banco de dados."""
        if self.conn:
            self.conn.close()


# Singleton para acesso ao banco em qualquer lugar da aplicação
db_manager = DatabaseManager()
