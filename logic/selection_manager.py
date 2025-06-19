import json
from database import crud
from database.connection import SessionLocal
from genetic_algorithm.algorithm import GeneticAlgorithm


class SelectionManager:
	def __init__(self, cities: dict[int, tuple[float, float]], city_count: int):
		self.cities = cities
		self.city_count = city_count


	def start_selection(self, population_size: int, termination_condition: str, termination_value: int):
		db = SessionLocal()
		try:
			existing = crud.get_active_selection(db)
			if existing:
				raise Exception("There is already an active selection.")
			
			selection = crud.create_selection(
				db, population_size, termination_condition, termination_value
			)
			
			algo = GeneticAlgorithm(
				db, selection, self.city_count, self.cities
			)
			algo.run()
		finally:
			db.close()

	def delete_selection(self):
		db = SessionLocal()
		try:
			selection = crud.get_last_selection(db)
			if selection:
				crud.delete_selection(db, selection)
		finally:
			db.close()

	def get_current_selection_status(self):
		db = SessionLocal()
		try:
			selection = crud.get_last_selection(db)
			if not selection:
				return None
			
			generations = crud.get_all_generations(db, selection.id)
			return {
				"population_size": selection.population_size,
				"termination_condition": selection.termination_condition,
				"termination_value": selection.termination_value,
				"is_finished": selection.is_finished,
				"best_distance": selection.best_distance,
				"generations": [(gen.generation_number, gen.best_distance) for gen in generations]
			}
		finally:
			db.close()

	def solve_task(self, task_cities: dict[int, tuple[float, float]]):
		db = SessionLocal()
		try:
			selection = crud.get_last_selection(db)
			if not selection or not selection.is_finished:
				raise Exception("No finished selection to solve the task.")
			
			best_individual = crud.get_best_individual(db, selection.id)
			sequence = json.loads(best_individual.sequence)
			
			max_city_index = max(task_cities.keys())
			if max(sequence) > max_city_index:
				sequence = [i for i in sequence if i in task_cities]
				
				if len(sequence) < len(task_cities):
					sequence = list(task_cities.keys())
			
			distance = 0.0
			for i in range(len(sequence)):
				a = task_cities[sequence[i]]
				b = task_cities[sequence[(i + 1) % len(sequence)]]
				distance += ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
			
			return sequence, distance
		finally:
			db.close()