from .__init__ import PedidosModal
from database import db_manager

def _carregar_clientes(self):
    """Carrega lista de clientes do banco de dados"""
    try:
        clientes = db_manager.listar_clientes()
        self.clientes_dict = {}
        for cliente in clientes:
            if len(cliente) >= 13:  # Todos os campos disponíveis
                cliente_id = cliente[0]
                nome = cliente[1] or ''
                cpf = cliente[2] or ''
                cnpj = cliente[3] or ''
                inscricao_estadual = cliente[4] or ''
                telefone = cliente[5] or ''
                email = cliente[6] or ''
                rua = cliente[7] or ''
                numero = cliente[8] or ''
                bairro = cliente[9] or ''
                cidade = cliente[10] or ''
                estado = cliente[11] or ''
                referencia = cliente[12] or ''
                
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
