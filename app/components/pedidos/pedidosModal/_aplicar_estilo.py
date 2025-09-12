from .__init__ import PedidosModal

def _aplicar_estilo(self):
    self.setStyleSheet("""
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1a1a1a, stop:1 #2d2d2d);
            color: #ffffff;
            border-radius: 15px;
        }
        QDialog QWidget {
            background-color: transparent;
            color: #ffffff;
        }
        QScrollArea { 
            background: transparent; 
            border: none; 
            border-radius: 10px;
        }
        QScrollArea > QWidget > QWidget { 
            background: transparent; 
        }
        QFrame { 
            background: transparent; 
        }
        QGroupBox {
            font-weight: 600;
            font-size: 14px;
            border: 2px solid #0d7377;
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 20px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(13, 115, 119, 0.1), stop:1 rgba(13, 115, 119, 0.05));
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 15px 0 15px;
            color: #0d7377;
            background: #2d2d2d;
            border-radius: 6px;
            font-weight: bold;
        }
        QLabel {
            color: #ffffff;
            background-color: transparent;
            font-size: 13px;
        }
        QLineEdit, QTextEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #404040, stop:1 #353535);
            color: #ffffff;
            border: 2px solid #555555;
            border-radius: 8px;
            padding: 12px 15px;
            font-size: 13px;
            selection-background-color: #0d7377;
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #0d7377;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #454545, stop:1 #3a3a3a);
        }
        QLineEdit:hover, QTextEdit:hover {
            border: 2px solid #666666;
        }
        QComboBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #404040, stop:1 #353535);
            color: #ffffff;
            border: 2px solid #555555;
            border-radius: 8px;
            padding: 12px 15px;
            font-size: 13px;
            min-height: 20px;
        }
        QComboBox:hover {
            border: 2px solid #666666;
        }
        QComboBox:focus {
            border: 2px solid #0d7377;
        }
        QComboBox::drop-down {
            border: none;
            background: transparent;
            width: 25px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid #888888;
            margin-right: 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #404040;
            color: #ffffff;
            border: 2px solid #0d7377;
            border-radius: 8px;
            selection-background-color: #0d7377;
            outline: none;
        }
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0d7377, stop:1 #0a5d61);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            padding: 12px 20px;
            font-weight: 600;
            font-size: 13px;
            min-height: 15px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0e8a8f, stop:1 #0c6b70);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #094e52, stop:1 #073d41);
        }
        QPushButton#btn_limpar, QPushButton#btn_limpar_cli {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #666666, stop:1 #555555);
        }
        QPushButton#btn_limpar:hover, QPushButton#btn_limpar_cli:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #777777, stop:1 #666666);
        }
        QPushButton#btn_cancelar {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #cc5555, stop:1 #aa4444);
        }
        QPushButton#btn_cancelar:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #dd6666, stop:1 #bb5555);
        }
        QScrollBar:vertical {
            background-color: rgba(64, 64, 64, 0.5);
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0d7377, stop:1 #14a085);
            border-radius: 6px;
            min-height: 30px;
            margin: 1px;
        }
        QScrollBar::handle:vertical:hover {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0e8a8f, stop:1 #17b297);
        }
        QScrollBar::handle:vertical:pressed {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #0a5d61, stop:1 #0f7e6b);
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
        QCheckBox {
            color: #ffffff;
            font-size: 13px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid #555555;
            background-color: #353535;
        }
        QCheckBox::indicator:checked {
            border: 2px solid #0d7377;
            background-color: #0d7377;
            image: url(data:image/svg+xml;charset=utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path fill="white" d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/></svg>);
        }
        QCheckBox::indicator:hover {
            border: 2px solid #666666;
        }
    """)
