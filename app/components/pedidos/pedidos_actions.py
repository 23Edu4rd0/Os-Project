"""
Ações de gerenciamento de pedidos
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, WARNING, DANGER
from tkinter import messagebox
import urllib.parse
import webbrowser

from database import db_manager


class PedidosActions:
    """Gerencia ações de pedidos (alterar status, excluir, WhatsApp, etc.)"""
    
    def __init__(self, interface):
        self.interface = interface
    
    def alterar_status(self, pedido):
        """Altera status do pedido"""
        status_atual = pedido.get('status', 'em produção')
        statuses = ["em produção", "enviado", "entregue", "cancelado"]
        
        win = tb.Toplevel(self.interface.parent)
        win.title('Alterar Status')
        win.transient(self.interface.parent)
        win.grab_set()
        win.geometry('350x200')
        
        frame = tb.Frame(win, padding=20)
        frame.pack(fill='both', expand=True)
        
        tb.Label(frame, text=f'OS #{pedido.get("numero_os")} - {pedido.get("nome_cliente")}', 
                font=('Arial', 12, 'bold')).pack(pady=(0, 15))
        
        tb.Label(frame, text='Novo Status:', font=('Arial', 10)).pack(anchor='w')
        
        status_var = tb.StringVar(value=status_atual)
        status_combo = tb.Combobox(frame, textvariable=status_var, values=statuses, 
                                  state="readonly", width=20)
        status_combo.pack(pady=(5, 20))
        
        def salvar():
            novo_status = status_var.get()
            if novo_status != status_atual:
                try:
                    success = db_manager.atualizar_status_pedido(pedido['id'], novo_status)
                    if success:
                        self.interface.carregar_dados()
                        messagebox.showinfo('Sucesso', f'Status alterado para "{novo_status}"!')
                        win.destroy()
                    else:
                        messagebox.showerror('Erro', 'Falha ao alterar status.')
                except Exception as e:
                    messagebox.showerror('Erro', f'Erro ao alterar status: {e}')
            else:
                win.destroy()
        
        btn_frame = tb.Frame(frame)
        btn_frame.pack()
        
        tb.Button(btn_frame, text='💾 Salvar', bootstyle=SUCCESS, 
                 command=salvar).pack(side='left', padx=5)
        tb.Button(btn_frame, text='❌ Cancelar', 
                 command=win.destroy).pack(side='left', padx=5)
    
    def excluir_pedido(self, pedido):
        """Exclui pedido"""
        if messagebox.askyesno('Confirmar Exclusão', 
                              f'Tem certeza que deseja excluir a OS #{pedido.get("numero_os")}?\\n\\n'
                              f'Cliente: {pedido.get("nome_cliente")}\\n'
                              f'Esta ação não pode ser desfeita.'):
            try:
                success = db_manager.deletar_pedido(pedido['id'])
                if success:
                    self.interface.carregar_dados()
                    messagebox.showinfo('Sucesso', 'Pedido excluído com sucesso!')
                else:
                    messagebox.showerror('Erro', 'Falha ao excluir pedido.')
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao excluir pedido: {e}')
    
    def enviar_whatsapp(self, pedido):
        """Gera PDF e envia WhatsApp para o cliente do pedido"""
        try:
            telefone = pedido.get('telefone_cliente', '').strip()
            nome_cliente = pedido.get('nome_cliente', '').strip()
            numero_os = pedido.get('numero_os', '')
            
            if not telefone:
                messagebox.showerror("Erro", "Este pedido não possui telefone do cliente!")
                return
            
            if not nome_cliente:
                messagebox.showerror("Erro", "Nome do cliente não encontrado!")
                return
            
            # GERAR PDF PRIMEIRO
            try:
                from documents.os_pdf import OrdemServicoPDF
                
                # Preparar dados para o PDF
                dados_pdf = {
                    'numero_os': numero_os,
                    'nome_cliente': nome_cliente,
                    'cpf_cliente': pedido.get('cpf_cliente', ''),
                    'telefone_cliente': telefone,
                    'detalhes_produto': pedido.get('detalhes_produto', ''),
                    'valor_produto': pedido.get('valor_produto', 0),
                    'valor_entrada': pedido.get('valor_entrada', 0),
                    'frete': pedido.get('frete', 0),
                    'forma_pagamento': pedido.get('forma_pagamento', ''),
                    'prazo': pedido.get('prazo', 30)
                }
                
                # Gerar PDF - passando dados no construtor
                pdf_generator = OrdemServicoPDF(dados_pdf, tamanho_folha="pequena")
                arquivo_pdf = pdf_generator.gerar()
                
                print(f"PDF gerado: {arquivo_pdf}")
                
            except Exception as pdf_error:
                print(f"Erro ao gerar PDF: {pdf_error}")
                messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(pdf_error)}")
                return
            
            # Limpar e formatar telefone
            telefone_limpo = ''.join(filter(str.isdigit, telefone))
            
            # Adicionar código do país se necessário
            if len(telefone_limpo) == 11 and telefone_limpo.startswith('11'):
                telefone_formatado = f"55{telefone_limpo}"
            elif len(telefone_limpo) == 10:
                telefone_formatado = f"5511{telefone_limpo}"
            elif len(telefone_limpo) == 11:
                telefone_formatado = f"55{telefone_limpo}"
            else:
                telefone_formatado = telefone_limpo
            
            # Criar mensagem personalizada baseada no status
            status = pedido.get('status', 'em produção')
            
            if status == 'em produção':
                mensagem = f"Olá {nome_cliente}! Sua OS #{numero_os:05d} está em produção. Segue o PDF com os detalhes. Em breve entraremos em contato!"
            elif status == 'enviado':
                mensagem = f"Olá {nome_cliente}! Sua OS #{numero_os:05d} foi enviada. Segue o PDF com os detalhes. Acompanhe a entrega!"
            elif status == 'entregue':
                mensagem = f"Olá {nome_cliente}! Esperamos que esteja satisfeito com sua OS #{numero_os:05d}. Segue o PDF para seus registros. Obrigado!"
            else:
                mensagem = f"Olá {nome_cliente}! Segue o PDF da sua OS #{numero_os:05d} com todas as informações."
            
            # Codificar mensagem para URL
            mensagem_encoded = urllib.parse.quote(mensagem)
            
            # Abrir WhatsApp Web
            url_whatsapp = f"https://api.whatsapp.com/send?phone={telefone_formatado}&text={mensagem_encoded}"
            webbrowser.open(url_whatsapp)
            
            messagebox.showinfo("WhatsApp", 
                               f"PDF gerado e WhatsApp aberto para {nome_cliente}\\n"
                               f"OS: #{numero_os:05d}\\n"
                               f"Telefone: {telefone}\\n\\n"
                               f"PDF salvo em: {arquivo_pdf}\\n\\n"
                               "Anexe o PDF manualmente na conversa do WhatsApp.")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar WhatsApp: {str(e)}")
    
    def editar_pedido_simples(self, pedido):
        """Abre modal simples para editar pedido (versão simplificada)"""
        win = tb.Toplevel(self.interface.parent)
        win.title(f'Editar OS #{pedido.get("numero_os")}')
        win.transient(self.interface.parent)
        win.grab_set()
        win.geometry('600x500')
        
        frame = tb.Frame(win, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Título
        tb.Label(frame, text=f'Editar Ordem de Serviço #{pedido.get("numero_os")}', 
                font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # Campos editáveis
        fields = {}
        
        # Cliente
        tb.Label(frame, text='Cliente:', font=('Arial', 10, 'bold')).pack(anchor='w')
        fields['cliente'] = tb.Entry(frame, width=50)
        fields['cliente'].pack(fill='x', pady=(0, 10))
        fields['cliente'].insert(0, pedido.get('nome_cliente', ''))
        
        # Telefone
        tb.Label(frame, text='Telefone:', font=('Arial', 10, 'bold')).pack(anchor='w')
        fields['telefone'] = tb.Entry(frame, width=20)
        fields['telefone'].pack(anchor='w', pady=(0, 10))
        fields['telefone'].insert(0, pedido.get('telefone_cliente', ''))
        
        # Descrição/Detalhes
        tb.Label(frame, text='Descrição do Produto:', font=('Arial', 10, 'bold')).pack(anchor='w')
        fields['descricao'] = tk.Text(frame, width=60, height=8, wrap='word')
        fields['descricao'].pack(fill='both', expand=True, pady=(0, 10))
        fields['descricao'].insert('1.0', pedido.get('detalhes_produto', ''))
        
        # Frame para valores
        valores_frame = tb.Frame(frame)
        valores_frame.pack(fill='x', pady=(0, 10))
        
        # Valor do produto
        tb.Label(valores_frame, text='Valor:', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=(0, 10))
        fields['valor'] = tb.Entry(valores_frame, width=15)
        fields['valor'].grid(row=0, column=1, sticky='w', padx=(0, 20))
        valor_atual = pedido.get('valor_produto', 0)
        if valor_atual:
            fields['valor'].insert(0, f"{float(valor_atual):.2f}")
        
        # Frete
        tb.Label(valores_frame, text='Frete:', font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='w', padx=(0, 10))
        fields['frete'] = tb.Entry(valores_frame, width=15)
        fields['frete'].grid(row=0, column=3, sticky='w')
        frete_atual = pedido.get('frete', 0)
        if frete_atual:
            fields['frete'].insert(0, f"{float(frete_atual):.2f}")
        
        # Prazo
        prazo_frame = tb.Frame(frame)
        prazo_frame.pack(fill='x', pady=(0, 20))
        
        tb.Label(prazo_frame, text='Prazo (dias):', font=('Arial', 10, 'bold')).pack(side='left')
        fields['prazo'] = tb.Entry(prazo_frame, width=10)
        fields['prazo'].pack(side='left', padx=(10, 0))
        prazo_atual = pedido.get('prazo_dias', pedido.get('prazo', ''))
        if prazo_atual:
            fields['prazo'].insert(0, str(prazo_atual))
        
        def salvar_edicao():
            try:
                # Coletar dados do formulário
                novo_cliente = fields['cliente'].get().strip()
                novo_telefone = fields['telefone'].get().strip()
                nova_descricao = fields['descricao'].get('1.0', 'end-1c').strip()
                novo_valor = fields['valor'].get().strip()
                novo_frete = fields['frete'].get().strip()
                novo_prazo = fields['prazo'].get().strip()
                
                # Validações
                if not novo_cliente:
                    messagebox.showerror('Erro', 'Nome do cliente é obrigatório!')
                    return
                
                if not nova_descricao:
                    messagebox.showerror('Erro', 'Descrição do produto é obrigatória!')
                    return
                
                # Preparar dados para atualização
                campos_atualizacao = {
                    'nome_cliente': novo_cliente,
                    'telefone_cliente': novo_telefone or None,
                    'detalhes_produto': nova_descricao
                }
                
                # Processar valores numéricos
                if novo_valor:
                    try:
                        campos_atualizacao['valor_produto'] = float(novo_valor.replace(',', '.'))
                    except ValueError:
                        messagebox.showerror('Erro', 'Valor do produto inválido!')
                        return
                
                if novo_frete:
                    try:
                        campos_atualizacao['frete'] = float(novo_frete.replace(',', '.'))
                    except ValueError:
                        messagebox.showerror('Erro', 'Valor do frete inválido!')
                        return
                
                if novo_prazo:
                    try:
                        campos_atualizacao['prazo'] = int(novo_prazo)
                    except ValueError:
                        messagebox.showerror('Erro', 'Prazo deve ser um número inteiro!')
                        return
                
                # Atualizar no banco
                sucesso = db_manager.atualizar_ordem(pedido['id'], campos_atualizacao)
                
                if sucesso:
                    messagebox.showinfo('Sucesso', f'OS #{pedido.get("numero_os")} atualizada com sucesso!')
                    self.interface.carregar_dados()  # Recarregar lista
                    win.destroy()
                else:
                    messagebox.showerror('Erro', 'Falha ao salvar alterações no banco de dados!')
                    
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao salvar: {str(e)}')
        
        # Botões
        btn_frame = tb.Frame(frame)
        btn_frame.pack(fill='x', pady=10)
        
        tb.Button(btn_frame, text='💾 Salvar', bootstyle=SUCCESS, 
                 command=salvar_edicao).pack(side='left', padx=(0, 10))
        tb.Button(btn_frame, text='❌ Cancelar', 
                 command=win.destroy).pack(side='left')
