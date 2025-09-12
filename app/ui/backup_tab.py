from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel,
    QFileDialog, QMessageBox, QInputDialog, QPlainTextEdit
)
from PyQt6.QtCore import Qt
from pathlib import Path
import os
from datetime import datetime

from app.backup import criar_backup, restaurar_backup, substituir_por_arquivo, apagar_tudo, apagar_anteriores
from app.ui.category_manager import CategoryManagerDialog
from app.ui.status_manager import StatusManagerDialog
from database.db_setup import DatabaseSetup


class BackupTab(QWidget):
    """Interface simples para operações de backup e limpeza do banco.

    Botões:
    - Criar backup
    - Restaurar (selecionar arquivo .db)
    - Substituir por arquivo (upload/import)
    - Apagar tudo (exige confirmação de texto)
    - Apagar registros anteriores a X anos

    Observação: operações destrutivas mostram confirmações; a UI não força autenticação.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db_path = DatabaseSetup.get_database_path()
        self._backups_dir = os.path.join(os.path.dirname(self._db_path), 'backups')
        os.makedirs(self._backups_dir, exist_ok=True)
        self._build_ui()
        # apply visual polish (colors, spacing, rounded corners)
        self._apply_styles()
        self.refresh_backups()

    def _build_ui(self):
        self.setLayout(QVBoxLayout())
        header = QLabel("Área de Backup")
        header.setObjectName('header')
        header.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.layout().addWidget(header)

        # backups list + controls
        top_row = QHBoxLayout()
        self.backup_list = QListWidget()
        # give list a comfortable minimum size
        self.backup_list.setMinimumHeight(320)
        top_row.addWidget(self.backup_list)

        right_col = QVBoxLayout()
        right_col.setSpacing(12)
        right_col.setContentsMargins(8, 0, 8, 0)

        # action buttons (stacked)
        self.btn_refresh = QPushButton("Atualizar lista")
        self.btn_refresh.clicked.connect(self.refresh_backups)
        right_col.addWidget(self.btn_refresh)

        self.btn_create = QPushButton("Criar backup")
        self.btn_create.clicked.connect(self.on_create_backup)
        right_col.addWidget(self.btn_create)

        self.btn_restore = QPushButton("Restaurar a partir de arquivo")
        self.btn_restore.clicked.connect(self.on_restore_from_file)
        right_col.addWidget(self.btn_restore)

        self.btn_replace = QPushButton("Substituir DB por arquivo")
        self.btn_replace.clicked.connect(self.on_replace_with_file)
        right_col.addWidget(self.btn_replace)

        # category management
        self.btn_manage_categories = QPushButton("Gerenciar categorias")
        self.btn_manage_categories.clicked.connect(self.on_manage_categories)
        right_col.addWidget(self.btn_manage_categories)

        # status management (mirror of categories manager)
        self.btn_manage_statuses = QPushButton("Gerenciar status")
        self.btn_manage_statuses.clicked.connect(self.on_manage_statuses)
        right_col.addWidget(self.btn_manage_statuses)

        # visual tweaks for right column buttons
        for b in (self.btn_refresh, self.btn_create, self.btn_restore, self.btn_replace):
            b.setMinimumHeight(36)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet('padding:6px 12px;')

        # style for manage categories button (same family)
        self.btn_manage_categories.setMinimumHeight(36)
        self.btn_manage_categories.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_manage_categories.setStyleSheet('padding:6px 12px;')

        # style for manage statuses button
        self.btn_manage_statuses.setMinimumHeight(36)
        self.btn_manage_statuses.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_manage_statuses.setStyleSheet('padding:6px 12px;')

        top_row.addLayout(right_col)
        self.layout().addLayout(top_row)

        # bottom row: destructive operations
        bottom_row = QHBoxLayout()
        self.btn_delete_all = QPushButton("Apagar todos os dados")
        self.btn_delete_all.clicked.connect(self.on_delete_all)
        self.btn_delete_all.setMinimumHeight(36)
        bottom_row.addWidget(self.btn_delete_all)

        self.btn_delete_old = QPushButton("Apagar registros > X anos")
        self.btn_delete_old.clicked.connect(self.on_delete_old)
        self.btn_delete_old.setMinimumHeight(36)
        bottom_row.addWidget(self.btn_delete_old)

        self.layout().addLayout(bottom_row)

        # status and logs
        self.status = QLabel("")
        self.status.setObjectName('status')
        self.layout().addWidget(self.status)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(160)
        # nicer monospace and spacing for logs
        self.log.setStyleSheet('font-family: Consolas, "Courier New", monospace; font-size: 11px;')
        self.layout().addWidget(self.log)

        # initial log
        self.add_log('Backup tab carregada')

    def refresh_backups(self):
        self.backup_list.clear()
        p = Path(self._backups_dir)
        if not p.exists():
            self.status.setText('Nenhum diretório de backups encontrado')
            return
        files = sorted(p.glob('*.db'), reverse=True)
        for f in files:
            self.backup_list.addItem(str(f.name))
        self.status.setText(f"DB atual: {os.path.basename(self._db_path)}   |  backups: {len(files)}")
        self.add_log(f'Lista de backups atualizada ({len(files)} arquivos)')

    def on_create_backup(self):
        try:
            path = criar_backup(dest_dir=self._backups_dir)
            QMessageBox.information(self, 'Backup criado', f'Backup criado em:\n{path}')
            self.add_log(f'Backup criado: {path}')
            self.refresh_backups()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao criar backup: {e}')
            self.add_log(f'ERRO ao criar backup: {e}')

    def on_restore_from_file(self):
        fn, _ = QFileDialog.getOpenFileName(self, 'Selecionar arquivo de backup (.db)', self._backups_dir, 'SQLite DB (*.db)')
        if not fn:
            return
        # confirmação
        resp = QMessageBox.question(self, 'Confirmar restauração', 'A restauração substituirá o DB atual. Deseja continuar?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if int(resp) != int(QMessageBox.StandardButton.Yes):
            return
        try:
            restaurar_backup(fn)
            QMessageBox.information(self, 'Restaurado', 'Banco restaurado com sucesso. (Feche e reabra a aplicação para recarregar)')
            self.add_log(f'Restauração feita a partir de: {fn}')
            self.refresh_backups()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao restaurar: {e}')
            self.add_log(f'ERRO ao restaurar: {e}')

    def on_replace_with_file(self):
        fn, _ = QFileDialog.getOpenFileName(self, 'Selecionar arquivo de banco (.db) para substituir o atual', '.', 'SQLite DB (*.db)')
        if not fn:
            return
        resp = QMessageBox.question(self, 'Confirmar substituição', 'Isto substituirá o DB atual por este arquivo. Deseja continuar?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if int(resp) != int(QMessageBox.StandardButton.Yes):
            return
        try:
            substituir_por_arquivo(fn)
            QMessageBox.information(self, 'Substituído', 'DB substituído com sucesso. (Feche e reabra a aplicação para recarregar)')
            self.add_log(f'DB substituído por arquivo: {fn}')
            self.refresh_backups()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao substituir DB: {e}')
            self.add_log(f'ERRO ao substituir DB: {e}')

    def on_delete_all(self):
        # pedir confirmação textual para evitar cliques acidentais
        text, ok = QInputDialog.getText(self, 'Confirmar apagar tudo', 'Digite APAGAR para confirmar:')
        if not ok or text.strip().upper() != 'APAGAR':
            QMessageBox.information(self, 'Cancelado', 'Operação cancelada.')
            return
        # executar operação destrutiva
        try:
            ok = apagar_tudo(confirm=True)
            if ok:
                QMessageBox.information(self, 'Feito', 'Todos os dados foram apagados.')
            else:
                QMessageBox.critical(self, 'Erro', 'Falha ao apagar os dados ou operação não confirmada.')
            self.add_log(f'Apagar tudo executado: sucesso={ok}')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao apagar tudo: {e}')
            self.add_log(f'ERRO ao apagar tudo: {e}')

    def on_delete_old(self):
        anos, ok = QInputDialog.getInt(self, 'Apagar registros antigos', 'Apagar registros anteriores a quantos anos?', value=1, min=1, max=50)
        if not ok:
            return
        try:
            res = apagar_anteriores(anos=anos)
            # mostrar resumo
            lines = [f"{t}: {c} registros removidos" for t, c in res.items()]
            QMessageBox.information(self, 'Resultados', '\n'.join(lines) if lines else 'Nenhum registro removido.')
            # log
            summary = '\n'.join(lines) if lines else 'Nenhum registro removido.'
            self.add_log(f'Apagar anteriores ({anos} anos) executado:\n{summary}')
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Falha ao apagar registros antigos: {e}')
            self.add_log(f'ERRO ao apagar registros antigos: {e}')

    def add_log(self, message: str):
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # manter uma linha por mensagem; se multiline, separar
        for line in str(message).split('\n'):
            self.log.appendPlainText(f'[{ts}] {line}')
        # also update status briefly
        self.status.setText(f'Última ação: {ts}')

    def on_manage_categories(self):
        dlg = CategoryManagerDialog(self)
        if dlg.exec():
            # saved — notify and refresh any UI that depends on categories
            self.add_log('Categorias atualizadas via Gerenciar categorias')
            # future: emit signal or refresh product dialogs if needed

    def on_manage_statuses(self):
        dlg = StatusManagerDialog(self)
        if dlg.exec():
            self.add_log('Status atualizados via Gerenciar status')
            # future: emit signal or refresh pedidos UI if needed

    def _apply_styles(self):
        """Apply a compact dark stylesheet with subtle rounded panels."""
        style = """
        QWidget { background: #262626; color: #e6e6e6; }
        QLabel#header { color: #ffffff; font-weight: 600; font-size: 16px; }
        QLabel#status { color: #bdbdbd; padding: 4px 6px; }
        QListWidget { background: #1f1f1f; border: 1px solid #393939; border-radius: 6px; padding: 6px; }
        QPushButton { background: #323232; border: 1px solid #444444; border-radius: 6px; color: #eaeaea; }
        QPushButton:hover { background: #3d3d3d; }
        QPlainTextEdit { background: #141414; border: 1px solid #333333; border-radius: 6px; }
        """
        self.setStyleSheet(style)
        # make right column buttons visually consistent width
        maxw = 180
        for b in (self.btn_refresh, self.btn_create, self.btn_restore, self.btn_replace):
            b.setMaximumWidth(maxw)
        # status bar subtle background
        self.status.setStyleSheet('background: transparent;')
