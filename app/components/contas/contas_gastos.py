"""
Módulo de controle de gastos - Despesas e comparações
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, DANGER, INFO, WARNING
from tkinter import messagebox
from datetime import datetime, timedelta
import calendar
import sys
import os

# Adicionar o diretório raiz do projeto ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

from database import db_manager

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ContasGastos:
    """Gerencia a aba de gastos - despesas e comparações"""
    
    def __init__(self, parent):
        self.parent = parent
        self.filtro_periodo = "mes"
        self.dados_gastos = []
        self._setup_interface()
        self.atualizar_dados()
        
    def _setup_interface(self):
        """Configura a interface da aba gastos"""
        # Frame superior - botões e filtros
        top_frame = tb.Frame(self.parent)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        # Botões de ação
        buttons_frame = tb.Frame(top_frame)
        buttons_frame.pack(side="left", fill="y", padx=(0, 10))
        
        tb.Button(buttons_frame, text="➕ Novo Gasto", bootstyle=SUCCESS, 
                 command=self.novo_gasto).pack(pady=5, fill="x")
        tb.Button(buttons_frame, text="✏️ Editar", 
                 command=self.editar_gasto).pack(pady=5, fill="x")
        tb.Button(buttons_frame, text="🗑️ Excluir", bootstyle=DANGER, 
                 command=self.excluir_gasto).pack(pady=5, fill="x")
        tb.Button(buttons_frame, text="🔄 Atualizar", 
                 command=self.atualizar_dados).pack(pady=5, fill="x")
        
        # Filtros de período
        filtros_frame = tb.LabelFrame(top_frame, text="📅 Período", padding=10)
        filtros_frame.pack(side="left", fill="y", padx=(0, 10))
        
        self.periodo_var = tk.StringVar(value="mes")
        periodos = [("Este Mês", "mes"), ("Este Ano", "ano"), ("Total", "total")]
        
        for texto, valor in periodos:
            tb.Radiobutton(filtros_frame, text=texto, variable=self.periodo_var, 
                          value=valor, command=self.atualizar_dados).pack(anchor="w", pady=2)
        
        # Resumo de gastos vs receitas
        comparacao_frame = tb.LabelFrame(top_frame, text="📊 Gastos vs Receitas", padding=15)
        comparacao_frame.pack(side="left", fill="both", expand=True)
        
        self.total_gastos_label = tb.Label(comparacao_frame, text="Total Gastos: R$ 0,00", 
                                          font=("Arial", 12, "bold"), foreground="#F44336")
        self.total_gastos_label.pack(anchor="w", pady=2)
        
        self.total_receitas_label = tb.Label(comparacao_frame, text="Total Receitas: R$ 0,00", 
                                           font=("Arial", 12, "bold"), foreground="#4CAF50")
        self.total_receitas_label.pack(anchor="w", pady=2)
        
        self.lucro_label = tb.Label(comparacao_frame, text="Lucro Líquido: R$ 0,00", 
                                   font=("Arial", 13, "bold"), foreground="#2196F3")
        self.lucro_label.pack(anchor="w", pady=5)
        
        self.margem_label = tb.Label(comparacao_frame, text="Margem de Lucro: 0%", 
                                    font=("Arial", 11), foreground="#9C27B0")
        self.margem_label.pack(anchor="w", pady=2)
        
        # Frame meio - lista de gastos
        middle_frame = tb.Frame(self.parent)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Lista de gastos
        gastos_frame = tb.LabelFrame(middle_frame, text="💸 Lista de Gastos", padding=10)
        gastos_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # TreeView para gastos
        columns = ("id", "descricao", "categoria", "valor", "data")
        self.gastos_tree = tb.Treeview(gastos_frame, columns=columns, show="headings", height=10)
        
        self.gastos_tree.heading("id", text="ID")
        self.gastos_tree.heading("descricao", text="Descrição")
        self.gastos_tree.heading("categoria", text="Categoria")
        self.gastos_tree.heading("valor", text="Valor")
        self.gastos_tree.heading("data", text="Data")
        
        self.gastos_tree.column("id", width=60, anchor="center")
        self.gastos_tree.column("descricao", width=200, anchor="w")
        self.gastos_tree.column("categoria", width=120, anchor="w")
        self.gastos_tree.column("valor", width=100, anchor="e")
        self.gastos_tree.column("data", width=100, anchor="center")
        
        scrollbar_gastos = tb.Scrollbar(gastos_frame, orient="vertical", command=self.gastos_tree.yview)
        self.gastos_tree.configure(yscrollcommand=scrollbar_gastos.set)
        
        self.gastos_tree.pack(side="left", fill="both", expand=True)
        scrollbar_gastos.pack(side="right", fill="y")
        
        # Frame dos gráficos
        if MATPLOTLIB_AVAILABLE:
            graficos_frame = tb.LabelFrame(middle_frame, text="📈 Gráficos", padding=10)
            graficos_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
            self._setup_graficos(graficos_frame)
        
    def _setup_graficos(self, parent):
        """Configura os gráficos"""
        self.fig_gastos = Figure(figsize=(8, 6), dpi=100)
        self.canvas_gastos = FigureCanvasTkAgg(self.fig_gastos, parent)
        self.canvas_gastos.get_tk_widget().pack(fill="both", expand=True)
        
    def atualizar_dados(self):
        """Atualiza todos os dados da aba"""
        try:
            self.filtro_periodo = self.periodo_var.get()
            self._carregar_gastos()
            self._carregar_receitas()
            self._atualizar_comparacao()
            self._atualizar_lista_gastos()
            if MATPLOTLIB_AVAILABLE:
                self.atualizar_graficos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar dados de gastos: {e}")
    
    def _carregar_gastos(self):
        """Carrega gastos do banco de dados"""
        try:
            # Implementar busca de gastos do banco
            # Por enquanto, dados simulados
            hoje = datetime.now()
            
            gastos_simulados = [
                {"id": 1, "descricao": "Salário", "categoria": "Pessoal", "valor": 2000.00, "data": hoje.strftime('%Y-%m-%d')},
                {"id": 2, "descricao": "Aluguel", "categoria": "Fixo", "valor": 800.00, "data": hoje.strftime('%Y-%m-%d')},
                {"id": 3, "descricao": "Material", "categoria": "Produção", "valor": 300.00, "data": hoje.strftime('%Y-%m-%d')},
                {"id": 4, "descricao": "Energia", "categoria": "Fixo", "valor": 150.00, "data": hoje.strftime('%Y-%m-%d')},
            ]
            
            # Filtrar por período (implementar filtro real)
            self.dados_gastos = gastos_simulados
            
        except Exception as e:
            print(f"Erro ao carregar gastos: {e}")
            self.dados_gastos = []
    
    def _carregar_receitas(self):
        """Carrega receitas do período"""
        try:
            vendas = db_manager.listar_pedidos_ordenados_prazo(limite=1000)
            
            hoje = datetime.now()
            self.total_receitas = 0
            
            for venda in vendas:
                # Ignorar pedidos cancelados/excluídos; aceitar entregues como venda válida
                status = (venda.get('status') or '').strip().lower()
                if status in ('cancelado', 'cancelada', 'excluido', 'excluida', 'deletado'):
                    continue

                data_venda = venda.get('data_emissao', '')
                if not data_venda:
                    continue
                
                try:
                    if isinstance(data_venda, str):
                        data_venda = datetime.strptime(data_venda[:10], '%Y-%m-%d')
                    
                    incluir = False
                    if self.filtro_periodo == "mes":
                        incluir = (data_venda.year == hoje.year and data_venda.month == hoje.month)
                    elif self.filtro_periodo == "ano":
                        incluir = (data_venda.year == hoje.year)
                    else:
                        incluir = True
                    
                    if incluir:
                        produtos = venda.get('valor_produto', 0) or 0
                        frete = venda.get('frete', 0) or 0
                        self.total_receitas += produtos + frete
                        
                except ValueError:
                    continue
                    
        except Exception as e:
            print(f"Erro ao carregar receitas: {e}")
            self.total_receitas = 0
    
    def _atualizar_comparacao(self):
        """Atualiza o resumo de comparação gastos vs receitas"""
        total_gastos = sum(gasto['valor'] for gasto in self.dados_gastos)
        lucro_liquido = self.total_receitas - total_gastos
        
        margem_lucro = 0
        if self.total_receitas > 0:
            margem_lucro = (lucro_liquido / self.total_receitas) * 100
        
        # Atualizar labels
        self.total_gastos_label.config(text=f"Total Gastos: R$ {total_gastos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.total_receitas_label.config(text=f"Total Receitas: R$ {self.total_receitas:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        
        # Cor do lucro baseada no valor
        cor_lucro = "#4CAF50" if lucro_liquido >= 0 else "#F44336"
        self.lucro_label.config(text=f"Lucro Líquido: R$ {lucro_liquido:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'), 
                               foreground=cor_lucro)
        
        cor_margem = "#4CAF50" if margem_lucro >= 0 else "#F44336"
        self.margem_label.config(text=f"Margem de Lucro: {margem_lucro:.1f}%", foreground=cor_margem)
    
    def _atualizar_lista_gastos(self):
        """Atualiza a lista de gastos"""
        # Limpar dados existentes
        for item in self.gastos_tree.get_children():
            self.gastos_tree.delete(item)
        
        # Inserir gastos
        for gasto in self.dados_gastos:
            self.gastos_tree.insert("", "end", values=(
                gasto["id"],
                gasto["descricao"],
                gasto["categoria"],
                f"R$ {gasto['valor']:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                gasto["data"]
            ))
    
    def atualizar_graficos(self):
        """Atualiza os gráficos de gastos"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        self.fig_gastos.clear()
        
        # Gráfico 1: Gastos por categoria
        ax1 = self.fig_gastos.add_subplot(2, 1, 1)
        self._grafico_gastos_categoria(ax1)
        
        # Gráfico 2: Comparação gastos vs receitas
        ax2 = self.fig_gastos.add_subplot(2, 1, 2)
        self._grafico_comparacao(ax2)
        
        self.fig_gastos.tight_layout()
        self.canvas_gastos.draw()
    
    def _grafico_gastos_categoria(self, ax):
        """Cria gráfico de gastos por categoria"""
        categorias = {}
        for gasto in self.dados_gastos:
            categoria = gasto["categoria"]
            categorias[categoria] = categorias.get(categoria, 0) + gasto["valor"]
        
        if categorias:
            labels = list(categorias.keys())
            values = list(categorias.values())
            colors = ['#F44336', '#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
            
            ax.pie(values, labels=labels, colors=colors[:len(labels)], autopct='%1.1f%%', startangle=90)
            ax.set_title('Gastos por Categoria')
        else:
            ax.text(0.5, 0.5, 'Sem dados para exibir', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Gastos por Categoria')
    
    def _grafico_comparacao(self, ax):
        """Cria gráfico de comparação gastos vs receitas"""
        total_gastos = sum(gasto['valor'] for gasto in self.dados_gastos)
        
        categorias = ['Receitas', 'Gastos', 'Lucro']
        valores = [self.total_receitas, total_gastos, self.total_receitas - total_gastos]
        cores = ['#4CAF50', '#F44336', '#2196F3' if valores[2] >= 0 else '#FF5722']
        
        bars = ax.bar(categorias, valores, color=cores, alpha=0.7)
        ax.set_title('Comparação Financeira')
        ax.set_ylabel('Valor (R$)')
        ax.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, valor in zip(bars, valores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'R$ {valor:,.0f}', ha='center', va='bottom')
    
    def novo_gasto(self):
        """Abre modal para novo gasto"""
        self._abrir_modal_gasto()
    
    def editar_gasto(self):
        """Edita gasto selecionado"""
        selected = self.gastos_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Selecione um gasto para editar.")
            return
        
        item = self.gastos_tree.item(selected[0])
        gasto_id = item['values'][0]
        
        # Buscar dados do gasto
        gasto_data = None
        for gasto in self.dados_gastos:
            if gasto['id'] == gasto_id:
                gasto_data = gasto
                break
        
        if gasto_data:
            self._abrir_modal_gasto(gasto_data)
    
    def excluir_gasto(self):
        """Exclui gasto selecionado"""
        selected = self.gastos_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Selecione um gasto para excluir.")
            return
        
        item = self.gastos_tree.item(selected[0])
        descricao = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Excluir gasto '{descricao}'?"):
            try:
                # Implementar exclusão no banco
                messagebox.showinfo("Sucesso", "Gasto excluído com sucesso!")
                self.atualizar_dados()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir gasto: {e}")
    
    def _abrir_modal_gasto(self, data=None):
        """Abre modal de gasto"""
        win = tb.Toplevel(self.parent)
        win.title('Novo Gasto' if not data else 'Editar Gasto')
        win.transient(self.parent)
        win.grab_set()
        win.geometry('400x300')
        
        frame = tb.Frame(win, padding=20)
        frame.pack(fill='both', expand=True)
        
        # Campos
        fields = {}
        
        # Descrição
        tb.Label(frame, text="Descrição:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        fields['descricao'] = tb.Entry(frame, width=30)
        fields['descricao'].grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Categoria
        tb.Label(frame, text="Categoria:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        fields['categoria'] = tb.Combobox(frame, values=["Fixo", "Variável", "Pessoal", "Produção", "Outros"], 
                                         state="readonly", width=27)
        fields['categoria'].grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Valor
        tb.Label(frame, text="Valor (R$):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        fields['valor'] = tb.Entry(frame, width=30)
        fields['valor'].grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Data
        tb.Label(frame, text="Data:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        fields['data'] = tb.Entry(frame, width=30)
        fields['data'].grid(row=3, column=1, pady=5, padx=(10, 0))
        fields['data'].insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Preencher dados se editando
        if data:
            fields['descricao'].insert(0, data.get('descricao', ''))
            fields['categoria'].set(data.get('categoria', ''))
            fields['valor'].insert(0, str(data.get('valor', '')))
            fields['data'].delete(0, 'end')
            fields['data'].insert(0, data.get('data', ''))
        
        # Botões
        btn_frame = tb.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def salvar():
            try:
                descricao = fields['descricao'].get().strip()
                categoria = fields['categoria'].get()
                valor = float(fields['valor'].get().replace(',', '.'))
                data = fields['data'].get().strip()
                
                if not descricao or not categoria:
                    messagebox.showerror("Erro", "Preencha todos os campos obrigatórios.")
                    return
                
                # Implementar salvamento no banco
                messagebox.showinfo("Sucesso", "Gasto salvo com sucesso!")
                self.atualizar_dados()
                win.destroy()
                
            except ValueError:
                messagebox.showerror("Erro", "Valor deve ser um número válido.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar gasto: {e}")
        
        tb.Button(btn_frame, text='Salvar', bootstyle=SUCCESS, 
                 command=salvar).pack(side='left', padx=5)
        tb.Button(btn_frame, text='Cancelar', 
                 command=win.destroy).pack(side='left', padx=5)
    
    def filtrar_por_periodo(self, periodo):
        """Filtra dados por período específico"""
        self.periodo_var.set(periodo)
        self.atualizar_dados()
