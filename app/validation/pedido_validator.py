"""
Módulo para validação de dados de pedidos
"""
from tkinter import messagebox

def validar_dados_cliente(campos):
    """Valida dados do cliente"""
    if not campos['nome_cliente'].get().strip():
        messagebox.showerror("Erro", "Nome do cliente é obrigatório!")
        return False
    
    cpf = campos['cpf'].get().strip()
    if len(cpf) != 11 or not cpf.isdigit():
        messagebox.showerror("Erro", "CPF deve ter 11 dígitos!")
        return False
    
    return True

def validar_produtos(produtos_list):
    """Valida lista de produtos"""
    if not produtos_list:
        messagebox.showerror("Erro", "Adicione pelo menos um produto!")
        return False
    
    for i, produto in enumerate(produtos_list):
        tipo = produto['tipo'].get().strip()
        valor = produto['valor'].get().replace(',', '.') or '0'
        
        if not tipo:
            messagebox.showerror("Erro", f"Produto {i+1}: Tipo é obrigatório!")
            return False
        
        try:
            valor_float = float(valor)
            if valor_float <= 0:
                messagebox.showerror("Erro", f"Produto {i+1}: Valor deve ser maior que zero!")
                return False
        except ValueError:
            messagebox.showerror("Erro", f"Produto {i+1}: Valor inválido!")
            return False
    
    return True

def processar_produtos(produtos_list):
    """Processa lista de produtos e retorna dados formatados"""
    produtos_dados = []
    total_produtos = 0
    
    for produto in produtos_list:
        tipo = produto['tipo'].get().strip()
        cor = produto['cor'].get().strip()
        gavetas = produto['gavetas'].get() or "1"
        valor = float(produto['valor'].get().replace(',', '.') or '0')
        reforco = produto['reforco_var'].get()
        
        valor_final = valor + (15.0 if reforco else 0.0)
        total_produtos += valor_final
        
        desc = f"{tipo} - Cor: {cor} - {gavetas} gaveta(s)"
        if reforco:
            desc += " - Com reforço"
        desc += f" - R$ {valor_final:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        produtos_dados.append(desc)
    
    return produtos_dados, total_produtos
