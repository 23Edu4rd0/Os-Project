from database import db_manager

def buscar_produtos_por_nome(parcial: str, limite: int = 10):
    """
    Busca produtos no banco de dados pelo nome (parcial, case-insensitive).
    Retorna uma lista de dicts: {id, nome, preco, categoria, reforco}
    """
    if not parcial:
        return []
    produtos = db_manager.listar_produtos(busca=parcial, limite=limite)
    resultado = []
    for prod in produtos:
        # Suportar variações de schema na tabela produtos.
        # Possíveis formatos observados:
        # (id, nome, preco, descricao, categoria, criado_em)
        # (id, nome, preco, reforco, categoria, criado_em)
        # (id, nome, preco, cor, reforco, categoria, criado_em)
        p = {
            'id': None,
            'nome': '',
            'preco': 0.0,
            'categoria': '',
            'reforco': False,
            'cor': None,
        }
        try:
            if len(prod) >= 7:
                # id, nome, preco, cor, reforco, categoria, criado_em
                p['id'] = prod[0]
                p['nome'] = str(prod[1]) if prod[1] is not None else ''
                p['preco'] = float(prod[2]) if prod[2] is not None else 0.0
                p['cor'] = prod[3]
                p['reforco'] = bool(prod[4])
                p['categoria'] = str(prod[5]) if prod[5] is not None else ''
            elif len(prod) == 6:
                # Ambíguo: verificar tipo do índice 3
                p['id'] = prod[0]
                p['nome'] = str(prod[1]) if prod[1] is not None else ''
                p['preco'] = float(prod[2]) if prod[2] is not None else 0.0
                if isinstance(prod[3], (int, bool)):
                    # assumir que é reforco
                    p['reforco'] = bool(prod[3])
                    p['categoria'] = str(prod[4]) if prod[4] is not None else ''
                else:
                    # assumir que é descricao (sem reforco na tabela)
                    p['reforco'] = False
                    p['categoria'] = str(prod[4]) if prod[4] is not None else ''
            elif len(prod) == 5:
                # id, nome, preco, categoria, criado_em
                p['id'] = prod[0]
                p['nome'] = str(prod[1]) if prod[1] is not None else ''
                p['preco'] = float(prod[2]) if prod[2] is not None else 0.0
                p['categoria'] = str(prod[3]) if prod[3] is not None else ''
        except Exception:
            # fallback genérico
            try:
                p['id'] = prod[0]
                p['nome'] = str(prod[1])
                p['preco'] = float(prod[2])
            except Exception:
                continue

        resultado.append(p)

    return resultado
