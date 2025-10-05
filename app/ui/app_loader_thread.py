from PyQt6.QtCore import QThread, pyqtSignal
import time

class AppLoaderThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def run(self):
        # Simula processamento pesado do app (ex: carregando dados, inicializando módulos)
        for i in range(1, 6):
            time.sleep(0.5)  # Simula trabalho
            self.progress.emit(i * 20)  # Progresso em %
        self.finished.emit()
