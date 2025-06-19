import ttkbootstrap as ttkb
import tkinter as tk
from tkinter import messagebox


class SelectionSettingsWindow(ttkb.Toplevel):
	def __init__(self, parent, on_start_callback):
		super().__init__(parent)
		self.title("Налаштування відбору")
		self.geometry("400x300")
		self.resizable(False, False)
		self.on_start_callback = on_start_callback
		self._create_widgets()


	def _create_widgets(self):
		frame = ttkb.Frame(self)
		frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
		
		ttkb.Label(frame, text="Розмір популяції:").pack(anchor="w")
		self.population_size_var = tk.IntVar(value=100)
		ttkb.Entry(frame, textvariable=self.population_size_var).pack(fill=tk.X, pady=5)
		
		ttkb.Label(frame, text="Умова завершення:").pack(anchor="w")
		self.termination_condition_var = tk.StringVar(value="generations")
		cond_frame = ttkb.Frame(frame)
		cond_frame.pack(fill=tk.X, pady=5)
		
		ttkb.Radiobutton(cond_frame, text="Кількість поколінь", 
			variable=self.termination_condition_var, value="generations").pack(anchor="w")
		ttkb.Radiobutton(cond_frame, text="Відсутність покращень", 
			variable=self.termination_condition_var, value="no_improve").pack(anchor="w")
		
		ttkb.Label(frame, text="Значення умови:").pack(anchor="w")
		self.termination_value_var = tk.IntVar(value=50)
		ttkb.Entry(frame, textvariable=self.termination_value_var).pack(fill=tk.X, pady=5)
		
		btn_frame = ttkb.Frame(frame)
		btn_frame.pack(fill=tk.X, pady=10)
		
		btn_start = ttkb.Button(btn_frame, text="Почати", command=self._on_start)
		btn_start.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
		
		btn_cancel = ttkb.Button(btn_frame, text="Відмінити", command=self.destroy)
		btn_cancel.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

	def _on_start(self):
		pop_size = self.population_size_var.get()
		term_cond = self.termination_condition_var.get()
		term_val = self.termination_value_var.get()
		
		if pop_size <= 0:
			messagebox.showerror("Помилка", "Розмір популяції повинен бути додатним числом")
			return
			
		if term_val <= 0:
			messagebox.showerror("Помилка", "Значення умови повинно бути додатним числом")
			return
			
		self.on_start_callback(pop_size, term_cond, term_val)
		self.destroy()