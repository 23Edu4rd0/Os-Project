import platform
import tkinter.messagebox as messagebox
import ttkbootstrap as tb
try:
    import win32print
except ImportError:
    win32print = None


class ImpressApp:
    def __init__(self, root):
        self.root = root

    def selecionar_impressora(self):
        """
        Abre uma janela para selecionar a impressora padrão do sistema,
        com layout aprimorado.
        """
        sistema = platform.system()

        if sistema == "Windows":
            if not win32print:
                messagebox.showerror(
                    "Erro",
                    ("Biblioteca 'pywin32' não instalada ou não pôde ser "
                     "importada. Use 'pip install pywin32'.")
                )
                return
            try:
                impressoras = win32print.EnumPrinters(
                    win32print.PRINTER_ENUM_LOCAL |
                    win32print.PRINTER_ENUM_CONNECTIONS
                )
                impressoras_nomes = [imp[2] for imp in impressoras]

                janela_impressora = tb.Toplevel(self.root)
                janela_impressora.title("Selecionar Impressora")
                janela_impressora.geometry("420x320")
                janela_impressora.resizable(False, False)
                # Centralizar na tela
                largura = 420
                altura = 320
                x = ((janela_impressora.winfo_screenwidth() // 2)
                     - (largura // 2))
                y = ((janela_impressora.winfo_screenheight() // 2)
                     - (altura // 2))
                janela_impressora.geometry(f"{largura}x{altura}+{x}+{y}")

                # Título destacado
                tb.Label(
                    janela_impressora, text="Selecione uma Impressora",
                    font=("Montserrat", 14, "bold"), bootstyle="light"
                ).pack(pady=(20, 10))

                impressora_selecionada = tb.StringVar()
                impressora_combobox = tb.Combobox(
                    janela_impressora,
                    textvariable=impressora_selecionada,
                    state="readonly", font=("Montserrat", 12)
                )
                impressora_combobox["values"] = impressoras_nomes
                impressora_combobox.pack(pady=10, padx=40, fill="x")

                status_label = tb.Label(
                    janela_impressora, text="", font=("Montserrat", 11),
                    bootstyle="info"
                )
                status_label.pack(pady=10)

                def confirmar_selecao():
                    impressora = impressora_selecionada.get()
                    if impressora:
                        win32print.SetDefaultPrinter(impressora)
                        status_label.config(
                            text=f"Impressora selecionada: {impressora}",
                            bootstyle="success"
                        )
                    else:
                        status_label.config(
                            text="Nenhuma impressora selecionada.",
                            bootstyle="danger"
                        )

                btn_frame = tb.Frame(janela_impressora)
                btn_frame.pack(pady=20)
                tb.Button(
                    btn_frame, text="Confirmar", command=confirmar_selecao,
                    bootstyle="success", width=15
                ).pack(side="left", padx=10)
                tb.Button(
                    btn_frame, text="Fechar",
                    command=janela_impressora.destroy,
                    bootstyle="secondary", width=15
                ).pack(side="left", padx=10)

            except ImportError:  # Should be caught by the top-level check
                messagebox.showerror(
                    "Erro",
                    ("Biblioteca 'pywin32' não instalada. "
                     "Use 'pip install pywin32'.")
                )
            except Exception as e:
                messagebox.showerror("Erro",
                                     f"Erro ao listar impressoras: {e}")

        elif sistema == "Linux":
            try:
                import subprocess
                resultado = subprocess.run(
                    ["lpstat", "-p"], capture_output=True, text=True
                )
                linhas = resultado.stdout.splitlines() \
                    if resultado.returncode == 0 else []
                impressoras = [
                    linha.split()[1] for linha in linhas
                    if linha.startswith("printer")
                ]

                janela_impressora = tb.Toplevel(self.root)
                janela_impressora.title("Selecionar Impressora")
                janela_impressora.geometry("420x320")
                janela_impressora.resizable(False, False)
                largura = 420
                altura = 320
                x = ((janela_impressora.winfo_screenwidth() // 2)
                     - (largura // 2))
                y = ((janela_impressora.winfo_screenheight() // 2)
                     - (altura // 2))
                janela_impressora.geometry(f"{largura}x{altura}+{x}+{y}")

                tb.Label(
                    janela_impressora, text="Selecione uma Impressora",
                    font=("Montserrat", 14, "bold"), bootstyle="primary"
                ).pack(pady=(20, 10))

                impressora_selecionada = tb.StringVar()
                impressora_combobox = tb.Combobox(
                    janela_impressora,
                    textvariable=impressora_selecionada,
                    state="readonly", font=("Montserrat", 12)
                )
                impressora_combobox["values"] = impressoras
                impressora_combobox.pack(pady=10, padx=40, fill="x")

                status_label = tb.Label(
                    janela_impressora, text="", font=("Montserrat", 11),
                    bootstyle="info"
                )
                status_label.pack(pady=10)

                if not impressoras:
                    status_label.config(
                        text="Nenhuma impressora encontrada no sistema.",
                        bootstyle="warning"
                    )

                def confirmar_selecao():
                    impressora = impressora_selecionada.get()
                    if impressora:
                        subprocess.run([
                            "lpoptions", "-d", impressora
                        ], check=True)
                        status_label.config(
                            text=f"Impressora selecionada: {impressora}",
                            bootstyle="success"
                        )
                    else:
                        status_label.config(
                            text="Nenhuma impressora selecionada.",
                            bootstyle="danger"
                        )

                btn_frame = tb.Frame(janela_impressora)
                btn_frame.pack(pady=20)
                tb.Button(
                    btn_frame, text="Confirmar", command=confirmar_selecao,
                    bootstyle="success", width=15
                ).pack(side="left", padx=10)
                tb.Button(
                    btn_frame, text="Fechar",
                    command=janela_impressora.destroy,
                    bootstyle="secondary", width=15
                ).pack(side="left", padx=10)

            except FileNotFoundError:
                messagebox.showerror(
                    "Erro",
                    ("O comando 'lpstat' não está disponível. "
                     "Instale o CUPS com 'sudo apt install cups'.")
                )
            except subprocess.CalledProcessError as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao executar comando do sistema: {e}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao listar impressoras: {e}"
                )

        else:
            messagebox.showerror(
                "Erro",
                (f"Sistema operacional '{sistema}' não suportado para "
                 "seleção de impressoras.")
            )
