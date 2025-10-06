"""
tooltip_service.py - Tooltip positioning service

Provides custom tooltip positioning near cursor.
"""

from PyQt6.QtCore import QObject, QEvent
from PyQt6.QtWidgets import QToolTip, QApplication
from PyQt6.QtGui import QCursor


class ToolTipEventFilter(QObject):
    """Event filter for custom tooltip positioning."""
    
    def eventFilter(self, obj, event):
        """Filter tooltip events to position them near cursor."""
        if event.type() == QEvent.Type.ToolTip:
            cursor_pos = QCursor.pos()
            tooltip_pos = cursor_pos + type(cursor_pos)(5, 10)
            
            if obj.toolTip():
                QToolTip.showText(tooltip_pos, obj.toolTip(), obj)
                return True
        
        return super().eventFilter(obj, event)


def install_tooltip_fix(app: QApplication) -> None:
    """
    Install an application-wide event filter to fix tooltip positioning.
    
    Args:
        app: The QApplication instance
    """
    tooltip_filter = ToolTipEventFilter(app)
    app.installEventFilter(tooltip_filter)
