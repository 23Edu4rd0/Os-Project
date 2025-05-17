""" Pega as informações do cliente e produto, gerando um PDF com os dados

    Returns:
        PDF : Dados do cliente e do produto
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime, timedelta
from tkinter import messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from impress import imprimir_pdf
from numero_os import Contador
import platform

class OrdemServicoPDF:
    def __init__(self, dados, arquivo_pdf="ordem_servico.pdf"):
        self.dados = dados
        self.arquivo_pdf = arquivo_pdf

    def gerar(self):
        numero_os = self.dados["numero_os"]
        nome_cliente = self.dados["nome_cliente"]
        cpf_cliente = self.dados["cpf_cliente"]
        telefone_cliente = self.dados["telefone_cliente"]
        detalhes_produto = self.dados["detalhes_produto"]
        valor_estimado = self.dados["valor_estimado"]
        forma_pagamento = self.dados["forma_pagamento"]
        prazo = self.dados["prazo"]

        data_e_hora_atuais = datetime.now()
        data_e_hora_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
        data_de_entrega = data_e_hora_atuais + timedelta(days=prazo)
        data_de_entrega = data_de_entrega.strftime('%d/%m/%Y')

        c = canvas.Canvas(self.arquivo_pdf, pagesize=(80 * mm, 250 * mm))
        width, height = 80 * mm, 250 * mm

        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2, height - 20, "OuriPrata - Ourivesaria")
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, height - 30, "Av. 1° de Junho, 411 - 501 - Centro - Divinópolis - MG")
        c.drawCentredString(width / 2, height - 40, "Tel: (37) 9862-3061")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, height - 70, f"NÚMERO DA OS: {numero_os}")
        c.line(10, height - 75, width - 10, height - 75)  # Linha separadora

        # Ajusta o espaçamento para 10 px
        y_position = height - 85

        c.setFont("Helvetica", 9)
        c.drawString(10, y_position, f"Data de Emissão: {data_e_hora_texto}")
        y_position -= 20  # Espaçamento ajustado para 20 px

        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y_position, "DADOS DO CLIENTE")
        c.line(10, y_position - 5, width - 10, y_position - 5)  # Linha separadora
        y_position -= 20  # Espaçamento ajustado para 20 px

        c.setFont("Helvetica", 9)
        c.drawString(10, y_position, f'Nome: {nome_cliente}')
        y_position -= 15  # Espaçamento ajustado para 15 px
        c.drawString(10, y_position, f'CPF: {cpf_cliente}')
        y_position -= 15  # Espaçamento ajustado para 15 px
        c.drawString(10, y_position, f'Telefone: {telefone_cliente}')
        y_position -= 25  # Espaçamento ajustado para 25 px

        # Adiciona o título "DETALHES DO PRODUTO"
        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y_position, "DETALHES DO PRODUTO")
        c.line(10, y_position - 5, width - 10, y_position - 5)  # Linha separadora
        y_position -= 20  # Espaçamento ajustado para 20 px

        # Adiciona os detalhes do produto
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = "Helvetica"
        style.fontSize = 9
        style.leading = 12

        detalhes_paragraph = Paragraph(detalhes_produto, style)
        text_width = width - 20
        _, h = detalhes_paragraph.wrap(text_width, y_position)
        detalhes_paragraph.drawOn(c, 10, y_position - h)
        y_position -= h + 25  # Espaçamento ajustado após os detalhes do produto

        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y_position, "ORÇAMENTO")
        c.line(10, y_position - 5, width - 10, y_position - 5)  # Linha separadora
        y_position -= 20
        c.setFont("Helvetica", 9)
        c.drawString(10, y_position, f'Valor estimado: R$ {valor_estimado:.2f}')
        y_position -= 15
        c.drawString(10, y_position, f'Forma de pagamento: {forma_pagamento}')
        y_position -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y_position, "DATA DE ENTREGA")
        c.line(10, y_position - 5, width - 10, y_position - 5)  # Linha separadora
        y_position -= 20
        c.setFont("Helvetica", 9)
        c.drawString(10, y_position, f'Prazo estimado para entrega: {data_de_entrega}')
        y_position -= 15

        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y_position, "TERMOS E CONDIÇÕES")
        c.line(10, y_position - 5, width - 10, y_position - 5)  # Linha separadora
        y_position -= 15

        termos_condicoes = """
        1. Valor pode variar conforme material e complexidade do serviço.<br/>
        2. Prazos podem mudar por aprovação ou falta de material.<br/>
        3. Alterações após início implicam novo prazo e valor.<br/>
        4. Entrega só é válida com este documento.
        """
        termos_paragraph = Paragraph(termos_condicoes, style)
        w, h = termos_paragraph.wrap(text_width, y_position)
        termos_paragraph.drawOn(c, 10, y_position - h)
        y_position -= h
        y_position -= 20

        c.showPage()
        c.save()

class OrdemServicoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ordem de Serviço")
        self.root.geometry("700x500")
        self.root.minsize(500, 400)
        self.numero_os = Contador.ler_contador()
        self.arquivo_pdf = "ordem_servico.pdf"

        # Centralizar a janela na tela
        largura_janela = 700
        altura_janela = 500
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela - largura_janela) // 2
        pos_y = (altura_tela - altura_janela) // 2
        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        # Configuração da interface
        tb.Label(root, text="Número da OS:").grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.numero_os_label = tb.Label(root, text=str(self.numero_os), anchor='center')
        self.numero_os_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.botao_diminuir_os = tb.Button(root, text="-", width=3, command=self.diminuir_os)
        self.botao_diminuir_os.grid(row=0, column=2, padx=2, pady=5, sticky="ew")

        self.botao_aumentar_os = tb.Button(root, text="+", width=3, command=self.aumentar_os)
        self.botao_aumentar_os.grid(row=0, column=3, padx=(2, 10), pady=5, sticky="ew")

        # Configuração de outros campos
        tb.Label(root, text="Nome do Cliente:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.nome_cliente_entry = tb.Entry(root)
        self.nome_cliente_entry.grid(row=1, column=1, columnspan=3, padx=10, pady=5, sticky="ew")

        tb.Label(root, text="CPF do Cliente:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.cpf_cliente_entry = tb.Entry(root)
        self.cpf_cliente_entry.grid(row=2, column=1, columnspan=3, padx=10, pady=5, sticky="ew")

        tb.Label(root, text="Telefone do Cliente:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.telefone_cliente_entry = tb.Entry(root)
        self.telefone_cliente_entry.grid(row=3, column=1, columnspan=3, padx=10, pady=5, sticky="ew")

        tb.Label(root, text="Detalhes do Produto:", font=("Helvetica", 9)).grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        self.detalhes_produto_text = tb.Text(root, height=4, wrap="word")
        self.detalhes_produto_text.grid(row=4, column=1, columnspan=3, padx=10, pady=5, sticky="nsew")

        tb.Label(root, text="Valor Estimado:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.valor_estimado_entry = tb.Entry(root)
        self.valor_estimado_entry.grid(row=5, column=1, columnspan=3, padx=10, pady=5, sticky="ew")

        tb.Label(root, text="Forma de Pagamento:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.pagamento_combobox = tb.Combobox(
            root, 
            values=["Pix", "Crédito", "Débito", "Dinheiro Físico"], 
            state="readonly"
        )
        self.pagamento_combobox.grid(row=6, column=1, columnspan=3, padx=10, pady=5, sticky="ew")

        tb.Label(root, text="Prazo de Entrega (dias):").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.prazo_entry = tb.Entry(root)
        self.prazo_entry.grid(row=7, column=1, columnspan=3, padx=10, pady=5, sticky="ew")

        self.gerar_pdf_button = tb.Button(root, text="Gerar PDF", command=self.gerar_pdf, bootstyle=PRIMARY)
        self.gerar_pdf_button.grid(row=8, column=0, padx=(10, 5), pady=10, sticky="ew")

        self.imprimir_pdf_button = tb.Button(root, text="Imprimir PDF", command=self.imprimir_pdf, bootstyle=PRIMARY)
        self.imprimir_pdf_button.grid(row=8, column=1, columnspan=3, padx=(5, 10), pady=10, sticky="ew")

        # Exemplo para os campos principais:
        self.nome_cliente_entry.bind("<Return>", lambda e: self.cpf_cliente_entry.focus_set())
        self.cpf_cliente_entry.bind("<Return>", lambda e: self.telefone_cliente_entry.focus_set())
        self.telefone_cliente_entry.bind("<Return>", lambda e: self.detalhes_produto_text.focus_set())
        self.detalhes_produto_text.bind("<Return>", lambda e: (self.valor_estimado_entry.focus_set(), "break")[1])  # Para Text, precisa retornar "break"
        self.valor_estimado_entry.bind("<Return>", lambda e: self.pagamento_combobox.focus_set())
        self.pagamento_combobox.bind("<Return>", lambda e: self.prazo_entry.focus_set())
        self.prazo_entry.bind("<Return>", lambda e: self.gerar_pdf_button.focus_set())

        # Configuração de layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)

        for i in range(12):
            self.root.grid_rowconfigure(i, weight=1)

        # Adiciona o menu
        menu_bar = tb.Menu(root)
        root.config(menu=menu_bar)

        arquivo_menu = tb.Menu(menu_bar, tearoff=0)
        arquivo_menu.add_command(label="Sair", command=root.quit)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)

        ajuda_menu = tb.Menu(menu_bar, tearoff=0)
        ajuda_menu.add_command(label="Sobre", command=self.mostrar_sobre)
        menu_bar.add_cascade(label="Ajuda", menu=ajuda_menu)

        impressora_menu = tb.Menu(menu_bar, tearoff=0)
        impressora_menu.add_command(label="Selecionar Impressora", command=self.selecionar_impressora)
        menu_bar.add_cascade(label="Impressora", menu=impressora_menu)

    def diminuir_os(self):
        atual = Contador.ler_contador()
        if atual > 0:
            novo_valor = atual - 1
            Contador.salvar_contador(novo_valor)
            self.numero_os = novo_valor
            self.numero_os_label.config(text=str(self.numero_os))
            messagebox.showinfo("Contador", f"Número da OS ajustado para {self.numero_os}")
        else:
            messagebox.showwarning("Aviso", "Não é possível diminuir o número da OS abaixo de 0.")

    def aumentar_os(self):
        atual = Contador.ler_contador()
        novo_valor = atual + 1
        Contador.salvar_contador(novo_valor)
        self.numero_os = novo_valor
        self.numero_os_label.config(text=str(self.numero_os))
        messagebox.showinfo("Contador", f"Número da OS ajustado para {self.numero_os}")

    def coletar_dados(self):
        try:
            valor_estimado = float(self.valor_estimado_entry.get().strip())
            prazo = int(self.prazo_entry.get().strip()) if self.prazo_entry.get().strip() else 30
        except ValueError:
            valor_estimado = None
            prazo = None

        return {
            "numero_os": self.numero_os_label['text'],
            "nome_cliente": self.nome_cliente_entry.get().strip(),
            "cpf_cliente": self.cpf_cliente_entry.get().strip(),
            "telefone_cliente": self.telefone_cliente_entry.get().strip(),
            "detalhes_produto": self.detalhes_produto_text.get("1.0", "end").strip(),
            "valor_estimado": valor_estimado,
            "forma_pagamento": self.pagamento_combobox.get().strip(),
            "prazo": prazo
        }

    def validar_dados(self, dados):
        if not all([dados["numero_os"], dados["nome_cliente"], dados["cpf_cliente"], dados["telefone_cliente"],
                    dados["detalhes_produto"], dados["valor_estimado"], dados["forma_pagamento"]]):
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return False
        if len(dados["cpf_cliente"]) != 11 or not dados["cpf_cliente"].isdigit():
            messagebox.showerror("Erro", "CPF inválido. Insira somente números e 11 dígitos.")
            return False
        if dados["valor_estimado"] is None or dados["valor_estimado"] <= 0:
            messagebox.showerror("Erro", "Valor estimado inválido. Insira um valor valido.")
            return False
        if dados["prazo"] is None or dados["prazo"] <= 0:
            messagebox.showerror("Erro", "Prazo inválido. Insira um número inteiro positivo.")
            return False
        return True

    def gerar_pdf(self):
        numero_os = int(self.numero_os_label['text'])  
        dados = self.coletar_dados()
        dados['numero_os'] = numero_os
        if not self.validar_dados(dados):
            return
        pdf = OrdemServicoPDF(dados, self.arquivo_pdf)
        pdf.gerar()
        Contador.salvar_contador(numero_os)
        # Atualiza o label para o próximo número disponível
        self.numero_os_label.config(text=str(numero_os + 1))
        messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")

    def imprimir_pdf(self):
        try:
            imprimir_pdf(self.arquivo_pdf)
            messagebox.showinfo("Impressão", "Enviado para a impressora!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao imprimir: {e}")

    def mostrar_sobre(self):
        messagebox.showinfo("Sobre", "Aplicação de Ordem de Serviço v1.1\nDesenvolvido por Eduardo\n")

    def selecionar_impressora(self):
        """
        Abre uma janela para selecionar a impressora padrão.
        """
        sistema = platform.system()

        if sistema == "Windows":
            try:
                import win32print
                impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
                impressoras_nomes = [imp[2] for imp in impressoras]

                # Cria uma nova janela para seleção de impressora
                janela_impressora = tb.Toplevel(self.root)
                janela_impressora.title("Selecionar Impressora")
                janela_impressora.geometry("400x300")

                tb.Label(janela_impressora, text="Selecione uma Impressora:", bootstyle="light").pack(pady=10)

                impressora_selecionada = tb.StringVar()
                impressora_combobox = tb.Combobox(janela_impressora, textvariable=impressora_selecionada, state="readonly")
                impressora_combobox["values"] = impressoras_nomes
                impressora_combobox.pack(pady=10, padx=20, fill="x")

                status_label = tb.Label(janela_impressora, text="", bootstyle="info")
                status_label.pack(pady=10)

                def confirmar_selecao():
                    impressora = impressora_selecionada.get()
                    if impressora:
                        win32print.SetDefaultPrinter(impressora)
                        status_label.config(text=f"Impressora selecionada: {impressora}", bootstyle="success")
                    else:
                        status_label.config(text="Nenhuma impressora selecionada.", bootstyle="danger")

                tb.Button(janela_impressora, text="Confirmar", command=confirmar_selecao, bootstyle="success").pack(pady=10)

            except ImportError:
                messagebox.showerror("Erro", "Biblioteca 'pywin32' não instalada. Use 'pip install pywin32'.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao listar impressoras: {e}")

        elif sistema == "Linux":
            try:
                import subprocess
                resultado = subprocess.run(["lpstat", "-p"], capture_output=True, text=True)
                linhas = resultado.stdout.splitlines()
                impressoras = [linha.split()[1] for linha in linhas if linha.startswith("printer")]

                # Cria uma nova janela para seleção de impressora
                janela_impressora = tb.Toplevel(self.root)
                janela_impressora.title("Selecionar Impressora")
                janela_impressora.geometry("400x300")

                tb.Label(janela_impressora, text="Selecione uma Impressora:", bootstyle="primary").pack(pady=10)

                impressora_selecionada = tb.StringVar()
                impressora_combobox = tb.Combobox(janela_impressora, textvariable=impressora_selecionada, state="readonly")
                impressora_combobox["values"] = impressoras
                impressora_combobox.pack(pady=10, padx=20, fill="x")

                status_label = tb.Label(janela_impressora, text="", bootstyle="info")
                status_label.pack(pady=10)

                def confirmar_selecao():
                    impressora = impressora_selecionada.get()
                    if impressora:
                        subprocess.run(["lpoptions", "-d", impressora])
                        tb.Label(janela_impressora, text=f"Impressora selecionada: {impressora}", bootstyle="success").pack(pady=10)
                    else:
                        tb.Label(janela_impressora, text="Nenhuma impressora selecionada.", bootstyle="danger").pack(pady=10)

                tb.Button(janela_impressora, text="Confirmar", command=confirmar_selecao, bootstyle="success").pack(pady=10)

            except FileNotFoundError:
                messagebox.showerror("Erro", "O comando 'lpstat' não está disponível. Instale o CUPS com 'sudo apt install cups'.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao listar impressoras: {e}")

        else:
            messagebox.showerror("Erro", f"Sistema operacional '{sistema}' não suportado para seleção de impressoras.")

