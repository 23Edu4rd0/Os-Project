"""
Ações de pedidos em PyQt6
"""

from PyQt6.QtWidgets import QMessageBox, QInputDialog
from database import db_manager


class PedidosActions:
    """Gerencia as ações dos pedidos"""
    
    def __init__(self, interface):
        self.interface = interface
        
    def excluir_pedido(self, pedido_id):
        """Exclui um pedido"""
        reply = QMessageBox.question(
            self.interface,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o pedido #{pedido_id}?\n\nEsta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Excluir do banco de dados
                db_manager.excluir_pedido(pedido_id)
                
                QMessageBox.information(
                    self.interface,
                    "Sucesso",
                    "Pedido excluído com sucesso!"
                )
                
                # Atualizar interface
                self.interface.refresh_after_action()
                return True
                
            except Exception as e:
                QMessageBox.critical(
                    self.interface,
                    "Erro",
                    f"Erro ao excluir pedido: {e}"
                )
                return False
        
        return False
        
    def atualizar_status(self, pedido_id, novo_status=None):
        """Atualiza o status de um pedido"""
        if novo_status is None:
            # Pedir novo status ao usuário
            status_options = ["em produção", "enviado", "entregue", "cancelado"]
            novo_status, ok = QInputDialog.getItem(
                self.interface,
                "Atualizar Status",
                f"Selecione o novo status para o pedido #{pedido_id}:",
                status_options,
                0,
                False
            )
            
            if not ok:
                return False
        
        try:
            # Atualizar no banco de dados
            db_manager.atualizar_status_pedido(pedido_id, novo_status)
            
            QMessageBox.information(
                self.interface,
                "Sucesso",
                f"Status atualizado para '{novo_status}' com sucesso!"
            )
            
            # Atualizar interface
            self.interface.refresh_after_action()
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self.interface,
                "Erro",
                f"Erro ao atualizar status: {e}"
            )
            return False
    
    def duplicar_pedido(self, pedido_id):
        """Duplica um pedido existente"""
        try:
            # Buscar dados do pedido original
            pedidos = db_manager.listar_pedidos_ordenados_por_prazo()
            pedido_original = None
            
            for pedido in pedidos:
                if pedido.get('id') == pedido_id:
                    pedido_original = pedido
                    break
            
            if not pedido_original:
                QMessageBox.warning(
                    self.interface,
                    "Erro",
                    "Pedido não encontrado!"
                )
                return False
            
            # Confirmar duplicação
            reply = QMessageBox.question(
                self.interface,
                "Confirmar Duplicação",
                f"Tem certeza que deseja duplicar o pedido #{pedido_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Criar novo pedido baseado no original
                from app.numero_os import Contador
                contador = Contador()
                novo_numero_os = contador.get_proximo_numero()
                
                dados_novo = pedido_original.copy()
                dados_novo.pop('id', None)  # Remover ID original
                dados_novo['numero_os'] = novo_numero_os
                dados_novo['status'] = 'em produção'  # Reset status
                dados_novo.pop('data_criacao', None)  # Nova data será gerada
                
                # Salvar novo pedido
                db_manager.inserir_pedido(dados_novo)
                
                QMessageBox.information(
                    self.interface,
                    "Sucesso",
                    f"Pedido duplicado com sucesso! Nova OS #{novo_numero_os:05d}"
                )
                
                # Atualizar interface
                self.interface.refresh_after_action()
                return True
            
        except Exception as e:
            QMessageBox.critical(
                self.interface,
                "Erro",
                f"Erro ao duplicar pedido: {e}"
            )
            return False
        
        return False
