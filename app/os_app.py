""" Pega as informações do cliente e produto, gerando um PDF com os dados

    Returns:
        PDF : Dados do cliente e do produto
"""

import ttkbootstrap as tb
from tkinter import messagebox
import os  # Adicionar import os
import platform  # Added import platform
# Certifique-se que o nome da classe está correto
from documents.os_pdf import OrdemServicoPDF
from app.numero_os import Contador
# Renomear para evitar conflito
from services.impress import imprimir_pdf as imprimir_pdf_service
from ttkbootstrap.constants import PRIMARY
from app.impressApp import ImpressApp

# It's good practice to handle platform-specific imports gracefully
try:
    if platform.system() == "Windows":
        import win32print
except ImportError:
    win32print = None  # Define it as None if import fails


class OrdemServicoApp:
    """
    Classe principal da aplicação de Ordem de Serviço.
    Responsável por criar a interface gráfica, coletar e validar dados,
    gerar PDF, imprimir e selecionar impressora.
    """
    def __init__(self, root):
        """
        Inicializa a interface gráfica principal da Ordem de Serviço.
        Configura todos os widgets, menus e dicas de preenchimento.
        """
        self.root = root
        self.root.title("Ordem de Serviço")
        self.root.geometry("500x600")
        self.root.minsize(300, 700)
        self.numero_os = Contador.ler_contador()
        self.arquivo_pdf = "ordem_servico.pdf"  # Nome do arquivo PDF gerado
        self.impressora_padrao = None  # Impressora padrão selecionada
        self.impressora_menu = ImpressApp(self.root)

        # Parâmetros base para ajuste dinâmico de fonte/layout
        self.base_width = 800
        self.base_height = 600
        self.base_font_size = 11
        self.base_font_size_label = 11

        # Layout: labels acima, campos ocupando toda a largura
        row = 0
        # OS Number Display
        os_frame = tb.Frame(root)
        os_frame.grid(row=row, column=0, columnspan=2, padx=30,
                      pady=(10, 5), sticky="ew")

        tb.Label(
            os_frame, text="Nº OS:", font=("Montserrat", 12, "bold")
        ).pack(side="left", padx=(0, 5))
        self.numero_os_label = tb.Label(
            os_frame, text=str(self.numero_os),
            font=("Montserrat", 12, "bold"), bootstyle="PRIMARY"
        )
        self.numero_os_label.pack(side="left")

        # Botões para aumentar/diminuir o número da OS
        btn_diminuir_os = tb.Button(
            os_frame, text="-", command=self.diminuir_os, width=3,
            bootstyle="secondary"
        )
        # Botão para diminuir o número da OS
        btn_diminuir_os.pack(
            side="left", padx=(10, 2), ipady=5  # Espaçamento e altura
        )
        btn_aumentar_os = tb.Button(
            os_frame, text="+", command=self.aumentar_os, width=3,
            bootstyle="secondary"
        )
        # Botão para aumentar o número da OS
        btn_aumentar_os.pack(
            side="left", padx=(0, 10), ipady=5  # Espaçamento e altura
        )

        row += 1  # Próxima linha após exibir o número da OS
        tb.Label(root, text="Nome do Cliente:", font=("Montserrat", 12)).grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(5, 5), sticky="w"  # Espaçamento superior/inferior
        )
        row += 1
        self.nome_cliente_entry = tb.Entry(root, font=("Montserrat", 12))
        self.nome_cliente_entry.grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(0, 15), sticky="ew"
        )
        row += 1
        tb.Label(root, text="CPF:", font=("Montserrat", 12)).grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(0, 5), sticky="w"
        )
        row += 1
        self.cpf_entry = tb.Entry(root, font=("Montserrat", 12))
        self.cpf_entry.grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(0, 15), sticky="ew"
        )
        row += 1
        tb.Label(root, text="Telefone:", font=("Montserrat", 12)).grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(0, 5), sticky="w"
        )
        row += 1
        self.telefone_entry = tb.Entry(root, font=("Montserrat", 12))
        self.telefone_entry.grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(0, 15), sticky="ew"
        )
        row += 1
        tb.Label(root, text="Detalhes do Produto/Serviço:",
                 font=("Montserrat", 12)).grid(
            row=row, column=0, columnspan=2, padx=30, pady=(0, 5), sticky="w"
        )
        row += 1
        self.detalhes_text = tb.Text(root, height=4,
                                     font=("Montserrat", 12), wrap="word")
        self.detalhes_text.grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(0, 0), sticky="ew"  # Sem espaçamento inferior extra
        )
        row += 1
        tb.Label(root, text="Valor Estimado:", font=("Montserrat", 12)).grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(5, 5), sticky="w"  # Espaçamento superior/inferior
        )
        row += 1
        self.valor_entry = tb.Entry(root, font=("Montserrat", 12))
        self.valor_entry.grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(0, 0), sticky="ew"
        )
        row += 1
        tb.Label(root, text="Forma de Pagamento:",
                 font=("Montserrat", 12)).grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(5, 5), sticky="w"
        )
        row += 1
        self.pagamento_combo = tb.Combobox(
            root, values=["Pix", "Crédito", "Débito", "Dinheiro"],
            font=("Montserrat", 12)
        )
        self.pagamento_combo.grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(0, 0), sticky="ew"
        )
        row += 1
        tb.Label(root, text="Prazo (dias):", font=("Montserrat", 12)).grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(5, 5), sticky="w"
        )
        row += 1
        self.prazo_entry = tb.Entry(root, font=("Montserrat", 12))
        self.prazo_entry.grid(
            row=row, column=0, columnspan=2, padx=30,
            pady=(0, 20), sticky="ew"
        )
        row += 1
        self.gerar_pdf_btn = tb.Button(
            root, text="Gerar PDF", bootstyle=PRIMARY, width=20,
            command=self.gerar_pdf  # Largura aumentada
        )
        self.gerar_pdf_btn.grid(
            row=row, column=0, padx=(30, 10), pady=(10, 30),
            sticky="ew", ipady=5  # Altura aumentada
        )

        self.imprimir_btn = tb.Button(
            root, text="Imprimir PDF", bootstyle=PRIMARY, width=20,
            command=self.imprimir_pdf  # Largura aumentada
        )
        self.imprimir_btn.grid(
            row=row, column=1, padx=(10, 30), pady=(10, 30),
            sticky="ew", ipady=5  # Altura aumentada
        )
        # Menu principal
        menu_bar = tb.Menu(root)
        root.config(menu=menu_bar)
        arquivo_menu = tb.Menu(menu_bar, tearoff=0)
        arquivo_menu.add_command(label="Sair", command=root.quit)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)
        ajuda_menu = tb.Menu(menu_bar, tearoff=0)
        ajuda_menu.add_command(label="Sobre", command=self.mostrar_sobre)
        menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)
        impressora_menu = tb.Menu(menu_bar, tearoff=0)
        impressora_menu.add_command(
            label="Selecionar Impressora",
            command=self.impressora_menu.selecionar_impressora
        )
        menu_bar.add_cascade(label="Impressora", menu=impressora_menu)

        # Lista de widgets para ajuste dinâmico de fonte
        self.widgets_to_resize = [
            self.nome_cliente_entry, self.cpf_entry, self.telefone_entry,
            self.detalhes_text, self.valor_entry, self.pagamento_combo,
            self.prazo_entry, self.gerar_pdf_btn, self.imprimir_btn,
            self.numero_os_label
        ]
        # Ajuste dinâmico de fonte ao redimensionar a janela
        self.root.bind('<Configure>', self._ajustar_fontes)
        # Expansão automática das linhas e colunas
        for i in range(row + 1):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(2):
            self.root.grid_columnconfigure(j, weight=1)
        # Dicas de preenchimento (placeholders) para os campos
        self.add_placeholder(
            self.nome_cliente_entry, "Digite o nome do cliente"
        )
        self.add_placeholder(
            self.cpf_entry, "Somente números, 11 dígitos"
        )
        self.add_placeholder(
            self.telefone_entry, "Ex: 37999999999"
        )
        self.add_placeholder(
            self.valor_entry, "Ex: 100,00"
        )
        self.add_placeholder(
            self.prazo_entry,
            "Insira o número de dias. Ex: 30 -> daqui a 30 dias"
        )
        # Navegação entre campos com Enter
        self.nome_cliente_entry.bind(
            "<Return>", lambda e: self.cpf_entry.focus_set()
        )
        self.cpf_entry.bind(
            "<Return>", lambda e: self.telefone_entry.focus_set()
        )
        self.telefone_entry.bind(
            "<Return>", lambda e: self.detalhes_text.focus_set()
        )
        self.detalhes_text.bind(
            "<Return>", lambda e: (self.valor_entry.focus_set(), "break")[1]
        )
        self.valor_entry.bind(
            "<Return>", lambda e: self.pagamento_combo.focus_set()
        )
        self.pagamento_combo.bind(
            "<Return>", lambda e: self.prazo_entry.focus_set()
        )
        self.prazo_entry.bind(
            "<Return>", lambda e: self.gerar_pdf_btn.focus_set()
        )

        def open_combo_options(event):
            self.pagamento_combo.event_generate('<Down>')

        def on_combo_selected(event):
            self.prazo_entry.focus_set()
        self.pagamento_combo.bind("<Return>", open_combo_options)
        self.pagamento_combo.bind("<<ComboboxSelected>>", on_combo_selected)

    def add_placeholder(self, entry, placeholder_text):
        """
        Adiciona uma dica de preenchimento (placeholder) ao campo Entry.
        O texto aparece em cinza e some ao focar no campo.
        """
        entry.insert(0, placeholder_text)
        entry.config(foreground='grey')

        def on_focus_in(event):
            if entry.get() == placeholder_text:
                entry.delete(0, 'end')
                entry.config(foreground='white')  # Mantém branco ao digitar

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder_text)
                entry.config(foreground='grey')

        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

    def diminuir_os(self):
        """
        Diminui o número da OS, atualizando o contador e o rótulo.
        Não permite valores menores que 1.
        """
        atual = Contador.ler_contador()
        if atual > 1:
            novo_valor = atual - 1
            Contador.salvar_contador(novo_valor)
            self.numero_os = novo_valor
            self.numero_os_label.config(text=str(self.numero_os))
        else:
            messagebox.showwarning(
                "Aviso",
                "Não é possível diminuir o número da OS abaixo de 1."
            )

    def aumentar_os(self):
        """
        Aumenta o número da OS, atualizando o contador e o rótulo.
        """
        atual = Contador.ler_contador()
        novo_valor = atual + 1
        Contador.salvar_contador(novo_valor)
        self.numero_os = novo_valor
        self.numero_os_label.config(text=str(self.numero_os))

    def coletar_dados(self):
        """
        Coleta os dados dos campos da interface e retorna um dicionário.
        Placeholders e campos vazios são tratados como string vazia ou None.
        """
        dados = {}
        dados["numero_os"] = self.numero_os_label['text']

        # Nome Cliente
        nome_cliente = self.nome_cliente_entry.get().strip()
        if nome_cliente == "Digite o nome do cliente":
            nome_cliente = ""
        dados["nome_cliente"] = nome_cliente

        # CPF Cliente
        cpf_cliente = self.cpf_entry.get().strip()
        if cpf_cliente == "Somente números, 11 dígitos":
            cpf_cliente = ""
        dados["cpf_cliente"] = cpf_cliente

        # Telefone Cliente
        telefone_cliente = self.telefone_entry.get().strip()
        if telefone_cliente == "Ex: 37999999999":
            telefone_cliente = ""
        dados["telefone_cliente"] = telefone_cliente

        # Detalhes Produto
        detalhes_produto = self.detalhes_text.get("1.0", "end-1c").strip()
        dados["detalhes_produto"] = detalhes_produto

        # Valor Estimado
        valor_str = self.valor_entry.get().strip()
        if valor_str == "Ex: 100,00" or not valor_str:
            valor_estimado = None
        else:
            try:
                valor_estimado = float(valor_str.replace(',', '.'))
            except ValueError:
                valor_estimado = None
        dados["valor_estimado"] = valor_estimado

        # Forma de Pagamento
        forma_pagamento = self.pagamento_combo.get().strip()
        dados["forma_pagamento"] = forma_pagamento

        # Prazo
        prazo_str = self.prazo_entry.get().strip()
        placeholder_prazo = ("Insira o numero de dias. "
                             "Ex: 30 -> daqui a 30 dias")
        if prazo_str == placeholder_prazo or not prazo_str:
            prazo = None
        else:
            try:
                prazo = int(prazo_str)
            except ValueError:
                prazo = None
        dados["prazo"] = prazo

        return dados

    def validar_dados(self, dados: dict):
        """
        Valida os dados coletados dos campos.
        Exibe mensagens de erro se algum campo estiver inválido.
        """
        if (len(dados["cpf_cliente"]) != 11 or
                not dados["cpf_cliente"].isdigit()):
            messagebox.showerror(
                "Erro",
                "CPF inválido. Insira somente números e 11 dígitos."
            )
            return False
        if dados["valor_estimado"] is None or dados["valor_estimado"] <= 0:
            messagebox.showerror(
                "Erro",
                "Valor estimado inválido. Insira um valor valido."
            )
            return False
        if dados["prazo"] is None or dados["prazo"] <= 0:
            messagebox.showerror(
                "Erro",
                "Prazo inválido. Insira um número inteiro positivo."
            )
            return False
        if not all([
            dados["numero_os"],
            dados["nome_cliente"],
            dados["cpf_cliente"],
            dados["telefone_cliente"],
            dados["detalhes_produto"],
            dados["valor_estimado"],
            dados["forma_pagamento"]
        ]):
            messagebox.showerror(
                "Erro",
                "Todos os campos devem ser preenchidos."
            )
            return False
        return True

    def gerar_pdf(self):
        """
        Gera o PDF da Ordem de Serviço com os dados coletados e validados.
        Atualiza o número da OS após gerar o PDF.
        """
        dados = self.coletar_dados()

        # Define fields to check for the "all empty" condition
        campos_chave_formulario = [
            "nome_cliente", "cpf_cliente", "telefone_cliente",
            "detalhes_produto", "valor_estimado", "forma_pagamento", "prazo"
        ]

        # Check if all relevant fields are effectively empty
        if not any(dados.get(key) for key in campos_chave_formulario):
            messagebox.showerror(
                "Erro",
                ("Todos os campos estão vazios.\\n"
                 "Por favor, preencha os dados para gerar a OS.")
            )
            return

        # If we are here, at least one field was filled.
        # Now, apply default for prazo if it was left empty by the user.
        if dados["prazo"] is None:
            dados["prazo"] = 30  # Default prazo

        # Now, validate the (potentially modified) data
        if not self.validar_dados(dados):
            # validar_dados already shows specific error messages
            return

        try:
            # O número da OS já deve estar nos dados coletados do label
            numero_os_str = dados.get("numero_os")
            if not numero_os_str or not numero_os_str.isdigit():
                messagebox.showerror("Erro", "Número da OS inválido.")
                return

            numero_os = int(numero_os_str)

            pdf = OrdemServicoPDF(dados, self.arquivo_pdf)
            pdf.gerar()

            # Salva o número da OS que foi usada
            Contador.salvar_contador(numero_os)

            # Atualiza o label para o próximo número disponível
            proximo_numero_os = Contador.ler_contador()  # Lê o próximo número
            if hasattr(self, 'numero_os_label') and self.numero_os_label:
                self.numero_os_label.config(text=str(proximo_numero_os))

            messagebox.showinfo(
                "Sucesso",
                f"PDF da OS Nº {numero_os} gerado com sucesso!"
            )

        except Exception as e:
            messagebox.showerror(
                "Erro ao Gerar PDF",
                f"Ocorreu um erro inesperado: {e}"
            )

    def imprimir_pdf(self):
        """
        Envia o PDF gerado para a impressora padrão selecionada.
        Exibe mensagens de sucesso ou erro conforme o resultado.
        """
        if not os.path.exists(self.arquivo_pdf):
            messagebox.showerror(
                "Erro de Impressão",
                (f"O arquivo '{self.arquivo_pdf}' não foi encontrado.\\n"
                 "Por favor, gere o PDF primeiro.")
            )
            return

        try:
            # Chama a função de impressão do módulo de serviço
            # A função imprimir_pdf_service deve retornar uma tupla
            # (bool_sucesso, mensagem_string)
            sucesso, mensagem = imprimir_pdf_service(
                self.arquivo_pdf, self.impressora_padrao
            )
            if sucesso:
                messagebox.showinfo("Impressão", mensagem)
            else:
                messagebox.showerror("Erro de Impressão", mensagem)
        except Exception as e:
            messagebox.showerror(
                "Erro ao Imprimir",
                (
                    f"Ocorreu um erro inesperado durante a tentativa de "
                    f"impressão: {e}"
                )
            )

    def mostrar_sobre(self):
        """
        Exibe informações sobre o aplicativo.
        """
        messagebox.showinfo(
            "Sobre",
            "Aplicação de Ordem de Serviço v1.3\nDesenvolvido por Eduardo\n"
        )

    def _ajustar_fontes(self, event):
        """
        Ajusta o tamanho das fontes dos widgets principais conforme o tamanho
        da janela, mantendo a responsividade da interface.
        """
        # Ajuste de fonte proporcional ao tamanho da janela
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        fator = min(largura / self.base_width, altura / self.base_height)
        tamanho_base = 12
        tamanho = max(int(tamanho_base * fator), 10)
        for widget in self.widgets_to_resize:
            try:
                widget.config(font=("Montserrat", tamanho))
            except Exception:
                pass
