import ttkbootstrap as ttkb
import tkinter as tk
from tkinter.filedialog import askopenfilename
import json
from tkinter import messagebox


class SolveTaskWindow(ttkb.Toplevel):
	def __init__(self, parent, selection_manager):
		super().__init__(parent)
		self.title("Вирішення завдання")
		self.geometry("600x400")
		self.selection_manager = selection_manager
		self._create_widgets()


	def _create_widgets(self):
		frame = ttkb.Frame(self)
		frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
		
		btn_load = ttkb.Button(frame, text="Завантажити файл завдання", command=self.load_task_file)
		btn_load.pack(pady=5)
		
		self.txt_result = tk.Text(frame, height=15, state=tk.DISABLED)
		self.txt_result.pack(fill=tk.BOTH, expand=True, pady=5)

	def load_task_file(self):
		filepath = askopenfilename(filetypes=[("JSON files", "*.json")])
		if not filepath:
			return
			
		try:
			with open(filepath, "r", encoding="utf-8") as f:
				data = json.load(f)
				
			# Очікуємо формат:
			# { "cities": { "0": [x0, y0], "1": [x1, y1], ... }, "start": 0, "end": 10 }
			cities_raw = data.get("cities")
			if not cities_raw:
				messagebox.showerror("Помилка", "Файл не містить 'cities'")
				return
				
			task_cities = {int(k): tuple(v) for k, v in cities_raw.items()}
			
			sequence, distance = self.selection_manager.solve_task(task_cities)
			
			self.txt_result.config(state=tk.NORMAL)
			self.txt_result.delete("1.0", tk.END)
			self.txt_result.insert(tk.END, f"Оптимальна послідовність: {sequence}\n")
			self.txt_result.insert(tk.END, f"Загальна відстань: {distance:.3f}\n")
			self.txt_result.config(state=tk.DISABLED)
			
		except Exception as e:
			messagebox.showerror("Помилка", f"Не вдалося вирішити завдання: {e}")