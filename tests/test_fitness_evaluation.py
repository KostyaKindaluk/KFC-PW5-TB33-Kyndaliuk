import pytest
import math
from unittest.mock import Mock
from genetic_algorithm.algorithm import GeneticAlgorithm


@pytest.fixture
def algorithm_setup():
	mock_db = Mock()
	mock_selection = Mock()
	mock_selection.population_size = 10
	mock_selection.termination_condition = "generations"
	mock_selection.termination_value = 5
	mock_selection.id = 1
	
	test_cities = {
		0: (0.0, 0.0),
		1: (3.0, 0.0),
		2: (3.0, 4.0),
		3: (0.0, 4.0)
	}
	
	algorithm = GeneticAlgorithm(
		db_session=mock_db,
		selection=mock_selection,
		city_count=4,
		cities=test_cities
	)
	
	return algorithm


def test_fitness_calculation_accuracy(algorithm_setup):
	"""Тестує точність обчислення фітнесу для відомого маршруту"""
	algorithm = algorithm_setup
	
	test_route = [0, 1, 2, 3]
	
	expected_distance = 3 + 4 + 3 + 4
	calculated_distance = algorithm.evaluate_fitness(test_route)
	
	assert abs(calculated_distance - expected_distance) < 0.001


def test_population_fitness_evaluation(algorithm_setup):
	algorithm = algorithm_setup
	
	algorithm.population = [
		[0, 1, 2, 3],
		[1, 2, 3, 0],
		[2, 3, 0, 1]
	]
	
	fitness_values = algorithm.evaluate_population()
	
	assert len(fitness_values) == len(algorithm.population)
	
	for fitness in fitness_values:
		assert fitness > 0
	
	for i in range(1, len(fitness_values)):
		assert abs(fitness_values[i] - fitness_values[0]) < 0.001


def test_fitness_consistency(algorithm_setup):
	algorithm = algorithm_setup
	
	test_route = [0, 1, 2, 3]
	
	fitness1 = algorithm.evaluate_fitness(test_route)
	fitness2 = algorithm.evaluate_fitness(test_route)
	fitness3 = algorithm.evaluate_fitness(test_route.copy())
	
	assert fitness1 == fitness2 == fitness3
	
	rotated_route = [1, 2, 3, 0]
	fitness_rotated = algorithm.evaluate_fitness(rotated_route)
	
	assert abs(fitness1 - fitness_rotated) < 0.001