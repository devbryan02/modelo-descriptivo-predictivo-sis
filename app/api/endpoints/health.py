from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db, test_connection
from datetime import datetime
from typing import Dict, Any

# Endpoint de healthcheck
# GET /api/v1/health
# Basado en requirements.md sección "Funcionalidades Requeridas"

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, str]:
    """
    Endpoint básico de healthcheck
    
    Returns:
        Diccionario con estado básico de la API
    """
    return {
        "status": "ok",
        "service": "API de Análisis del SIS",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/detailed", response_model=None)
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Healthcheck detallado que verifica conexión a BD
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Diccionario con estado detallado de la API y BD
        
    Raises:
        HTTPException: Si hay problemas de conectividad
    """
    health_status = {
        "status": "ok",
        "service": "API de Análisis del SIS",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "database": "unknown",
        "checks": {}
    }
    
    try:
        # Verificar conexión a base de datos
        db_connected = test_connection()
        
        if db_connected:
            health_status["database"] = "connected"
            health_status["checks"]["database"] = "Conexión exitosa"
            
            # Verificar que podamos hacer una query simple
            try:
                result = db.execute("SELECT 1 as test").fetchone()
                if result and result[0] == 1:
                    health_status["checks"]["query_test"] = "Query de prueba exitosa"
                else:
                    health_status["checks"]["query_test"] = "Query de prueba falló"
            except Exception as e:
                health_status["checks"]["query_test"] = f"Error en query: {str(e)}"
                health_status["status"] = "degraded"
        else:
            health_status["database"] = "disconnected"
            health_status["checks"]["database"] = "Sin conexión a BD"
            health_status["status"] = "error"
            
        # Verificar configuración
        from app.core.settings import settings
        health_status["checks"]["config"] = "Configuración cargada"
        health_status["environment"] = settings.ENVIRONMENT
        
        # Si hay errores, cambiar status general
        if any("Error" in check or "falló" in check or "Sin conexión" in check for check in health_status["checks"].values()):
            health_status["status"] = "error" if health_status["status"] == "ok" else health_status["status"]
            
    except Exception as e:
        health_status["status"] = "error"
        health_status["database"] = "error"
        health_status["checks"]["error"] = f"Error crítico: {str(e)}"
        
        # Si hay errores críticos, lanzar excepción HTTP
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Servicio no disponible",
                "error": str(e),
                "health_status": health_status
            }
        )
    
    return health_status


@router.get("/ping")
async def ping() -> Dict[str, str]:
    """
    Endpoint simple de ping para monitoreo básico
    
    Returns:
        Respuesta de pong con timestamp
    """
    return {
        "message": "pong",
        "timestamp": datetime.now().isoformat()
    }