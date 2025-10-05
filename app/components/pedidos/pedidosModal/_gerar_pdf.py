from .__init__ import PedidosModal
from documents.os_pdf import OrdemServicoPDF
from PyQt6.QtWidgets import QMessageBox
from database.core.db_manager import DatabaseManager

def _gerar_pdf(self, pedido_data):
    try:
        # Enriquecer pedido_data com dados completos do cliente
        pedido_completo = pedido_data.copy()
        
        # Buscar dados completos do cliente se houver CPF
        if pedido_data.get('cpf_cliente'):
            db = DatabaseManager()
            cliente_completo = db.buscar_cliente_por_cpf(pedido_data['cpf_cliente'])
            
            if cliente_completo:
                # Adicionar dados completos do endereço ao pedido
                pedido_completo.update({
                    'cep_cliente': cliente_completo.get('cep', ''),
                    'rua_cliente': cliente_completo.get('rua', ''),
                    'numero_cliente': cliente_completo.get('numero', ''),
                    'bairro_cliente': cliente_completo.get('bairro', ''),
                    'cidade_cliente': cliente_completo.get('cidade', ''),
                    'estado_cliente': cliente_completo.get('estado', ''),
                    'cnpj_cliente': cliente_completo.get('cnpj', ''),
                    'inscricao_estadual_cliente': cliente_completo.get('inscricao_estadual', ''),
                    'email_cliente': cliente_completo.get('email', ''),
                    'referencia_cliente': cliente_completo.get('referencia', '')
                })
                
                # Montar endereço completo
                endereco_partes = []
                if cliente_completo.get('rua'):
                    endereco_partes.append(cliente_completo['rua'])
                if cliente_completo.get('numero'):
                    endereco_partes.append(f"nº {cliente_completo['numero']}")
                if cliente_completo.get('bairro'):
                    endereco_partes.append(cliente_completo['bairro'])
                if cliente_completo.get('cidade'):
                    endereco_partes.append(cliente_completo['cidade'])
                if cliente_completo.get('estado'):
                    endereco_partes.append(cliente_completo['estado'])
                
                if endereco_partes:
                    pedido_completo['endereco_cliente'] = ' - '.join(endereco_partes)
        
        pdf_generator = OrdemServicoPDF()
        pdf_path = pdf_generator.gerar_pdf(pedido_completo)
        QMessageBox.information(self, "PDF Gerado", f"PDF salvo em: {pdf_path}")
    except Exception as e:
        QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {e}")
