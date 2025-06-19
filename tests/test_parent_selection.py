import pytest
from unittest.mock import Mock

from genetic_algorithm.algorithm import GeneticAlgorithm


@pytest.fixture
def algorithm_with_population():
	mock_db = Mock()
	mock_selection = Mock()
	mock_selection.population_size = 10
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
	
	algorithm.population = [
		[0, 1, 2, 3],
		[1, 2, 3, 0],
		[2, 3, 0, 1],
		[3, 0, 1, 2],
		[0, 2, 1, 3],
		[1, 3, 2, 0],
		[2, 0, 3, 1],
		[3, 1, 0, 2],
		[0, 3, 2, 1],
		[1, 0, 3, 2]
	]
	
	algorithm.fitness = [4.0, 4.0, 4.0, 4.0, 5.0, 5.0, 6.0, 6.0, 7.0, 8.0]
	
	return algorithm

def test_parent_selection_returns_correct_count(algorithm_with_population):
	algorithm = algorithm_with_population
	
	parents = algorithm.select_parents()
	
	expected_count = algorithm.population_size // 2
	assert len(parents) == expected_count

def test_parent_selection_returns_valid_individuals(algorithm_with_population):
	algorithm = algorithm_with_population
	
	parents = algorithm.select_parents()
	
	for parent in parents:
		assert len(parent) == algorithm.city_count
		assert set(parent) == set(range(algorithm.city_count))
		assert parent in algorithm.population

def test_tournament_selection_bias_towards_better(algorithm_with_population):
	algorithm = algorithm_with_population
	
	selection_counts = {}
	for individual in algorithm.population:
		selection_counts[tuple(individual)] = 0
	
	num_trials = 1000
	for _ in range(num_trials):
		parents = algorithm.select_parents()
		for parent in parents:
			selection_counts[tuple(parent)] += 1
	
	best_fitness_indices = [i for i, f in enumerate(algorithm.fitness) if f == min(algorithm.fitness)]
	worst_fitness_indices = [i for i, f in enumerate(algorithm.fitness) if f == max(algorithm.fitness)]
	
	best_selections = sum(selection_counts[tuple(algorithm.population[i])] for i in best_fitness_indices)
	worst_selections = sum(selection_counts[tuple(algorithm.population[i])] for i in worst_fitness_indices)
	
	assert best_selections > worst_selections