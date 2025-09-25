
# Nenhum widget PyQt6 usado diretamente, mas garantir import se necessário
from .__init__ import PedidosModal

def _add_produto(self):
    def parse_valor(val):
        """Converte texto em valor float, removendo R$ e trocando , por ."""
        try:
            if not val:
                return 0.0
            val = str(val).replace('R$', '').replace(' ', '').replace(',', '.')
            return float(val)
        except:
            return 0.0


    # Pegar valores dos campos
    desc = (self.input_desc.text() or '').strip()
    val_text = (self.input_valor.text() or '').strip()
    quantidade = 1  # valor padrão
    
    # Capturar quantidade se o campo existir
    try:
        if hasattr(self, 'input_quantidade') and self.input_quantidade:
            quantidade = self.input_quantidade.value()
        else:
            quantidade = 1
    except Exception:
        quantidade = 1


    # Validação: verificar se campos obrigatórios estão preenchidos
    if not desc:
        return
    
    if not val_text or val_text == '0' or val_text == '0.00' or val_text == '0,00':
        return

    # Se descrição vem com preço anexado "Nome | R$ 123,45" e campo valor está vazio, extrair
    if '|' in desc and 'R$' in desc and not val_text:
        try:
            nome_parte, resto = desc.split('|', 1)
            desc = nome_parte.strip()
            parte = resto.split('R$')[-1].strip()
            val_text = parte
        except Exception as e:
            pass

    # Converter valor do campo (prioridade máxima)
    valor = parse_valor(val_text)

    # Buscar produto no catálogo para pegar código e preço correto
    codigo_val = ''
    produto_encontrado = None
    
    try:
        pdict = getattr(self, 'produtos_dict', None) or {}
        
        # Busca 1: Nome exato
        if desc in pdict:
            produto_encontrado = pdict[desc]
        
        # Busca 2: Nome case-insensitive  
        elif desc.lower() in pdict:
            produto_encontrado = pdict[desc.lower()]
        
        # Busca 3: Busca manual case-insensitive
        else:
            for key, produto in pdict.items():
                if produto.get('nome', '').lower() == desc.lower():
                    produto_encontrado = produto
                    break
        
        # Se encontrou o produto, usar dados do catálogo
        if produto_encontrado:
            codigo_val = produto_encontrado.get('codigo', '')
            preco_catalogo = produto_encontrado.get('preco', 0)
            nome_catalogo = produto_encontrado.get('nome', desc)
            
            # SEMPRE usar preço do catálogo se disponível
            if preco_catalogo and preco_catalogo > 0:
                valor = float(preco_catalogo)
                desc = nome_catalogo  # Normalizar nome
        else:
            pass  # Produto não encontrado no catálogo
            
    except Exception as e:
        import traceback
        traceback.print_exc()

    # Capturar cor selecionada
    cor_sel = ''
    try:
        combo_cor = self.campos.get('cor')
        if combo_cor:
            cor = combo_cor.currentText().strip()
            cor_sel = '' if cor in ('Selecione uma cor', '') else cor
    except Exception as e:
        pass

    # Capturar reforço se existir
    reforco_sel = False
    try:
        reforco_widget = self.campos.get('reforco')
        if reforco_widget:
            if hasattr(reforco_widget, 'isChecked'):
                reforco_sel = reforco_widget.isChecked()
            else:
                texto = reforco_widget.currentText().strip().lower() if hasattr(reforco_widget, 'currentText') else ''
                reforco_sel = texto == 'sim'
    except Exception as e:
        pass

    # Aplicar acréscimo se tem reforço
    if reforco_sel:
        valor += 15.0

    # Garantir que a lista existe
    if not hasattr(self, 'produtos_list') or self.produtos_list is None:
        self.produtos_list = []

    # Montar produto para adicionar (incluir codigo e quantidade se disponível)
    produto = {
        'descricao': desc,
        'valor': valor,
        'quantidade': quantidade,
        'cor': cor_sel,
        'reforco': reforco_sel,
    }
    if codigo_val:
        produto['codigo'] = codigo_val


    # Adicionar à lista
    self.produtos_list.append(produto)

    # Limpar campos de entrada
    try:
        if hasattr(self, 'input_desc'):
            self.input_desc.clear()
        if hasattr(self, 'input_valor'):
            self.input_valor.clear()
        combo_cor = self.campos.get('cor')
        if combo_cor:
            combo_cor.setCurrentIndex(0)
    except Exception as e:
        pass

    # Atualizar interface
    try:
        self._refresh_produtos_ui()
    except Exception as e:
        pass

