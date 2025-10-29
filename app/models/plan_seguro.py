from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class PlanSeguro(Base):
    """
    Modelo SQLAlchemy para tabla planes_seguro
    Basado en requirements.md sección "Modelo de Datos"
    
    Representa los diferentes tipos de planes del SIS:
    - Gratuito, Independiente, NRUS, Microempresa, Para Todos
    """
    __tablename__ = "planes_seguro"

    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    descripcion = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación one-to-many con atenciones
    atenciones = relationship("Atencion", back_populates="plan_seguro")

    def __repr__(self):
        return f"<PlanSeguro(id={self.id}, nombre='{self.nombre}')>"

    def __str__(self):
        return self.nombre