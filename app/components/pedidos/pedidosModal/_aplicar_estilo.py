from .__init__ import PedidosModal

def _aplicar_estilo(self):
    self.setStyleSheet("""
        QDialog {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QDialog QWidget {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QScrollArea { background: transparent; border: none; }
        QScrollArea > QWidget > QWidget { background: #2d2d2d; }
        QFrame { background: transparent; }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #404040;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background-color: #353535;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: #ffffff;
            background-color: #353535;
        }
        QLabel {
            color: #ffffff;
            background-color: transparent;
        }
        QLineEdit, QTextEdit {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #606060;
            border-radius: 5px;
            padding: 8px;
            font-size: 12px;
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #0d7377;
        }
        QComboBox {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #606060;
            border-radius: 5px;
            padding: 8px;
            font-size: 12px;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #505050;
        }
        QComboBox QAbstractItemView {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #606060;
            selection-background-color: #0d7377;
        }
        QPushButton {
            background-color: #0d7377;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 10px 15px;
            font-weight: 500;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #0a5d61;
        }
        QPushButton:pressed {
            background-color: #084a4d;
        }
        QScrollBar:vertical {
            background-color: #404040;
            width: 14px;
            border-radius: 7px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background-color: #606060;
            border-radius: 7px;
            min-height: 30px;
            margin: 2px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #707070;
        }
        QScrollBar::handle:vertical:pressed {
            background-color: #808080;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
            background: transparent;
        }
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
        }
    """)
