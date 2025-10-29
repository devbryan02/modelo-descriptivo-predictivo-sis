from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
import re


class IPRESSBase(BaseModel):
    """
    Schema base para IPRESS con campos compartidos
    """
    codigo: str = Field(..., min_length=3, max_length=50, description="Código único del establecimiento")
    nombre: str = Field(..., min_length=3, max_length=200, description="Nombre del establecimiento")
    nivel: str = Field(..., description="Nivel del establecimiento de salud")
    region: str = Field(..., min_length=3, max_length=100, description="Región donde se ubica")
    provincia: Optional[str] = Field(None, max_length=100, description="Provincia donde se ubica")
    distrito: Optional[str] = Field(None, max_length=100, description="Distrito donde se ubica")

    @validator('codigo')
    def validate_codigo(cls, v):
        """Validar que el código sea alfanumérico"""
        if not re.match(r'^[A-Za-z0-9]+$', v):
            raise ValueError('Código debe ser alfanumérico')
        return v.upper()

    @validator('nivel')
    def validate_nivel(cls, v):
        """Validar que el nivel sea I, II o III"""
        niveles_validos = ["I", "II", "III"]
        if v not in niveles_validos:
            raise ValueError(f'Nivel debe ser uno de: {", ".join(niveles_validos)}')
        return v

    @validator('nombre')
    def validate_nombre(cls, v):
        """Validar longitud mínima del nombre"""
        if len(v.strip()) < 3:
            raise ValueError('Nombre debe tener al menos 3 caracteres')
        return v.strip()


class IPRESSCreate(IPRESSBase):
    """
    Schema para crear un nuevo establecimiento IPRESS
    """
    pass


class IPRESSResponse(IPRESSBase):
    """
    Schema para respuestas de la API con IPRESS
    """
    id: int = Field(..., description="ID único del establecimiento")
    created_at: datetime = Field(..., description="Fecha de creación del registro")

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class IPRESSUpdate(BaseModel):
    """
    Schema para actualizar un establecimiento IPRESS
    """
    codigo: Optional[str] = Field(None, min_length=3, max_length=50)
    nombre: Optional[str] = Field(None, min_length=3, max_length=200)
    nivel: Optional[str] = Field(None)
    region: Optional[str] = Field(None, min_length=3, max_length=100)
    provincia: Optional[str] = Field(None, max_length=100)
    distrito: Optional[str] = Field(None, max_length=100)

    @validator('codigo')
    def validate_codigo(cls, v):
        if v is not None and not re.match(r'^[A-Za-z0-9]+$', v):
            raise ValueError('Código debe ser alfanumérico')
        return v.upper() if v else v

    @validator('nivel')
    def validate_nivel(cls, v):
        if v is not None:
            niveles_validos = ["I", "II", "III"]
            if v not in niveles_validos:
                raise ValueError(f'Nivel debe ser uno de: {", ".join(niveles_validos)}')
        return v