import sys, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import app.ui.backup_tab as bt
    print('IMPORT_OK')
except Exception as e:
    print('EXCEPTION:', type(e), e)
    traceback.print_exc()
