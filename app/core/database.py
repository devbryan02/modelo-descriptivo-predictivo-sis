from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.core.settings import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear engine de SQLAlchemy
# pool_pre_ping=True para manejar desconexiones automáticamente
# echo=settings.DEBUG para log de queries en desarrollo
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
    # Configuraciones adicionales para PostgreSQL
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,  # Reciclar conexiones cada 5 minutos
    pool_timeout=30    # Timeout de 30 segundos para obtener conexión
)

# Crear SessionLocal con configuración optimizada
# autocommit=False: Transacciones manuales para mejor control
# autoflush=False: Flush manual para mejor performance
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base declarativa para todos los modelos ORM
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos en FastAPI
    Usa yield pattern para garantizar que la sesión se cierre
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en sesión de base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """
    Crear todas las tablas definidas en los modelos
    Usar solo en desarrollo, en producción usar Alembic
    """
    logger.info("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas exitosamente")


def test_connection():
    """
    Probar la conexión a la base de datos
    Útil para healthchecks y diagnósticos
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Conexión a base de datos exitosa")
            return True
    except Exception as e:
        logger.error(f"Error conectando a base de datos: {e}")
        return False