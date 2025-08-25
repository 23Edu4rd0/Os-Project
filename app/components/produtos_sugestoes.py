from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from app.utils.produtos_busca import buscar_produtos_por_nome
from PyQt6.QtCore import Qt

def setup_produtos_sugestoes(modal):
    """
    Adiciona sugestões/autocomplete de produtos ao campo input_desc do modal.
    """
    def buscar_sugestoes_produtos(texto):
        texto = texto.strip()
        if not texto:
            modal.sugestoes_produtos.hide()
            return
        produtos = buscar_produtos_por_nome(texto, limite=8)
        modal.sugestoes_produtos.clear()
        for prod in produtos:
            nome = prod['nome']
            valor = prod['preco']
            # Corrige valores absurdos vindos do banco (centavos)
            if valor > 9999:
                valor = valor / 100
            categoria = prod['categoria']
            item = QListWidgetItem(f"{nome} | R$ {valor:.2f} | {categoria}")
            prod_corrigido = prod.copy(); prod_corrigido['preco'] = valor
            item.setData(Qt.ItemDataRole.UserRole, prod_corrigido)
            modal.sugestoes_produtos.addItem(item)
        if modal.sugestoes_produtos.count() > 0:
            modal.sugestoes_produtos.setMinimumWidth(modal.input_desc.width())
            modal.sugestoes_produtos.move(modal.input_desc.mapToGlobal(modal.input_desc.rect().bottomLeft()))
            modal.sugestoes_produtos.show()
        else:
            modal.sugestoes_produtos.hide()

    def preencher_produto_sugestao(item):
        prod = item.data(Qt.ItemDataRole.UserRole)
        modal.input_desc.setText(str(prod['nome']) if prod['nome'] is not None else "")
        try:
            valor = float(prod['preco']) if prod['preco'] is not None else 0.0
            if valor > 9999:
                valor = valor / 100
        except Exception:
            valor = 0.0
        modal.input_valor.setText(f"{valor:.2f}")
        # Preencher reforço e cor se campos existirem
        if hasattr(modal, 'campos'):
            if 'reforco' in modal.campos:
                reforco_val = prod.get('reforco', False)
                is_ref = reforco_val in [1, True, '1', 'Sim', 'sim', 'True', 'true']
                try:
                    ref_w = modal.campos['reforco']
                    if hasattr(ref_w, 'setChecked'):
                        ref_w.setChecked(bool(is_ref))
                    else:
                        reforco_txt = 'sim' if is_ref else 'não'
                        idx = ref_w.findText(reforco_txt)
                        if idx >= 0:
                            ref_w.setCurrentIndex(idx)
                except Exception:
                    pass
            if 'cor' in modal.campos:
                cor_val = prod.get('cor', None)
                if cor_val:
                    try:
                        idx = modal.campos['cor'].findText(str(cor_val))
                        if idx >= 0:
                            modal.campos['cor'].setCurrentIndex(idx)
                    except Exception:
                        pass
        modal.sugestoes_produtos.hide()

    modal.input_desc.textEdited.connect(buscar_sugestoes_produtos)
    modal.sugestoes_produtos.itemClicked.connect(preencher_produto_sugestao)
