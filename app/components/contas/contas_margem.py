"""
Módulo de análise de margem de lucro - Custos e rentabilidade dos produtos
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


class ContasMargem:
    """Gerencia a análise de margem de lucro dos produtos"""
    
    def __init__(self, parent):
        self.parent = parent
        self.tipo_produto = "caixa_p"
        self.dados_custos = {}
        self.dados_vendas = []
        self._setup_interface()
        self.atualizar_dados()
        
    def _setup_interface(self):
        """Configura a interface da aba margem"""
        # Frame superior - configurações de custos
        top_frame = tb.Frame(self.parent)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        # Configuração de custos
        custos_frame = tb.LabelFrame(top_frame, text="💰 Configuração de Custos", padding=15)
        custos_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Seletor de produto
        tb.Label(custos_frame, text="Produto:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.produto_var = tk.StringVar(value="caixa_p")
        produto_combo = tb.Combobox(custos_frame, textvariable=self.produto_var, 
                                   values=[("caixa_p", "Caixa P"), ("caixa_g", "Caixa G")],
                                   state="readonly", width=20)
        produto_combo.grid(row=0, column=1, pady=5, padx=(10, 0))
        produto_combo.bind('<<ComboboxSelected>>', lambda e: self.atualizar_dados())
        
        # Custo de material
        tb.Label(custos_frame, text="Custo Material (R$):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.custo_material_var = tk.StringVar()
        self.custo_material_entry = tb.Entry(custos_frame, textvariable=self.custo_material_var, width=20)
        self.custo_material_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Custo de produção
        tb.Label(custos_frame, text="Custo Produção (R$):", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        self.custo_producao_var = tk.StringVar()
        self.custo_producao_entry = tb.Entry(custos_frame, textvariable=self.custo_producao_var, width=20)
        self.custo_producao_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Outros custos
        tb.Label(custos_frame, text="Outros Custos (R$):", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        self.outros_custos_var = tk.StringVar()
        self.outros_custos_entry = tb.Entry(custos_frame, textvariable=self.outros_custos_var, width=20)
        self.outros_custos_entry.grid(row=3, column=1, pady=5, padx=(10, 0))
        
        # Botão salvar custos
        tb.Button(custos_frame, text="💾 Salvar Custos", bootstyle=SUCCESS, 
                 command=self.salvar_custos).grid(row=4, column=0, columnspan=2, pady=15)
        
        # Resumo da análise
        analise_frame = tb.LabelFrame(top_frame, text="📊 Análise de Rentabilidade", padding=15)
        analise_frame.pack(side="right", fill="both", expand=True)
        
        self.custo_total_label = tb.Label(analise_frame, text="Custo Total: R$ 0,00", 
                                        font=("Arial", 12, "bold"), foreground="#F44336")
        self.custo_total_label.pack(anchor="w", pady=2)
        
        self.preco_medio_label = tb.Label(analise_frame, text="Preço Médio: R$ 0,00", 
                                        font=("Arial", 12, "bold"), foreground="#2196F3")
        self.preco_medio_label.pack(anchor="w", pady=2)
        
        self.lucro_unitario_label = tb.Label(analise_frame, text="Lucro Unitário: R$ 0,00", 
                                           font=("Arial", 12, "bold"), foreground="#4CAF50")
        self.lucro_unitario_label.pack(anchor="w", pady=2)
        
        self.margem_percentual_label = tb.Label(analise_frame, text="Margem %: 0%", 
                                              font=("Arial", 13, "bold"), foreground="#9C27B0")
        self.margem_percentual_label.pack(anchor="w", pady=5)
        
        self.vendas_periodo_label = tb.Label(analise_frame, text="Vendas (mês): 0 unidades", 
                                           font=("Arial", 11), foreground="#607D8B")
        self.vendas_periodo_label.pack(anchor="w", pady=2)
        
        self.receita_periodo_label = tb.Label(analise_frame, text="Receita (mês): R$ 0,00", 
                                            font=("Arial", 11), foreground="#795548")
        self.receita_periodo_label.pack(anchor="w", pady=2)
        
        # Frame meio - dados e gráficos
        middle_frame = tb.Frame(self.parent)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Histórico de vendas por produto
        vendas_frame = tb.LabelFrame(middle_frame, text="📈 Histórico de Vendas", padding=10)
        vendas_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # TreeView para vendas
        columns = ("data", "quantidade", "preco_unit", "receita", "lucro_unit", "lucro_total")
        self.vendas_tree = tb.Treeview(vendas_frame, columns=columns, show="headings", height=12)
        
        self.vendas_tree.heading("data", text="Data")
        self.vendas_tree.heading("quantidade", text="Qtd")
        self.vendas_tree.heading("preco_unit", text="Preço Unit.")
        self.vendas_tree.heading("receita", text="Receita")
        self.vendas_tree.heading("lucro_unit", text="Lucro Unit.")
        self.vendas_tree.heading("lucro_total", text="Lucro Total")
        
        self.vendas_tree.column("data", width=80, anchor="center")
        self.vendas_tree.column("quantidade", width=60, anchor="center")
        self.vendas_tree.column("preco_unit", width=80, anchor="e")
        self.vendas_tree.column("receita", width=80, anchor="e")
        self.vendas_tree.column("lucro_unit", width=80, anchor="e")
        self.vendas_tree.column("lucro_total", width=80, anchor="e")
        
        scrollbar_vendas = tb.Scrollbar(vendas_frame, orient="vertical", command=self.vendas_tree.yview)
        self.vendas_tree.configure(yscrollcommand=scrollbar_vendas.set)
        
        self.vendas_tree.pack(side="left", fill="both", expand=True)
        scrollbar_vendas.pack(side="right", fill="y")
        
        # Frame dos gráficos
        if MATPLOTLIB_AVAILABLE:
            graficos_frame = tb.LabelFrame(middle_frame, text="📊 Análise Gráfica", padding=10)
            graficos_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
            self._setup_graficos(graficos_frame)
        
    def _setup_graficos(self, parent):
        """Configura os gráficos de margem"""
        self.fig_margem = Figure(figsize=(8, 6), dpi=100)
        self.canvas_margem = FigureCanvasTkAgg(self.fig_margem, parent)
        self.canvas_margem.get_tk_widget().pack(fill="both", expand=True)
        
    def atualizar_dados(self):
        """Atualiza todos os dados da aba"""
        try:
            self.tipo_produto = self.produto_var.get()
            self._carregar_custos_produto()
            self._carregar_vendas_produto()
            self._calcular_analise()
            self._atualizar_lista_vendas()
            if MATPLOTLIB_AVAILABLE:
                self.atualizar_graficos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar dados de margem: {e}")
    
    def _carregar_custos_produto(self):
        """Carrega custos configurados para o produto"""
        try:
            # Implementar busca de custos do banco
            # Por enquanto, valores padrão
            custos_padrao = {
                "caixa_p": {"material": 5.00, "producao": 3.00, "outros": 2.00},
                "caixa_g": {"material": 8.00, "producao": 5.00, "outros": 3.00}
            }
            
            custos = custos_padrao.get(self.tipo_produto, {"material": 0, "producao": 0, "outros": 0})
            
            self.custo_material_var.set(str(custos["material"]))
            self.custo_producao_var.set(str(custos["producao"]))
            self.outros_custos_var.set(str(custos["outros"]))
            
            self.dados_custos = custos
            
        except Exception as e:
            print(f"Erro ao carregar custos: {e}")
            self.dados_custos = {"material": 0, "producao": 0, "outros": 0}
    
    def _carregar_vendas_produto(self):
        """Carrega vendas do produto selecionado"""
        try:
            vendas = db_manager.listar_pedidos_ordenados_prazo(limite=1000)
            
            hoje = datetime.now()
            self.dados_vendas = []
            
            for venda in vendas:
                # Ignorar pedidos cancelados/excluídos; caixas entregues contam como vendas
                status = (venda.get('status') or '').strip().lower()
                if status in ('cancelado', 'cancelada', 'excluido', 'excluida', 'deletado'):
                    continue

                produtos_txt = venda.get('produtos', '')
                if not produtos_txt:
                    continue
                
                # Parsear produtos do pedido
                quantidade_produto = 0
                if self.tipo_produto == "caixa_p" and "Caixa P" in produtos_txt:
                    # Extrair quantidade de Caixa P
                    linhas = produtos_txt.split('\n')
                    for linha in linhas:
                        if "Caixa P" in linha:
                            try:
                                # Formato: "X - Caixa P - R$ Y"
                                quantidade_produto = int(linha.split(' - ')[0])
                                break
                            except:
                                continue
                
                elif self.tipo_produto == "caixa_g" and "Caixa G" in produtos_txt:
                    # Extrair quantidade de Caixa G
                    linhas = produtos_txt.split('\n')
                    for linha in linhas:
                        if "Caixa G" in linha:
                            try:
                                # Formato: "X - Caixa G - R$ Y"
                                quantidade_produto = int(linha.split(' - ')[0])
                                break
                            except:
                                continue
                
                if quantidade_produto > 0:
                    data_venda = venda.get('data_emissao', '')
                    valor_produto = venda.get('valor_produto', 0) or 0
                    
                    try:
                        if isinstance(data_venda, str):
                            data_venda = datetime.strptime(data_venda[:10], '%Y-%m-%d')
                        
                        preco_unitario = valor_produto / quantidade_produto if quantidade_produto > 0 else 0
                        
                        self.dados_vendas.append({
                            'data': data_venda,
                            'quantidade': quantidade_produto,
                            'preco_unitario': preco_unitario,
                            'receita': valor_produto
                        })
                        
                    except ValueError:
                        continue
            
            # Ordenar por data
            self.dados_vendas.sort(key=lambda x: x['data'], reverse=True)
            
        except Exception as e:
            print(f"Erro ao carregar vendas do produto: {e}")
            self.dados_vendas = []
    
    def _calcular_analise(self):
        """Calcula análise de rentabilidade"""
        try:
            # Custo total unitário
            custo_material = float(self.custo_material_var.get() or 0)
            custo_producao = float(self.custo_producao_var.get() or 0)
            outros_custos = float(self.outros_custos_var.get() or 0)
            
            custo_total = custo_material + custo_producao + outros_custos
            
            # Calcular médias de preço das vendas
            precos = [venda['preco_unitario'] for venda in self.dados_vendas if venda['preco_unitario'] > 0]
            preco_medio = sum(precos) / len(precos) if precos else 0
            
            # Calcular lucro e margem
            lucro_unitario = preco_medio - custo_total
            margem_percentual = (lucro_unitario / preco_medio * 100) if preco_medio > 0 else 0
            
            # Vendas do mês atual
            hoje = datetime.now()
            vendas_mes = [v for v in self.dados_vendas 
                         if v['data'].year == hoje.year and v['data'].month == hoje.month]
            
            quantidade_mes = sum(v['quantidade'] for v in vendas_mes)
            receita_mes = sum(v['receita'] for v in vendas_mes)
            
            # Atualizar labels
            self.custo_total_label.config(text=f"Custo Total: R$ {custo_total:.2f}")
            self.preco_medio_label.config(text=f"Preço Médio: R$ {preco_medio:.2f}")
            
            cor_lucro = "#4CAF50" if lucro_unitario >= 0 else "#F44336"
            self.lucro_unitario_label.config(text=f"Lucro Unitário: R$ {lucro_unitario:.2f}", foreground=cor_lucro)
            
            cor_margem = "#4CAF50" if margem_percentual >= 20 else "#FF9800" if margem_percentual >= 10 else "#F44336"
            self.margem_percentual_label.config(text=f"Margem %: {margem_percentual:.1f}%", foreground=cor_margem)
            
            self.vendas_periodo_label.config(text=f"Vendas (mês): {quantidade_mes} unidades")
            self.receita_periodo_label.config(text=f"Receita (mês): R$ {receita_mes:.2f}")
            
        except ValueError as e:
            print(f"Erro ao calcular análise: {e}")
    
    def _atualizar_lista_vendas(self):
        """Atualiza a lista de vendas"""
        # Limpar dados existentes
        for item in self.vendas_tree.get_children():
            self.vendas_tree.delete(item)
        
        # Calcular custos
        try:
            custo_total = (float(self.custo_material_var.get() or 0) + 
                          float(self.custo_producao_var.get() or 0) + 
                          float(self.outros_custos_var.get() or 0))
        except:
            custo_total = 0
        
        # Inserir vendas
        for venda in self.dados_vendas:
            lucro_unitario = venda['preco_unitario'] - custo_total
            lucro_total = lucro_unitario * venda['quantidade']
            
            self.vendas_tree.insert("", "end", values=(
                venda['data'].strftime('%d/%m/%Y'),
                venda['quantidade'],
                f"R$ {venda['preco_unitario']:.2f}",
                f"R$ {venda['receita']:.2f}",
                f"R$ {lucro_unitario:.2f}",
                f"R$ {lucro_total:.2f}"
            ))
    
    def atualizar_graficos(self):
        """Atualiza os gráficos de margem"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        self.fig_margem.clear()
        
        # Gráfico 1: Evolução da margem ao longo do tempo
        ax1 = self.fig_margem.add_subplot(2, 1, 1)
        self._grafico_evolucao_margem(ax1)
        
        # Gráfico 2: Composição do custo
        ax2 = self.fig_margem.add_subplot(2, 1, 2)
        self._grafico_composicao_custo(ax2)
        
        self.fig_margem.tight_layout()
        self.canvas_margem.draw()
    
    def _grafico_evolucao_margem(self, ax):
        """Cria gráfico de evolução da margem"""
        if not self.dados_vendas:
            ax.text(0.5, 0.5, 'Sem dados de vendas para exibir', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Evolução da Margem de Lucro')
            return
        
        try:
            custo_total = (float(self.custo_material_var.get() or 0) + 
                          float(self.custo_producao_var.get() or 0) + 
                          float(self.outros_custos_var.get() or 0))
        except:
            custo_total = 0
        
        # Agrupar vendas por mês
        vendas_mes = {}
        for venda in self.dados_vendas:
            mes_ano = venda['data'].strftime('%Y-%m')
            if mes_ano not in vendas_mes:
                vendas_mes[mes_ano] = {'receita': 0, 'quantidade': 0}
            vendas_mes[mes_ano]['receita'] += venda['receita']
            vendas_mes[mes_ano]['quantidade'] += venda['quantidade']
        
        # Calcular margem por mês
        meses = sorted(vendas_mes.keys())
        margens = []
        
        for mes in meses:
            dados_mes = vendas_mes[mes]
            preco_medio = dados_mes['receita'] / dados_mes['quantidade'] if dados_mes['quantidade'] > 0 else 0
            margem = ((preco_medio - custo_total) / preco_medio * 100) if preco_medio > 0 else 0
            margens.append(margem)
        
        if meses:
            ax.plot(range(len(meses)), margens, marker='o', linewidth=2, markersize=6, color='#2196F3')
            ax.set_title('Evolução da Margem de Lucro (%)')
            ax.set_ylabel('Margem (%)')
            ax.set_xticks(range(len(meses)))
            ax.set_xticklabels([datetime.strptime(m, '%Y-%m').strftime('%m/%Y') for m in meses], rotation=45)
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
    
    def _grafico_composicao_custo(self, ax):
        """Cria gráfico de composição do custo"""
        try:
            custo_material = float(self.custo_material_var.get() or 0)
            custo_producao = float(self.custo_producao_var.get() or 0)
            outros_custos = float(self.outros_custos_var.get() or 0)
            
            custos = [custo_material, custo_producao, outros_custos]
            labels = ['Material', 'Produção', 'Outros']
            colors = ['#F44336', '#FF9800', '#9C27B0']
            
            # Filtrar custos não zero
            custos_filtrados = []
            labels_filtrados = []
            colors_filtrados = []
            
            for i, custo in enumerate(custos):
                if custo > 0:
                    custos_filtrados.append(custo)
                    labels_filtrados.append(labels[i])
                    colors_filtrados.append(colors[i])
            
            if custos_filtrados:
                ax.pie(custos_filtrados, labels=labels_filtrados, colors=colors_filtrados, 
                      autopct='%1.1f%%', startangle=90)
                ax.set_title('Composição do Custo Unitário')
            else:
                ax.text(0.5, 0.5, 'Nenhum custo configurado', ha='center', va='center', transform=ax.transAxes)
                ax.set_title('Composição do Custo Unitário')
                
        except ValueError:
            ax.text(0.5, 0.5, 'Valores de custo inválidos', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Composição do Custo Unitário')
    
    def salvar_custos(self):
        """Salva custos configurados"""
        try:
            custo_material = float(self.custo_material_var.get() or 0)
            custo_producao = float(self.custo_producao_var.get() or 0)
            outros_custos = float(self.outros_custos_var.get() or 0)
            
            # Implementar salvamento no banco
            self.dados_custos = {
                "material": custo_material,
                "producao": custo_producao,
                "outros": outros_custos
            }
            
            messagebox.showinfo("Sucesso", "Custos salvos com sucesso!")
            self.atualizar_dados()
            
        except ValueError:
            messagebox.showerror("Erro", "Valores de custo devem ser números válidos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar custos: {e}")
    
    def definir_produto(self, tipo):
        """Define o tipo de produto para análise"""
        self.produto_var.set(tipo)
        self.atualizar_dados()
