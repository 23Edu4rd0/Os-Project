from database import db_manager

# inserir
print('inserindo...')
id = db_manager.inserir_gasto('Teste', 'CRUD test', 12.34, None)
print('id inserido =', id)
# atualizar
if id:
    ok = db_manager.atualizar_gasto(id, tipo='Teste2', descricao='Atualizado', valor=99.99)
    print('atualizado?', ok)
    # buscar para verificar
    rows = db_manager.cursor.execute('SELECT id, tipo, descricao, valor FROM gastos WHERE id = ?', (id,)).fetchall()
    print('registro apos update:', rows)
    # deletar
    ok2 = db_manager.deletar_gasto(id)
    print('deletado?', ok2)
    rows2 = db_manager.cursor.execute('SELECT id FROM gastos WHERE id = ?', (id,)).fetchall()
    print('registro apos delete (deve estar vazio):', rows2)
else:
    print('insercao falhou')
