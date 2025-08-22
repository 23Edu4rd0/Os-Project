"""Compat: redireciona para a implementação real do PedidosManager.

Este arquivo existia apenas para um placeholder. Agora garante que,
se for importado por engano, usará a implementação completa sem exibir
qualquer texto de 'Em desenvolvimento'.
"""

from .__init__ import PedidosManager  # reexporta a classe real

__all__ = ["PedidosManager"]
