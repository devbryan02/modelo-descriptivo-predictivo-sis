from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Atencion(Base):
    """
    Modelo SQLAlchemy para tabla atenciones (registro principal)
    Basado en requirements.md sección "Modelo de Datos"
    
    Registro principal que conecta todas las entidades del sistema
    y almacena la información de cada atención médica del SIS
    """
    __tablename__ = "atenciones"

    # Clave primaria
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Campos temporales
    año = Column(Integer, nullable=False, index=True)
    mes = Column(Integer, nullable=False, index=True)  # 1-12

    # Ubicación geográfica
    region = Column(String(100), nullable=False, index=True)
    provincia = Column(String(100), nullable=True)
    distrito = Column(String(100), nullable=True)

    # Datos demográficos del paciente
    sexo = Column(String(20), nullable=False, index=True)  # Masculino/Femenino
    grupo_edad = Column(String(20), nullable=False, index=True)  # 00-04, 05-11, etc.

    # Cantidad de atenciones registradas
    cantidad_atenciones = Column(Integer, nullable=False, default=1)

    # Claves foráneas (relaciones)
    plan_seguro_id = Column(Integer, ForeignKey("planes_seguro.id"), nullable=False, index=True)
    ipress_id = Column(Integer, ForeignKey("ipress.id"), nullable=False, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False, index=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones (back_populates)
    plan_seguro = relationship("PlanSeguro", back_populates="atenciones")
    ipress = relationship("IPRESS", back_populates="atenciones")
    servicio = relationship("Servicio", back_populates="atenciones")

    def __repr__(self):
        return f"<Atencion(id={self.id}, año={self.año}, mes={self.mes}, región='{self.region}')>"

    def __str__(self):
        return f"Atención {self.id}: {self.cantidad_atenciones} en {self.mes}/{self.año}"

    @property
    def fecha_periodo(self):
        """Devuelve el periodo como string MM/YYYY"""
        return f"{self.mes:02d}/{self.año}"

    @property
    def resumen_demografico(self):
        """Resumen demográfico del registro"""
        return f"{self.sexo}, {self.grupo_edad}"


# Índices para optimizar queries más comunes
# Basado en requirements.md para mejorar performance
Index('idx_atencion_año_mes', Atencion.año, Atencion.mes)
Index('idx_atencion_region', Atencion.region)
Index('idx_atencion_grupo_edad', Atencion.grupo_edad)
Index('idx_atencion_periodo_region', Atencion.año, Atencion.mes, Atencion.region)
