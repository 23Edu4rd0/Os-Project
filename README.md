# Projeto Ordem de Serviço - Merkava Ferramentas

Este é um aplicativo desktop para geração e gerenciamento de Ordens de Serviço, desenvolvido em Python com interface gráfica moderna (ttkbootstrap). O aplicativo **funciona independentemente** de ter aplicativos de impressão específicos instalados e **mantém histórico de todas as ordens** para consulta e reimpressão!

---

## ✨ Principais Funcionalidades

- ✅ **Histórico completo de ordens** - salva todas as ordens para consulta e reimpressão posterior
- ✅ **Gerenciador de OS anteriores** - pesquisa por número ou nome do cliente
- ✅ **PDF com nome único** - arquivos salvos com nome do cliente e data em pasta organizada
- ✅ **Banco de dados integrado** - armazena dados completos de todas as ordens anteriores
- ✅ **Navegação facilitada** - menu de histórico com últimas 10 ordens geradas
- ✅ **Funciona sem dependências de impressão** - o app sempre abrirá e funcionará
- ✅ **Geração de PDF profissional** com dados completos da OS
- ✅ **Impressão inteligente** - tenta imprimir diretamente, se não conseguir, abre o PDF para impressão manual
- ✅ **Botão "Abrir PDF"** - sempre funciona, independente da impressora
- ✅ **Interface moderna e responsiva** com ttkbootstrap
- ✅ **Campos separados** para valor do produto, entrada e frete
- ✅ **Cálculo automático** do valor restante no PDF
- ✅ **Múltiplos tamanhos de PDF** (pequeno/grande) via menu

---

## 🚀 Como usar (Cliente)

1. **Execute `main.py`** ou o executável para iniciar o programa
2. **Preencha os campos** solicitados na interface
3. **Clique em "Gerar PDF"** para criar a ordem de serviço
4. **Para imprimir:**
   - **"Imprimir PDF"**: Tenta imprimir automaticamente ou abre o arquivo
   - **"Abrir PDF"**: Sempre funciona, abre o PDF para impressão manual (Ctrl+P)
5. **Para recuperar ordens anteriores:**
   - **Menu "Arquivo" -> "Gerenciar Ordens Anteriores"**: Abre o gerenciador completo
   - **Menu "Arquivo" -> "Buscar por Número de OS"**: Busca direta por número
   - **Menu "Histórico"**: Mostra as últimas 10 ordens geradas
6. **No gerenciador de ordens:**
   - Pesquise por nome do cliente ou número da OS
   - Selecione uma ordem e use os botões para carregar, abrir ou imprimir

---

## 🔧 Instalação e Execução

### Método 1: Execução Simples (Recomendado)
```bash
# 1. Instalar dependências principais
pip install reportlab ttkbootstrap

# 2. Executar o aplicativo
python main.py
```

### Método 2: Instalação Completa
```bash
# 1. Instalar todas as dependências
pip install -r requirements.txt

# 2. (Opcional) Para melhor suporte à impressão no Windows
pip install pywin32

# 3. Executar
python main.py
```

### Método 3: Gerar Executável
```bash
# 1. Instalar PyInstaller
pip install pyinstaller

# 2. Gerar executável
pyinstaller --onefile --noconsole main.py
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
│   ├── os_app.py           # Interface principal (ttkbootstrap)
│   ├── numero_os.py        # Controle numeração automática
│   └── impressApp.py       # Seleção de impressora
├── assets/
│   ├── Montserrat-Regular.ttf
│   └── Montserrat-Bold.ttf
├── database/
│   ├── __init__.py
│   └── db_manager.py       # Gerenciador do banco de dados SQLite
├── documents/
│   └── os_pdf.py           # Geração PDF (ReportLab)
├── pdfs/                   # Pasta onde os PDFs são salvos
│   └── [PDFs gerados]      # Organizados por cliente e data 
├── services/
│   └── impress.py          # Sistema de impressão inteligente
├── main.py                 # Arquivo principal
├── requirements.txt        # Dependências
└── README.md               # Esta documentação
```

---

## 🛠️ Resolução de Problemas

### "O app não imprime"
- ✅ **Use o botão "Abrir PDF"** - sempre funciona
- ✅ No arquivo aberto, use **Ctrl+P** para imprimir
- ✅ Verifique se há impressoras instaladas no sistema

### "Erro de biblioteca não encontrada"
- ✅ **O app ainda funcionará** - apenas a impressão direta pode falhar
- ✅ Use **"Abrir PDF"** como alternativa
- ✅ Para melhor experiência: `pip install pywin32` (Windows)

### "PDF não abre"
- ✅ Instale um leitor de PDF (Adobe Reader, SumatraPDF, etc.)
- ✅ O arquivo PDF fica salvo na pasta do programa

---

## 📋 Dependências

### Obrigatórias (sempre necessárias)
- `reportlab` - Geração de PDF
- `ttkbootstrap` - Interface moderna
- `sqlite3` - Banco de dados (incluído na biblioteca padrão Python)

### Opcionais (melhoram a experiência)
- `pywin32` - Impressão direta no Windows
- `cups` - Impressão no Linux (sudo apt install cups)

---

## 💡 Dicas de Uso

1. **Recuperação de ordens:** Menu Histórico mostra últimas 10 ordens geradas
2. **Busca rápida:** Arquivo → Buscar por Número de OS para acesso direto
3. **Gerenciador completo:** Arquivo → Gerenciar Ordens Anteriores para pesquisa avançada 
4. **Reimpressão facilitada:** Carregue uma OS antiga e clique em Imprimir PDF
5. **Arquivos organizados:** PDFs salvos na pasta "pdfs" com nome do cliente e data
6. **Sempre funciona:** Mesmo sem impressoras, use "Abrir PDF" → Ctrl+P
7. **Múltiplos tamanhos:** Menu → Tamanho do PDF → Pequeno/Grande
8. **Campos inteligentes:** Placeholders mostram exemplos de preenchimento
9. **Cálculo automático:** Valor restante = (Produto + Frete) - Entrada

---

**Desenvolvido para Merkava Ferramentas** 🔧
