
from PyQt6.QtWidgets import QCompleter
from PyQt6.QtCore import Qt
from .__init__ import PedidosModal

def _montar_produtos_completer(self, categoria: str | None = None):
    def parse_preco_seguro(valor):
        """Converte valor para float de forma segura, retornando 0.0 se inválido"""
        try:
            if valor is None:
                return 0.0
            valor_str = str(valor).replace('R$', '').replace(' ', '').replace(',', '.')
            return float(valor_str)
        except:
            return 0.0
    
    try:
        dic = {}
        source = getattr(self, '_produtos_rows', [])
        for r in source:
            if categoria and categoria != "Todas" and (r[4] or "") != categoria:
                continue
            nome = (r[1] or '').strip()
            preco = parse_preco_seguro(r[2])  # Usar função segura
            # Mapear reforco e cor se presentes no row
            reforco = None
            cor = None
            try:
                if len(r) >= 6:
                    # tentar posições conhecidas
                    # (id, nome, preco, reforco_or_descricao, categoria, criado_em)
                    if isinstance(r[3], (int, bool)):
                        reforco = bool(r[3])
                    else:
                        # pode ser cor ou descricao; assumir texto => cor
                        cor = r[3]
                    # categoria está em r[4]
            except Exception:
                pass
            display = nome
            dic[display] = {"id": r[0], "nome": nome, "preco": preco, "categoria": (r[4] or ''), 'reforco': reforco, 'cor': cor}
        self.produtos_dict = dic
        if dic:
            # criar completer somente com nomes (comportamento similar a clientes)
            self.produtos_completer = QCompleter(list(dic.keys()))
            self.produtos_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.produtos_completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.input_desc.setCompleter(self.produtos_completer)
            try:
                self.produtos_completer.activated[str].disconnect()
            except Exception:
                pass
            self.produtos_completer.activated[str].connect(self._on_produto_completer_activated)
    except Exception:
        pass
