"""
Widget para exibição de métricas em cards
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

class MetricCard(QFrame):
    """Card para exibir uma métrica específica"""
    
    def __init__(self, title, value, icon="📊", color="#2fa6a0", trend=None):
        """Inicializa o card de métrica"""
        super().__init__()
        self.setObjectName("metricCard")
        self._setup_ui(title, value, icon, color, trend)
        
    def _setup_ui(self, title, value, icon, color, trend):
        """Configura a interface do card"""
        # Layout principal
        self._layout = QVBoxLayout(self)
        self._layout.setSpacing(12)  # Aumentado de 8 para 12
        self._layout.setContentsMargins(24, 20, 24, 20)  # Aumentado as margens
        
        # Header com ícone e título
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # Ícone
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("""
            font-size: 24px;
            margin-right: 5px;
        """)
        header.addWidget(icon_label)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #b0b0b0;
            font-size: 12px;
            font-weight: 500;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(title_label)
        
        # Espaço flexível no header
        header.addStretch()
        self._layout.addLayout(header)
        
        # Valor principal
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            color: {color};
            font-size: 32px;  # Aumentado de 28px para 32px
            font-weight: bold;
            margin: 8px 0px;  # Aumentado de 5px para 8px
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._layout.addWidget(value_label)
        
        # Tendência (se fornecida)
        if trend:
            trend_label = QLabel(trend)
            trend_color = "#4CAF50" if "↑" in trend else "#F44336" if "↓" in trend else "#9E9E9E"
            trend_label.setStyleSheet(f"""
                color: {trend_color};
                font-size: 11px;
                margin-top: 2px;
            """)
            trend_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._layout.addWidget(trend_label)