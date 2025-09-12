"""
Módulo de inicialização do banco de dados.

Este arquivo expõe o singleton `db_manager` para uso em todo o projeto.
Também tenta permitir que o módulo seja executado diretamente para um
cheque rápido, sem falhar por causa de imports relativos quando não
há contexto de pacote.
"""

try:
	# Import dentro de um pacote (o caso normal: "from database import db_manager")
	from .db_manager import DatabaseManager
except Exception:
	# Fallback quando o módulo for executado diretamente (ex.: python database\__init__.py)
	# ou quando o contexto de pacote não estiver disponível.
	from database.db_manager import DatabaseManager


# Criar instância singleton compartilhada
db_manager = DatabaseManager()


if __name__ == '__main__':
	# Execução direta: mostra informações rápidas para sanity-check
	print(f"Database path: {getattr(db_manager, 'db_path', '<unknown>')}")
	try:
		clientes = db_manager.listar_clientes(10)
		pedidos = db_manager.listar_pedidos_ordenados_por_prazo(10)
		print(f"Clientes (até 10): {len(clientes)}  Pedidos (até 10): {len(pedidos)}")
	except Exception as e:
		print(f"Erro ao consultar DB: {e}")
