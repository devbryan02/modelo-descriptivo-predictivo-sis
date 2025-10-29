from fastapi import APIRouter

# Router principal para la API del SIS
# Centraliza todas las rutas y endpoints

api_router = APIRouter()

# Importar los routers de endpoints
from app.api.endpoints import health, atenciones

# Health check endpoints
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# Análisis de atenciones  
api_router.include_router(atenciones.router, prefix="/api/v1", tags=["Atenciones"])

# Endpoints implementados según requirements.md:
# Health check (básico y detallado)
# Estadísticas generales 
# Análisis por región
# Análisis por servicio
# Análisis demográfico
# Tendencias temporales
# Búsqueda con filtros múltiples