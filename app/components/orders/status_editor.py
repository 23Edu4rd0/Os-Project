from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtGui import QCursor
from database import db_manager
import json


def show_status_menu(parent, pedido_id):
    """Abre um menu no cursor para alterar o status do pedido.

    Este helper busca o status atual do pedido, marca a opção correspondente
    no menu e atualiza o pedido ao selecionar uma ação.
    """
    try:
        # Buscar status atual do pedido (dados_json)
        current_status = ''
        try:
            db_manager.cursor.execute('SELECT dados_json FROM ordem_servico WHERE id = ?', (pedido_id,))
            row = db_manager.cursor.fetchone()
            if row and row[0]:
                try:
                    dados = json.loads(row[0])
                    current_status = dados.get('status', '')
                except Exception:
                    current_status = ''
        except Exception:
            current_status = ''

        menu = QMenu(parent)
        # load statuses from centralized storage so all UIs use the same set
        try:
            from app.utils.statuses import load_statuses
            statuses = load_statuses()
        except Exception:
            statuses = ["em produção", "pronto", "entregue", "cancelado"]
        for s in statuses:
            act = menu.addAction(s)
            act.setCheckable(True)
            if s == current_status:
                act.setChecked(True)

            def make_handler(status):
                def handler():
                    try:
                        ok = db_manager.atualizar_status_pedido(pedido_id, status)
                        if ok:
                            # atualiza célula na UI se possível para feedback imediato
                            try:
                                tbl = getattr(parent, 'orders_table', None)
                                if tbl is not None:
                                    # procurar row com id na coluna 0
                                    for r in range(tbl.rowCount()):
                                        it = tbl.item(r, 0)
                                        if it and str(it.text()) == str(pedido_id):
                                            tbl.setItem(r, 5, tbl.item(r, 5) or None)
                                            from PyQt6.QtWidgets import QTableWidgetItem
                                            tbl.setItem(r, 5, QTableWidgetItem(str(status)))
                                            break
                            except Exception:
                                pass

                            # tente recarregar a interface se o parent fornecer este método
                            try:
                                parent.carregar_pedidos()
                            except Exception:
                                pass
                            # também tente atualizar a aba Pedidos no app principal
                            try:
                                from PyQt6.QtWidgets import QApplication
                                for w in QApplication.topLevelWidgets():
                                    if hasattr(w, 'pedidos_manager'):
                                        try:
                                            w.pedidos_manager.carregar_dados(force_refresh=True)
                                            break
                                        except Exception:
                                            pass
                            except Exception:
                                pass
                            # Also refresh any open Cliente detail dialogs or other widgets
                            # that expose a `carregar_pedidos` method so their tables update.
                            try:
                                from PyQt6.QtWidgets import QApplication
                                for w in QApplication.topLevelWidgets():
                                    try:
                                        if hasattr(w, 'carregar_pedidos') and callable(getattr(w, 'carregar_pedidos')):
                                            try:
                                                w.carregar_pedidos()
                                            except Exception:
                                                pass
                                    except Exception:
                                        pass
                            except Exception:
                                pass
                        else:
                            QMessageBox.warning(parent, "Erro", "Não foi possível atualizar o status.")
                    except Exception as e:
                        QMessageBox.critical(parent, "Erro", f"Falha ao atualizar status: {e}")
                return handler

            act.triggered.connect(make_handler(s))

        # Mostrar menu no cursor do mouse (global)
        pos = QCursor.pos()
        menu.exec(pos)
    except Exception as e:
        try:
            QMessageBox.critical(parent, "Erro", f"Erro ao abrir menu de status: {e}")
        except Exception:
            pass
