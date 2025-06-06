from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


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

        # --- Font Handling Start ---
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_path_regular = os.path.normpath(
            os.path.join(script_dir, '..', 'assets', 'Montserrat-Regular.ttf')
        )
        font_path_bold = os.path.normpath(
            os.path.join(script_dir, '..', 'assets', 'Montserrat-Bold.ttf')
        )

        custom_font_name = 'AppMontserrat'
        custom_font_bold = 'AppMontserratBold'
        default_font_name = 'Helvetica'
        default_font_bold = 'Helvetica-Bold'
        font_to_use = default_font_name  # Regular
        font_bold_to_use = default_font_bold  # Bold

        # Registrar Regular
        print(f"INFO: Tentando carregar fonte regular: {font_path_regular}")
        if os.path.exists(font_path_regular):
            try:
                pdfmetrics.registerFont(
                    TTFont(custom_font_name, font_path_regular)
                )
                font_to_use = custom_font_name
                print(f"INFO: Fonte regular registrada: '{custom_font_name}'")
            except Exception as e:
                print(f"ERRO ao registrar fonte regular: {e}")
        else:
            print(f"AVISO: Fonte regular não encontrada em "
                  f"{font_path_regular}")

        # Registrar Bold
        print(f"INFO: Tentando carregar fonte bold: {font_path_bold}")
        if os.path.exists(font_path_bold):
            try:
                pdfmetrics.registerFont(
                    TTFont(custom_font_bold, font_path_bold)
                )
                font_bold_to_use = custom_font_bold
                print(f"INFO: Fonte bold registrada: '{custom_font_bold}'")
            except Exception as e:
                print(f"ERRO ao registrar fonte bold: {e}")
        else:
            print(f"AVISO: Fonte bold não encontrada em {font_path_bold}")
        # --- Font Handling End ---

        c = canvas.Canvas(self.arquivo_pdf, pagesize=(80 * mm, 250 * mm))
        width, height = 80 * mm, 250 * mm

        # Cabeçalho
        c.setFont(font_bold_to_use, 12)
        c.drawCentredString(width / 2, height - 20, "OuriPrata - Ourivesaria")
        c.setFont(font_to_use, 8)
        c.drawCentredString(
            width / 2,
            height - 30,
            "Av. 1° de Junho, 411 - 501 - Centro - Divinópolis - MG"
        )
        c.drawCentredString(width / 2, height - 40, "Tel: (37) 9862-3061")

        c.setFont(font_bold_to_use, 12)
        c.drawString(10, height - 70, f"NÚMERO DA OS: {numero_os}")
        c.line(10, height - 75, width - 10, height - 75)

        y_position = height - 85
        c.setFont(font_to_use, 9)
        c.drawString(10, y_position, f"Data de Emissão: {data_e_hora_texto}")
        y_position -= 20

        c.setFont(font_bold_to_use, 12)
        c.drawString(10, y_position, "DADOS DO CLIENTE")
        c.line(10, y_position - 5, width - 10, y_position - 5)
        y_position -= 20

        c.setFont(font_to_use, 9)
        c.drawString(10, y_position, f'Nome: {nome_cliente}')
        y_position -= 15
        c.drawString(10, y_position, f'CPF: {cpf_cliente}')
        y_position -= 15
        c.drawString(10, y_position, f'Telefone: {telefone_cliente}')
        y_position -= 25

        c.setFont(font_bold_to_use, 12)
        c.drawString(10, y_position, "DETALHES DO PRODUTO")
        c.line(10, y_position - 5, width - 10, y_position - 5)
        y_position -= 20

        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = font_to_use  # Regular para detalhes
        style.fontSize = 9
        style.leading = 12

        detalhes_paragraph = Paragraph(detalhes_produto, style)
        text_width = width - 20
        _, h = detalhes_paragraph.wrap(text_width, y_position)
        detalhes_paragraph.drawOn(c, 10, y_position - h)
        y_position -= h + 25

        c.setFont(font_bold_to_use, 12)
        c.drawString(10, y_position, "ORÇAMENTO")
        c.line(10, y_position - 5, width - 10, y_position - 5)
        y_position -= 20
        c.setFont(font_to_use, 9)
        valor_formatado = f'{valor_estimado:.2f}'.replace('.', ',')
        c.drawString(10, y_position, f'Valor estimado: R$ {valor_formatado}')
        y_position -= 15
        c.drawString(10, y_position, f'Forma de pagamento: {forma_pagamento}')
        y_position -= 30

        c.setFont(font_bold_to_use, 12)
        c.drawString(10, y_position, "DATA DE ENTREGA")
        c.line(10, y_position - 5, width - 10, y_position - 5)
        y_position -= 20
        c.setFont(font_to_use, 9)
        c.drawString(
            10, y_position,
            f'Prazo estimado para entrega: {data_de_entrega}'
        )
        y_position -= 15

        y_position -= 20
        c.setFont(font_bold_to_use, 12)
        c.drawString(10, y_position, "TERMOS E CONDIÇÕES")
        c.line(10, y_position - 5, width - 10, y_position - 5)
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
