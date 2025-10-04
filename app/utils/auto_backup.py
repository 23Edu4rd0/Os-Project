"""
Sistema de Backup Automático Agendado.

Funcionalidades:
- Backup diário às 23h
- Mantém últimos 30 backups
- Notificações de sucesso/falha
- Limpeza automática de backups antigos
"""

from PyQt6.QtCore import QTimer, QTime, QDateTime, Qt
from PyQt6.QtWidgets import QMessageBox
from datetime import datetime, timedelta
import os
import shutil
from pathlib import Path
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)


class AutoBackupScheduler:
    """Agendador de backups automáticos"""
    
    def __init__(self, parent_widget=None):
        """
        Inicializa o agendador de backups.
        
        Args:
            parent_widget: Widget pai para mostrar notificações
        """
        self.parent = parent_widget
        self.backup_time = QTime(23, 0)  # 23:00 (11 PM)
        self.max_backups = 30
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_backup_time)
        self.last_backup_date = None
        
        logger.info("AutoBackupScheduler inicializado")
    
    def start(self):
        """Inicia o agendador (verifica a cada 1 minuto)"""
        self.timer.start(60000)  # 60000ms = 1 minuto
        logger.info("Agendador de backup iniciado - verificará a cada minuto")
        
        # Verificar imediatamente se precisa fazer backup
        self._check_backup_time()
    
    def stop(self):
        """Para o agendador"""
        self.timer.stop()
        logger.info("Agendador de backup parado")
    
    def _check_backup_time(self):
        """Verifica se chegou a hora do backup"""
        now = QDateTime.currentDateTime()
        current_time = now.time()
        current_date = now.date()
        
        # Verifica se é a hora do backup (23:00)
        # Considera uma janela de 1 minuto (23:00 - 23:01)
        hora_backup = current_time.hour() == self.backup_time.hour()
        minuto_backup = current_time.minute() == self.backup_time.minute()
        
        # Verifica se já fez backup hoje
        hoje_str = current_date.toString("yyyy-MM-dd")
        
        if hora_backup and minuto_backup and self.last_backup_date != hoje_str:
            logger.info(f"Hora do backup automático: {current_time.toString()}")
            self._execute_backup()
            self.last_backup_date = hoje_str
    
    def _execute_backup(self):
        """Executa o backup"""
        try:
            logger.info("Iniciando backup automático...")
            
            # Fazer backup
            sucesso, mensagem = self.create_backup()
            
            if sucesso:
                logger.info(f"Backup automático concluído: {mensagem}")
                self._notify_success(mensagem)
                
                # Limpar backups antigos
                removidos = self.cleanup_old_backups()
                if removidos > 0:
                    logger.info(f"{removidos} backups antigos removidos")
            else:
                logger.error(f"Falha no backup automático: {mensagem}")
                self._notify_failure(mensagem)
                
        except Exception as e:
            error_msg = f"Erro no backup automático: {str(e)}"
            logger.error(error_msg)
            self._notify_failure(error_msg)
    
    def create_backup(self) -> Tuple[bool, str]:
        """
        Cria um backup do banco de dados.
        
        Returns:
            Tupla (sucesso: bool, mensagem: str)
        """
        try:
            # Caminhos
            db_path = self._get_database_path()
            backup_dir = self._get_backup_dir()
            
            # Garantir que diretório existe
            os.makedirs(backup_dir, exist_ok=True)
            
            # Nome do backup com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_auto_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Copiar banco de dados
            shutil.copy2(db_path, backup_path)
            
            # Verificar se foi criado
            if os.path.exists(backup_path):
                size_mb = os.path.getsize(backup_path) / (1024 * 1024)
                return True, f"Backup criado: {backup_filename} ({size_mb:.2f} MB)"
            else:
                return False, "Arquivo de backup não foi criado"
                
        except FileNotFoundError:
            return False, "Banco de dados não encontrado"
        except PermissionError:
            return False, "Sem permissão para criar backup"
        except Exception as e:
            return False, f"Erro ao criar backup: {str(e)}"
    
    def cleanup_old_backups(self) -> int:
        """
        Remove backups antigos, mantendo apenas os últimos N.
        
        Returns:
            Número de backups removidos
        """
        try:
            backup_dir = self._get_backup_dir()
            
            # Listar todos os backups automáticos
            backups = []
            for filename in os.listdir(backup_dir):
                if filename.startswith("backup_auto_") and filename.endswith(".db"):
                    filepath = os.path.join(backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    backups.append((filepath, mtime))
            
            # Ordenar por data (mais recente primeiro)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            # Remover backups excedentes
            removidos = 0
            for filepath, _ in backups[self.max_backups:]:
                try:
                    os.remove(filepath)
                    removidos += 1
                    logger.info(f"Backup antigo removido: {os.path.basename(filepath)}")
                except Exception as e:
                    logger.error(f"Erro ao remover {filepath}: {e}")
            
            return removidos
            
        except Exception as e:
            logger.error(f"Erro na limpeza de backups: {e}")
            return 0
    
    def get_backup_list(self) -> List[Tuple[str, str, float]]:
        """
        Lista todos os backups automáticos.
        
        Returns:
            Lista de tuplas (nome, data_formatada, tamanho_mb)
        """
        try:
            backup_dir = self._get_backup_dir()
            backups = []
            
            for filename in os.listdir(backup_dir):
                if filename.startswith("backup_auto_") and filename.endswith(".db"):
                    filepath = os.path.join(backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                    
                    # Formatar data
                    date_str = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")
                    
                    backups.append((filename, date_str, size))
            
            # Ordenar por data (mais recente primeiro)
            backups.sort(key=lambda x: x[1], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Erro ao listar backups: {e}")
            return []
    
    def _get_database_path(self) -> str:
        """Retorna o caminho do banco de dados"""
        base_path = os.path.expanduser("~/Documents")
        db_dir = os.path.join(base_path, "OrdemServico")
        return os.path.join(db_dir, "ordem_servico.db")
    
    def _get_backup_dir(self) -> str:
        """Retorna o diretório de backups automáticos"""
        base_path = os.path.expanduser("~/Documents")
        return os.path.join(base_path, "OrdemServico", "BackupsAutomaticos")
    
    def _notify_success(self, mensagem: str):
        """Notifica sucesso do backup"""
        if self.parent:
            try:
                msg = QMessageBox(self.parent)
                msg.setWindowTitle("✅ Backup Automático")
                msg.setText(f"Backup realizado com sucesso!\n\n{mensagem}")
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowModality(Qt.WindowModality.NonModal)
                
                # Auto-close após 10 segundos
                QTimer.singleShot(10000, msg.accept)
                msg.show()
            except Exception as e:
                logger.error(f"Erro ao mostrar notificação: {e}")
    
    def _notify_failure(self, mensagem: str):
        """Notifica falha do backup"""
        if self.parent:
            try:
                msg = QMessageBox(self.parent)
                msg.setWindowTitle("❌ Falha no Backup Automático")
                msg.setText(f"Erro ao realizar backup:\n\n{mensagem}")
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowModality(Qt.WindowModality.NonModal)
                
                # Não fecha automaticamente (erro é importante)
                msg.show()
            except Exception as e:
                logger.error(f"Erro ao mostrar notificação de falha: {e}")
    
    def set_backup_time(self, hour: int, minute: int):
        """
        Define novo horário para backup automático.
        
        Args:
            hour: Hora (0-23)
            minute: Minuto (0-59)
        """
        self.backup_time = QTime(hour, minute)
        logger.info(f"Horário de backup alterado para {hour:02d}:{minute:02d}")
    
    def set_max_backups(self, max_backups: int):
        """
        Define quantidade máxima de backups a manter.
        
        Args:
            max_backups: Número máximo de backups
        """
        self.max_backups = max_backups
        logger.info(f"Máximo de backups alterado para {max_backups}")
    
    def force_backup_now(self) -> Tuple[bool, str]:
        """
        Força um backup imediato (manual).
        
        Returns:
            Tupla (sucesso: bool, mensagem: str)
        """
        logger.info("Backup manual forçado")
        sucesso, mensagem = self.create_backup()
        
        if sucesso:
            removidos = self.cleanup_old_backups()
            if removidos > 0:
                mensagem += f"\n{removidos} backups antigos removidos"
        
        return sucesso, mensagem


# Instância global do agendador
_auto_backup_scheduler = None

def get_auto_backup_scheduler(parent=None) -> AutoBackupScheduler:
    """Retorna a instância global do agendador de backups"""
    global _auto_backup_scheduler
    if _auto_backup_scheduler is None:
        _auto_backup_scheduler = AutoBackupScheduler(parent)
    return _auto_backup_scheduler
