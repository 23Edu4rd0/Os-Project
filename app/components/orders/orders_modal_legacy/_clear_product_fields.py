def limpar_campos_produto(self):
    # Campos usados na seção de produtos: input_desc, input_valor
    try:
        if hasattr(self, 'input_desc') and self.input_desc is not None:
            try:
                self.input_desc.clear()
            except Exception:
                pass
        if hasattr(self, 'input_valor') and self.input_valor is not None:
            try:
                self.input_valor.clear()
            except Exception:
                pass
        # Limpar quantidade e resetar para 1
        if hasattr(self, 'input_quantidade') and self.input_quantidade is not None:
            try:
                self.input_quantidade.setValue(1)
            except Exception:
                pass
        # cor and divisórias
        if 'cor' in getattr(self, 'campos', {}):
            try:
                w = self.campos['cor']
                if hasattr(w, 'setCurrentIndex'):
                    w.setCurrentIndex(0)
            except Exception:
                pass
                pass
        # reset base price
        try:
            self._base_produto_valor = 0.0
        except Exception:
            pass
        try:
            # focar no campo de descrição do produto para entrada rápida
            if hasattr(self, 'input_desc'):
                self.input_desc.setFocus()
        except Exception:
            pass
    except Exception:
        pass
