from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from datetime import datetime

from app.core.settings import settings
from app.api.routes.main import api_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="API de Análisis del SIS",
    description="""
    API para análisis de datos del Sistema Integral de Salud (SIS) del Perú.
    
    Esta API proporciona endpoints para analizar las atenciones médicas del SIS,
    incluyendo estadísticas generales, análisis por región, servicios, demografía
    y tendencias temporales.
    
    Basado en requirements.md - Sistema de Análisis del SIS.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log del request
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )
    
    # Procesar request
    response = await call_next(request)
    
    # Log del response
    process_time = time.time() - start_time
    logger.info(
        f"Response: {response.status_code} "
        f"completed in {process_time:.4f}s"
    )
    
    return response

# Incluir routers
app.include_router(api_router)

# Endpoint raíz
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API del SIS
    
    Proporciona información básica sobre la API y enlaces a la documentación.
    """
    return {
        "message": "API de Análisis del SIS - Sistema Integral de Salud del Perú",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "estadisticas_generales": "/api/v1/atenciones/estadisticas",
            "por_region": "/api/v1/atenciones/por-region",
            "por_servicio": "/api/v1/atenciones/por-servicio",
            "demografico": "/api/v1/atenciones/demografico",
            "tendencias": "/api/v1/atenciones/tendencias",
            "buscar": "/api/v1/atenciones/buscar"
        },
        "environment": settings.ENVIRONMENT
    }

# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Error global en {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "message": "Error interno del servidor",
            "detail": "Ha ocurrido un error inesperado. Por favor contacte al administrador.",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

# Evento de inicio
@app.on_event("startup")
async def startup_event():
    logger.info("Iniciando API de Análisis del SIS")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("API disponible en /docs para documentación interactiva")

# Evento de cierre
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Cerrando API de Análisis del SIS")

if __name__ == "__main__":
    import uvicorn
    
    # Configuración para desarrollo
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
        log_level="info"
    )
