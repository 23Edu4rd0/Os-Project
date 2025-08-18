"""
Módulo de controle financeiro - Receitas e lucros
"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import SUCCESS, INFO, WARNING
from tkinter import messagebox
from datetime import datetime, timedelta
import calendar

from database import db_manager
from .contas_grafico import criar_grafico

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ContasFinanceiro:
    """Gerencia a aba financeira - receitas e lucros"""
    
    def __init__(self, parent):
        self.parent = parent
        self.dados_vendas = []
        self.filtro_periodo = 'mes'  # mes, ano, total
        
        self._setup_interface()
        self.atualizar_dados()
    
    def _setup_interface(self):
        """Configura a interface da aba financeira"""
        # Frame de filtros
        filtros_frame = tb.Frame(self.parent)
        filtros_frame.pack(fill='x', padx=10, pady=5)
        
        # Label de filtros
        tb.Label(filtros_frame, text="Filtros", 
                font=("Arial", 12, "bold")).pack(side='left', padx=5)
        
        # Período
        tb.Label(filtros_frame, text="Período:").pack(side='left', padx=(20, 5))
        
        self.periodo_var = tk.StringVar(value='mes')
        periodo_options = [('Este Mês', 'mes'), ('Este Ano', 'ano'), ('Total', 'total')]
        
        for text, value in periodo_options:
            rb = tb.Radiobutton(filtros_frame, text=text, variable=self.periodo_var, 
                               value=value, command=self._alterar_periodo)
            rb.pack(side='left', padx=5)
        
        # Botão reconstruir rollup
        tb.Button(filtros_frame, text="Reconstruir Rollup", 
                 bootstyle="warning-outline", 
                 command=self._reconstruir_rollup).pack(side='right', padx=5)
        
        # Frame principal dividido
        main_frame = tb.Frame(self.parent)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Setup dos componentes
        self._setup_resumo(main_frame)
        self._setup_graficos(main_frame)
        self._setup_detalhes(main_frame)
    
    def _setup_resumo(self, parent):
        """Configura a seção de resumo financeiro"""
        resumo_frame = tb.LabelFrame(parent, text="💰 Resumo Financeiro", 
                                    bootstyle="info")
        resumo_frame.pack(fill='x', pady=(0, 5))
        
        # Grid de resumo
        info_frame = tb.Frame(resumo_frame)
        info_frame.pack(fill='x', padx=10, pady=10)
        
        # Labels de resumo
        self.total_vendas_label = tb.Label(info_frame, text="Total em Vendas: R$ 0,00", 
                                          font=("Arial", 11, "bold"), foreground="#2E8B57")
        self.total_vendas_label.grid(row=0, column=0, sticky='w', padx=5, pady=2)
        
        self.total_produtos_label = tb.Label(info_frame, text="Total dos Produtos: R$ 0,00", 
                                            font=("Arial", 10))
        self.total_produtos_label.grid(row=0, column=1, sticky='w', padx=20, pady=2)
        
        self.quantidade_vendas_label = tb.Label(info_frame, text="Quantidade de Vendas: 0", 
                                              font=("Arial", 10))
        self.quantidade_vendas_label.grid(row=1, column=0, sticky='w', padx=5, pady=2)
    
    def _setup_graficos(self, parent):
        """Configura a seção de gráficos"""
        if not MATPLOTLIB_AVAILABLE:
            aviso_frame = tb.Frame(parent)
            aviso_frame.pack(fill='x', pady=5)
            tb.Label(aviso_frame, text="📊 Gráficos não disponíveis", 
                    font=("Arial", 12, "bold"), foreground="red").pack()
            tb.Label(aviso_frame, text="(instale matplotlib: pip install matplotlib)", 
                    font=("Arial", 9), foreground="gray").pack()
            return
        
        grafico_frame = tb.LabelFrame(parent, text="📊 Gráficos", bootstyle="info")
        grafico_frame.pack(fill='x', pady=5)
        
        # Container para o gráfico
        self.grafico_container = tb.Frame(grafico_frame)
        self.grafico_container.pack(fill='x', padx=10, pady=10)
    
    def _setup_detalhes(self, parent):
        """Configura a seção de vendas detalhadas"""
        detalhes_frame = tb.LabelFrame(parent, text="📋 Vendas Detalhadas", 
                                      bootstyle="info")
        detalhes_frame.pack(fill='both', expand=True, pady=5)
        
        # Treeview para vendas
        tree_frame = tb.Frame(detalhes_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configurar Treeview (removendo coluna Frete)
        colunas = ("OS", "Cliente", "Data", "Produtos", "Total")
        self.vendas_tree = tb.Treeview(tree_frame, columns=colunas, show='headings', height=8)
        
        # Configurar cabeçalhos
        for col in colunas:
            self.vendas_tree.heading(col, text=col)
            if col == "OS":
                self.vendas_tree.column(col, width=80, anchor='center')
            elif col == "Cliente":
                self.vendas_tree.column(col, width=150)
            elif col == "Data":
                self.vendas_tree.column(col, width=100, anchor='center')
            else:
                self.vendas_tree.column(col, width=100, anchor='e')
        
        # Scrollbar para Treeview
        scrollbar_tree = tb.Scrollbar(tree_frame, orient='vertical', command=self.vendas_tree.yview)
        self.vendas_tree.configure(yscrollcommand=scrollbar_tree.set)
        
        self.vendas_tree.pack(side='left', fill='both', expand=True)
        scrollbar_tree.pack(side='right', fill='y')
    
    def _alterar_periodo(self):
        """Altera o filtro de período"""
        self.filtro_periodo = self.periodo_var.get()
        self.atualizar_dados()
    
    def atualizar_dados(self):
        """Atualiza todos os dados da interface"""
        try:
            self._carregar_vendas()
            self._atualizar_resumo()
            self._atualizar_detalhes()
            self.atualizar_graficos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar dados financeiros: {e}")
    
    def _reconstruir_rollup(self):
        """Reconstrói o rollup de dados"""
        try:
            # Atualiza a UI
            self.atualizar_dados()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao reconstruir rollup: {e}")
    
    def _carregar_vendas(self):
        """Carrega vendas do banco de dados"""
        try:
            hoje = datetime.now()

            # Tentar ler rollup (resumo) para desempenho
            if self.filtro_periodo == 'mes':
                resumo = db_manager.obter_resumo_mes(hoje.year, hoje.month)
                # criar um resumo sintético para manter compatibilidade
                self.dados_vendas = []
                self._resumo_simples = resumo
                return
            elif self.filtro_periodo == 'ano':
                resumo = db_manager.obter_resumo_ano(hoje.year)
                self.dados_vendas = []
                self._resumo_simples = resumo
                return
            else:
                resumo = db_manager.obter_resumo_total()
                self.dados_vendas = []
                self._resumo_simples = resumo
                return
            
        except Exception as e:
            print(f"Erro ao carregar vendas: {e}")
            self.dados_vendas = []
    
    def _atualizar_resumo(self):
        """Atualiza o resumo financeiro - SEM FRETE (cliente paga)"""
        # Se tivermos um resumo pré-computado use-o (mais rápido)
        total_produtos = 0
        quantidade = 0
        if hasattr(self, '_resumo_simples') and self._resumo_simples:
            # _resumo_simples pode ser uma tupla do banco
            if isinstance(self._resumo_simples, (tuple, list)):
                # Formato: (total_pedidos, total_valor, total_entradas)
                # Usar apenas valor dos produtos (sem frete)
                if len(self._resumo_simples) >= 2:
                    quantidade = int(self._resumo_simples[0] or 0)
                    # Buscar dados detalhados para calcular só produtos
                    try:
                        pedidos = db_manager.listar_pedidos_ordenados_prazo(limite=1000) or []
                        for pedido in pedidos:
                            if isinstance(pedido, dict):
                                total_produtos += pedido.get('valor_produto', 0) or 0
                            elif len(pedido) > 6:
                                total_produtos += pedido[6] or 0
                    except:
                        total_produtos = float(self._resumo_simples[1] or 0)  # fallback
            elif isinstance(self._resumo_simples, dict):
                total_produtos = float(self._resumo_simples.get('total_produtos', 0) or 0)
                quantidade = int(self._resumo_simples.get('qt_vendas', 0) or 0)
        else:
            quantidade = len(self.dados_vendas)
            for venda in self.dados_vendas:
                if isinstance(venda, dict):
                    total_produtos += venda.get('valor_produto', 0) or 0
                    # NÃO somar frete
        
        # Atualizar labels (removendo referências ao frete)
        self.total_vendas_label.config(text=f"Total em Vendas: R$ {total_produtos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.total_produtos_label.config(text=f"Total dos Produtos: R$ {total_produtos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'))
        self.quantidade_vendas_label.config(text=f"Quantidade de Vendas: {quantidade}")
    
    def _atualizar_detalhes(self):
        """Atualiza a tabela de detalhes das vendas"""
        # Limpar dados existentes
        for item in self.vendas_tree.get_children():
            self.vendas_tree.delete(item)
        
        # Se não temos detalhes carregados (por usar rollup), buscar ordens para exibir
        detalhe_rows = []
        if self.dados_vendas:
            detalhe_rows = list(self.dados_vendas)
        else:
            try:
                # Buscar ordens recentes para popular a tabela de detalhes
                pedidos = db_manager.listar_pedidos_ordenados_prazo(limite=1000) or []
                # Aplicar mesmo filtro de período usado no resumo
                hoje = datetime.now()
                for venda in pedidos:
                    # Verificar se venda é dict ou tupla/lista
                    if isinstance(venda, dict):
                        status = (venda.get('status') or '').strip().lower()
                        data_emissao = venda.get('data_criacao', '') or venda.get('data_emissao', '')
                        numero_os = venda.get('numero_os', '')
                        nome_cliente = venda.get('nome_cliente', '')
                        detalhes = venda.get('detalhes_produto', '')
                        valor_produto = venda.get('valor_produto', 0) or 0
                        frete = venda.get('frete', 0) or 0
                    else:
                        # Se é tupla/lista, usar índices
                        if len(venda) >= 8:
                            status = 'em produção'  # padrão para tuplas
                            data_emissao = venda[11] if len(venda) > 11 else ''  # data_criacao
                            numero_os = venda[1] if len(venda) > 1 else ''
                            nome_cliente = venda[2] if len(venda) > 2 else ''
                            detalhes = venda[5] if len(venda) > 5 else ''
                            valor_produto = venda[6] if len(venda) > 6 else 0
                            frete = venda[8] if len(venda) > 8 else 0
                        else:
                            continue
                    
                    if status in ('cancelado','cancelada','excluido','excluida','deletado'):
                        continue
                    if not data_emissao:
                        continue
                    try:
                        if isinstance(data_emissao, str):
                            dt = datetime.strptime(data_emissao[:10], '%Y-%m-%d')
                        else:
                            dt = data_emissao
                    except Exception:
                        continue

                    incluir = True
                    if self.filtro_periodo == 'mes':
                        incluir = (dt.year == hoje.year and dt.month == hoje.month)
                    elif self.filtro_periodo == 'ano':
                        incluir = (dt.year == hoje.year)
                    if incluir:
                        detalhe_rows.append(venda)
            except Exception:
                detalhe_rows = []

        # Inserir vendas na Treeview
        for venda in detalhe_rows:
            # Verificar se venda é dict ou tupla/lista
            if isinstance(venda, dict):
                os_num = venda.get('numero_os', 'N/A')
                nome_cliente = (venda.get('nome_cliente') or '').strip() or 'N/A'
                data_formatada = venda.get('data_criacao', 'N/A')
                detalhes = (venda.get('detalhes_produto') or '').strip() or 'N/A'
                valor_produto = venda.get('valor_produto', 0) or 0
                frete = venda.get('frete', 0) or 0
            else:
                # Se é tupla/lista, usar índices
                if len(venda) >= 8:
                    os_num = venda[1] if len(venda) > 1 else 'N/A'
                    nome_cliente = (venda[2] if len(venda) > 2 else '').strip() or 'N/A'
                    data_formatada = venda[11] if len(venda) > 11 else 'N/A'
                    detalhes = (venda[5] if len(venda) > 5 else '').strip() or 'N/A'
                    valor_produto = venda[6] if len(venda) > 6 else 0
                    frete = venda[8] if len(venda) > 8 else 0
                else:
                    continue
            
            # Obter telefone dependendo do tipo de dados
            if isinstance(venda, dict):
                telefone = (venda.get('telefone_cliente') or '').strip()
            else:
                telefone = (venda[4] if len(venda) > 4 else '').strip()
            
            # Formatar como 'Primeiro Sobrenome' + últimos 2 dígitos do telefone (ex: Eduardo Viana30)
            parts = nome_cliente.split()
            if parts and parts[0] != 'N/A':
                if len(parts) >= 2:
                    display_name = f"{parts[0]} {parts[-1]}"
                else:
                    display_name = parts[0]
            else:
                display_name = 'N/A'

            last2 = telefone[-2:] if telefone and len(telefone) >= 2 else ''
            cliente_display = f"{display_name}{last2}" if last2 else display_name

            # Formatar data
            if isinstance(venda, dict):
                data = venda.get('data_criacao', 'N/A')
            else:
                data = data_formatada
                
            if data and data != 'N/A':
                data = data[:10]  # Apenas a data

            produtos = float(valor_produto or 0)
            # Total agora é só produtos (sem frete)
            total = produtos

            self.vendas_tree.insert("", "end", values=(
                f"#{os_num}",
                cliente_display,
                data,
                f"R$ {produtos:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                f"R$ {total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            ))
    
    def atualizar_graficos(self):
        """Atualiza os gráficos"""
        # Recria o gráfico usando o helper modularizado. Se matplotlib não disponível, sai.
        if not MATPLOTLIB_AVAILABLE:
            return

        # Limpar gráfico anterior
        for widget in self.grafico_container.winfo_children():
            widget.destroy()
        
        try:
            # Dados para gráfico baseado no período
            dados_grafico = []
            if self.filtro_periodo == 'mes':
                # Vendas diárias do mês
                dados_grafico = db_manager.obter_vendas_diarias(30)
            elif self.filtro_periodo == 'ano':
                # Vendas mensais do ano
                dados_grafico = db_manager.obter_vendas_diarias(365)
            else:
                # Vendas dos últimos 30 dias
                dados_grafico = db_manager.obter_vendas_diarias(30)
            
            # Criar gráfico usando módulo
            canvas = criar_grafico(self.grafico_container, dados_grafico, self.filtro_periodo)
            
        except Exception as e:
            print(f"Erro ao criar gráfico: {e}")
            # Fallback: mostrar mensagem
            tb.Label(self.grafico_container, 
                    text="Erro ao carregar gráfico", 
                    font=("Arial", 10)).pack(pady=20)
