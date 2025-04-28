import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timedelta
from impress import imprimir_pdf

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
        c.setFont("Helvetica", 9)
        c.drawString(10, height - 85, f"Data de Emissão: {data_e_hora_texto}")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, height - 110, "DADOS DO CLIENTE")
        c.setFont("Helvetica", 9)
        c.drawString(10, height - 130, f'Nome: {nome_cliente}')
        c.drawString(10, height - 145, f'CPF: {cpf_cliente}')
        c.drawString(10, height - 160, f'Telefone: {telefone_cliente}')

        y_position = height - 190

        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y_position, "DESCRIÇÃO DO PRODUTO")
        y_position -= 15

        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = "Helvetica"
        style.fontSize = 9
        style.leading = 12

        detalhes_paragraph = Paragraph(detalhes_produto, style)
        text_width = width - 20
        w, h = detalhes_paragraph.wrap(text_width, y_position)
        detalhes_paragraph.drawOn(c, 10, y_position - h)
        y_position -= h + 20

        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y_position, "ORÇAMENTO")
        y_position -= 20
        c.setFont("Helvetica", 9)
        c.drawString(10, y_position, f'Valor estimado: R$ {valor_estimado:.2f}')
        y_position -= 15
        c.drawString(10, y_position, f'Forma de pagamento: {forma_pagamento}')
        y_position -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y_position, "PRAZOS")
        y_position -= 20
        c.setFont("Helvetica", 9)
        c.drawString(10, y_position, f'Prazo estimado para entrega: {data_de_entrega}')
        y_position -= 15

        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(10, y_position, "TERMOS E CONDIÇÕES")
        y_position -= 15

        termos_condicoes = """
        1. Peças não retiradas no prazo de 30 (trinta) dias serão consideradas propriedade da empresa.<br/>
        2. Valor pode variar conforme material e complexidade do serviço.<br/>
        3. Prazos podem mudar por aprovação ou falta de material.<br/>
        4. Alterações após início implicam novo prazo e valor.<br/>
        5. Entrega só é válida com este documento.
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
        self.root.geometry("325x350")

        ttk.Label(root, text="Número da OS:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.numero_os_entry = ttk.Entry(root)
        self.numero_os_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(root, text="Nome do Cliente:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.nome_cliente_entry = ttk.Entry(root)
        self.nome_cliente_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(root, text="CPF do Cliente:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.cpf_cliente_entry = ttk.Entry(root)
        self.cpf_cliente_entry.grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(root, text="Telefone do Cliente:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.telefone_cliente_entry = ttk.Entry(root)
        self.telefone_cliente_entry.grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(root, text="Detalhes do Produto:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.detalhes_produto_entry = ttk.Entry(root)
        self.detalhes_produto_entry.grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(root, text="Valor Estimado:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.valor_estimado_entry = ttk.Entry(root)
        self.valor_estimado_entry.grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(root, text="Forma de Pagamento:").grid(row=6, column=0, padx=10, pady=5, sticky="w")
        self.pagamento_combobox = ttk.Combobox(root, values=["Pix", "Crédito", "Débito", "Dinheiro Físico"])
        self.pagamento_combobox.grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(root, text="Prazo de Entrega (dias):").grid(row=7, column=0, padx=10, pady=5, sticky="w")
        self.prazo_entry = ttk.Entry(root)
        self.prazo_entry.grid(row=7, column=1, padx=10, pady=5)

        self.gerar_pdf_button = ttk.Button(root, text="Gerar PDF", command=self.gerar_pdf)
        self.gerar_pdf_button.grid(row=8, column=0, columnspan=2, pady=10)

        self.imprimir_pdf_button = ttk.Button(root, text="Imprimir PDF", command=self.imprimir_pdf)
        self.imprimir_pdf_button.grid(row=9, column=0, columnspan=2, pady=10)

        self.arquivo_pdf = "ordem_servico.pdf"

    def coletar_dados(self):
        try:
            valor_estimado = float(self.valor_estimado_entry.get().strip())
            prazo = int(self.prazo_entry.get().strip()) if self.prazo_entry.get().strip() else 30
        except ValueError:
            valor_estimado = None
            prazo = None

        return {
            "numero_os": self.numero_os_entry.get().strip(),
            "nome_cliente": self.nome_cliente_entry.get().strip(),
            "cpf_cliente": self.cpf_cliente_entry.get().strip(),
            "telefone_cliente": self.telefone_cliente_entry.get().strip(),
            "detalhes_produto": self.detalhes_produto_entry.get().strip(),
            "valor_estimado": valor_estimado,
            "forma_pagamento": self.pagamento_combobox.get().strip(),
            "prazo": prazo
        }

    def validar_dados(self, dados):
        if not all([dados["numero_os"], dados["nome_cliente"], dados["cpf_cliente"], dados["telefone_cliente"],
                    dados["detalhes_produto"], dados["valor_estimado"], dados["forma_pagamento"]]):
            messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
            return False
        if dados["valor_estimado"] is None or dados["valor_estimado"] <= 0:
            messagebox.showerror("Erro", "Valor estimado inválido. Insira um número válido.")
            return False
        if dados["prazo"] is None or dados["prazo"] <= 0:
            messagebox.showerror("Erro", "Prazo inválido. Insira um número inteiro positivo.")
            return False
        return True

    def gerar_pdf(self):
        dados = self.coletar_dados()
        if not self.validar_dados(dados):
            return
        pdf = OrdemServicoPDF(dados, self.arquivo_pdf)
        pdf.gerar()
        messagebox.showinfo("Sucesso", "PDF gerado com sucesso!")

    def imprimir_pdf(self):
        try:
            imprimir_pdf(self.arquivo_pdf)
            messagebox.showinfo("Impressão", "Enviado para a impressora!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao imprimir: {e}")

