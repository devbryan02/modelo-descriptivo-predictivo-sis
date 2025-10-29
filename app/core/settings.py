from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import os


class Settings(BaseSettings):
    """
    Configuración de variables de entorno usando Pydantic BaseSettings
    Basado en requirements.md sección "Deploy y Entorno"
    """
    
    # Información del proyecto
    PROJECT_NAME: str = "API de Análisis del SIS"
    PROJECT_DESCRIPTION: str = "Modelo de Análisis Descriptivo y Predictivo para la Identificación de Patrones en las Atenciones del Seguro Integral de Salud (SIS)"
    
    # Base de datos
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/sis_db",
        description="URL de conexión a PostgreSQL"
    )
    
    # Seguridad
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-12345678",
        description="Clave secreta para JWT y encriptación"
    )
    
    # Configuración de aplicación
    DEBUG: bool = Field(default=True, description="Modo debug")
    API_VERSION: str = Field(default="v1", description="Versión de la API")
    ENVIRONMENT: str = Field(default="development", description="Entorno de ejecución")
    
    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Orígenes permitidos para CORS (separados por comas)"
    )
    
    # Rutas de archivos
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CSV_PATH: str = os.path.join(BASE_DIR, "static", "dataset.csv")
    MODEL_PATH: str = os.path.join(BASE_DIR, "ml", "models", "predictor.pkl")
    
    @validator('DATABASE_URL')
    def validate_database_url(cls, v):
        """Validar que la URL de la base de datos sea válida"""
        if not v.startswith(('postgresql://', 'postgresql+psycopg2://')):
            raise ValueError('DATABASE_URL debe ser una URL de PostgreSQL válida')
        return v
    
    @validator('SECRET_KEY')
    def validate_secret_key(cls, v):
        """Validar que la clave secreta tenga longitud mínima"""
        if len(v) < 32:
            raise ValueError('SECRET_KEY debe tener al menos 32 caracteres')
        return v
    
    @validator('CORS_ORIGINS')
    def parse_cors_origins(cls, v):
        """Parsear CORS_ORIGINS desde string separado por comas"""
        if isinstance(v, str):
            return v  # Mantener como string, luego convertir en property
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Obtener CORS_ORIGINS como lista"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]
        return self.CORS_ORIGINS

    class Config:
        env_file = ".env"
        case_sensitive = True
        

# Instancia global de configuración
settings = Settings()