from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import date

from app.core.database import get_db
from app.api.services.atencion_service import AtencionService
from app.schemas.atencion_schema import EstadisticasResponse, AtencionResponse

# Endpoints de análisis de atenciones del SIS
# Basado en requirements.md - Funcionalidades Requeridas

router = APIRouter(prefix="/atenciones", tags=["Análisis de Atenciones"])


@router.get("/estadisticas", response_model=EstadisticasResponse)
async def get_estadisticas_generales(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para el filtro (YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para el filtro (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas generales de las atenciones del SIS
    
    - **fecha_inicio**: Filtro opcional de fecha inicio
    - **fecha_fin**: Filtro opcional de fecha fin
    
    Retorna métricas como:
    - Total de atenciones
    - Costo total y promedio
    - Distribución por género
    - Rango de fechas de los datos
    """
    try:
        estadisticas = AtencionService.get_estadisticas_generales(
            db=db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return estadisticas
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas generales: {str(e)}"
        )


@router.get("/por-region")
async def get_atenciones_por_region(
    limit: int = Query(10, ge=1, le=50, description="Número máximo de regiones a retornar"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para el filtro"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para el filtro"),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Obtiene estadísticas de atenciones agrupadas por región (departamento)
    
    - **limit**: Número máximo de regiones a mostrar (1-50)
    - **fecha_inicio**: Filtro opcional de fecha inicio
    - **fecha_fin**: Filtro opcional de fecha fin
    
    Retorna para cada región:
    - Total de atenciones
    - Costo total y promedio
    - Número de IPRESS
    """
    try:
        resultados = AtencionService.get_atenciones_por_region(
            db=db,
            limit=limit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return resultados
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas por región: {str(e)}"
        )


@router.get("/por-servicio")
async def get_atenciones_por_servicio(
    limit: int = Query(10, ge=1, le=50, description="Número máximo de servicios a retornar"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para el filtro"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para el filtro"),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Obtiene estadísticas de atenciones agrupadas por tipo de servicio
    
    - **limit**: Número máximo de servicios a mostrar (1-50)
    - **fecha_inicio**: Filtro opcional de fecha inicio
    - **fecha_fin**: Filtro opcional de fecha fin
    
    Retorna para cada servicio:
    - Código y nombre del servicio
    - Total de atenciones
    - Costo total y promedio
    """
    try:
        resultados = AtencionService.get_atenciones_por_servicio(
            db=db,
            limit=limit,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return resultados
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas por servicio: {str(e)}"
        )


@router.get("/demografico")
async def get_analisis_demografico(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para el filtro"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para el filtro"),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Obtiene análisis demográfico detallado de las atenciones
    
    - **fecha_inicio**: Filtro opcional de fecha inicio
    - **fecha_fin**: Filtro opcional de fecha fin
    
    Retorna análisis por:
    - Grupos de edad (categorías definidas)
    - Género (con promedios de edad)
    - Estadísticas generales de edad
    """
    try:
        analisis = AtencionService.get_analisis_demografico(
            db=db,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return analisis
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener análisis demográfico: {str(e)}"
        )


@router.get("/tendencias")
async def get_tendencias_temporales(
    agrupacion: str = Query("mes", regex="^(mes|trimestre|año)$", description="Tipo de agrupación temporal"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para el filtro"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para el filtro"),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Obtiene tendencias temporales de las atenciones
    
    - **agrupacion**: Tipo de agrupación (mes, trimestre, año)
    - **fecha_inicio**: Filtro opcional de fecha inicio
    - **fecha_fin**: Filtro opcional de fecha fin
    
    Retorna series temporales con:
    - Periodo agrupado
    - Total de atenciones por periodo
    - Costo total y promedio por periodo
    """
    try:
        tendencias = AtencionService.get_tendencias_temporales(
            db=db,
            agrupacion=agrupacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return tendencias
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener tendencias temporales: {str(e)}"
        )


@router.get("/buscar", response_model=None)
async def buscar_atenciones(
    skip: int = Query(0, ge=0, description="Número de registros a omitir para paginación"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    departamento: Optional[str] = Query(None, description="Filtro por departamento"),
    servicio_codigo: Optional[str] = Query(None, description="Filtro por código de servicio"),
    plan_codigo: Optional[str] = Query(None, description="Filtro por código de plan"),
    sexo: Optional[str] = Query(None, regex="^[MF]$", description="Filtro por sexo (M/F)"),
    edad_min: Optional[int] = Query(None, ge=0, le=120, description="Edad mínima"),
    edad_max: Optional[int] = Query(None, ge=0, le=120, description="Edad máxima"),
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio para el filtro"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin para el filtro"),
    db: Session = Depends(get_db)
):
    """
    Busca atenciones con múltiples filtros y paginación
    
    Parámetros de filtro:
    - **departamento**: Busca por departamento (búsqueda parcial)
    - **servicio_codigo**: Código exacto del servicio
    - **plan_codigo**: Código exacto del plan
    - **sexo**: Género (M/F)
    - **edad_min/edad_max**: Rango de edad
    - **fecha_inicio/fecha_fin**: Rango de fechas
    
    Parámetros de paginación:
    - **skip**: Registros a omitir
    - **limit**: Máximo de registros (1-1000)
    
    Retorna:
    - Lista de atenciones encontradas
    - Metadatos de paginación
    """
    try:
        # Validación de rango de edad
        if edad_min is not None and edad_max is not None and edad_min > edad_max:
            raise HTTPException(
                status_code=400,
                detail="La edad mínima no puede ser mayor que la edad máxima"
            )
        
        # Validación de rango de fechas
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise HTTPException(
                status_code=400,
                detail="La fecha de inicio no puede ser posterior a la fecha de fin"
            )
        
        atenciones, total = AtencionService.buscar_atenciones(
            db=db,
            skip=skip,
            limit=limit,
            departamento=departamento,
            servicio_codigo=servicio_codigo,
            plan_codigo=plan_codigo,
            sexo=sexo,
            edad_min=edad_min,
            edad_max=edad_max,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        # Convertir a diccionarios para la respuesta
        atenciones_dict = [
            {
                "id": atencion.id,
                "fecha_atencion": atencion.fecha_atencion,
                "sexo": atencion.sexo,
                "edad": atencion.edad,
                "monto_pagado": float(atencion.monto_pagado),
                "departamento": atencion.ipress.departamento if atencion.ipress else None,
                "provincia": atencion.ipress.provincia if atencion.ipress else None,
                "distrito": atencion.ipress.distrito if atencion.ipress else None,
                "ipress_nombre": atencion.ipress.nombre if atencion.ipress else None,
                "servicio_nombre": atencion.servicio.nombre if atencion.servicio else None,
                "servicio_codigo": atencion.servicio.codigo if atencion.servicio else None,
                "plan_nombre": atencion.plan_seguro.nombre if atencion.plan_seguro else None,
                "plan_codigo": atencion.plan_seguro.codigo if atencion.plan_seguro else None
            }
            for atencion in atenciones
        ]
        
        return {
            "atenciones": atenciones_dict,
            "paginacion": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "tiene_siguiente": (skip + limit) < total,
                "tiene_anterior": skip > 0,
                "pagina_actual": (skip // limit) + 1,
                "total_paginas": (total + limit - 1) // limit
            },
            "filtros_aplicados": {
                "departamento": departamento,
                "servicio_codigo": servicio_codigo,
                "plan_codigo": plan_codigo,
                "sexo": sexo,
                "edad_min": edad_min,
                "edad_max": edad_max,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar atenciones: {str(e)}"
        )