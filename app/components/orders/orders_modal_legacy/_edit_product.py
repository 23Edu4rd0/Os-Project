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
            if 'cor' in prod and prod.get('cor') and 'cor' in getattr(self, 'campos', {}):
                try:
                    combo_cor = self.campos['cor']
                    idx = combo_cor.findText(prod.get('cor'))
                    if idx >= 0:
                        combo_cor.setCurrentIndex(idx)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            if 'divisorias' in prod and hasattr(self.campos.get('divisorias'), 'setValue'):
                self.campos['divisorias'].setValue(int(prod.get('divisorias', 0)))
        except Exception:
            pass
        try:
            if 'divisorias' in prod and hasattr(self.campos.get('divisorias'), 'setValue'):
                self.campos['divisorias'].setValue(int(prod.get('divisorias', 0)))
        except Exception:
            pass
    except Exception:
        pass
