from .__init__ import PedidosModal
from database import db_manager

def _carregar_clientes(self):
    """Carrega lista de clientes do banco de dados"""
    try:
        clientes = db_manager.listar_clientes()
        self.clientes_dict = {}
        for cliente in clientes:
            if len(cliente) >= 7:
                cliente_id = cliente[0]
                nome = cliente[1] or ''
                cpf = cliente[2] or ''
                telefone = cliente[3] or ''
                email = cliente[4] or ''
                rua = cliente[5] or ''
                numero = cliente[6] or ''
                if nome:
                    telefone_fmt = self._format_phone(telefone)
                    nome_exibicao = f"{nome} | {telefone_fmt}" if telefone_fmt else nome
                    self.clientes_dict[nome_exibicao] = {
                        'id': cliente_id,
                        'nome': nome,
                        'cpf': cpf,
                        'telefone': telefone,
                        'email': email,
                        'rua': rua,
                        'numero': numero
                    }
    except Exception as e:
        print(f"Erro ao carregar clientes: {e}")
        self.clientes_dict = {}
