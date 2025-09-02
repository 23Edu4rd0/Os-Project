Backup module

Arquivos:
- backup_file.py: criar_backup(dest_dir, nome_prefixo) -> copia o arquivo .db para backups/
- restore_file.py: restaurar_backup(path) -> substitui o DB atual por um arquivo; substituir_por_arquivo alias
- cleanup.py: apagar_tudo(confirm=False) -> exige confirm=True; apagar_anteriores(anos=1, tabelas=None) -> apaga por data

Uso seguro:
- As funções destrutivas exigem confirmação no nível da UI. Não chame apagar_tudo(True) sem confirmação do usuário.
- Antes de restaurar, o módulo fará uma cópia de segurança automática do DB atual em backups/pre_restore_*.db
