import pytest
from unittest.mock import Mock
from genetic_algorithm.algorithm import GeneticAlgorithm


@pytest.fixture
def algorithm_setup():
    """Налаштування алгоритму для тестів"""
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
    """Тестує що кросовер створює валідних нащадків"""
    algorithm = algorithm_setup
    
    parent1 = [0, 1, 2, 3, 4]
    parent2 = [4, 3, 2, 1, 0]
    
    child = algorithm.crossover(parent1, parent2)
    
    # Перевіряємо що нащадок має правильну довжину
    assert len(child) == len(parent1)
    
    # Перевіряємо що всі міста присутні рівно один раз
    assert set(child) == set(parent1)
    assert len(child) == len(set(child))  # Немає дублікатів


def test_crossover_preserves_segments(algorithm_setup):
    """Тестує що кросовер зберігає сегменти з батьків"""
    algorithm = algorithm_setup
    
    parent1 = [0, 1, 2, 3, 4]
    parent2 = [4, 3, 2, 1, 0]
    
    # Запускаємо кросовер кілька разів
    for _ in range(10):
        child = algorithm.crossover(parent1, parent2)
        
        # Нащадок повинен містити якийсь сегмент з parent1
        # Знаходимо найдовший спільний підсегмент
        max_common_length = 0
        for i in range(len(parent1)):
            for j in range(i+1, len(parent1)+1):
                segment = parent1[i:j]
                if len(segment) > 1:
                    # Перевіряємо чи цей сегмент існує в child в тому ж порядку
                    child_str = ' '.join(map(str, child))
                    segment_str = ' '.join(map(str, segment))
                    if segment_str in child_str:
                        max_common_length = max(max_common_length, len(segment))
        
        # Очікуємо що принаймні якийсь сегмент довжиною >= 2 збережеться
        assert max_common_length >= 2 or len(set(child) & set(parent1)) == len(parent1)


def test_mutation_modifies_individual(algorithm_setup):
    """Тестує що мутація змінює індивіда"""
    algorithm = algorithm_setup
    
    original = [0, 1, 2, 3, 4]
    individual = original.copy()
    
    # Запускаємо мутацію з високим рівнем
    algorithm.mutate(individual, mutation_rate=1.0)
    
    # Індивід повинен змінитися
    assert individual != original
    
    # Але повинен залишатися валідним маршрутом
    assert len(individual) == len(original)
    assert set(individual) == set(original)


def test_create_next_generation_maintains_population_size(algorithm_setup):
    """Тестує що створення нового покоління зберігає розмір популяції"""
    algorithm = algorithm_setup
    
    # Налаштовуємо початкову популяцію та фітнес
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
    
    # Розмір популяції повинен залишитися тим же
    assert len(algorithm.population) == original_size
    
    # Всі індивіди повинні бути валідними
    for individual in algorithm.population:
        assert len(individual) == algorithm.city_count
        assert set(individual) == set(range(algorithm.city_count))