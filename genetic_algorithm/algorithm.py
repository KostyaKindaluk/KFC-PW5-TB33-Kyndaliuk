import random
import math
from concurrent.futures import ThreadPoolExecutor

from database import crud


class GeneticAlgorithm:
	def __init__(self, db_session, selection, city_count: int, cities: dict[int, tuple[float, float]], max_workers=4):
		self.db = db_session
		self.selection = selection
		self.population_size = selection.population_size
		self.termination_condition = selection.termination_condition
		self.termination_value = selection.termination_value
		self.city_count = city_count
		self.cities = cities
		self.population = []
		self.generation_number = 0
		self.max_workers = max_workers

	def run(self):
		self.history = []
		self.initialize_population()
		self.fitness = self.evaluate_population()
		self.generation_number = 0

		best_individual, best_distance = self.get_best_individual()
		self.history.append(best_distance)
		crud.add_generation(self.db, self.selection.id, self.generation_number, best_distance)
		crud.add_individual(self.db, self.selection.id, best_individual, best_distance, self.generation_number)

		while not self.check_termination():
			self.generation_number += 1
			parents = self.select_parents()
			self.create_next_generation(parents)
			self.evaluate_new_generation()
			self.select_next_population()
			best_individual, best_distance = self.get_best_individual()
			self.history.append(best_distance)

			crud.add_generation(self.db, self.selection.id, self.generation_number, best_distance)
			crud.add_individual(self.db, self.selection.id, best_individual, best_distance, self.generation_number)

		best_individual, best_distance = self.get_best_individual()
		crud.finish_selection(self.db, self.selection, best_distance)


	# 1. Ініціалізація популяції
	def initialize_population(self):
		self.population = []
		base = list(range(self.city_count))
		for _ in range(self.population_size):
			individual = base[:]
			random.shuffle(individual)
			self.population.append(individual)

	# 2. Оцінка придатності
	def evaluate_fitness(self, individual):
		distance = 0.0
		for i in range(len(individual)):
			a = self.cities[individual[i]]
			b = self.cities[individual[(i + 1) % len(individual)]]
			distance += math.dist(a, b)
		return distance

	def evaluate_population(self):
		with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
			distances = list(executor.map(self.evaluate_fitness, self.population))
		return distances

	# 3. Вибір батьків (турнірний вибір)
	def select_parents(self):
		tournament_size = 3
		parents = []
		for _ in range(self.population_size // 2):
			competitors = random.sample(list(zip(self.population, self.fitness)), tournament_size)
			winner = min(competitors, key=lambda x: x[1])[0]
			parents.append(winner)
		return parents

	# 4. Створення нащадків
	def crossover(self, parent1, parent2):
		size = len(parent1)
		start, end = sorted(random.sample(range(size), 2))
		child = [None] * size
		child[start:end+1] = parent1[start:end+1]
		pointer = 0
		for gene in parent2:
			if gene not in child:
				while child[pointer] is not None:
					pointer += 1
				child[pointer] = gene
		return child

	def mutate(self, individual, mutation_rate=0.05):
		for i in range(len(individual)):
			if random.random() < mutation_rate:
				j = random.randint(0, len(individual)-1)
				individual[i], individual[j] = individual[j], individual[i]

	def create_next_generation(self, parents):
		next_population = []

		best_index = self.fitness.index(min(self.fitness))
		elite_individual = self.population[best_index]
		next_population.append(elite_individual)

		while len(next_population) < self.population_size:
			parent1, parent2 = random.sample(parents, 2)
			child1 = self.crossover(parent1, parent2)
			child2 = self.crossover(parent2, parent1)
			self.mutate(child1)
			self.mutate(child2)
			next_population.extend([child1, child2])

		self.population = next_population[:self.population_size]

	# 5. Оцінка придатності нової популяції
	def evaluate_new_generation(self):
		self.fitness = self.evaluate_population()

	# 6. Вибір для наступної популяції (елітність)
	def select_next_population(self):
		combined = list(zip(self.population, self.fitness))
		combined.sort(key=lambda x: x[1])
		self.population = [ind for ind, _ in combined[:self.population_size]]
		self.fitness = [fit for _, fit in combined[:self.population_size]]


	# 7. Умова зупинки
	def check_termination(self):
		if self.termination_condition == "generations":
			return self.generation_number >= self.termination_value
		elif self.termination_condition == "no_improve":
			if len(self.history) < self.termination_value:
				return False
			
			recent_history = self.history[-self.termination_value:]
			best_in_recent = min(recent_history)
			oldest_in_recent = recent_history[0]
			
			improvement_threshold = 0.001
			return (oldest_in_recent - best_in_recent) < improvement_threshold
		
		return False

	# 8. Вивід результатів
	def get_best_individual(self):
		best_index = self.fitness.index(min(self.fitness))
		return self.population[best_index], self.fitness[best_index]