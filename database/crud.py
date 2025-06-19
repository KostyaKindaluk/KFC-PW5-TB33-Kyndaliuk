from sqlalchemy.orm import Session
from sqlalchemy import select, delete
import json

from database import models


def create_selection(db: Session, population_size: int, termination_condition: str, termination_value: int) -> models.Selection:
	selection = models.Selection(
		population_size=population_size,
		termination_condition=termination_condition,
		termination_value=termination_value,
		is_finished=False,
	)
	db.add(selection)
	db.commit()
	db.refresh(selection)
	return selection

def get_active_selection(db: Session) -> models.Selection:
	stmt = select(models.Selection).where(models.Selection.is_finished == False)
	return db.scalar(stmt)

def get_last_selection(db: Session) -> models.Selection:
	stmt = select(models.Selection).order_by(models.Selection.created_at.desc())
	return db.scalar(stmt)

def finish_selection(db: Session, selection: models.Selection, best_distance: float):
	selection.is_finished = True
	selection.best_distance = best_distance
	db.commit()

def delete_selection(db: Session, selection: models.Selection):
	db.delete(selection)
	db.commit()


def add_individual(db: Session, selection_id: int, sequence: list[int], distance: float, generation_number: int) -> models.Individual:
	individual = models.Individual(
		selection_id=selection_id,
		sequence=json.dumps(sequence),
		distance=distance,
		generation_number=generation_number
	)
	db.add(individual)
	db.commit()
	db.refresh(individual)
	return individual

def get_best_individual(db: Session, selection_id: int) -> models.Individual:
	stmt = select(models.Individual).where(models.Individual.selection_id == selection_id).order_by(models.Individual.distance.asc())
	return db.scalar(stmt)


def add_generation(db: Session, selection_id: int, generation_number: int, best_distance: float) -> models.Generation:
	generation = models.Generation(
		selection_id=selection_id,
		generation_number=generation_number,
		best_distance=best_distance
	)
	db.add(generation)
	db.commit()
	db.refresh(generation)
	return generation

def get_all_generations(db: Session, selection_id: int):
	stmt = select(models.Generation).where(models.Generation.selection_id == selection_id).order_by(models.Generation.generation_number)
	return db.scalars(stmt).all()