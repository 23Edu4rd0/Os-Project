import sys, traceback
print('IMPORT_MODAL_DIRECT_START', flush=True)
sys.path.insert(0, r'c:\Users\eduar\OneDrive\Área de Trabalho\Os-Project')
try:
    print('about to import pedidosModal', flush=True)
    import app.components.pedidos.pedidosModal as pedidosModal
    print('imported pedidosModal OK', flush=True)
except Exception:
    traceback.print_exc()
    print('IMPORT_MODAL_FAILED', flush=True)
print('IMPORT_MODAL_DIRECT_END', flush=True)
