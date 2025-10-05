
"""
Database initialization module.
This file exposes the singleton `db_manager` for use throughout the project.
It also allows the module to be run directly for a quick check, without failing due to relative imports when there is no package context.
All user-facing messages are in Portuguese. All comments, docstrings, and logs are in English.
"""


try:
    # Import within a package (normal case: "from database import db_manager")
    from .core.db_manager import DatabaseManager
    from .core.db_setup import DatabaseSetup
    from .crud.order_crud import OrderCRUD
    from .crud.products_crud import ProductsCRUD
    from .queries.report_queries import ReportQueries
    from .services.sync_compras import sync_numero_compras
except Exception:
    # Fallback when the module is run directly (e.g., python database/__init__.py)
    # or when the package context is not available.
    from database.core.db_manager import DatabaseManager
    from database.core.db_setup import DatabaseSetup
    from database.crud.order_crud import OrderCRUD
    from database.crud.products_crud import ProductsCRUD
    from database.queries.report_queries import ReportQueries
    from database.services.sync_compras import sync_numero_compras


# Create shared singleton instance
db_manager = DatabaseManager()

# Export public API
__all__ = [
    'db_manager',
    'DatabaseManager',
    'DatabaseSetup',
    'OrderCRUD',
    'ProductsCRUD',
    'ReportQueries',
    'sync_numero_compras'
]


if __name__ == '__main__':
	# Direct execution: show quick info for sanity-check
	print(f"Database path: {getattr(db_manager, 'db_path', '<unknown>')}")
	try:
		clientes = db_manager.listar_clientes(10)
		pedidos = db_manager.listar_pedidos_ordenados_por_prazo(10)
		print(f"Clientes (até 10): {len(clientes)}  Pedidos (até 10): {len(pedidos)}")  # User-facing message in Portuguese
	except Exception as e:
		print(f"Erro ao consultar DB: {e}")  # User-facing message in Portuguese
		print(f"Error querying DB: {e}")  # Log in English
