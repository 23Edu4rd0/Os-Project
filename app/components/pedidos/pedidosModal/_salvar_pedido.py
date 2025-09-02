from PyQt6.QtWidgets import QMessageBox
from app.numero_os import Contador
from database import db_manager

def _format_currency(val):
    try:
        return float(str(val).replace('R$', '').replace(' ', '').replace(',', '.'))
    except Exception:
        return 0.0


def _salvar_pedido(self, numero_os=None, pedido_data=None):
    """Coleta campos do modal e salva (ou atualiza) a ordem no banco."""
    try:
        # Cliente
        nome_cliente = (self.campos.get('nome_cliente') and self.campos['nome_cliente'].text()) or ''
        cpf_cliente = (self.campos.get('cpf_cliente') and self.campos['cpf_cliente'].text()) or ''
        telefone_cliente = (self.campos.get('telefone_cliente') and self.campos['telefone_cliente'].text()) or ''

        # Produtos -> monta texto e soma valores
        linhas = []
        total_produtos = 0.0
        for p in getattr(self, 'produtos_list', []):
            desc = p.get('descricao', '')
            valor = float(p.get('valor', 0) or 0)
            extras = []
            if p.get('cor'):
                extras.append(f"Cor: {p.get('cor')}")
            if 'reforco' in p:
                extras.append(f"Reforço: {'sim' if p.get('reforco') else 'não'}")
            extras_txt = ("  —  " + "  |  ".join(extras)) if extras else ""
            # Formatação simples para salvar
            linhas.append(f"• {desc}{extras_txt} - R$ {valor:.2f}")
            total_produtos += valor
        detalhes_produto = "\n".join(linhas)

        # Pagamento / valores
        try:
            valor_entrada = _format_currency(self.campos.get('entrada').text()) if self.campos.get('entrada') else 0.0
        except Exception:
            valor_entrada = 0.0
        try:
            frete = _format_currency(self.campos.get('frete').text()) if self.campos.get('frete') else 0.0
        except Exception:
            frete = 0.0
        try:
            desconto = _format_currency(self.campos.get('desconto').text()) if self.campos.get('desconto') else 0.0
        except Exception:
            desconto = 0.0

        forma_pagamento = (self.campos.get('forma_pagamento') and self.campos['forma_pagamento'].currentText()) or ''
        try:
            prazo = int(self.campos.get('prazo_entrega').text()) if self.campos.get('prazo_entrega') and self.campos['prazo_entrega'].text() else 0
        except Exception:
            prazo = 0

        # Ordem-level cor/reforco (campos podem ser checkbox/combo)
        try:
            cor = (self.campos.get('cor') and (self.campos['cor'].currentText() if hasattr(self.campos['cor'], 'currentText') else str(self.campos['cor'].text()))) or ''
        except Exception:
            cor = ''
        try:
            reforco_widget = self.campos.get('reforco')
            if reforco_widget is None:
                reforco = False
            elif hasattr(reforco_widget, 'isChecked'):
                reforco = bool(reforco_widget.isChecked())
            else:
                reforco = (reforco_widget.currentText() if hasattr(reforco_widget, 'currentText') else '').strip().lower() == 'sim'
        except Exception:
            reforco = False

        # Número da OS
        if numero_os is None:
            try:
                contador = Contador()
                numero = contador.get_proximo_numero()
            except Exception:
                numero = 0
        else:
            numero = numero_os

        dados = {
            'numero_os': numero,
            'nome_cliente': nome_cliente,
            'cpf_cliente': cpf_cliente,
            'telefone_cliente': telefone_cliente,
            'detalhes_produto': detalhes_produto,
            'valor_produto': float(total_produtos),
            'valor_entrada': float(valor_entrada),
            'frete': float(frete),
            'forma_pagamento': forma_pagamento,
            'prazo': int(prazo or 0),
            'status': (self.campos.get('status') and self.campos['status'].currentText()) or 'em produção',
            'desconto': float(desconto or 0.0),
            'cor': cor,
            'reforco': bool(reforco)
        }

        # Attach structured produtos list (descricao, valor) so CRUD can compute totals reliably
        structured = []
        for p in getattr(self, 'produtos_list', []):
            try:
                desc = str(p.get('descricao') or '').strip()
                valor = float(p.get('valor') or 0)
            except Exception:
                desc = str(p.get('descricao') or '').strip()
                try:
                    valor = float(str(p.get('valor') or '0').replace(',', '.'))
                except Exception:
                    valor = 0.0
            structured.append({'descricao': desc, 'valor': valor, 'cor': p.get('cor'), 'reforco': p.get('reforco')})
        dados['produtos'] = structured

        # Salvar novo ou atualizar existente
        if not pedido_data:
            ok = db_manager.salvar_ordem(dados, "")
            if ok:
                try:
                    QMessageBox.information(self, "Sucesso", f"Pedido salvo com sucesso! OS #{numero:05d}")
                except Exception:
                    pass
                try:
                    self.pedido_salvo.emit()
                except Exception:
                    pass
                try:
                    self.accept()
                except Exception:
                    pass
                return True
            else:
                try:
                    QMessageBox.critical(self, "Erro", "Falha ao salvar pedido no banco de dados.")
                except Exception:
                    pass
                return False
        else:
            # Atualizar colunas simples
            try:
                pedido_id = pedido_data.get('id')
                campos = {
                    'nome_cliente': dados['nome_cliente'],
                    'cpf_cliente': dados['cpf_cliente'],
                    'telefone_cliente': dados['telefone_cliente'],
                    'detalhes_produto': dados['detalhes_produto'],
                    'valor_produto': dados['valor_produto'],
                    'valor_entrada': dados['valor_entrada'],
                    'frete': dados['frete'],
                    'forma_pagamento': dados['forma_pagamento'],
                    'prazo': dados['prazo']
                }
                resp = db_manager.atualizar_pedido(pedido_id, campos)
                # atualizar JSON com status/desconto/cor/reforco
                _ = db_manager.atualizar_json_campos(pedido_id, {
                    'status': dados['status'],
                    'desconto': dados['desconto'],
                    'cor': dados['cor'],
                    'reforco': dados['reforco']
                })
                if resp:
                    try:
                        QMessageBox.information(self, "Sucesso", "Pedido atualizado com sucesso!")
                    except Exception:
                        pass
                    try:
                        self.pedido_salvo.emit()
                    except Exception:
                        pass
                    try:
                        self.accept()
                    except Exception:
                        pass
                    return True
                else:
                    try:
                        QMessageBox.critical(self, "Erro", "Falha ao atualizar pedido no banco de dados.")
                    except Exception:
                        pass
                    return False
            except Exception as e:
                try:
                    QMessageBox.critical(self, "Erro", f"Erro ao atualizar pedido: {e}")
                except Exception:
                    pass
                return False

    except Exception as e:
        try:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar pedido: {e}")
        except Exception:
            pass
        return False
