
# Nenhum widget PyQt6 usado diretamente, mas garantir import se necessário
from .__init__ import PedidosModal
from database import db_manager

def _carregar_produtos(self):
    """
    Carrega produtos do banco de dados e monta o dicionário para busca.
    Estrutura esperada do banco: (id, nome, codigo, preco, descricao, categoria, criado_em)
    """
    try:
        rows = db_manager.listar_produtos()
        self._produtos_rows = rows
        self.produtos_dict = {}
        
        print(f"[DEBUG] Carregando {len(rows)} produtos do banco...")
        
        for i, row in enumerate(rows):
            try:
                # Estrutura: (id, nome, codigo, preco, descricao, categoria, criado_em)
                produto_id = row[0]  # int
                nome = (row[1] or '').strip()  # str
                codigo = (row[2] or '').strip()  # str  
                preco = float(row[3]) if row[3] is not None else 0.0  # float
                descricao = (row[4] or '').strip()  # str
                categoria = (row[5] or '').strip()  # str
                
                if not nome:  # Pular produtos sem nome
                    continue
                
                # Log para debug
                print(f"[DEBUG] Produto {i}: nome='{nome}', codigo='{codigo}', preco={preco}")
                
                # Criar entrada principal pelo nome (chave primária)
                produto_data = {
                    "id": produto_id,
                    "nome": nome,
                    "codigo": codigo,
                    "preco": preco,
                    "categoria": categoria,
                    "descricao": descricao
                }
                
                # Usar nome como chave principal
                self.produtos_dict[nome] = produto_data
                
                # Também indexar por nome em lowercase para busca case-insensitive
                self.produtos_dict[nome.lower()] = produto_data
                
                # Se tiver código, indexar por código também
                if codigo:
                    self.produtos_dict[codigo] = produto_data
                    self.produtos_dict[codigo.lower()] = produto_data
                
            except Exception as e:
                print(f"[DEBUG] Erro ao processar produto linha {i}: {e}")
                continue
        
        # Criar set de categorias
        self._produtos_categorias = set()
        for row in rows:
            try:
                categoria = (row[5] or '').strip()
                if categoria:
                    self._produtos_categorias.add(categoria)
            except:
                pass
        
        print(f"[DEBUG] Carregados {len(self.produtos_dict)} entradas no dicionário")
        print(f"[DEBUG] Categorias encontradas: {self._produtos_categorias}")
        
        # Log algumas entradas para debug
        count = 0
        for key, data in self.produtos_dict.items():
            if count < 3:
                print(f"[DEBUG] Entrada: '{key}' -> {data}")
                count += 1
        
    except Exception as e:
        print(f"[ERROR] Erro ao carregar produtos: {e}")
        import traceback
        traceback.print_exc()
        self.produtos_dict = {}
        self._produtos_categorias = set()
