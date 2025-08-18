"""
Script para inspecionar completamente o banco de dados
"""

import sqlite3
import os
import platform

# Caminho do banco
if platform.system() == "Windows":
    base_path = os.path.expanduser("~\\Documents")
else:
    base_path = os.path.expanduser("~/Documents")

db_path = os.path.join(base_path, "OrdemServico", "ordem_servico.db")

print(f"Caminho do banco: {db_path}")
print(f"Banco existe: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(ordem_servico)")
        colunas = cursor.fetchall()
        print(f"\nEstrutura da tabela ordem_servico:")
        for col in colunas:
            print(f"  {col[1]} ({col[2]})")
        
        # Contar total de registros
        cursor.execute("SELECT COUNT(*) FROM ordem_servico")
        total = cursor.fetchone()[0]
        print(f"\nTotal de registros: {total}")
        
        # Mostrar todos os registros
        cursor.execute("SELECT * FROM ordem_servico ORDER BY numero_os")
        registros = cursor.fetchall()
        
        print(f"\nTodos os registros:")
        for i, reg in enumerate(registros):
            print(f"\nRegistro {i+1}:")
            print(f"  ID: {reg[0]}")
            print(f"  Número OS: {reg[1]}")
            print(f"  Data: {reg[2]}")
            print(f"  Cliente: {reg[3]}")
            print(f"  CPF: {reg[4]}")
            print(f"  Telefone: {reg[5]}")
            print(f"  Produtos: {reg[6][:50]}..." if len(reg[6]) > 50 else f"  Produtos: {reg[6]}")
            print(f"  Valor: R$ {reg[7]}")
            print(f"  Entrada: R$ {reg[8]}")
            print(f"  Frete: R$ {reg[9]}")
            print(f"  Pagamento: {reg[10]}")
            print(f"  Prazo: {reg[11]} dias")
            print(f"  PDF: {reg[12]}")
            print(f"  JSON: {reg[13]}")
        
        # Verificar clientes únicos
        cursor.execute("SELECT DISTINCT nome_cliente, cpf_cliente, telefone_cliente FROM ordem_servico")
        clientes_unicos = cursor.fetchall()
        print(f"\nClientes únicos encontrados:")
        for cliente in clientes_unicos:
            print(f"  Nome: {cliente[0]}, CPF: {cliente[1]}, Telefone: {cliente[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Erro ao acessar banco: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Banco não existe!")
