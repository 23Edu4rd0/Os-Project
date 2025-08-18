from pathlib import Path
p = Path('app/components/contas/contas_financeiro.py')
lines = p.read_text(encoding='utf-8').splitlines()
for i in range(100,130):
    print(f"{i+1:03}: {repr(lines[i])}")
