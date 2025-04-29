import ttkbootstrap as tb
from os_app import OrdemServicoApp

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = OrdemServicoApp(root)
    root.mainloop()