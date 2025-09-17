
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget, QTableWidgetItem
from .__init__ import PedidosModal

def _refresh_produtos_ui(self):
    from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout, QPushButton
    print('[DEBUG] Iniciando _refresh_produtos_ui...')
    try:
        # localizar a tabela em múltiplos atributos possíveis
        table = getattr(self, 'lista_produtos_table', None) or getattr(self, 'lista_table', None) or getattr(self, 'lista_produtos_container', None)
        print(f'[DEBUG] Tabela encontrada: {table is not None}')
        
        # criar fallback mínimo se necessário (não anexa ao layout automaticamente)
        if table is None:
            print('[DEBUG] Nenhuma tabela encontrada. Criando tabela fallback mínima (não anexada).')
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['Produto', 'Valor', 'Cor', 'Ações'])
            self.lista_produtos_table = table

        produtos_list = getattr(self, 'produtos_list', []) or []
        print(f'[DEBUG] Lista de produtos tem {len(produtos_list)} itens')

        # Limpar e preencher tabela
        table.setRowCount(0)

        # Detectar índices das colunas com base nos rótulos do header (tolerante a variações)
        def _find_col(keywords):
            for i in range(table.columnCount()):
                try:
                    hdr = table.horizontalHeaderItem(i)
                    txt = hdr.text().lower() if hdr else ''
                except Exception:
                    txt = ''
                for kw in keywords:
                    if kw in txt:
                        return i
            return None

        name_col = _find_col(['nome', 'produto'])
        code_col = _find_col(['cód', 'cod', 'codigo'])
        valor_col = _find_col(['valor'])
        cor_col = _find_col(['cor'])
        acoes_col = _find_col(['ação', 'acao', 'ações', 'acoes', 'aç'])

        # Fallbacks conforme o número de colunas
        if table.columnCount() >= 5:
            name_col = 0 if name_col is None else name_col
            code_col = 1 if code_col is None else code_col
            valor_col = 2 if valor_col is None else valor_col
            cor_col = 3 if cor_col is None else cor_col
            acoes_col = 4 if acoes_col is None else acoes_col
            # Ajustar larguras para layout com código
            try:
                table.setColumnWidth(code_col, 80)
                table.setColumnWidth(valor_col, 120)
                table.setColumnWidth(cor_col, 120)
                table.setColumnWidth(acoes_col, 220)
            except Exception:
                pass
        else:
            # layout clássico com 4 colunas: Produto, Valor, Cor, Ações
            name_col = 0 if name_col is None else name_col
            valor_col = 1 if valor_col is None else valor_col
            cor_col = 2 if cor_col is None else cor_col
            acoes_col = 3 if acoes_col is None else acoes_col
            try:
                table.setColumnWidth(valor_col, 140)
                table.setColumnWidth(cor_col, 120)
                table.setColumnWidth(acoes_col, 220)
            except Exception:
                pass

        for idx, prod in enumerate(produtos_list):
            table.insertRow(idx)
            desc = prod.get('descricao') or ''
            valor = prod.get('valor') or 0.0
            cor = prod.get('cor') or ''
            db_marker = '' if prod.get('_source') != 'db' else '[DB] '

            # Nome/Descrição
            desc_item = QTableWidgetItem(f"{db_marker}{desc}")
            table.setItem(idx, name_col, desc_item)

            # Código (se houver campo de código no objeto)
            codigo_val = prod.get('codigo') or prod.get('cod') or prod.get('sku') or ''
            if code_col is not None and codigo_val:
                table.setItem(idx, code_col, QTableWidgetItem(str(codigo_val)))

            # Valor/Preço
            try:
                valor_item = QTableWidgetItem(f"R$ {float(valor):.2f}")
            except Exception:
                valor_item = QTableWidgetItem(str(valor))
            table.setItem(idx, valor_col, valor_item)

            # Cor
            cor_item = QTableWidgetItem(cor if cor else "-")
            table.setItem(idx, cor_col, cor_item)

            # ações (botões maiores e centralizados)
            btn_widget = QWidget()
            layout = QHBoxLayout(btn_widget)
            layout.setContentsMargins(6, 6, 6, 6)
            layout.setSpacing(10)
            btn_edit = QPushButton('Editar')
            btn_edit.setFixedSize(84, 32)
            btn_edit.clicked.connect(lambda _, i=idx: self._editar_produto(i))
            btn_rem = QPushButton('Remover')
            btn_rem.setFixedSize(84, 32)
            btn_rem.clicked.connect(lambda _, i=idx: self._remove_produto(i))
            layout.addWidget(btn_edit)
            layout.addWidget(btn_rem)
            table.setCellWidget(idx, acoes_col, btn_widget)

            # Assegurar que cor e código apareçam (caso estejam vazios, preencher com '-')
            if code_col is not None and not table.item(idx, code_col):
                table.setItem(idx, code_col, QTableWidgetItem(str(codigo_val) if codigo_val else '-'))
            if not table.item(idx, cor_col):
                table.setItem(idx, cor_col, QTableWidgetItem(cor if cor else '-'))

            # Ajustar altura da linha para melhor visual
            try:
                table.setRowHeight(idx, 48)
            except Exception:
                pass

        print(f'[DEBUG] Tabela atualizada com {table.rowCount()} linhas')

        # Atualizar total
        try:
            total = sum(float(p.get('valor', 0) or 0) for p in produtos_list)
            if hasattr(self, 'campos') and 'valor_total' in self.campos:
                self.campos['valor_total'].setText(f"R$ {total:.2f}")
                print(f'[DEBUG] Total atualizado: R$ {total:.2f}')
        except Exception as e:
            print(f'[DEBUG] Erro ao atualizar total: {e}')

        print('[DEBUG] _refresh_produtos_ui concluído!')
    except Exception as e:
        print(f'[DEBUG] Erro em _refresh_produtos_ui: {e}')
        import traceback
        traceback.print_exc()
