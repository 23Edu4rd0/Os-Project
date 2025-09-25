"""
Dashboard Principal - Visão Geral do Sistema
Exibe métricas, gráficos e resumos de performance
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QFont, QPainter, QPen, QBrush, QColor, QLinearGradient
import sqlite3
import json
from datetime import datetime, timedelta
from database import db_manager
from app.components.widgets.metric_card import MetricCard


class SimpleChart(QWidget):
    """Widget para exibir gráficos simples"""
    
    def __init__(self, title, data, color="#2fa6a0"):
        super().__init__()
        self.title = title
        self.data = data  # Lista de valores numéricos
        self.color = QColor(color)
        
        self.setMinimumHeight(120)
        self.setup_ui()
        
    def setup_ui(self):
        """Configurar interface do gráfico"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel(self.title)
        title_label.setStyleSheet("color: #b0b0b0; font-size: 12px;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
    def paintEvent(self, event):
        """Desenhar o gráfico"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Área útil para desenho
        rect = QRectF(0, 20, self.width(), self.height() - 30)
        
        if not self.data:
            return
            
        # Encontrar valores mínimo e máximo
        min_value = min(self.data)
        max_value = max(self.data)
        value_range = max_value - min_value
        
        if value_range == 0:
            return
            
        # Configurar pincel e caneta
        gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
        gradient.setColorAt(0, self.color)
        gradient.setColorAt(1, QColor(self.color.red(), self.color.green(), self.color.blue(), 0))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self.color, 2))
        
        # Calcular pontos
        points = []
        point_spacing = rect.width() / (len(self.data) - 1)
        
        for i, value in enumerate(self.data):
            x = rect.left() + (i * point_spacing)
            y_normalized = (value - min_value) / value_range
            y = rect.bottom() - (y_normalized * rect.height())
            points.append((x, y))
            
        # Desenhar área preenchida
        path = QPainter.QPainterPath()
        path.moveTo(points[0][0], rect.bottom())
        
        for x, y in points:
            path.lineTo(x, y)
            
        path.lineTo(points[-1][0], rect.bottom())
        path.closeSubpath()
        
        painter.drawPath(path)
        
        # Desenhar linha principal
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))


class DashboardWidget(QWidget):
    """Widget principal do dashboard"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface do usuário"""
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area para conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Widget de conteúdo
        content = QWidget()
        content.setObjectName("dashboardContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(20)
        
        # Seção de métricas principais
        metrics_widget = QWidget()
        metrics_widget.setObjectName("metricsWidget")
        self.metrics_layout = QGridLayout(metrics_widget)
        self.metrics_layout.setSpacing(15)
        content_layout.addWidget(metrics_widget)
        
        # Seção de gráficos
        charts_widget = QWidget()
        charts_widget.setObjectName("chartsWidget")
        self.charts_layout = QGridLayout(charts_widget)
        self.charts_layout.setSpacing(15)
        content_layout.addWidget(charts_widget)
        
        # Adicionar conteúdo ao scroll
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Estilização
        self.setStyleSheet("""
            QWidget#dashboardContent {
                background-color: transparent;
            }
            QWidget#metricsWidget, QWidget#chartsWidget {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
    def get_total_revenue(self):
        """Obter faturamento total"""
        try:
            orders = db_manager.listar_pedidos_ordenados_por_prazo(limite=1000)  # Pegar bastante histórico
            if not orders:
                return 0
                
            total = 0
            for order in orders:
                try:
                    if len(order) < 13:
                        continue
                        
                    # Extrair campos principais
                    valor_produto = float(order[6] or 0)  # valor_produto
                    valor_entrada = float(order[7] or 0)  # valor_entrada
                    frete = float(order[8] or 0)  # frete
                    dados_json = order[12]  # dados_json
                    
                    # Verificar desconto no JSON
                    desconto = 0
                    if dados_json:
                        try:
                            dados = json.loads(dados_json)
                            desconto = float(dados.get('desconto', 0) or 0)
                        except:
                            pass
                            
                    # Calcular valor total (valor total - entrada + frete - desconto)
                    valor_total = (valor_produto - valor_entrada) + frete - desconto
                    total += valor_total
                except Exception as e:
                    print(f"[WARN] Erro ao processar pedido {order[0]} no faturamento: {e}")
                    continue
                
            return total
        except Exception as e:
            print(f"[ERROR] Erro ao calcular faturamento: {e}")
            return 0
    
    def get_total_orders(self):
        """Obter número total de ordens"""
        try:
            orders = db_manager.listar_pedidos_ordenados_por_prazo()
            return len(orders) if orders else 0
        except Exception as e:
            print(f"[ERROR] Erro ao contar ordens: {e}")
            return 0

    def get_average_order_value(self):
        """Obter valor médio por ordem"""
        total = self.get_total_revenue()
        orders = self.get_total_orders()
        return total / orders if orders > 0 else 0
        
    def get_orders_by_period(self, days=30):
        """Obter dados de pedidos por período"""
        try:
            orders = db_manager.listar_pedidos_ordenados_por_prazo(limite=1000)
            if not orders:
                return []
                
            # Agrupar valores por dia
            daily_values = {}
            date_now = datetime.now()
            
            for order in orders:
                try:
                    # Data do pedido está no campo data_criacao
                    date_str = order[11]  # data_criacao é o 12º campo (índice 11)
                    if not date_str:
                        continue
                    
                    order_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    days_ago = (date_now - order_date).days
                    
                    if days_ago < days:
                        # Calcular valor total
                        valor_produto = float(order[6] or 0)  # valor_produto
                        valor_entrada = float(order[7] or 0)  # valor_entrada
                        frete = float(order[8] or 0)  # frete
                        
                        dados_json = order[12]  # dados_json 
                        desconto = 0
                        if dados_json:
                            try:
                                dados = json.loads(dados_json)
                                desconto = float(dados.get('desconto', 0) or 0)
                            except:
                                pass
                        
                        valor_total = (valor_produto - valor_entrada) + frete - desconto
                        
                        # Agrupar por data
                        date_key = order_date.date()
                        if date_key in daily_values:
                            daily_values[date_key] += valor_total
                        else:
                            daily_values[date_key] = valor_total
                except Exception as e:
                    print(f"[WARN] Erro ao processar pedido para gráfico: {e}")
                    continue
                    
            # Ordenar valores por data
            sorted_values = []
            current_date = (date_now - timedelta(days=days-1)).date()
            
            while current_date <= date_now.date():
                sorted_values.append(daily_values.get(current_date, 0))
                current_date += timedelta(days=1)
                
            return sorted_values
            
        except Exception as e:
            print(f"[ERROR] Erro ao buscar dados por período: {e}")
            return []
            
    def get_orders_by_status(self):
        """Obter contagem de pedidos por status"""
        try:
            orders = db_manager.listar_pedidos_ordenados_por_prazo()
            if not orders:
                return {}
                
            status_count = {}
            for order in orders:
                try:
                    dados_json = order[12]  # Campo dados_json
                    if not dados_json:
                        continue
                        
                    dados = json.loads(dados_json)
                    if not dados:
                        continue
                        
                    # Tentar obter o status do pedido
                    status = str(dados.get('status', 'Em Produção')).strip()
                    
                    # Se não tem status definido, usar padrão
                    if not status:
                        status = 'Em Produção'
                        
                    # Incrementar contador
                    if status in status_count:
                        status_count[status] += 1
                    else:
                        status_count[status] = 1
                except Exception as e:
                    print(f"[WARN] Erro ao processar status do pedido {order[0]}: {e}")
                    continue
                    
            return status_count
            
        except Exception as e:
            print(f"[ERROR] Erro ao contar pedidos por status: {e}")
            return {}
            
    def format_currency(self, value):
        """Formatar valor como moeda"""
        if isinstance(value, (int, float)):
            return f"R$ {value:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")
        return str(value)
        
    def calculate_trend(self, current, previous):
        """Calcular tendência entre dois valores"""
        if previous == 0:
            return None
            
        change = ((current - previous) / previous) * 100
        if change > 0:
            return f"↑ {change:.1f}%"
        elif change < 0:
            return f"↓ {abs(change):.1f}%"
        return "→ 0%"
    
    def update_data(self):
        """Atualizar dados do dashboard"""
        try:
            # Limpar layouts
            for layout in [self.metrics_layout, self.charts_layout]:
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                        
            # 1. Métricas principais
            # Calcular valores atuais
            faturamento_total = self.get_total_revenue()
            total_orders = self.get_total_orders()
            avg_order = self.get_average_order_value()
            
            # Adicionar cards de métricas
            self.metrics_layout.addWidget(
                MetricCard(
                    "Faturamento Total",
                    self.format_currency(faturamento_total), 
                    "💰"
                ), 
                0, 0
            )
            
            self.metrics_layout.addWidget(
                MetricCard(
                    "Total de Ordens", 
                    total_orders,
                    "📋"
                ),
                0, 1
            )
            
            self.metrics_layout.addWidget(
                MetricCard(
                    "Valor Médio", 
                    self.format_currency(avg_order),
                    "📊"
                ),
                0, 2
            )
            
            # 2. Gráficos
            # Gráfico de faturamento diário
            daily_values = self.get_orders_by_period(days=30)
            if daily_values:
                chart = SimpleChart(
                    "Faturamento dos Últimos 30 Dias",
                    daily_values
                )
                self.charts_layout.addWidget(chart, 0, 0)
                
            # Status dos pedidos
            status_count = self.get_orders_by_status()
            if status_count:
                status_text = "Status dos Pedidos:\n\n"
                for status, count in status_count.items():
                    status_text += f"{status}: {count}\n"
                    
                status_label = QLabel(status_text)
                status_label.setStyleSheet("""
                    background-color: #3a3a3a;
                    padding: 15px;
                    border-radius: 12px;
                    color: #fff;
                """)
                self.charts_layout.addWidget(status_label, 0, 1)
                
        except Exception as e:
            print(f"[ERROR] Erro ao atualizar dashboard: {e}")