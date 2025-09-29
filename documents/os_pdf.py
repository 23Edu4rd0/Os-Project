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
        produtos = self.dados.get("produtos", [])  # Lista estruturada de produtos
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

        # Escolha do tamanho da folha
        if self.tamanho_folha == "grande":
            width, height = 210 * mm, 297 * mm  # A4
        else:
            width, height = 80 * mm, 250 * mm  # Bobina
        c = canvas.Canvas(self.arquivo_pdf, pagesize=(width, height))

        # --- Inserir logo no topo, se existir ---
        logo_path = os.path.normpath(os.path.join(script_dir, '..', 'assets', 'logo.png'))
        if os.path.exists(logo_path):
            try:
                # Largura máxima do logo: 40mm ou largura da página - 20mm
                max_logo_width = min(40 * mm, width - 20 * mm)
                # Altura máxima do logo: 20mm
                max_logo_height = 20 * mm
                from reportlab.lib.utils import ImageReader
                logo_img = ImageReader(logo_path)
                img_width, img_height = logo_img.getSize()
                aspect = img_height / img_width
                draw_width = max_logo_width
                draw_height = draw_width * aspect
                if draw_height > max_logo_height:
                    draw_height = max_logo_height
                    draw_width = draw_height / aspect
                x = (width - draw_width) / 2
                y = height - draw_height - 8  # 8pt margin from top
                c.drawImage(logo_path, x, y, width=draw_width, height=draw_height, mask='auto')
                y_logo_base = y - 5  # Espaço após o logo
            except Exception:
                y_logo_base = height - 20  # fallback
        else:
            y_logo_base = height - 20

        # Cabeçalho
        c.setFont(font_bold_to_use, 12)
        c.drawCentredString(width / 2, y_logo_base, "Merkava Ferramentas")
        c.setFont(font_to_use, 8)
        c.drawCentredString(
            width / 2,
            y_logo_base - 10,
            "Rua José Gabriel Medef, 41 - Padre Liberio - Divinópolis - MG"
        )
        c.drawCentredString(width / 2, y_logo_base - 20, "Tel: (37) 98402-9655")

        y_position = y_logo_base - 50  # aumenta o espaço entre empresa e número da OS

        c.setFont(font_bold_to_use, 12)
        c.drawString(10, y_position, f"NÚMERO DA OS: {numero_os}")
        c.line(10, y_position - 5, width - 10, y_position - 5)
        y_position -= 15

        c.setFont(font_to_use, 9)
        c.drawString(10, y_position, f"Data de Emissão: {data_e_hora_texto}")
        y_position -= 20

        c.setFont(font_bold_to_use, 12)
        c.drawString(10, y_position, "DADOS DO CLIENTE")
        c.line(10, y_position - 5, width - 10, y_position - 5)
        y_position -= 20

        c.setFont(font_to_use, 9)
        c.drawString(10, y_position, f'Nome: {nome_cliente}')


        # --- Seção de Produtos ---
        c.setFont(font_bold_to_use, 12)
        c.drawString(10, y_position, "PRODUTOS")
        c.line(10, y_position - 5, width - 10, y_position - 5)
        y_position -= 20
        
        # Usar lista estruturada se disponível, senão usar detalhes_produto como fallback
        if produtos and isinstance(produtos, list):
            c.setFont(font_to_use, 9)
            for produto in produtos:
                nome = produto.get('descricao', produto.get('nome', 'Produto'))
                quantidade = produto.get('quantidade', 1)
                valor_unit = produto.get('valor', 0)
                valor_total_item = quantidade * valor_unit
                
                # Exibir: "2x Produto ABC - R$ 50,00 (unit: R$ 25,00)"
                if quantidade > 1:
                    linha_produto = f"{quantidade}x {nome} - R$ {valor_total_item:.2f} (unit: R$ {valor_unit:.2f})"
                else:
                    linha_produto = f"{nome} - R$ {valor_unit:.2f}"
                
                linha_produto = linha_produto.replace('.', ',')
                c.drawString(15, y_position, f"• {linha_produto}")
                y_position -= 12
            y_position -= 13  # Espaço extra após lista de produtos
        else:
            # Fallback para detalhes_produto como string
            style = getSampleStyleSheet()["Normal"]
            text_width = width - 20
            detalhes_paragraph = Paragraph(detalhes_produto, style)
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
        1. O valor e o prazo podem ser ajustados conforme necessidade de materiais, mudanças no pedido ou imprevistos.<br/>
        2. Mudanças ou condições especiais serão sempre comunicadas e acordadas previamente.<br/>
        3. Caso precise cancelar ou alterar qualquer informação do pedido (como pagamento, endereço, itens, etc.), entre em contato o quanto antes para avaliarmos juntos a melhor solução.
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
