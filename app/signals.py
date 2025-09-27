from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    # Sinais para status
    statuses_updated = pyqtSignal()
    
    # Sinais para pedidos
    pedido_criado = pyqtSignal(int)  # pedido_id
    pedido_editado = pyqtSignal(int)  # pedido_id
    pedido_excluido = pyqtSignal(int)  # pedido_id
    pedido_status_atualizado = pyqtSignal(int, str)  # pedido_id, novo_status
    pedidos_atualizados = pyqtSignal()  # Atualização geral
    
    # Sinais para clientes
    cliente_criado = pyqtSignal(int)  # cliente_id
    cliente_editado = pyqtSignal(int)  # cliente_id
    cliente_excluido = pyqtSignal(int)  # cliente_id
    clientes_atualizados = pyqtSignal()
    
    # Sinais para produtos
    produto_criado = pyqtSignal(int)  # produto_id
    produto_editado = pyqtSignal(int)  # produto_id
    produto_excluido = pyqtSignal(int)  # produto_id
    produtos_atualizados = pyqtSignal()


# single shared instance
_signals = AppSignals()


def get_signals() -> AppSignals:
    return _signals
