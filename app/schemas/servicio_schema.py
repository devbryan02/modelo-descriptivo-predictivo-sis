from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class ServicioBase(BaseModel):
    """
    Schema base para Servicio con campos compartidos
    """
    nombre: str = Field(..., min_length=3, max_length=200, description="Nombre del servicio médico")
    categoria: Optional[str] = Field(None, max_length=100, description="Categoría del servicio")

    @validator('nombre')
    def validate_nombre(cls, v):
        """Validar y limpiar el nombre del servicio"""
        nombre_limpio = v.strip()
        if len(nombre_limpio) < 3:
            raise ValueError('Nombre debe tener al menos 3 caracteres')
        return nombre_limpio

    @validator('categoria')
    def validate_categoria(cls, v):
        """Validar y limpiar la categoría si se proporciona"""
        if v is not None:
            categoria_limpia = v.strip()
            return categoria_limpia if categoria_limpia else None
        return v


class ServicioCreate(ServicioBase):
    """
    Schema para crear un nuevo servicio médico
    """
    pass


class ServicioResponse(ServicioBase):
    """
    Schema para respuestas de la API con servicio
    """
    id: int = Field(..., description="ID único del servicio")
    created_at: datetime = Field(..., description="Fecha de creación del registro")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ServicioUpdate(BaseModel):
    """
    Schema para actualizar un servicio médico
    """
    nombre: Optional[str] = Field(None, min_length=3, max_length=200)
    categoria: Optional[str] = Field(None, max_length=100)

    @validator('nombre')
    def validate_nombre(cls, v):
        if v is not None:
            nombre_limpio = v.strip()
            if len(nombre_limpio) < 3:
                raise ValueError('Nombre debe tener al menos 3 caracteres')
            return nombre_limpio
        return v

    @validator('categoria')
    def validate_categoria(cls, v):
        if v is not None:
            categoria_limpia = v.strip()
            return categoria_limpia if categoria_limpia else None
        return v