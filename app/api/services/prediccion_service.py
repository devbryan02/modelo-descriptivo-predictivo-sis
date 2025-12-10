"""
Servicio de predicción de demanda de atenciones del SIS
Basado en REQUERIMENTS.MD - Endpoints de Predicción

Carga modelos entrenados y realiza predicciones
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from app.ml.predictor import SISPredictor
from app.schemas.prediccion_schema import (
    PrediccionRequest,
    PrediccionResponse,
    BatchPrediccionRequest,
    BatchPrediccionResponse,
    ModeloInfoResponse,
    PrediccionBatchItem
)

logger = logging.getLogger(__name__)


class PrediccionService:
    """
    Servicio de negocio para predicciones de demanda del SIS
    
    Gestiona la carga de modelos y realización de predicciones
    """
    
    # Cache de modelos cargados
    _modelos_cache: Dict[str, SISPredictor] = {}
    
    @classmethod
    def _get_modelo(cls, model_type: str) -> SISPredictor:
        """
        Obtiene un modelo desde el cache o lo carga
        
        Args:
            model_type: Tipo de modelo a cargar
            
        Returns:
            Instancia de SISPredictor con modelo cargado
        """
        # Si ya está en cache, retornarlo
        if model_type in cls._modelos_cache:
            logger.debug(f"Modelo {model_type} obtenido desde cache")
            return cls._modelos_cache[model_type]
        
        # Cargar modelo
        logger.info(f"Cargando modelo {model_type}...")
        predictor = SISPredictor(model_type=model_type)
        
        try:
            predictor.load_model()
            cls._modelos_cache[model_type] = predictor
            logger.info(f"Modelo {model_type} cargado exitosamente")
            return predictor
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Modelo '{model_type}' no encontrado. "
                "Ejecute el script de entrenamiento primero: "
                "python app/ml/training/train_model.py"
            )
    
    @classmethod
    def predecir_demanda(
        cls,
        request: PrediccionRequest
    ) -> PrediccionResponse:
        """
        Realiza predicción de demanda individual
        
        Args:
            request: Parámetros de la predicción
            
        Returns:
            Respuesta con la predicción
        """
        logger.info(f"Realizando predicción para {request.region}, {request.mes}/{request.año}")
        
        # Obtener modelo
        model_type = request.modelo.value if request.modelo else "random_forest"
        predictor = cls._get_modelo(model_type)
        
        # Realizar predicción (nuevo formato retorna Dict)
        result = predictor.predict(
            año=request.año,
            mes=request.mes,
            region=request.region,
            sexo=request.sexo,
            grupo_edad=request.grupo_edad,
            nivel_ipress=request.nivel_ipress,
            servicio_categoria=request.servicio_categoria,
            plan_seguro=request.plan_seguro
        )
        
        # Extraer valores del nuevo formato
        prediccion = result['expected_value']
        prediccion_redondeada = result['rounded_prediction']
        nivel_demanda = result['demand_level']
        
        # Calcular intervalo de confianza (estimación simple)
        # Para Random Forest y Gradient Boosting, usar desviación estándar
        intervalo = None
        if model_type in ['random_forest', 'gradient_boosting', 'poisson']:
            # Estimación: ±1.96 * RMSE para 95% confianza
            rmse = predictor.metrics.get('test', {}).get('rmse', prediccion * 0.1)
            margen = 1.96 * rmse
            intervalo = {
                'inferior': max(0, prediccion - margen),
                'superior': prediccion + margen,
                'nivel': '95%'
            }
        
        # Construir respuesta
        response = PrediccionResponse(
            prediccion=round(prediccion, 2),
            prediccion_redondeada=prediccion_redondeada,
            modelo_usado=model_type,
            parametros={
                'año': request.año,
                'mes': request.mes,
                'region': request.region,
                'grupo_edad': request.grupo_edad,
                'sexo': request.sexo,
                'nivel_ipress': request.nivel_ipress,
                'servicio_categoria': request.servicio_categoria,
                'plan_seguro': request.plan_seguro
            },
            metricas_modelo=predictor.metrics.get('test'),
            intervalo_confianza=intervalo
        )
        
        logger.info(f"Predicción completada: {prediccion:.2f} atenciones")
        return response
    
    @classmethod
    def predecir_batch(
        cls,
        request: BatchPrediccionRequest
    ) -> BatchPrediccionResponse:
        """
        Realiza predicciones masivas (batch)
        
        Args:
            request: Lista de escenarios a predecir
            
        Returns:
            Respuesta con todas las predicciones
        """
        logger.info(f"Realizando predicción batch de {len(request.predicciones)} escenarios")
        
        # Obtener modelo
        model_type = request.modelo.value if request.modelo else "random_forest"
        predictor = cls._get_modelo(model_type)
        
        # Realizar predicciones
        resultados = []
        predicciones_valores = []
        
        for item in request.predicciones:
            try:
                result = predictor.predict(
                    año=item.año,
                    mes=item.mes,
                    region=item.region,
                    sexo=item.sexo,
                    grupo_edad=item.grupo_edad,
                    nivel_ipress=item.nivel_ipress,
                    servicio_categoria=item.servicio_categoria,
                    plan_seguro=item.plan_seguro
                )
                
                resultados.append({
                    'prediccion': round(result['expected_value'], 2),
                    'prediccion_redondeada': result['rounded_prediction'],
                    'parametros': {
                        'año': item.año,
                        'mes': item.mes,
                        'region': item.region,
                        'grupo_edad': item.grupo_edad,
                        'sexo': item.sexo
                    }
                })
                
                predicciones_valores.append(result['expected_value'])
                
            except Exception as e:
                logger.error(f"Error en predicción batch: {str(e)}")
                resultados.append({
                    'prediccion': None,
                    'error': str(e),
                    'parametros': {
                        'año': item.año,
                        'mes': item.mes,
                        'region': item.region
                    }
                })
        
        # Calcular resumen estadístico
        predicciones_array = np.array([p for p in predicciones_valores if p is not None])
        
        resumen = {
            'prediccion_promedio': round(float(np.mean(predicciones_array)), 2),
            'prediccion_minima': round(float(np.min(predicciones_array)), 2),
            'prediccion_maxima': round(float(np.max(predicciones_array)), 2),
            'desviacion_estandar': round(float(np.std(predicciones_array)), 2),
            'total_exitosas': len(predicciones_valores),
            'total_fallidas': len(resultados) - len(predicciones_valores)
        }
        
        response = BatchPrediccionResponse(
            total_predicciones=len(request.predicciones),
            modelo_usado=model_type,
            resultados=resultados,
            resumen=resumen
        )
        
        logger.info(f"Predicción batch completada: {len(predicciones_valores)} exitosas")
        return response
    
    @classmethod
    def obtener_info_modelos(cls) -> ModeloInfoResponse:
        """
        Obtiene información sobre los modelos disponibles
        
        Returns:
            Información de modelos disponibles y sus métricas
        """
        logger.info("Obteniendo información de modelos disponibles")
        
        # Ruta corregida: desde services -> api -> app -> ml -> models
        models_dir = Path(__file__).parent.parent.parent / "ml" / "models"
        
        modelos_disponibles = []
        mejor_r2 = 0
        modelo_recomendado = None
        
        # Tipos de modelos a verificar
        model_types = [
            ('linear', 'Regresión Lineal'),
            ('random_forest', 'Random Forest Regressor'),
            ('gradient_boosting', 'Gradient Boosting Regressor')
        ]
        
        for model_type, nombre in model_types:
            model_file = models_dir / f"sis_predictor_{model_type}.pkl"
            
            if model_file.exists():
                try:
                    predictor = cls._get_modelo(model_type)
                    metricas_test = predictor.metrics.get('test', {})
                    
                    modelo_info = {
                        'tipo': model_type,
                        'nombre': nombre,
                        'metricas': {
                            'r2': round(metricas_test.get('r2', 0), 4),
                            'rmse': round(metricas_test.get('rmse', 0), 4),
                            'mae': round(metricas_test.get('mae', 0), 4)
                        },
                        'estado': 'disponible',
                        'archivo': str(model_file.name)
                    }
                    
                    modelos_disponibles.append(modelo_info)
                    
                    # Determinar mejor modelo
                    r2 = metricas_test.get('r2', 0)
                    if r2 > mejor_r2:
                        mejor_r2 = r2
                        modelo_recomendado = model_type
                        
                except Exception as e:
                    logger.warning(f"No se pudo cargar modelo {model_type}: {str(e)}")
                    modelos_disponibles.append({
                        'tipo': model_type,
                        'nombre': nombre,
                        'estado': 'error',
                        'mensaje': str(e)
                    })
            else:
                modelos_disponibles.append({
                    'tipo': model_type,
                    'nombre': nombre,
                    'estado': 'no_encontrado',
                    'mensaje': 'Modelo no entrenado'
                })
        
        # Modelo recomendado por defecto si no hay ninguno
        if modelo_recomendado is None:
            modelo_recomendado = 'random_forest'
        
        return ModeloInfoResponse(
            modelos_disponibles=modelos_disponibles,
            modelo_recomendado=modelo_recomendado
        )
    
    @classmethod
    def limpiar_cache(cls):
        """Limpia el cache de modelos cargados"""
        logger.info("Limpiando cache de modelos")
        cls._modelos_cache.clear()
