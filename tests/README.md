# 🧪 Testes - Sistema de Ordem de Serviço

Esta pasta contém scripts e utilitários para testar o sistema.

## 📁 Arquivos

### `criar_pedidos_teste.py`

Script para popular o banco de dados com pedidos de teste.

#### 🚀 Como usar:

**Criar 6 pedidos (padrão):**
```bash
python tests/criar_pedidos_teste.py
```

**Criar quantidade personalizada:**
```bash
python tests/criar_pedidos_teste.py 10
```

**Ou usar Python 3 explicitamente:**
```bash
python3 tests/criar_pedidos_teste.py 15
```

#### 📋 O que o script faz:

- ✅ Cria pedidos com dados realistas
- 📊 Varia status: Pendente, Em Produção, Concluído, etc.
- 💰 Gera valores aleatórios entre R$ 3.000 e R$ 20.000
- 📅 Distribui datas nos últimos 30 dias
- 👥 Usa 10 clientes fictícios diferentes
- 🛠️ Usa 10 produtos diferentes
- 💳 Varia formas de pagamento

#### 🎯 Dados gerados:

**Clientes de teste:**
- Maria Silva Santos
- João Pedro Costa
- Ana Carolina Oliveira
- Carlos Eduardo Lima
- Juliana Fernandes
- Roberto Almeida Junior
- Patricia Costa Mendes
- Fernando Santos Lima
- Camila Rodrigues
- Lucas Oliveira Silva

**Produtos de teste:**
- CX7GVT 60cm Diesel
- CX8GVT 80cm Agro
- Arrasto 2m Premium
- Grade Niveladora 1.5m
- Plantadeira 4 linhas
- Carrinho Transporte
- Distribuidor de Adubo
- Pulverizador 400L
- Subsolador 3 hastes
- Cultivador 7 linhas

**Status possíveis:**
- Pendente
- Em Produção
- Aguardando Peças
- Concluído
- Cancelado

#### ⚠️ Observações:

- O banco de dados precisa existir antes de executar o script
- Execute a aplicação principal pelo menos uma vez para criar o banco
- Os pedidos são numerados sequencialmente após o último pedido existente
- Limite máximo: 50 pedidos por execução

#### 💡 Dica:

Após criar os pedidos de teste, abra a aplicação e clique no botão **"🔄 Recarregar"** na tela de Pedidos para visualizar os novos registros!

---

## 🔮 Scripts Futuros

Esta pasta pode conter:
- Testes unitários
- Testes de integração
- Scripts de migração de dados
- Scripts de limpeza do banco
- Validadores de dados
