# Sistema de Ordem de Serviço v1.0.0

Sistema completo de gerenciamento de Ordens de Serviço desenvolvido em Python com PyQt6. Interface moderna com tema escuro, gerenciamento completo de clientes, pedidos e produtos, com sistema de soft delete e backup automático.

---

## ✨ Principais Funcionalidades

### 📋 Gestão de Pedidos (Ordens de Serviço)
- ✅ **Criação e edição de pedidos** com informações completas
- ✅ **Sistema de status** personalizável (Em andamento, Concluído, Cancelado, etc.)
- ✅ **Histórico completo** de todas as ordens de serviço
- ✅ **Busca avançada** por cliente, CPF, telefone ou número da OS
- ✅ **Geração de PDF profissional** com logo e dados completos
- ✅ **Impressão direta** ou visualização do PDF
- ✅ **Numeração automática** sequencial de OS

### 👥 Gestão de Clientes
- ✅ **Cadastro completo** com CPF/CNPJ, telefone, email e endereço
- ✅ **Busca de CEP automática** via API
- ✅ **Validação de CPF/CNPJ e telefone**
- ✅ **Histórico de pedidos** por cliente
- ✅ **Visualização de compras** e informações detalhadas
- ✅ **Importação/Exportação** de dados

### 📦 Gestão de Produtos
- ✅ **Catálogo completo** de produtos e serviços
- ✅ **Categorias personalizáveis**
- ✅ **Códigos únicos** para cada produto
- ✅ **Busca rápida** por nome ou código
- ✅ **Controle de preços**
- ✅ **Sugestões inteligentes** ao digitar

### 💾 Backup e Recuperação
- ✅ **Backup automático diário** às 23h
- ✅ **Backup manual** a qualquer momento
- ✅ **Restauração de backups** anteriores
- ✅ **Soft delete** - recuperação de registros deletados em até 30 dias
- ✅ **Limpeza automática** de registros antigos
- ✅ **Visualização de registros** deletados por tipo

### 🎨 Interface Moderna
- ✅ **Tema escuro** profissional e elegante
- ✅ **Atalhos de teclado** para ações rápidas (F5, Ctrl+N, etc.)
- ✅ **Tooltips informativos** com posicionamento inteligente
- ✅ **Diálogos estilizados** com design consistente
- ✅ **Tabelas responsivas** com ordenação por coluna
- ✅ **Botões coloridos** por função (verde=sucesso, vermelho=perigo)

---

## 🚀 Como Usar

### Iniciando o Sistema
1. **Execute `main.py`** com Python 3.10+ ou use o executável
2. O sistema abrirá com 4 abas principais: **Clientes**, **Pedidos**, **Produtos** e **Backup**

### Gerenciando Clientes
1. Na aba **Clientes**, clique em **"Novo"** para cadastrar
2. Preencha os dados (CPF/CNPJ são validados automaticamente)
3. Use o botão **"Busca CEP"** para preencher endereço automaticamente
4. Clique em **"Editar"** para modificar ou **"Excluir"** para mover para lixeira
5. Use a barra de pesquisa para encontrar clientes rapidamente

### Criando Pedidos (OS)
1. Na aba **Pedidos**, clique em **"Novo Pedido"**
2. Selecione o cliente ou cadastre um novo
3. Adicione produtos/serviços ao pedido
4. Defina valores, entrada e frete
5. Escolha o status do pedido
6. Clique em **"Salvar"** para gerar o PDF automaticamente

### Gerenciando Produtos
1. Na aba **Produtos**, clique em **"Novo"** para adicionar
2. Preencha nome, preço, categoria e código
3. Use **"Editar"** para modificar ou **"Excluir"** para remover
4. A busca filtra produtos em tempo real

### Backup e Recuperação
1. Na aba **Backup**, visualize backups existentes
2. Use **"Criar Backup"** para backup manual
3. **"Restaurar"** recupera dados de um backup anterior
4. **"Registros Deletados"** mostra itens que podem ser recuperados
5. Sistema faz backup automático diário às 23h

---

## 🔧 Instalação e Execução

### Requisitos
- Python 3.10 ou superior
- Sistema operacional: Windows, Linux ou macOS

### Instalação via requirements.txt (Recomendado)
```bash
# 1. Clone ou baixe o projeto
git clone https://github.com/23Edu4rd0/Os-Project.git
cd Os-Project

# 2. Crie um ambiente virtual (recomendado)
python -m venv .venv

# 3. Ative o ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute o sistema
python main.py
```

### Instalação Manual
```bash
# Dependências principais
pip install PyQt6 PyQt6-Qt6 reportlab requests Pillow

# Execute
python main.py
```

### Gerar Executável
```bash
# Instale PyInstaller
pip install pyinstaller

# Gere o executável
pyinstaller --onefile --noconsole --icon=assets/icon.ico main.py

# O executável estará em dist/main.exe (Windows) ou dist/main (Linux)
```

---

## 🖨️ Sistema de Impressão Inteligente

O aplicativo usa um **sistema de fallback inteligente** que garante funcionamento em qualquer situação:

### Windows
1. **Tentativa 1:** Impressão direta via `pywin32` (se instalado)
2. **Tentativa 2:** Impressão via PowerShell
3. **Fallback:** Abre o PDF com programa padrão

### Linux
1. **Tentativa 1:** Impressão via `lp` (CUPS)
2. **Tentativa 2:** Impressão via `lpr`
3. **Fallback:** Abre o PDF com `xdg-open`

### Sempre Funciona
- ✅ **Botão "Abrir PDF"** sempre abre o arquivo gerado
- ✅ Mensagens informativas guiam o usuário
- ✅ Instruções alternativas em caso de problemas

---

## 📁 Estrutura do Projeto

```
Os-Project/
├── app/
│   ├── components/         # Componentes da interface
│   │   ├── clientes_manager_pyqt.py    # Gerenciamento de clientes
│   │   ├── produtos_manager.py         # Gerenciamento de produtos
│   │   └── pedidos/                    # Módulo de pedidos
│   │       ├── pedidos_interface.py    # Interface principal
│   │       ├── pedidos_card.py         # Cards de pedidos
│   │       └── pedidos_actions.py      # Ações de pedidos
│   ├── ui/                 # Interface e temas
│   │   ├── theme.py        # Tema principal
│   │   ├── theme_manager.py # Gerenciador de temas
│   │   └── backup_tab.py   # Interface de backup
│   ├── utils/              # Utilitários
│   │   ├── soft_delete.py  # Sistema de soft delete
│   │   ├── auto_backup.py  # Backup automático
│   │   ├── cep_api.py      # API de CEP
│   │   └── keyboard_shortcuts.py # Atalhos de teclado
│   └── validation/         # Validadores
│       ├── cpf_validator.py
│       ├── cnpj_validator.py
│       └── telefone_validator.py
├── database/
│   ├── core/               # Core do banco
│   │   ├── db_manager.py   # Gerenciador principal
│   │   └── db_setup.py     # Setup inicial
│   ├── crud/               # Operações CRUD
│   │   ├── order_crud.py   # CRUD de pedidos
│   │   └── products_crud.py # CRUD de produtos
│   └── ordens_servico.db   # Banco SQLite
├── documents/
│   └── os_pdf.py           # Geração de PDF (ReportLab)
├── pdfs/                   # PDFs gerados
├── assets/                 # Recursos (fontes, ícones)
├── main.py                 # Arquivo principal
├── requirements.txt        # Dependências
└── README.md               # Esta documentação
```

---

## 🛠️ Resolução de Problemas

### Falha de Segmentação (Segfault) ao Fechar
- ✅ **Corrigido na versão atual** - event filter removido corretamente
- ✅ Se persistir, use `Ctrl+C` no terminal para forçar fechamento

### Erro ao Importar PyQt6
- ✅ Certifique-se de estar no ambiente virtual: `source .venv/bin/activate`
- ✅ Reinstale: `pip install --upgrade PyQt6`

### PDF não é gerado
- ✅ Verifique se a pasta `pdfs/` existe
- ✅ Confirme permissões de escrita
- ✅ Veja o log de erros no terminal

### Cliente/Produto não aparece na busca
- ✅ Verifique se não foi deletado (vá em Backup → Registros Deletados)
- ✅ Use o botão "Recarregar" (F5) para atualizar

### Erro de banco de dados
- ✅ Faça backup antes de qualquer correção
- ✅ Use Backup → Restaurar para voltar a um ponto anterior
- ✅ Se necessário, delete `database/ordens_servico.db` (perda de dados!)

---

## 📋 Dependências Principais

### Essenciais
- `PyQt6` >= 6.4.0 - Framework de interface gráfica
- `reportlab` >= 4.0.0 - Geração de PDFs
- `requests` >= 2.31.0 - Requisições HTTP (CEP API)
- `Pillow` >= 10.0.0 - Processamento de imagens

### Incluídas no Python
- `sqlite3` - Banco de dados
- `logging` - Sistema de logs
- `json` - Manipulação de JSON
- `datetime` - Manipulação de datas

---

## 💡 Dicas e Atalhos

### Atalhos de Teclado
- **F5** - Recarregar dados
- **Ctrl+N** - Novo registro (depende da aba)
- **Ctrl+E** - Editar selecionado
- **Delete** - Excluir selecionado
- **Ctrl+F** - Focar na busca
- **ESC** - Fechar diálogos

### Boas Práticas
1. **Faça backups regulares** - Use o backup manual antes de mudanças grandes
2. **Use soft delete** - Itens deletados podem ser recuperados em 30 dias
3. **Organize categorias** - Mantenha produtos bem categorizados
4. **Preencha endereços** - Use busca de CEP para dados corretos
5. **Revise antes de salvar** - Validações ajudam, mas revise informações importantes
6. **Mantenha backups externos** - Copie a pasta `database/` periodicamente

### Recursos Avançados
- **Exportação de dados** - Exporte clientes para CSV/Excel
- **Filtros de status** - Filtre pedidos por status na aba Pedidos
- **Ordenação de tabelas** - Clique nos cabeçalhos para ordenar
- **Recuperação seletiva** - Recupere apenas os registros necessários da lixeira

---

## 🤝 Contribuindo

Este é um projeto privado, mas sugestões são bem-vindas:
1. Abra uma issue descrevendo o problema ou sugestão
2. Se for um bug, inclua prints e logs
3. Para novas funcionalidades, descreva o caso de uso

---

## 📝 Licença

Este projeto é proprietário e desenvolvido para uso interno.

---

## 📧 Contato

**Desenvolvido por:** Eduardo  
**Para:** Merkava Ferramentas 🔧  
**Versão:** 1.0.0  
**Ano:** 2025
