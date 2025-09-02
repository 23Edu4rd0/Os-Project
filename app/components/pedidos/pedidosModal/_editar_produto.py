def _editar_produto(self, index):
    try:
        if index < 0 or index >= len(self.produtos_list):
            return
        prod = self.produtos_list.pop(index)
        # Populate inputs
        try:
            self.input_desc.setText(str(prod.get('descricao') or ''))
        except Exception:
            pass
        try:
            self.input_valor.setText(f"{float(prod.get('valor') or 0):.2f}")
        except Exception:
            try:
                self.input_valor.setText(str(prod.get('valor') or ''))
            except Exception:
                pass
        try:
            if 'cor' in prod and prod.get('cor'):
                idx = self.input_categoria.findText(prod.get('cor'))
                if idx >= 0:
                    self.input_categoria.setCurrentIndex(idx)
        except Exception:
            pass
        try:
            if 'reforco' in prod and hasattr(self.campos.get('reforco'), 'setChecked'):
                self.campos['reforco'].setChecked(bool(prod.get('reforco')))
        except Exception:
            pass
    except Exception:
        pass
