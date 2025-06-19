from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from database.connection import Base


class Individual(Base):
	__tablename__ = "individuals"

	id = Column(Integer, primary_key=True, index=True)
	selection_id = Column(Integer, ForeignKey("selections.id"), nullable=False)
	sequence = Column(Text, nullable=False)
	distance = Column(Float, nullable=False)
	generation_number = Column(Integer, nullable=False)

	selection = relationship("Selection", back_populates="individuals")

class Generation(Base):
	__tablename__ = "generations"

	id = Column(Integer, primary_key=True, index=True)
	selection_id = Column(Integer, ForeignKey("selections.id"), nullable=False)
	generation_number = Column(Integer, nullable=False)
	best_distance = Column(Float, nullable=False)

	selection = relationship("Selection", back_populates="generations")

class Selection(Base):
	__tablename__ = "selections"

	id = Column(Integer, primary_key=True, index=True)
	created_at = Column(DateTime, default=datetime.utcnow)
	population_size = Column(Integer, nullable=False)
	termination_condition = Column(String(50), nullable=False)
	termination_value = Column(Integer, nullable=False)
	is_finished = Column(Boolean, default=False)
	best_distance = Column(Float, nullable=True)

	individuals = relationship("Individual", back_populates="selection", cascade="all, delete-orphan")
	generations = relationship("Generation", back_populates="selection", cascade="all, delete-orphan")
