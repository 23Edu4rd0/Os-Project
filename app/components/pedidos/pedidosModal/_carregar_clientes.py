from .__init__ import PedidosModal
from database import db_manager

def _carregar_clientes(self):
    """Carrega lista de clientes do banco de dados"""
    try:
        clientes = db_manager.listar_clientes()
        self.clientes_dict = {}
        for cliente in clientes:
            if len(cliente) >= 14:  # Todos os campos disponíveis (incluindo CEP)
                cliente_id = cliente[0]
                nome = cliente[1] or ''
                cpf = cliente[2] or ''
                cnpj = cliente[3] or ''
                inscricao_estadual = cliente[4] or ''
                telefone = cliente[5] or ''
                email = cliente[6] or ''
                cep = cliente[7] or ''  # CEP estava sendo ignorado
                rua = cliente[8] or ''  # Corrigido do índice 7 para 8
                numero = cliente[9] or ''  # Corrigido do índice 8 para 9
                bairro = cliente[10] or ''  # Corrigido do índice 9 para 10
                cidade = cliente[11] or ''  # Corrigido do índice 10 para 11
                estado = cliente[12] or ''  # Corrigido do índice 11 para 12
                referencia = cliente[13] or ''  # Corrigido do índice 12 para 13
                
                if nome:
                    telefone_fmt = self._format_phone(telefone)
                    nome_exibicao = f"{nome} | {telefone_fmt}" if telefone_fmt else nome
                    self.clientes_dict[nome_exibicao] = {
                        'id': cliente_id,
                        'nome': nome,
                        'cpf': cpf,
                        'cnpj': cnpj,
                        'inscricao_estadual': inscricao_estadual,
                        'telefone': telefone,
                        'email': email,
                        'cep': cep,
                        'rua': rua,
                        'numero': numero,
                        'bairro': bairro,
                        'cidade': cidade,
                        'estado': estado,
                        'referencia': referencia
                    }
    except Exception as e:
        print(f"Erro ao carregar clientes: {e}")
        self.clientes_dict = {}
