"""
Paquete core - Configuración central y base de datos
"""

from .settings import settings
from .database import get_db, Base, engine, SessionLocal

__all__ = ['settings', 'get_db', 'Base', 'engine', 'SessionLocal']