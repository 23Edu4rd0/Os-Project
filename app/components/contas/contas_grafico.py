from datetime import datetime
import calendar

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_PRESENT = True
except Exception:
    MATPLOTLIB_PRESENT = False


def criar_grafico(parent, dados_vendas, periodo='mes'):
    """Cria e empacota um gráfico simples dentro de `parent`.

    - Se não houver dados, mostra uma mensagem clara.
    - Se houver dados, desenha um gráfico de barras (por dia ou por mês).
    Retorna (fig, canvas) quando matplotlib está disponível, ou (None, None).
    """
    if not MATPLOTLIB_PRESENT:
        return None, None

    fig = Figure(figsize=(8, 3.0), dpi=100)
    ax = fig.add_subplot(111)

    if not dados_vendas:
        ax.text(0.5, 0.5, 'Sem dados para exibir', ha='center', va='center', fontsize=10)
        ax.axis('off')
    else:
        try:
            if periodo == 'mes':
                hoje = datetime.now()
                dias = calendar.monthrange(hoje.year, hoje.month)[1]
                vendas_por_dia = {i: 0 for i in range(1, dias + 1)}
                for v in dados_vendas:
                    de = v.get('data_emissao', '')
                    if not de:
                        continue
                    if isinstance(de, str):
                        try:
                            dt = datetime.strptime(de[:10], '%Y-%m-%d')
                        except Exception:
                            continue
                    else:
                        dt = de
                    dia = getattr(dt, 'day', None)
                    if not dia:
                        continue
                    total = float(v.get('valor_produto') or 0) + float(v.get('frete') or 0)
                    vendas_por_dia[dia] += total

                dias_list = list(vendas_por_dia.keys())
                valores = list(vendas_por_dia.values())
                ax.bar(dias_list, valores, color='#2196F3')
                ax.set_title('Vendas por Dia (mês atual)')
                ax.set_xlabel('Dia')
                ax.set_ylabel('Valor (R$)')
            else:
                vendas_por_mes = {i: 0 for i in range(1, 13)}
                for v in dados_vendas:
                    de = v.get('data_emissao', '')
                    if not de:
                        continue
                    if isinstance(de, str):
                        try:
                            dt = datetime.strptime(de[:10], '%Y-%m-%d')
                        except Exception:
                            continue
                    else:
                        dt = de
                    mes = getattr(dt, 'month', None)
                    if not mes:
                        continue
                    total = float(v.get('valor_produto') or 0) + float(v.get('frete') or 0)
                    vendas_por_mes[mes] += total

                meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                valores = [vendas_por_mes[i] for i in range(1, 13)]
                ax.bar(meses, valores, color='#4CAF50')
                ax.set_title('Vendas por Mês')
                for label in ax.get_xticklabels():
                    label.set_rotation(45)
        except Exception:
            ax.text(0.5, 0.5, 'Erro ao gerar gráfico', ha='center', va='center')
            ax.axis('off')

    canvas = FigureCanvasTkAgg(fig, parent)
    canvas.get_tk_widget().pack(fill='x', expand=False)
    return fig, canvas
