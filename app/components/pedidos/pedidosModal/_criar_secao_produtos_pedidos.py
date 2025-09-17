from PyQt6.QtWidgets import QGroupBox, QFormLayout
from PyQt6.QtGui import QFont

from app.components.pedidos.ui.produtos_ui import criar_produtos_ui


def _criar_secao_produtos_pedidos(self, layout, pedido_data):
    # Cria UI (separada em ui/produtos_ui.py)
    widgets = criar_produtos_ui(self, layout, pedido_data)

    # Mapear widgets para os nomes já usados pelo modal
    self.input_desc = widgets['input_desc']
    self.input_valor = widgets['input_valor']
    self.campos['cor'] = widgets['campos_cor']
    # nova tabela de produtos (aceita ambos os nomes para compatibilidade)
    self.lista_produtos_table = widgets.get('lista_table') or widgets.get('lista_produtos_table')
    # Se ainda não encontrou, tentar procurar por outros nomes comuns
    if self.lista_produtos_table is None:
        possible = ['lista_table', 'lista_produtos_table', 'lista_produtos_container', 'lista_container']
        for k in possible:
            if k in widgets and widgets.get(k) is not None:
                self.lista_produtos_table = widgets.get(k)
                break
    self.campos['valor_total'] = widgets['valor_total']

    # conectar botões aos delegados
    try:
        widgets['btn_limpar'].clicked.connect(self._limpar_campos_produto)
    except Exception:
        pass
    # Conectar botão adicionar
    try:
        widgets['btn_add'].clicked.connect(self._add_produto)
    except Exception:
        pass

    # Completer e carregamento de catálogo (mantém lógica existente)
    try:
        self._carregar_produtos()
        try:
            self._montar_produtos_completer()
        except Exception:
            pass
    except Exception:
        pass

    # permitir adicionar com Enter
    try:
        self.input_valor.returnPressed.connect(self._add_produto)
        self.input_desc.returnPressed.connect(self._add_produto)
    except Exception:
        pass

    # Inicializar lista interna e preencher a partir de pedido_data
    try:
        if not hasattr(self, 'produtos_list') or self.produtos_list is None:
            self.produtos_list = []
    except Exception:
        self.produtos_list = []
    if pedido_data:
        # Prefer structured produtos saved in dados_json (new format)
        produtos_struct = pedido_data.get('produtos') if isinstance(pedido_data.get('produtos'), (list, tuple)) else None
        if produtos_struct:
            try:
                for p in produtos_struct:
                    try:
                        desc = str(p.get('descricao') or p.get('nome') or '').strip()
                        valor = float(p.get('valor') or p.get('preco') or 0)
                        cor = p.get('cor') if 'cor' in p else ''
                    except Exception:
                        desc = str(p.get('descricao') or '').strip()
                        try:
                            valor = float(str(p.get('valor') or '0').replace(',', '.'))
                        except Exception:
                            valor = 0.0
                        cor = p.get('cor') if 'cor' in p else ''
                    # Mark source as DB for clarity
                    self.produtos_list.append({"descricao": desc, "valor": valor, "cor": cor, "_source": "db"})
            except Exception:
                pass
        else:
            detalhes = pedido_data.get('detalhes_produto', '') or ''
            try:
                linhas = [l.strip() for l in detalhes.replace('\r', '\n').split('\n') if l.strip() and not l.strip().startswith('-')]
                for linha in linhas:
                    if ' - R$ ' in linha:
                        try:
                            desc, valtxt = linha.rsplit(' - R$ ', 1)
                            valor = float(valtxt.replace('.', '').replace(',', '.')) if valtxt else 0.0
                            self.produtos_list.append({"descricao": desc.strip('• ').strip(), "valor": valor})
                        except Exception:
                            self.produtos_list.append({"descricao": linha.strip('• ').strip(), "valor": 0.0})
                    else:
                        self.produtos_list.append({"descricao": linha.strip('• ').strip(), "valor": 0.0})
            except Exception:
                pass

    # Renderizar a lista na tabela
    try:
        # Garantir que exista uma tabela; se não existir, apenas logar
        if getattr(self, 'lista_produtos_table', None) is None:
            print('[DEBUG] Aviso: nenhuma tabela de produtos encontrada no modal ao criar seção')
        else:
            self._refresh_produtos_ui()
    except Exception:
        pass
