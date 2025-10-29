from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, List, Any


class AtencionBase(BaseModel):
    """
    Schema base para Atencion con campos compartidos
    Basado en requirements.md sección "Modelo de Datos"
    """
    año: int = Field(..., description="Año de la atención médica")
    mes: int = Field(..., description="Mes de la atención (1-12)")
    region: str = Field(..., min_length=3, max_length=100, description="Región donde se brindó la atención")
    provincia: Optional[str] = Field(None, max_length=100, description="Provincia de la atención")
    distrito: Optional[str] = Field(None, max_length=100, description="Distrito de la atención")
    sexo: str = Field(..., description="Sexo del paciente")
    grupo_edad: str = Field(..., description="Grupo etario del paciente")
    cantidad_atenciones: int = Field(..., ge=0, description="Número total de atenciones registradas")
    plan_seguro_id: int = Field(..., description="ID del plan de seguro")
    ipress_id: int = Field(..., description="ID del establecimiento IPRESS")
    servicio_id: int = Field(..., description="ID del servicio médico")

    @validator('año')
    def validate_año(cls, v):
        """Validar que el año esté en el rango permitido (2020-2025)"""
        if not (2020 <= v <= 2025):
            raise ValueError('Año debe estar entre 2020 y 2025')
        return v

    @validator('mes')
    def validate_mes(cls, v):
        """Validar que el mes esté en el rango 1-12"""
        if not (1 <= v <= 12):
            raise ValueError('Mes debe estar entre 1 y 12')
        return v

    @validator('sexo')
    def validate_sexo(cls, v):
        """Validar que el sexo sea Masculino o Femenino"""
        sexos_validos = ["Masculino", "Femenino"]
        if v not in sexos_validos:
            raise ValueError(f'Sexo debe ser uno de: {", ".join(sexos_validos)}')
        return v

    @validator('grupo_edad')
    def validate_grupo_edad(cls, v):
        """Validar que el grupo de edad sea uno de los rangos válidos"""
        grupos_validos = ["00-04", "05-11", "12-17", "18-29", "30-59", "60+"]
        if v not in grupos_validos:
            raise ValueError(f'Grupo de edad debe ser uno de: {", ".join(grupos_validos)}')
        return v


class AtencionCreate(AtencionBase):
    """
    Schema para crear una nueva atención médica
    """
    pass


class AtencionResponse(AtencionBase):
    """
    Schema para respuestas de la API con atención médica
    Incluye relaciones anidadas opcionales
    """
    id: int = Field(..., description="ID único de la atención")
    created_at: datetime = Field(..., description="Fecha de creación del registro")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AtencionFilter(BaseModel):
    """
    Schema para filtros en queries de atenciones
    Todos los campos son opcionales para permitir filtrado flexible
    """
    año: Optional[int] = Field(None, ge=2020, le=2025)
    mes: Optional[int] = Field(None, ge=1, le=12)
    region: Optional[str] = Field(None, max_length=100)
    provincia: Optional[str] = Field(None, max_length=100)
    distrito: Optional[str] = Field(None, max_length=100)
    sexo: Optional[str] = Field(None)
    grupo_edad: Optional[str] = Field(None)
    plan_seguro_id: Optional[int] = Field(None)
    ipress_id: Optional[int] = Field(None)
    servicio_id: Optional[int] = Field(None)

    @validator('sexo')
    def validate_sexo(cls, v):
        if v is not None:
            sexos_validos = ["Masculino", "Femenino"]
            if v not in sexos_validos:
                raise ValueError(f'Sexo debe ser uno de: {", ".join(sexos_validos)}')
        return v

    @validator('grupo_edad')
    def validate_grupo_edad(cls, v):
        if v is not None:
            grupos_validos = ["00-04", "05-11", "12-17", "18-29", "30-59", "60+"]
            if v not in grupos_validos:
                raise ValueError(f'Grupo de edad debe ser uno de: {", ".join(grupos_validos)}')
        return v


class EstadisticasResponse(BaseModel):
    """
    Schema para respuestas de estadísticas agregadas
    Basado en requirements.md sección "Funcionalidades Requeridas"
    """
    total_atenciones: int = Field(..., description="Total de atenciones en el periodo")
    promedio_mensual: float = Field(..., description="Promedio de atenciones por mes")
    distribucion_por_sexo: Dict[str, int] = Field(..., description="Distribución por sexo")
    distribucion_por_edad: Dict[str, int] = Field(..., description="Distribución por grupo etario")
    regiones_top_5: List[Dict[str, Any]] = Field(..., description="Top 5 regiones con más atenciones")


class AtencionUpdate(BaseModel):
    """
    Schema para actualizar una atención médica
    """
    año: Optional[int] = Field(None, ge=2020, le=2025)
    mes: Optional[int] = Field(None, ge=1, le=12)
    region: Optional[str] = Field(None, min_length=3, max_length=100)
    provincia: Optional[str] = Field(None, max_length=100)
    distrito: Optional[str] = Field(None, max_length=100)
    sexo: Optional[str] = Field(None)
    grupo_edad: Optional[str] = Field(None)
    cantidad_atenciones: Optional[int] = Field(None, ge=0)
    plan_seguro_id: Optional[int] = Field(None)
    ipress_id: Optional[int] = Field(None)
    servicio_id: Optional[int] = Field(None)

    @validator('sexo')
    def validate_sexo(cls, v):
        if v is not None:
            sexos_validos = ["Masculino", "Femenino"]
            if v not in sexos_validos:
                raise ValueError(f'Sexo debe ser uno de: {", ".join(sexos_validos)}')
        return v

    @validator('grupo_edad')
    def validate_grupo_edad(cls, v):
        if v is not None:
            grupos_validos = ["00-04", "05-11", "12-17", "18-29", "30-59", "60+"]
            if v not in grupos_validos:
                raise ValueError(f'Grupo de edad debe ser uno de: {", ".join(grupos_validos)}')
        return v
