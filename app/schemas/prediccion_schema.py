"""
Schemas Pydantic para endpoints de predicción del SIS
Basado en REQUERIMENTS.MD - Endpoints de Predicción
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from enum import Enum


class ModeloTipo(str, Enum):
    """Tipos de modelos disponibles"""
    LINEAR = "linear"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"


class PrediccionRequest(BaseModel):
    """
    Request para predicción de demanda de atenciones
    
    Según REQUERIMENTS.MD:
    Body: {año, mes, región, grupo_edad, sexo, plan_seguro}
    """
    año: int = Field(..., ge=2020, le=2030, description="Año de la predicción (2020-2030)")
    mes: int = Field(..., ge=1, le=12, description="Mes de la predicción (1-12)")
    region: str = Field(..., min_length=3, max_length=100, description="Región/Departamento")
    grupo_edad: str = Field(..., description="Grupo de edad (ej: '00-04', '18-29', '60+')")
    sexo: str = Field(..., description="Sexo del paciente")
    nivel_ipress: str = Field(default="I", description="Nivel del establecimiento de salud (I, II, III)")
    servicio_categoria: str = Field(default="GENERAL", description="Categoría del servicio médico")
    plan_seguro: str = Field(..., description="Tipo de plan de seguro del SIS")
    modelo: Optional[ModeloTipo] = Field(
        default=ModeloTipo.RANDOM_FOREST,
        description="Tipo de modelo a usar para la predicción"
    )
    
    @field_validator('sexo')
    @classmethod
    def validar_sexo(cls, v: str) -> str:
        sexo_upper = v.upper().strip()
        if sexo_upper not in ['MASCULINO', 'FEMENINO', 'M', 'F']:
            raise ValueError("Sexo debe ser 'MASCULINO', 'FEMENINO', 'M' o 'F'")
        # Normalizar
        if sexo_upper == 'M':
            return 'MASCULINO'
        if sexo_upper == 'F':
            return 'FEMENINO'
        return sexo_upper
    
    @field_validator('nivel_ipress')
    @classmethod
    def validar_nivel_ipress(cls, v: str) -> str:
        nivel_upper = v.upper().strip()
        if nivel_upper not in ['I', 'II', 'III']:
            raise ValueError("Nivel IPRESS debe ser 'I', 'II' o 'III'")
        return nivel_upper
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class PrediccionResponse(BaseModel):
    """
    Response de predicción de demanda
    
    Retorna: predicción de número de atenciones
    """
    prediccion: float = Field(..., description="Cantidad de atenciones predichas")
    prediccion_redondeada: int = Field(..., description="Predicción redondeada al entero más cercano")
    modelo_usado: str = Field(..., description="Tipo de modelo utilizado")
    parametros: Dict = Field(..., description="Parámetros usados en la predicción")
    metricas_modelo: Optional[Dict] = Field(
        default=None,
        description="Métricas del modelo (R², RMSE, MAE)"
    )
    intervalo_confianza: Optional[Dict] = Field(
        default=None,
        description="Intervalo de confianza de la predicción (si disponible)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediccion": 245.67,
                "prediccion_redondeada": 246,
                "modelo_usado": "random_forest",
                "parametros": {
                    "año": 2025,
                    "mes": 6,
                    "region": "LIMA",
                    "grupo_edad": "18-29",
                    "sexo": "FEMENINO"
                },
                "metricas_modelo": {
                    "r2": 0.87,
                    "rmse": 12.45,
                    "mae": 8.32
                },
                "intervalo_confianza": {
                    "inferior": 220.5,
                    "superior": 270.8,
                    "nivel": "95%"
                }
            }
        }


class PrediccionBatchItem(BaseModel):
    """Item individual para predicción batch"""
    año: int = Field(..., ge=2020, le=2030)
    mes: int = Field(..., ge=1, le=12)
    region: str
    grupo_edad: str
    sexo: str
    nivel_ipress: str = "I"
    servicio_categoria: str = "GENERAL"
    plan_seguro: str


class BatchPrediccionRequest(BaseModel):
    """
    Request para predicción masiva (batch)
    
    Permite predecir múltiples escenarios en una sola llamada
    """
    predicciones: List[PrediccionBatchItem] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Lista de escenarios a predecir (máximo 100)"
    )
    modelo: Optional[ModeloTipo] = Field(
        default=ModeloTipo.RANDOM_FOREST,
        description="Tipo de modelo a usar"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class BatchPrediccionResponse(BaseModel):
    """Response para predicción batch"""
    total_predicciones: int = Field(..., description="Número total de predicciones realizadas")
    modelo_usado: str = Field(..., description="Modelo utilizado")
    resultados: List[Dict] = Field(..., description="Lista de resultados individuales")
    resumen: Dict = Field(..., description="Resumen estadístico de las predicciones")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_predicciones": 2,
                "modelo_usado": "random_forest",
                "resultados": [
                    {
                        "prediccion": 245.67,
                        "parametros": {
                            "año": 2025,
                            "mes": 6,
                            "region": "LIMA"
                        }
                    },
                    {
                        "prediccion": 156.32,
                        "parametros": {
                            "año": 2025,
                            "mes": 7,
                            "region": "CUSCO"
                        }
                    }
                ],
                "resumen": {
                    "prediccion_promedio": 200.99,
                    "prediccion_minima": 156.32,
                    "prediccion_maxima": 245.67,
                    "desviacion_estandar": 63.18
                }
            }
        }


class ModeloInfoResponse(BaseModel):
    """Información sobre los modelos disponibles"""
    modelos_disponibles: List[Dict] = Field(..., description="Lista de modelos disponibles")
    modelo_recomendado: str = Field(..., description="Modelo recomendado para producción")
    
    class Config:
        json_schema_extra = {
            "example": {
                "modelos_disponibles": [
                    {
                        "tipo": "random_forest",
                        "nombre": "Random Forest Regressor",
                        "metricas": {
                            "r2": 0.87,
                            "rmse": 12.45,
                            "mae": 8.32
                        },
                        "estado": "disponible"
                    },
                    {
                        "tipo": "gradient_boosting",
                        "nombre": "Gradient Boosting Regressor",
                        "metricas": {
                            "r2": 0.85,
                            "rmse": 13.12,
                            "mae": 9.01
                        },
                        "estado": "disponible"
                    }
                ],
                "modelo_recomendado": "random_forest"
            }
        }
