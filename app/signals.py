from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    statuses_updated = pyqtSignal()


# single shared instance
_signals = AppSignals()


def get_signals() -> AppSignals:
    return _signals
