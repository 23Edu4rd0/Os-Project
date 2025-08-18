"""
Interface do formulário principal (aba Formulário)

Este módulo fornece uma classe mínima `FormularioTab(parent)` que monta
um formulário simples com campos de exemplo. Foi adicionada apenas para
garantir que a importação em `app/main_app.py` funcione — mantém-se
leve e sem dependências extras.
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import PRIMARY


class FormularioTab:
	"""Uma implementação mínima do formulário usada pela aba de UI.

	Args:
		parent: widget pai onde o formulário será montado
	"""

	def __init__(self, parent):
		self.parent = parent
		self._build()

	def _build(self):
		frame = tb.Frame(self.parent)
		frame.pack(fill="both", expand=True, padx=8, pady=8)

		title = tb.Label(frame, text="Formulário de Ordem de Serviço", font=(None, 14, 'bold'))
		title.pack(pady=(0, 10))

		form = tb.Frame(frame)
		form.pack(anchor="nw")

		tb.Label(form, text="Cliente:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
		self.cliente_entry = tb.Entry(form)
		self.cliente_entry.grid(row=0, column=1, padx=4, pady=4)

		tb.Label(form, text="Descrição:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
		self.descricao_entry = tb.Entry(form, width=60)
		self.descricao_entry.grid(row=1, column=1, padx=4, pady=4)

		tb.Label(form, text="Valor:").grid(row=2, column=0, sticky="w", padx=4, pady=4)
		self.valor_entry = tb.Entry(form)
		self.valor_entry.grid(row=2, column=1, padx=4, pady=4)

		btn_frame = tb.Frame(frame)
		btn_frame.pack(pady=12)

		salvar_btn = tb.Button(btn_frame, text="Salvar", bootstyle=PRIMARY, command=self._on_salvar)
		salvar_btn.pack()

	def _on_salvar(self):
		# Implementação mínima: apenas coleta os valores e limpa os campos.
		cliente = self.cliente_entry.get().strip()
		descricao = self.descricao_entry.get().strip()
		valor = self.valor_entry.get().strip()

		# Aqui você integraria com o db_manager ou callbacks do MainApp
		print(f"Salvar: cliente={cliente}, descricao={descricao}, valor={valor}")

		# Limpar campos
		self.cliente_entry.delete(0, 'end')
		self.descricao_entry.delete(0, 'end')
		self.valor_entry.delete(0, 'end')

