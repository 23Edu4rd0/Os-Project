# Projeto Ordem de Serviço - Shayder

Este é um aplicativo desktop para geração e gerenciamento de Ordens de Serviço, desenvolvido em Python com interface gráfica (Tkinter).

---

## Como usar (Cliente)

1. **Abra o arquivo `main.exe`** (enviado para você) para iniciar o programa.
2. **Preencha os campos** solicitados na tela.
3. **Gere e salve a Ordem de Serviço** conforme instruções do aplicativo.
4. O PDF gerado será salvo na mesma pasta onde o programa foi executado, a menos que especificado de outra forma.

---

## Como rodar (Desenvolvedor)

1. **Pré-requisitos**
   - Python 3.x instalado
   - Instalar dependências:

     ```bash
     pip install -r requirements.txt
     ```

   - (Opcional) Instalar o PyInstaller para gerar o executável:

     ```bash
     pip install pyinstaller
     ```

2. **Executar o app**

   ```bash
   python main.py
   ```

3. **Gerar o executável**

   ```bash
   pyinstaller --onefile --noconsole --icon=assets/icons8-o-um-anel-40.ico main.py
   ```

   O executável será criado na pasta `dist`.

---

## Estrutura do Projeto

```
Os-Project/
├── app/
│   ├── __init__.py
│   ├── os_app.py           # Interface principal (Tkinter/ttkbootstrap)
│   ├── numero_os.py        # Controle do número da OS
│   ├── impressApp.py       # Seleção de impressora (GUI)
├── assets/
│   ├── Montserrat-Regular.ttf
│   ├── Montserrat-Bold.ttf
├── documents/
│   ├── __init__.py
│   ├── os_pdf.py           # Geração do PDF da OS (ReportLab)
├── services/
│   ├── __init__.py
│   ├── impress.py          # Função para impressão cross-platform
├── main.py                 # Arquivo principal para iniciar o app
├── requirements.txt        # Dependências do projeto
└── README.md               # Documentação do projeto
```

---

## Observações

- O ícone do app pode ser alterado trocando o arquivo `.ico` em `assets/` e ajustando o caminho em `main.py`.
- O app não cria a pasta `__pycache__` no executável.
- Para suporte ou dúvidas, entre em contato com o desenvolvedor.
