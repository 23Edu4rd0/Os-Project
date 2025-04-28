import tkinter as tk
from os_app import OrdemServicoApp

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap(r'assets\icons8-o-um-anel-40.ico')
    app = OrdemServicoApp(root)
    root.mainloop()