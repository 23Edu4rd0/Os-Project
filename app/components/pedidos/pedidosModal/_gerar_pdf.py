from .__init__ import PedidosModal

def _gerar_pdf(self, pedido_data):
    try:
        pdf_generator = OrdemServicoPDF()
        pdf_path = pdf_generator.gerar_pdf(pedido_data)
        QMessageBox.information(self, "PDF Gerado", f"PDF salvo em: {pdf_path}")
    except Exception as e:
        QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {e}")
