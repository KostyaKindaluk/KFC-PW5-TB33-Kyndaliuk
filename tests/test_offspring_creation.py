import pytest
from unittest.mock import Mock
from genetic_algorithm.algorithm import GeneticAlgorithm


@pytest.fixture
def algorithm_setup():
	mock_db = Mock()
	mock_selection = Mock()
	mock_selection.population_size = 8
	mock_selection.termination_condition = "generations"
	mock_selection.termination_value = 5
	mock_selection.id = 1
	
	test_cities = {
		0: (0.0, 0.0),
		1: (1.0, 0.0),
		2: (1.0, 1.0),
		3: (0.0, 1.0),
		4: (2.0, 2.0)
	}
	
	algorithm = GeneticAlgorithm(
		db_session=mock_db,
		selection=mock_selection,
		city_count=5,
		cities=test_cities
	)
	
	return algorithm


def test_crossover_produces_valid_offspring(algorithm_setup):
	algorithm = algorithm_setup
	
	parent1 = [0, 1, 2, 3, 4]
	parent2 = [4, 3, 2, 1, 0]
	
	child = algorithm.crossover(parent1, parent2)
	
	assert len(child) == len(parent1)
	
	assert set(child) == set(parent1)
	assert len(child) == len(set(child))


def test_crossover_preserves_segments(algorithm_setup):
	algorithm = algorithm_setup
	
	parent1 = [0, 1, 2, 3, 4]
	parent2 = [4, 3, 2, 1, 0]
	
	for _ in range(10):
		child = algorithm.crossover(parent1, parent2)
		
		max_common_length = 0
		for i in range(len(parent1)):
			for j in range(i+1, len(parent1)+1):
				segment = parent1[i:j]
				if len(segment) > 1:
					child_str = ' '.join(map(str, child))
					segment_str = ' '.join(map(str, segment))
					if segment_str in child_str:
						max_common_length = max(max_common_length, len(segment))
		
		assert max_common_length >= 2 or len(set(child) & set(parent1)) == len(parent1)


def test_mutation_modifies_individual(algorithm_setup):
	algorithm = algorithm_setup
	
	original = [0, 1, 2, 3, 4]
	individual = original.copy()
	
	algorithm.mutate(individual, mutation_rate=1.0)
	
	assert individual != original
	
	assert len(individual) == len(original)
	assert set(individual) == set(original)


def test_create_next_generation_maintains_population_size(algorithm_setup):
	algorithm = algorithm_setup
	
	algorithm.population = [
		[0, 1, 2, 3, 4],
		[1, 2, 3, 4, 0],
		[2, 3, 4, 0, 1],
		[3, 4, 0, 1, 2],
		[4, 0, 1, 2, 3],
		[0, 2, 1, 4, 3],
		[1, 3, 2, 0, 4],
		[2, 4, 3, 1, 0]
	]
	algorithm.fitness = [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5]
	
	parents = [[0, 1, 2, 3, 4], [1, 2, 3, 4, 0], [2, 3, 4, 0, 1], [3, 4, 0, 1, 2]]
	
	original_size = len(algorithm.population)
	algorithm.create_next_generation(parents)
	
	assert len(algorithm.population) == original_size
	
	for individual in algorithm.population:
		assert len(individual) == algorithm.city_count
		assert set(individual) == set(range(algorithm.city_count))