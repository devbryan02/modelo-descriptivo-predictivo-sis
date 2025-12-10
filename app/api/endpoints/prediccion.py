"""
Endpoints de predicción de demanda del SIS
Basado en REQUERIMENTS.MD - Endpoints de Predicción

POST /prediccion/demanda - Predicción individual
POST /prediccion/batch - Predicción masiva
GET /prediccion/modelos - Información de modelos disponibles
"""

from fastapi import APIRouter, HTTPException, status
import logging

from app.api.services.prediccion_service import PrediccionService
from app.schemas.prediccion_schema import (
    PrediccionRequest,
    PrediccionResponse,
    BatchPrediccionRequest,
    BatchPrediccionResponse,
    ModeloInfoResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prediccion", tags=["Predicción de Demanda"])


@router.post("/demanda", response_model=PrediccionResponse, status_code=status.HTTP_200_OK)
async def predecir_demanda(request: PrediccionRequest):
    """
    Predice la demanda de atenciones médicas del SIS
    
    Basado en REQUERIMENTS.MD:
    - **Body**: {año, mes, región, grupo_edad, sexo, plan_seguro}
    - **Retorna**: Predicción de número de atenciones
    
    Utiliza modelos de Machine Learning entrenados con datos históricos
    para estimar la cantidad de atenciones esperadas según los parámetros.
    
    **Parámetros:**
    - **año**: Año de la predicción (2020-2030)
    - **mes**: Mes de la predicción (1-12)
    - **region**: Región/Departamento del Perú
    - **grupo_edad**: Grupo etario (ej: '00-04', '18-29', '60+')
    - **sexo**: Sexo del paciente (MASCULINO/FEMENINO)
    - **nivel_ipress**: Nivel del establecimiento (I, II, III)
    - **servicio_categoria**: Categoría del servicio médico
    - **plan_seguro**: Tipo de plan del SIS
    - **modelo**: Tipo de modelo ML a usar (opcional)
    
    **Modelos disponibles:**
    - `linear`: Regresión Lineal (baseline)
    - `random_forest`: Random Forest Regressor (recomendado)
    - `gradient_boosting`: Gradient Boosting Regressor
    
    **Ejemplo de uso:**
    ```json
    {
        "año": 2025,
        "mes": 6,
        "region": "LIMA",
        "grupo_edad": "18-29",
        "sexo": "FEMENINO",
        "nivel_ipress": "II",
        "servicio_categoria": "CONSULTA EXTERNA",
        "plan_seguro": "SIS GRATUITO",
        "modelo": "random_forest"
    }
    ```
    
    **Retorna:**
    - Predicción numérica de atenciones esperadas
    - Intervalo de confianza (95%)
    - Métricas del modelo utilizado
    - Parámetros de entrada
    """
    try:
        logger.info(f"Endpoint /prediccion/demanda llamado para {request.region}, {request.mes}/{request.año}")
        resultado = PrediccionService.predecir_demanda(request)
        return resultado
        
    except FileNotFoundError as e:
        logger.error(f"Modelo no encontrado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Modelo no encontrado",
                "mensaje": str(e),
                "solucion": "Ejecute el script de entrenamiento: python app/ml/training/train_model.py"
            }
        )
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Error de validación",
                "mensaje": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Error en predicción: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error interno del servidor",
                "mensaje": "No se pudo completar la predicción",
                "detalle": str(e)
            }
        )


@router.post("/batch", response_model=BatchPrediccionResponse, status_code=status.HTTP_200_OK)
async def predecir_batch(request: BatchPrediccionRequest):
    """
    Predicción masiva para múltiples escenarios
    
    Basado en REQUERIMENTS.MD:
    - Predicción masiva para múltiples escenarios
    
    Permite realizar predicciones para múltiples combinaciones de parámetros
    en una sola llamada. Útil para análisis comparativos y planificación.
    
    **Límites:**
    - Mínimo: 1 predicción
    - Máximo: 100 predicciones por llamada
    
    **Ejemplo de uso:**
    ```json
    {
        "predicciones": [
            {
                "año": 2025,
                "mes": 6,
                "region": "LIMA",
                "grupo_edad": "18-29",
                "sexo": "FEMENINO",
                "nivel_ipress": "II",
                "servicio_categoria": "CONSULTA EXTERNA",
                "plan_seguro": "SIS GRATUITO"
            },
            {
                "año": 2025,
                "mes": 7,
                "region": "CUSCO",
                "grupo_edad": "30-59",
                "sexo": "MASCULINO",
                "nivel_ipress": "I",
                "servicio_categoria": "EMERGENCIA",
                "plan_seguro": "SIS INDEPENDIENTE"
            }
        ],
        "modelo": "random_forest"
    }
    ```
    
    **Retorna:**
    - Lista de predicciones individuales
    - Resumen estadístico (promedio, mínimo, máximo, desviación estándar)
    - Información del modelo utilizado
    """
    try:
        logger.info(f"Endpoint /prediccion/batch llamado con {len(request.predicciones)} escenarios")
        resultado = PrediccionService.predecir_batch(request)
        return resultado
        
    except FileNotFoundError as e:
        logger.error(f"Modelo no encontrado: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "Modelo no encontrado",
                "mensaje": str(e),
                "solucion": "Ejecute el script de entrenamiento: python app/ml/training/train_model.py"
            }
        )
    except Exception as e:
        logger.error(f"Error en predicción batch: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error interno del servidor",
                "mensaje": "No se pudo completar la predicción batch",
                "detalle": str(e)
            }
        )


@router.get("/modelos", response_model=ModeloInfoResponse, status_code=status.HTTP_200_OK)
async def obtener_info_modelos():
    """
    Obtiene información sobre los modelos de predicción disponibles
    
    Retorna información detallada sobre:
    - Modelos entrenados y disponibles
    - Métricas de rendimiento (R², RMSE, MAE)
    - Modelo recomendado para producción
    - Estado de cada modelo
    
    **Uso recomendado:**
    Consulte este endpoint antes de hacer predicciones para conocer
    qué modelos están disponibles y cuál tiene mejor rendimiento.
    
    **Métricas:**
    - **R²**: Coeficiente de determinación (0-1, mayor es mejor)
    - **RMSE**: Raíz del error cuadrático medio (menor es mejor)
    - **MAE**: Error absoluto medio (menor es mejor)
    """
    try:
        logger.info("Endpoint /prediccion/modelos llamado")
        info = PrediccionService.obtener_info_modelos()
        return info
        
    except Exception as e:
        logger.error(f"Error obteniendo info de modelos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error interno del servidor",
                "mensaje": "No se pudo obtener información de los modelos",
                "detalle": str(e)
            }
        )


@router.post("/modelos/limpiar-cache", status_code=status.HTTP_200_OK)
async def limpiar_cache_modelos():
    """
    Limpia el cache de modelos cargados en memoria
    
    Útil cuando se actualizan los modelos entrenados y se necesita
    recargarlos sin reiniciar el servidor.
    
    **Uso:**
    - Después de re-entrenar modelos
    - Para liberar memoria
    - Cuando se detectan problemas con modelos en cache
    """
    try:
        logger.info("Limpiando cache de modelos")
        PrediccionService.limpiar_cache()
        return {
            "mensaje": "Cache de modelos limpiado exitosamente",
            "accion": "Los modelos se recargarán en la próxima predicción"
        }
    except Exception as e:
        logger.error(f"Error limpiando cache: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Error limpiando cache",
                "detalle": str(e)
            }
        )
