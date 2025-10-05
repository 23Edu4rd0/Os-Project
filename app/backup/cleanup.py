import sqlite3
from datetime import datetime, timedelta
from database.core.db_setup import DatabaseSetup


def apagar_tudo(confirm=False):
    """Apaga todos os dados do banco.

    - confirm: por segurança, exige True para executar a operação destrutiva.
    - Retorna True se executado, False caso contrário.
    """
    if not confirm:
        return False

    db_path = DatabaseSetup.get_database_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # buscar todas as tabelas criadas no setup e truncar (sem dropar schema)
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r[0] for r in cur.fetchall()]
        for t in tables:
            cur.execute(f"DELETE FROM {t};")
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao apagar tudo: {e}")
        return False
    finally:
        conn.close()


def apagar_anteriores(anos=1, tabelas=None):
    """Apaga registros anteriores a X anos nas tabelas especificadas.

    - anos: número de anos anteriores (default 1)
    - tabelas: lista de tabelas para aplicar (se None, tenta aplicar a tabelas com coluna 'data')
    - Retorna dicionário com contagens por tabela.
    """
    db_path = DatabaseSetup.get_database_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cutoff = datetime.now() - timedelta(days=anos*365)
    cutoff_str = cutoff.strftime('%Y-%m-%d')

    result = {}
    try:
        if tabelas is None:
            # detectar tabelas que possuem coluna chamada 'data'
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            tables = [r[0] for r in cur.fetchall()]
            tables_with_data = []
            for t in tables:
                try:
                    cur.execute(f"PRAGMA table_info({t})")
                    cols = [r[1] for r in cur.fetchall()]
                    if 'data' in cols:
                        tables_with_data.append(t)
                except Exception:
                    pass
            tables = tables_with_data

        for t in tables:
            # contar e deletar
            cur.execute(f"SELECT COUNT(*) FROM {t} WHERE date(data) < ?", (cutoff_str,))
            cnt = cur.fetchone()[0]
            if cnt > 0:
                cur.execute(f"DELETE FROM {t} WHERE date(data) < ?", (cutoff_str,))
            result[t] = cnt
        conn.commit()
        return result
    except Exception as e:
        print(f"Erro ao apagar anteriores: {e}")
        return {}
    finally:
        conn.close()
