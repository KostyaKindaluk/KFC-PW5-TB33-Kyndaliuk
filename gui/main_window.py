import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
import threading

from logic.selection_manager import SelectionManager
from gui.selection_settings_window import SelectionSettingsWindow
from gui.solve_task_window import SolveTaskWindow


class MainWindow(ttkb.Window):
	def __init__(self):
		super().__init__(themename="darkly")
		self.title("Генетичний алгоритм — Комівояжер")
		self.geometry("700x500")

		self.selection_manager = None
		self.city_count = 60
		self.cities = self._generate_dummy_cities(self.city_count)
		self.selection_thread = None

		self._create_widgets()
		self._refresh_status()


	def _generate_dummy_cities(self, n):
		import random
		return {i: (random.uniform(0, 100), random.uniform(0, 100)) for i in range(n)}

	def _create_widgets(self):
		self.frame_top = ttkb.Frame(self)
		self.frame_top.pack(fill=tk.X, padx=10, pady=10)

		self.btn_start = ttkb.Button(self.frame_top, text="Почати відбір", command=self.open_settings)
		self.btn_start.pack(side=tk.LEFT, padx=5)

		self.btn_delete = ttkb.Button(self.frame_top, text="Видалити відбір", command=self.delete_selection)
		self.btn_delete.pack(side=tk.LEFT, padx=5)

		self.btn_solve = ttkb.Button(self.frame_top, text="Вирішити завдання", command=self.open_solve_task)
		self.btn_solve.pack(side=tk.LEFT, padx=5)

		self.frame_stats = ttkb.Frame(self)
		self.frame_stats.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		vsb = ttkb.Scrollbar(self.frame_stats, orient="vertical")
		vsb.pack(side="right", fill="y")

		self.tree = ttk.Treeview(self.frame_stats, columns=("generation", "best_distance"), show="headings", yscrollcommand=vsb.set)
		self.tree.heading("generation", text="Покоління")
		self.tree.heading("best_distance", text="Найкраща відстань")
		self.tree.pack(side="left", fill=tk.BOTH, expand=True)

		vsb.config(command=self.tree.yview)

		self.lbl_best_model = ttkb.Label(self, text="", anchor="w")
		self.lbl_best_model.pack(fill=tk.X, padx=10, pady=5)

		self.after(1000, self._periodic_refresh)

	def _periodic_refresh(self):
		if self.selection_thread and self.selection_thread.is_alive():
			self._refresh_status()
		self.after(1000, self._periodic_refresh)

	def _refresh_status(self):
		if self.selection_manager is None:
			self.selection_manager = SelectionManager(self.cities, self.city_count)

		try:
			status = self.selection_manager.get_current_selection_status()
			self.tree.delete(*self.tree.get_children())
			
			if status:
				for gen_num, dist in status["generations"]:
					self.tree.insert("", tk.END, values=(gen_num, f"{dist:.3f}"))

				if status["is_finished"]:
					best_text = f"Найкраща модель (відстань): {status['best_distance']:.3f}"
					self.lbl_best_model.configure(text=best_text)
					self.btn_start.configure(state=tk.NORMAL)
					self.btn_delete.configure(state=tk.NORMAL)
					self.btn_solve.configure(state=tk.NORMAL)
				else:
					self.lbl_best_model.configure(text="Відбір у процесі...")
					self.btn_start.configure(state=tk.DISABLED)
					self.btn_delete.configure(state=tk.DISABLED)
					self.btn_solve.configure(state=tk.DISABLED)
			else:
				self.lbl_best_model.configure(text="Відбір не виконано")
				self.btn_start.configure(state=tk.NORMAL)
				self.btn_delete.configure(state=tk.DISABLED)
				self.btn_solve.configure(state=tk.DISABLED)
		except Exception as e:
			print(f"Error refreshing status: {e}")

	def open_settings(self):
		def on_start(pop_size, term_cond, term_val):
			def run_selection():
				try:
					self.selection_manager.start_selection(pop_size, term_cond, term_val)
					self.after(0, lambda: messagebox.showinfo("Готово", "Відбір завершено"))
				except Exception as e:
					self.after(0, lambda: messagebox.showerror("Помилка", str(e)))
				finally:
					self.after(0, self._refresh_status)

			if self.selection_thread and self.selection_thread.is_alive():
				messagebox.showerror("Помилка", "Відбір вже виконується")
				return

			self.selection_thread = threading.Thread(target=run_selection, daemon=True)
			self.selection_thread.start()
			self._refresh_status()

		win = SelectionSettingsWindow(self, on_start)
		win.grab_set()

	def delete_selection(self):
		if messagebox.askyesno("Підтвердження", "Видалити останній відбір?"):
			try:
				self.selection_manager.delete_selection()
				self._refresh_status()
			except Exception as e:
				messagebox.showerror("Помилка", str(e))

	def open_solve_task(self):
		if self.selection_manager is None:
			messagebox.showerror("Помилка", "Немає завершеного відбору.")
			return

		win = SolveTaskWindow(self, self.selection_manager)
		win.grab_set()

	def start(self):
		self.mainloop()