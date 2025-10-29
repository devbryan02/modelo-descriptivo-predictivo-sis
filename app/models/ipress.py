from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class IPRESS(Base):
    """
    Modelo SQLAlchemy para tabla ipress (establecimientos de salud)
    Basado en requirements.md sección "Modelo de Datos"
    
    Representa las Instituciones Prestadoras de Servicios de Salud
    con sus niveles (I, II, III) y ubicación geográfica
    """
    __tablename__ = "ipress"

    # Campos principales
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    nivel = Column(String(10), nullable=False, index=True)  # I, II, III
    
    # Ubicación geográfica
    region = Column(String(100), nullable=False, index=True)
    provincia = Column(String(100), nullable=True)
    distrito = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación one-to-many con atenciones
    atenciones = relationship("Atencion", back_populates="ipress")

    def __repr__(self):
        return f"<IPRESS(id={self.id}, codigo='{self.codigo}', nivel='{self.nivel}')>"

    def __str__(self):
        return f"{self.nombre} (Nivel {self.nivel})"
    
    @property
    def ubicacion_completa(self):
        """Devuelve la ubicación completa como string"""
        ubicacion = [self.distrito, self.provincia, self.region]
        return ", ".join(filter(None, ubicacion))