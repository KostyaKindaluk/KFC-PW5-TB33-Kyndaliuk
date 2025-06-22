import pytest
from unittest.mock import Mock

from genetic_algorithm.algorithm import GeneticAlgorithm


@pytest.fixture
def algorithm_with_mixed_population():
	mock_db = Mock()
	mock_selection = Mock()
	mock_selection.population_size = 5
	mock_selection.termination_condition = "generations"
	mock_selection.termination_value = 5
	mock_selection.id = 1
	
	test_cities = {
		0: (0.0, 0.0),
		1: (1.0, 0.0),
		2: (1.0, 1.0),
		3: (0.0, 1.0)
	}
	
	algorithm = GeneticAlgorithm(
		db_session=mock_db,
		selection=mock_selection,
		city_count=4,
		cities=test_cities
	)
	
	return algorithm

def test_elitism_preserves_best_individual(algorithm_with_mixed_population):
	algorithm = algorithm_with_mixed_population
	
	best_individual = [0, 1, 2, 3]
	algorithm.population = [
		[0, 2, 1, 3],
		[1, 3, 2, 0],
		best_individual,
		[2, 0, 3, 1],
		[3, 1, 0, 2]
	]
	
	algorithm.fitness = algorithm.evaluate_population()
	
	best_fitness = min(algorithm.fitness)
	best_index = algorithm.fitness.index(best_fitness)
	original_best = algorithm.population[best_index].copy()
	
	parents = [algorithm.population[0], algorithm.population[1]]
	algorithm.create_next_generation(parents)
	
	algorithm.evaluate_new_generation()
	new_best_fitness = min(algorithm.fitness)
	
	assert new_best_fitness <= best_fitness
	
	assert original_best in algorithm.population


def test_population_size_maintained_after_selection(algorithm_with_mixed_population):
	algorithm = algorithm_with_mixed_population
	
	algorithm.population = [
		[0, 1, 2, 3],
		[1, 2, 3, 0],
		[2, 3, 0, 1],
		[3, 0, 1, 2],
		[0, 2, 1, 3]
	]
	algorithm.fitness = algorithm.evaluate_population()
	
	original_size = len(algorithm.population)
	
	algorithm.select_next_population()
	
	assert len(algorithm.population) == original_size
	assert len(algorithm.fitness) == original_size


def test_selection_sorts_by_fitness(algorithm_with_mixed_population):
	algorithm = algorithm_with_mixed_population
	
	algorithm.population = [
		[0, 2, 1, 3],
		[0, 1, 2, 3],
		[1, 3, 2, 0],
		[2, 0, 3, 1],
		[3, 1, 0, 2]
	]
	
	algorithm.fitness = algorithm.evaluate_population()
	
	algorithm.select_next_population()
	
	for i in range(len(algorithm.fitness) - 1):
		assert algorithm.fitness[i] <= algorithm.fitness[i + 1]
	
	best_expected_fitness = 4.0
	assert abs(algorithm.fitness[0] - best_expected_fitness) < 0.001