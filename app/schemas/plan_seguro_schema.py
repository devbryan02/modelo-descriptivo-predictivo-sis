from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class PlanSeguroBase(BaseModel):
    """
    Schema base para PlanSeguro con campos compartidos
    """
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del plan de seguro")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción del plan")

    @validator('nombre')
    def validate_nombre(cls, v):
        """Validar que el nombre sea uno de los planes válidos del SIS"""
        planes_validos = ["Gratuito", "Independiente", "NRUS", "Microempresa", "Para Todos"]
        if v not in planes_validos:
            raise ValueError(f'Nombre debe ser uno de: {", ".join(planes_validos)}')
        return v


class PlanSeguroCreate(PlanSeguroBase):
    """
    Schema para crear un nuevo plan de seguro
    Hereda todos los campos de PlanSeguroBase
    """
    pass


class PlanSeguroResponse(PlanSeguroBase):
    """
    Schema para respuestas de la API con plan de seguro
    Incluye campos adicionales como id y created_at
    """
    id: int = Field(..., description="ID único del plan de seguro")
    created_at: datetime = Field(..., description="Fecha de creación del registro")

    class Config:
        from_attributes = True  # Permite crear desde objetos ORM
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class PlanSeguroUpdate(BaseModel):
    """
    Schema para actualizar un plan de seguro
    Todos los campos son opcionales
    """
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)

    @validator('nombre')
    def validate_nombre(cls, v):
        if v is not None:
            planes_validos = ["Gratuito", "Independiente", "NRUS", "Microempresa", "Para Todos"]
            if v not in planes_validos:
                raise ValueError(f'Nombre debe ser uno de: {", ".join(planes_validos)}')
        return v