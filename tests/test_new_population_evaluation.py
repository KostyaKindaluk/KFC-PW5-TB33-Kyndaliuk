import pytest
from unittest.mock import Mock

from genetic_algorithm.algorithm import GeneticAlgorithm


@pytest.fixture
def algorithm_with_new_population():
	mock_db = Mock()
	mock_selection = Mock()
	mock_selection.population_size = 6
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
		[1, 3, 2, 0]
	]
	
	return algorithm


def test_evaluate_new_generation_calculates_all_fitness(algorithm_with_new_population):
	algorithm = algorithm_with_new_population
	
	assert not hasattr(algorithm, 'fitness') or algorithm.fitness is None or len(algorithm.fitness) == 0
	
	algorithm.evaluate_new_generation()
	
	assert len(algorithm.fitness) == len(algorithm.population)
	
	for fitness_value in algorithm.fitness:
		assert fitness_value > 0
		assert isinstance(fitness_value, (int, float))

def test_fitness_values_are_consistent(algorithm_with_new_population):
	algorithm = algorithm_with_new_population
	
	algorithm.evaluate_new_generation()
	first_fitness = algorithm.fitness.copy()
	
	algorithm.evaluate_new_generation()
	second_fitness = algorithm.fitness.copy()
	
	assert len(first_fitness) == len(second_fitness)
	for i in range(len(first_fitness)):
		assert abs(first_fitness[i] - second_fitness[i]) < 1e-10

def test_fitness_reflects_route_quality(algorithm_with_new_population):
	algorithm = algorithm_with_new_population
	
	good_route = [0, 1, 2, 3]
	bad_route = [0, 2, 1, 3]
	
	algorithm.population = [good_route, bad_route]
	algorithm.evaluate_new_generation()
	
	good_fitness = algorithm.fitness[0]
	bad_fitness = algorithm.fitness[1]
	
	assert good_fitness <= bad_fitness
	
	expected_good_fitness = 4.0
	assert abs(good_fitness - expected_good_fitness) < 0.001