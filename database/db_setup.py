"""
Módulo para configuração e inicialização do banco
"""
import sqlite3
import os
import platform

class DatabaseSetup:
    @staticmethod
    def get_database_path():
        """Retorna caminho do banco baseado no SO"""
        if platform.system() == "Windows":
            base_path = os.path.expanduser("~\\Documents")
        else:
            base_path = os.path.expanduser("~/Documents")
        
        db_dir = os.path.join(base_path, "OrdemServico")
        os.makedirs(db_dir, exist_ok=True)
        
        return os.path.join(db_dir, "ordem_servico.db")
    
    @staticmethod
    def criar_tabelas(cursor):
        """Cria tabelas necessárias"""
        try:
            # Tabela de ordens de serviço
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordem_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                dados_json TEXT
            )
            ''')
            
            # Tabela de clientes separada
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT,
                telefone TEXT,
                email TEXT,
                rua TEXT,
                numero TEXT,
                bairro TEXT,
                cidade TEXT,
                estado TEXT,
                referencia TEXT,
                data_criacao TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(cpf) ON CONFLICT IGNORE
            )
            ''')
            
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_numero_os ON ordem_servico(numero_os)
            ''')
            
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_data_criacao ON ordem_servico(data_criacao)
            ''')
            
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cliente_nome ON clientes(nome)
            ''')
            
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cliente_cpf ON clientes(cpf)
            ''')
            
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
            raise
            
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_nome_cliente ON ordem_servico(nome_cliente)
            ''')
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
            return False
