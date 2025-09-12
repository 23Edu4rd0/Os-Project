import sys, traceback, time
print('IMPORT_TEST_START', flush=True)
sys.path.insert(0, r'c:\Users\eduar\OneDrive\Área de Trabalho\Os-Project')
try:
    print('about to import wrapper...', flush=True)
    from app.components.pedidos import pedidos_modal
    print('wrapper import OK', flush=True)
    print('about to import modular...', flush=True)
    from app.components.pedidos.pedidosModal import _criar_modal_completo
    print('modular import OK', flush=True)
except Exception:
    traceback.print_exc()
    print('IMPORT_FAILED', flush=True)
finally:
    print('IMPORT_TEST_END', flush=True)
    time.sleep(0.1)
