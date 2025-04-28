import tkinter as tk
from os_app import OrdemServicoApp

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap('icon.ico')
    app = OrdemServicoApp(root)
    root.mainloop()