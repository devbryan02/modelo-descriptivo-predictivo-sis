"""
Paquete models - Modelos SQLAlchemy ORM

Importar todos los modelos para que Alembic los detecte
Esto es necesario para autogenerar migraciones
"""

from app.models.plan_seguro import PlanSeguro
from app.models.ipress import IPRESS
from app.models.servicio import Servicio
from app.models.atencion import Atencion

__all__ = ['PlanSeguro', 'IPRESS', 'Servicio', 'Atencion']