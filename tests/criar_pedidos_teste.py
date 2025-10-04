#!/usr/bin/env python3
"""
Script para criar pedidos de teste no banco de dados.
Útil para popular o sistema com dados de exemplo durante desenvolvimento e testes.

Uso:
    python tests/criar_pedidos_teste.py [quantidade]
    
Exemplo:
    python tests/criar_pedidos_teste.py 6
"""

import sqlite3
import os
import sys
import json
from datetime import datetime, timedelta
import random

# Adicionar o diretório raiz ao path para importar módulos do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def get_database_path():
    """Retorna o caminho do banco de dados"""
    base_path = os.path.expanduser("~/Documents")
    db_dir = os.path.join(base_path, "OrdemServico")
    return os.path.join(db_dir, "ordem_servico.db")


def criar_pedidos_teste(quantidade=6):
    """
    Cria pedidos de teste no banco de dados.
    
    Args:
        quantidade (int): Número de pedidos a criar (padrão: 6)
    
    Returns:
        list: Lista com os números das OSs criadas
    """
    
    # Conectar ao banco
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"❌ Erro: Banco de dados não encontrado em {db_path}")
        print("Execute a aplicação principal primeiro para criar o banco.")
        return []
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Pegar o próximo número de OS
        cursor.execute("SELECT MAX(numero_os) FROM ordem_servico")
        max_os = cursor.fetchone()[0]
        next_os = (max_os or 0) + 1
        
        print(f"📋 Criando {quantidade} pedidos de teste...")
        print(f"🔢 Próximo número de OS: {next_os}")
        print("=" * 60)
        
        # Dados de clientes de teste
        clientes_test = [
            {"nome": "Maria Silva Santos", "cpf": "123.456.789-01", "telefone": "(11) 98765-4321"},
            {"nome": "João Pedro Costa", "cpf": "234.567.890-12", "telefone": "(11) 97654-3210"},
            {"nome": "Ana Carolina Oliveira", "cpf": "345.678.901-23", "telefone": "(11) 96543-2109"},
            {"nome": "Carlos Eduardo Lima", "cpf": "456.789.012-34", "telefone": "(11) 95432-1098"},
            {"nome": "Juliana Fernandes", "cpf": "567.890.123-45", "telefone": "(11) 94321-0987"},
            {"nome": "Roberto Almeida Junior", "cpf": "678.901.234-56", "telefone": "(11) 93210-9876"},
            {"nome": "Patricia Costa Mendes", "cpf": "789.012.345-67", "telefone": "(11) 92109-8765"},
            {"nome": "Fernando Santos Lima", "cpf": "890.123.456-78", "telefone": "(11) 91098-7654"},
            {"nome": "Camila Rodrigues", "cpf": "901.234.567-89", "telefone": "(11) 90987-6543"},
            {"nome": "Lucas Oliveira Silva", "cpf": "012.345.678-90", "telefone": "(11) 89876-5432"},
        ]
        
        # Produtos de teste
        produtos_test = [
            "CX7GVT 60cm Diesel",
            "CX8GVT 80cm Agro",
            "Arrasto 2m Premium",
            "Grade Niveladora 1.5m",
            "Plantadeira 4 linhas",
            "Carrinho Transporte",
            "Distribuidor de Adubo",
            "Pulverizador 400L",
            "Subsolador 3 hastes",
            "Cultivador 7 linhas"
        ]
        
        # Status possíveis
        status_options = [
            "Pendente",
            "Em Produção", 
            "Em Produção",
            "Aguardando Peças",
            "Concluído",
            "Cancelado"
        ]
        
        # Formas de pagamento
        formas_pagamento = ["Dinheiro", "PIX", "Cartão de Crédito", "Cartão de Débito", "Transferência", "Boleto"]
        
        pedidos_criados = []
        
        # Criar pedidos
        for i in range(quantidade):
            # Selecionar dados aleatoriamente (ou ciclicamente se passar do tamanho das listas)
            cliente = clientes_test[i % len(clientes_test)]
            produto = produtos_test[i % len(produtos_test)]
            status = random.choice(status_options)
            
            # Data: variar entre hoje e 30 dias atrás
            dias_atras = random.randint(0, 30)
            data_criacao = (datetime.now() - timedelta(days=dias_atras)).strftime("%Y-%m-%d %H:%M:%S")
            
            # Valores variados realistas
            valor_produto = round(random.uniform(3000, 20000), 2)
            valor_entrada = round(valor_produto * random.uniform(0.2, 0.5), 2)
            frete = round(random.uniform(100, 800), 2)
            prazo = random.choice([15, 20, 30, 45, 60, 90])
            
            # Dados JSON do pedido (estrutura esperada pelo sistema)
            dados_json = json.dumps({
                "status": status.lower().replace(" ", "_"),
                "data_entrega": None,
                "desconto": 0,
                "cor": "",
                "reforco": False,
                "produtos": [{
                    "descricao": produto,
                    "valor": valor_produto,
                    "quantidade": 1,
                    "nome": produto
                }],
                "observacoes": f"Pedido de teste criado automaticamente #{i+1}"
            }, ensure_ascii=False)
            
            # Inserir pedido no banco
            cursor.execute("""
                INSERT INTO ordem_servico (
                    numero_os, data_criacao, nome_cliente, cpf_cliente, telefone_cliente,
                    detalhes_produto, valor_produto, valor_entrada, frete,
                    forma_pagamento, prazo, nome_pdf, dados_json, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                next_os + i,
                data_criacao,
                cliente["nome"],
                cliente["cpf"],
                cliente["telefone"],
                produto,
                valor_produto,
                valor_entrada,
                frete,
                random.choice(formas_pagamento),
                prazo,
                f"OS_{str(next_os + i).zfill(5)}_{cliente['nome'].replace(' ', '_')}.pdf",
                dados_json,
                status
            ))
            
            pedidos_criados.append(next_os + i)
            
            # Exibir informação do pedido criado
            print(f"✅ OS #{next_os + i:05d} | {cliente['nome']:<30} | {status:<20} | R$ {valor_produto:>10,.2f}")
        
        # Commit das mudanças
        conn.commit()
        
        print("=" * 60)
        print(f"🎉 {quantidade} pedidos de teste criados com sucesso!")
        print(f"📋 Números de OS: {pedidos_criados[0]} até {pedidos_criados[-1]}")
        
        return pedidos_criados
        
    except Exception as e:
        print(f"❌ Erro ao criar pedidos: {e}")
        conn.rollback()
        return []
        
    finally:
        conn.close()


def main():
    """Função principal do script"""
    print("🧪 CRIADOR DE PEDIDOS DE TESTE")
    print("=" * 60)
    
    # Verificar se foi passado um argumento (quantidade)
    quantidade = 6  # Padrão
    
    if len(sys.argv) > 1:
        try:
            quantidade = int(sys.argv[1])
            if quantidade <= 0:
                print("⚠️ A quantidade deve ser maior que zero. Usando padrão (6).")
                quantidade = 6
            elif quantidade > 50:
                print("⚠️ Quantidade muito grande. Limitando a 50 pedidos.")
                quantidade = 50
        except ValueError:
            print("⚠️ Argumento inválido. Usando quantidade padrão (6).")
    
    # Criar pedidos
    pedidos = criar_pedidos_teste(quantidade)
    
    if pedidos:
        print(f"\n💡 Dica: Abra a aplicação e clique em 'Recarregar' para ver os novos pedidos!")
    else:
        print("\n❌ Nenhum pedido foi criado.")
        sys.exit(1)


if __name__ == "__main__":
    main()
