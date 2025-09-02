import importlib
mods=[
    'app.ui.backup_tab',
    'app.ui.status_manager',
    'app.components.pedidos.status_editor',
    'app.components.pedidos.pedidos_interface',
    'app.components.pedidos.pedidos_card',
    'app.components.pedidos.pedidos_actions',
    'app.components.pedidos.modal_parts.pagamento'
]
for m in mods:
    try:
        importlib.import_module(m)
        print(m + ': OK')
    except Exception as e:
        print(m + ': ERROR ->', e)
