
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

    print('[DEBUG] Iniciando _add_produto...')

    # Pegar valores dos campos
    desc = (self.input_desc.text() or '').strip()
    val_text = (self.input_valor.text() or '').strip()

    print(f'[DEBUG] Valores iniciais - Descrição: "{desc}", Valor campo: "{val_text}"')

    # Validação: verificar se campos obrigatórios estão preenchidos
    if not desc:
        print('[DEBUG] Descrição vazia, retornando...')
        return
    
    if not val_text or val_text == '0' or val_text == '0.00' or val_text == '0,00':
        print('[DEBUG] Valor inválido ou vazio, retornando...')
        return

    # Se descrição vem com preço anexado "Nome | R$ 123,45" e campo valor está vazio, extrair
    if '|' in desc and 'R$' in desc and not val_text:
        try:
            nome_parte, resto = desc.split('|', 1)
            desc = nome_parte.strip()
            parte = resto.split('R$')[-1].strip()
            val_text = parte
            print(f'[DEBUG] Valor extraído da descrição: "{val_text}"')
        except Exception as e:
            print(f'[DEBUG] Erro ao extrair valor da descrição: {e}')

    # Converter valor do campo (prioridade máxima)
    valor = parse_valor(val_text)
    print(f'[DEBUG] Valor após parse do campo: {valor}')

    # Buscar produto no catálogo para pegar código e preço correto
    codigo_val = ''
    produto_encontrado = None
    
    try:
        pdict = getattr(self, 'produtos_dict', None) or {}
        print(f'[DEBUG] Buscando "{desc}" no catálogo com {len(pdict)} entradas...')
        
        # Busca 1: Nome exato
        if desc in pdict:
            produto_encontrado = pdict[desc]
            print(f'[DEBUG] ENCONTRADO por nome exato: {produto_encontrado}')
        
        # Busca 2: Nome case-insensitive  
        elif desc.lower() in pdict:
            produto_encontrado = pdict[desc.lower()]
            print(f'[DEBUG] ENCONTRADO por nome lowercase: {produto_encontrado}')
        
        # Busca 3: Busca manual case-insensitive
        else:
            for key, produto in pdict.items():
                if produto.get('nome', '').lower() == desc.lower():
                    produto_encontrado = produto
                    print(f'[DEBUG] ENCONTRADO por busca manual: {produto_encontrado}')
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
                print(f'[DEBUG] ✅ USANDO DADOS DO CATÁLOGO:')
                print(f'[DEBUG]    Nome: {desc}')
                print(f'[DEBUG]    Preço: R$ {valor:.2f}')
                print(f'[DEBUG]    Código: {codigo_val}')
            else:
                print(f'[DEBUG] ⚠️ Produto encontrado mas sem preço válido no catálogo')
        else:
            print(f'[DEBUG] ❌ Produto "{desc}" NÃO encontrado no catálogo')
            print(f'[DEBUG] Usando valor digitado: R$ {valor:.2f}')
            
    except Exception as e:
        print(f'[DEBUG] ERRO ao consultar catálogo: {e}')
        import traceback
        traceback.print_exc()

    # Capturar cor selecionada
    cor_sel = ''
    try:
        combo_cor = self.campos.get('cor')
        if combo_cor:
            cor = combo_cor.currentText().strip()
            cor_sel = '' if cor in ('Selecione uma cor', '') else cor
        print(f'[DEBUG] Cor selecionada: "{cor_sel}"')
    except Exception as e:
        print(f'[DEBUG] Erro ao pegar cor: {e}')

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
        print(f'[DEBUG] Reforço selecionado: {reforco_sel}')
    except Exception as e:
        print(f'[DEBUG] Erro ao pegar reforço: {e}')

    # Aplicar acréscimo se tem reforço
    if reforco_sel:
        valor += 15.0
        print(f'[DEBUG] Valor após acréscimo de reforço: {valor}')

    # Garantir que a lista existe
    if not hasattr(self, 'produtos_list') or self.produtos_list is None:
        self.produtos_list = []
        print('[DEBUG] Lista de produtos inicializada')

    # Montar produto para adicionar (incluir codigo se disponível)
    produto = {
        'descricao': desc,
        'valor': valor,
        'cor': cor_sel,
        'reforco': reforco_sel,
    }
    if codigo_val:
        produto['codigo'] = codigo_val

    print(f'[DEBUG] Produto montado: {produto}')

    # Adicionar à lista
    self.produtos_list.append(produto)
    print(f'[DEBUG] Produto adicionado! Lista tem {len(self.produtos_list)} produtos')

    # Limpar campos de entrada
    try:
        if hasattr(self, 'input_desc'):
            self.input_desc.clear()
        if hasattr(self, 'input_valor'):
            self.input_valor.clear()
        combo_cor = self.campos.get('cor')
        if combo_cor:
            combo_cor.setCurrentIndex(0)
        print('[DEBUG] Campos limpos com sucesso')
    except Exception as e:
        print(f'[DEBUG] Erro ao limpar campos: {e}')

    # Atualizar interface
    try:
        self._refresh_produtos_ui()
        print('[DEBUG] Interface atualizada com sucesso')
    except Exception as e:
        print(f'[DEBUG] Erro ao atualizar interface: {e}')

    print('[DEBUG] _add_produto concluído com sucesso!')
