"""
Module for database configuration and initialization.
All user-facing messages are in Portuguese. All comments, docstrings, and logs are in English.
"""
import sqlite3
import os
import platform

class DatabaseSetup:
    @staticmethod
    def get_database_path():
        """Return database path based on OS."""
        if platform.system() == "Windows":
            base_path = os.path.expanduser("~\\Documents")
        else:
            base_path = os.path.expanduser("~/Documents")
        db_dir = os.path.join(base_path, "OrdemServico")
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, "ordem_servico.db")
    
    @staticmethod
    def criar_tabelas(cursor):
        """Create all required tables and indices. User-facing errors are in Portuguese; logs in English."""
        try:
            # Service orders table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordem_servico (
                id INTEGER PRIMARY KEY,
                numero_os INTEGER NOT NULL UNIQUE,
                data_criacao TEXT NOT NULL,
                nome_cliente TEXT NOT NULL,
                cpf_cliente TEXT,
                telefone_cliente TEXT,
                detalhes_produto TEXT,
                valor_produto REAL,
                valor_entrada REAL,
                frete REAL,
                forma_pagamento TEXT,
                prazo INTEGER,
                nome_pdf TEXT,
                dados_json TEXT,
                status TEXT DEFAULT 'Em Andamento'
            )
            ''')

            # Separate clients table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT,
                cnpj TEXT,
                inscricao_estadual TEXT,
                telefone TEXT,
                email TEXT,
                cep TEXT,
                rua TEXT,
                numero TEXT,
                bairro TEXT,
                cidade TEXT,
                estado TEXT,
                referencia TEXT,
                data_criacao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cpf) ON CONFLICT IGNORE,
                UNIQUE(cnpj) ON CONFLICT IGNORE
            )
            ''')

            # Indices for performance
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_numero_os ON ordem_servico(numero_os)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_data_criacao ON ordem_servico(data_criacao)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_status ON ordem_servico(status)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_nome_cliente ON ordem_servico(nome_cliente)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_cliente_nome ON clientes(nome)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_cliente_cpf ON clientes(cpf)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_cliente_telefone ON clientes(telefone)''')

            # Ensure CNPJ and Inscrição Estadual columns exist (migration)
            try:
                cursor.execute("ALTER TABLE clientes ADD COLUMN cnpj TEXT")
            except Exception:
                pass  # Ignore if already exists
            try:
                cursor.execute("ALTER TABLE clientes ADD COLUMN inscricao_estadual TEXT")
            except Exception:
                pass  # Ignore if already exists

            # Ensure status column for service orders (migration)
            try:
                cursor.execute("ALTER TABLE ordem_servico ADD COLUMN status TEXT DEFAULT 'Em Andamento'")
            except Exception:
                pass  # Ignore if already exists

            # Ensure CEP column for clients (migration)
            try:
                cursor.execute("ALTER TABLE clientes ADD COLUMN cep TEXT")
            except Exception:
                pass  # Ignore if already exists

            # Create CNPJ index after ensuring column exists
            try:
                cursor.execute('''CREATE INDEX IF NOT EXISTS idx_cliente_cnpj ON clientes(cnpj)''')
            except Exception:
                pass  # Ignore if already exists

            # Products table (catalog)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                codigo TEXT,
                preco REAL NOT NULL DEFAULT 0,
                descricao TEXT,
                categoria TEXT,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(nome) ON CONFLICT IGNORE
            )
            ''')

            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_produtos_nome ON produtos(nome)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_produtos_preco ON produtos(preco)''')
            # Ensure 'codigo' column exists for compatibility (simple migration)
            try:
                cursor.execute("ALTER TABLE produtos ADD COLUMN codigo TEXT")
            except Exception:
                pass  # Ignore if already exists

            # Expenses table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL, -- produto ou servico
                descricao TEXT,
                valor REAL NOT NULL DEFAULT 0,
                data TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_gastos_data ON gastos(data)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_gastos_tipo ON gastos(tipo)''')
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")  # User-facing error in Portuguese
            print(f"Error creating tables: {e}")  # Log in English
            return False
