
# Nenhum widget PyQt6 usado diretamente, mas garantir import se necessário
from .__init__ import PedidosModal

def _on_produto_completer_activated(self, texto: str):
    if texto in self.produtos_dict:
        p = self.produtos_dict[texto]
        try:
            was_blocked = self.input_desc.blockSignals(True)
            self.input_desc.setText(str(p.get('nome', '')))
            self.input_desc.blockSignals(was_blocked)
        except Exception:
            pass
        try:
            was_blocked = self.input_valor.blockSignals(True)
            self.input_valor.setText(str(f"{float(p.get('preco', 0)):.2f}"))
            self.input_valor.blockSignals(was_blocked)
        except Exception:
            pass
        try:
            # armazenar preço base para uso com divisórias
            self._base_produto_valor = float(p.get('preco', 0) or 0.0)
        except Exception:
            pass
        # preencher reforco (checkbox) e cor se disponíveis
        try:
            if 'reforco' in p and 'reforco' in getattr(self, 'campos', {}):
                reforco_val = p.get('reforco')
                is_ref = reforco_val in [1, True, '1', 'Sim', 'sim', 'True', 'true']
                try:
                    # suportar QCheckBox e QComboBox
                    ref_widget = self.campos['reforco']
                    if hasattr(ref_widget, 'setChecked'):
                        ref_widget.setChecked(bool(is_ref))
                    else:
                        # Combo
                        txt = 'sim' if is_ref else 'não'
                        idx = ref_widget.findText(txt)
                        if idx >= 0:
                            ref_widget.setCurrentIndex(idx)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if 'cor' in p and 'cor' in getattr(self, 'campos', {}):
                cor_val = p.get('cor')
                if cor_val:
                    try:
                        idx = self.campos['cor'].findText(str(cor_val))
                        if idx >= 0:
                            self.campos['cor'].setCurrentIndex(idx)
                    except Exception:
                        pass
        except Exception:
            pass
