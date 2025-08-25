
# Nenhum widget PyQt6 usado diretamente, mas garantir import se necessário
from .__init__ import PedidosModal

def _add_produto(self):
    desc = (self.input_desc.text() or '').strip()
    val_text_raw = (self.input_valor.text() or '').strip()
    # Se descrição vier no formato "Nome | R$ 123,45", separa o nome e extrai preço se necessário
    if '|' in desc and 'R$' in desc:
        try:
            nome_parte, resto = desc.split('|', 1)
            desc = nome_parte.strip()
            if not val_text_raw:
                if 'R$' in resto:
                    parte = resto.split('R$')[-1]
                else:
                    parte = resto
                num = ''.join(ch for ch in parte if ch.isdigit() or ch in ',.')
                if num:
                    val_text_raw = num
        except Exception:
            pass
    # Se descrição igual a display do catálogo, normaliza e pega preço
    if desc in getattr(self, 'produtos_dict', {}):
        try:
            p = self.produtos_dict[desc]
            if not val_text_raw:
                val_text_raw = f"{float(p.get('preco', 0)):.2f}"
            desc = p.get('nome', desc)
        except Exception:
            pass
    # Normalizar número
    val_text = val_text_raw.replace('R$', '').replace(' ', '').replace(',', '.')
    # Se descrição coincide com um item do catálogo (por nome), e não há valor, usar preço do catálogo
    if (not val_text) and getattr(self, 'produtos_dict', None):
        try:
            for display, pdata in self.produtos_dict.items():
                if pdata.get('nome', '').lower() == desc.lower():
                    val_text = str(pdata.get('preco', 0.0))
                    break
        except Exception:
            pass
    if not desc:
        return
    try:
        valor = float(val_text) if val_text else 0.0
    except Exception:
        valor = 0.0
    # Capturar cor/reforço atuais (por item)
    try:
        cor_sel = (self.campos.get('cor').currentText() if 'cor' in self.campos else '').strip()
    except Exception:
        cor_sel = ''
    try:
        reforco_widget = self.campos.get('reforco')
        if reforco_widget is None:
            reforco_sel = False
        elif hasattr(reforco_widget, 'isChecked'):
            reforco_sel = bool(reforco_widget.isChecked())
        else:
            reforco_sel = (reforco_widget.currentText() if hasattr(reforco_widget, 'currentText') else '').strip().lower() == 'sim'
    except Exception:
        reforco_sel = False
    # Aplicar acréscimo de R$15,00 se reforço
    try:
        if reforco_sel:
            valor += 15.0
    except Exception:
        pass
    # Adiciona o produto à lista do pedido
    try:
        self.produtos_list.append({"descricao": desc, "valor": valor, "cor": cor_sel, "reforco": reforco_sel})
    except Exception:
        # garantir que a lista exista
        try:
            self.produtos_list = [{"descricao": desc, "valor": valor, "cor": cor_sel, "reforco": reforco_sel}]
        except Exception:
            pass
    # Limpar campos de entrada e atualizar UI
    try:
        self.input_desc.clear()
    except Exception:
        pass
    try:
        self.input_valor.clear()
    except Exception:
        pass
    try:
        self._refresh_produtos_ui()
    except Exception:
        pass
