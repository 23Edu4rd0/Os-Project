from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os


class OrdemServicoPDF:
    def __init__(self, dados, arquivo_pdf="ordem_servico.pdf", tamanho_folha="pequena"):
        self.dados = dados
        self.arquivo_pdf = self._gerar_caminho_pdf(dados, arquivo_pdf)
        self.tamanho_folha = tamanho_folha  # "pequena" ou "grande"
        
    def _gerar_caminho_pdf(self, dados, arquivo_padrao):
        """
        Gera um caminho para o PDF com base nos dados da OS.
        Cria a estrutura de pastas necessária.
        
        Args:
            dados (dict): Dados da OS
            arquivo_padrao (str): Nome de arquivo padrão
            
        Returns:
            str: Caminho completo para o arquivo PDF
        """
        # Criar pasta pdfs se não existir
        pasta_pdfs = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pdfs')
        if not os.path.exists(pasta_pdfs):
            os.makedirs(pasta_pdfs, exist_ok=True)
            
        # Criar nome de arquivo baseado na OS, cliente e data
        numero_os = dados.get("numero_os", "00000")
        # Converter para inteiro se for string, ou usar valor padrão
        try:
            if isinstance(numero_os, str):
                numero_os = int(numero_os)
        except ValueError:
            numero_os = 0  # valor padrão se não puder converter
            
        nome_cliente = dados.get("nome_cliente", "cliente").replace(" ", "_")[:20]
        
        # Data melhor formatada: YYYY-MM-DD_HH-MM-SS
        agora = datetime.now()
        data_formatada = agora.strftime('%Y-%m-%d')
        hora_formatada = agora.strftime('%H-%M-%S')
        
        # Nome do arquivo: OS_00001_NomeCliente_2025-09-24_14-30-52.pdf
        nome_arquivo = f"OS_{numero_os:05d}_{nome_cliente}_{data_formatada}_{hora_formatada}.pdf"
        
        # Caminho completo
        return os.path.join(pasta_pdfs, nome_arquivo)

    def gerar(self):
        numero_os = self.dados["numero_os"]
        nome_cliente = self.dados["nome_cliente"]
        cpf_cliente = self.dados["cpf_cliente"]
        telefone_cliente = self.dados["telefone_cliente"]
        detalhes_produto = self.dados["detalhes_produto"]
        valor_produto = self.dados.get("valor_produto")
        valor_entrada = self.dados.get("valor_entrada")
        frete = self.dados.get("frete")
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

        # Registrar Regular (silencioso)
        if os.path.exists(font_path_regular):
            try:
                pdfmetrics.registerFont(
                    TTFont(custom_font_name, font_path_regular)
                )
                font_to_use = custom_font_name
            except Exception:
                pass  # Usar fonte padrão em caso de erro
        
        # Registrar Bold (silencioso)
        if os.path.exists(font_path_bold):
            try:
                pdfmetrics.registerFont(
                    TTFont(custom_font_bold, font_path_bold)
                )
                font_bold_to_use = custom_font_bold
            except Exception:
                pass  # Usar fonte padrão em caso de erro
        # --- Font Handling End ---

        # Escolha do tamanho da folha
        if self.tamanho_folha == "grande":
            width, height = 210 * mm, 297 * mm  # A4
        else:
            width, height = 80 * mm, 250 * mm  # Bobina
        c = canvas.Canvas(self.arquivo_pdf, pagesize=(width, height))

        # Cabeçalho
        c.setFont(font_bold_to_use, 12)
        c.drawCentredString(width / 2, height - 20, "Merkava Ferramentas")
        c.setFont(font_to_use, 8)
        c.drawCentredString(
            width / 2,
            height - 30,
            "Rua José Gabriel Medef, 41 - Padre Liberio - Divinópolis - MG"
        )
        c.drawCentredString(width / 2, height - 40, "Tel: (37) 98402-9655")

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
        valor_produto_fmt = f'{valor_produto:.2f}'.replace('.', ',') if valor_produto is not None else "-"
        valor_entrada_fmt = f'{valor_entrada:.2f}'.replace('.', ',') if valor_entrada is not None else "-"
        frete_fmt = f'{frete:.2f}'.replace('.', ',') if frete is not None else "0,00"
        c.drawString(10, y_position, f'Valor do produto: R$ {valor_produto_fmt}')
        y_position -= 15
        c.drawString(10, y_position, f'Valor da entrada: R$ {valor_entrada_fmt}')
        y_position -= 15
        c.drawString(10, y_position, f'Frete: R$ {frete_fmt}')
        y_position -= 15
        total = 0.0
        restante = 0.0
        try:
            total = float(valor_produto or 0) + float(frete or 0)
            restante = total - float(valor_entrada or 0)
        except Exception:
            total = 0.0
            restante = 0.0
        c.drawString(10, y_position, f'Total: R$ {total:.2f}'.replace('.', ','))
        y_position -= 15
        c.drawString(10, y_position, f'Restante: R$ {restante:.2f}'.replace('.', ','))
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
        
        # Retornar o caminho do arquivo gerado
        return self.arquivo_pdf
