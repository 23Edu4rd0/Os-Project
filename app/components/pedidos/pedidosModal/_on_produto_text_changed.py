
# Nenhum widget PyQt6 usado diretamente, mas garantir import se necessário
from .__init__ import PedidosModal

def _on_produto_text_changed(self, texto: str):
    if not texto:
        return
    try:
        if 'R$' in texto:
            parte = texto.split('R$')[-1]
            num = ''.join(ch for ch in parte if ch.isdigit() or ch in ',.')
            if num:
                num = num.replace('.', '').replace(',', '.')
                self.input_valor.setText(str(f"{float(num):.2f}"))
    except Exception:
        self.input_valor.setText("")
    if texto in self.produtos_dict:
        p = self.produtos_dict.get(texto, {})
        preco = p.get('preco', 0)
        try:
            preco_float = float(preco)
        except Exception:
            preco_float = 0.0
        self.input_valor.setText(str(f"{preco_float:.2f}"))
        try:
            self._base_produto_valor = float(preco_float)
        except Exception:
            pass
        try:
            self.input_desc.setText(str(p.get('nome', texto)))
        except Exception:
            pass
        return
    try:
        low = texto.strip().lower()
        best = None
        for _, pdata in self.produtos_dict.items():
            nome = pdata.get('nome', '').strip()
            nlow = nome.lower()
            if nlow == low:
                best = pdata
                break
            if best is None and nlow.startswith(low):
                best = pdata
        if best is None:
            for _, pdata in self.produtos_dict.items():
                if low in pdata.get('nome', '').strip().lower():
                    best = pdata
                    break
        if best:
            preco = best.get('preco', 0)
            try:
                preco_float = float(preco)
            except Exception:
                preco_float = 0.0
            self.input_valor.setText(str(f"{preco_float:.2f}"))
            try:
                cat = best.get('categoria') or 'Todas'
                idx = self.input_categoria.findText(cat)
                if idx >= 0:
                    self.input_categoria.setCurrentIndex(idx)
            except Exception:
                pass
            try:
                self._base_produto_valor = float(preco_float)
            except Exception:
                pass
            try:
                self.input_desc.setText(str(best.get('nome', texto)))
            except Exception:
                pass
    except Exception:
        self.input_valor.setText("")
