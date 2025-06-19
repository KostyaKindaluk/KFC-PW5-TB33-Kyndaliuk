import pytest
from sqlalchemy import text

from unittest.mock import Mock, patch
from database.connection import get_db, engine
from database.models import Selection
from genetic_algorithm.algorithm import GeneticAlgorithm


def test_gui_initializes():
	try:
		from gui.main_window import MainWindow
		
		app = MainWindow()
		
		assert app is not None
		assert hasattr(app, 'selection_manager')
		assert hasattr(app, 'cities')
		assert hasattr(app, 'city_count')
		
		app.update()
		
		app.destroy()
	except Exception as e:
		pytest.fail(f"GUI initialization failed: {e}")


def test_database_connection():
	try:
		db_gen = get_db()
		db = next(db_gen)
		
		assert db is not None
		
		result = db.execute(text("SELECT 1 as test_value"))
		row = result.fetchone()
		assert row[0] == 1
		
		db.close()
		
	except Exception as e:
		pytest.fail(f"Database connection failed: {e}")


def test_algorithm_initialization():
	try:
		mock_db = Mock()
		mock_selection = Mock()
		mock_selection.population_size = 10
		mock_selection.termination_condition = "generations"
		mock_selection.termination_value = 5
		mock_selection.id = 1
		
		cities = {
			0: (0.0, 0.0),
			1: (10.0, 0.0),
			2: (10.0, 10.0),
			3: (0.0, 10.0)
		}
		city_count = 4
		
		algorithm = GeneticAlgorithm(
			db_session=mock_db,
			selection=mock_selection,
			city_count=city_count,
			cities=cities,
			max_workers=1
		)
		
		assert algorithm.db == mock_db
		assert algorithm.selection == mock_selection
		assert algorithm.population_size == 10
		assert algorithm.termination_condition == "generations"
		assert algorithm.termination_value == 5
		assert algorithm.city_count == city_count
		assert algorithm.cities == cities
		assert algorithm.generation_number == 0
		assert algorithm.population == []
		
		algorithm.initialize_population()
		assert len(algorithm.population) == 10
		assert all(len(individual) == city_count for individual in algorithm.population)
		assert all(set(individual) == set(range(city_count)) for individual in algorithm.population)
		
	except Exception as e:
		pytest.fail(f"Algorithm initialization failed: {e}")