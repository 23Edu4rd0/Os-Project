"""
Módulo de contas - Interface principal
"""

from .contas_manager import ContasManager

class ContasInterface:
    """Interface principal para o módulo de contas"""
    
    def __init__(self, parent):
        self.parent = parent
        self.manager = ContasManager(parent)
        
    def carregar_dados(self):
        """Carrega dados das contas"""
        return self.manager.carregar_dados()
    
    def atualizar_graficos(self):
        """Atualiza gráficos da interface"""
        return self.manager.atualizar_graficos()
    
    def filtrar_por_periodo(self, periodo):
        """Filtra dados por período"""
        return self.manager.filtrar_por_periodo(periodo)
