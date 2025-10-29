from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Servicio(Base):
    """
    Modelo SQLAlchemy para tabla servicios (tipos de atención médica)
    Basado en requirements.md sección "Modelo de Datos"
    
    Representa los diferentes servicios médicos que se brindan
    en las IPRESS del SIS (consultas, emergencias, cirugías, etc.)
    """
    __tablename__ = "servicios"

    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nombre = Column(String(200), unique=True, nullable=False, index=True)
    categoria = Column(String(100), nullable=True, index=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación one-to-many con atenciones
    atenciones = relationship("Atencion", back_populates="servicio")

    def __repr__(self):
        return f"<Servicio(id={self.id}, nombre='{self.nombre}')>"

    def __str__(self):
        if self.categoria:
            return f"{self.nombre} ({self.categoria})"
        return self.nombre