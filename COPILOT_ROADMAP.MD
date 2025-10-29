🗺️ COPILOT ROADMAP - Plan de Desarrollo del Proyecto SIS

Instrucciones para GitHub Copilot: Este documento indica el progreso actual del proyecto y los próximos pasos a implementar. Usa este contexto para generar código coherente con la fase actual de desarrollo.


📍 ESTADO ACTUAL DEL PROYECTO
Última actualización: [FECHA - Actualiza manualmente]
Fase actual: FASE 0 - SETUP INICIAL ⏳
Completado:

✅ Estructura de carpetas creada
✅ requirements.md documentado
⏳ Configuración inicial pendiente


🎯 FASES DE DESARROLLO
leyenda de Estado

⏳ Pendiente
🔄 En progreso
✅ Completado
⚠️ Requiere revisión
❌ Bloqueado


🚀 FASE 0: SETUP INICIAL (15 min)
Objetivo: Preparar el entorno de desarrollo y dependencias básicas
📋 Checklist
0.1 Entorno Virtual ⏳
bash# Comandos a ejecutar:
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
Copilot: No requiere generación de código

0.2 Archivo requirements.txt ⏳
Archivo: requirements.txt
Copilot, genera este archivo con:
# Dependencias para proyecto de análisis y predicción del SIS
# Consulta requirements.md para contexto completo

# Framework web
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6

# Base de datos
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Data Science y ML
pandas==2.1.4
numpy==1.26.3
scikit-learn==1.4.0
joblib==1.3.2
matplotlib==3.8.2
seaborn==0.13.1

# Utilidades
python-dotenv==1.0.0
tqdm==4.66.1

# Testing
pytest==7.4.4
pytest-cov==4.1.0
httpx==0.26.0

# Validación y seguridad
email-validator==2.1.0
Validación:
bashpip install -r requirements.txt

0.3 Archivo .env ⏳
Archivo: .env
Copilot, genera:
bash# Variables de entorno para desarrollo local
# Basado en requirements.md sección "Deploy y Entorno"

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/sis_db
SECRET_KEY=dev-secret-key-change-in-production-12345678
DEBUG=True
API_VERSION=v1
ENVIRONMENT=development

# Configuración de CORS (para Next.js futuro)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
Nota: Agregar .env a .gitignore

0.4 Archivo .gitignore ⏳
Archivo: .gitignore
Copilot, genera archivo .gitignore para proyecto Python/FastAPI:
# Incluir: venv, __pycache__, .env, .pytest_cache, *.pyc, 
# alembic/versions/*.py (excepto inicial), .DS_Store, *.log
# Consulta convenciones de Python

0.5 Inicializar Git ⏳
bashgit init
git add .
git commit -m "Initial commit: project structure and requirements"
Copilot: No requiere generación de código

🏗️ FASE 1: CIMIENTOS (Core + Database) (30 min)
Objetivo: Configurar la base de la aplicación y conexión a BD
📋 Checklist
1.1 Configuración Central ⏳
Archivo: app/core/settings.py
Instrucciones para Copilot:
python# Configuración de variables de entorno usando Pydantic BaseSettings
# Basado en requirements.md sección "Deploy y Entorno"
# Debe incluir:
# - DATABASE_URL (str)
# - SECRET_KEY (str)
# - DEBUG (bool)
# - API_VERSION (str)
# - ENVIRONMENT (str)
# - CORS_ORIGINS (list[str])
#
# Usar pydantic_settings.BaseSettings
# Cargar desde archivo .env
# Incluir validadores para URLs y claves secretas

from pydantic_settings import BaseSettings
Validación:

Importar sin errores
Instanciar settings = Settings()
Verificar settings.DATABASE_URL


1.2 Conexión a Base de Datos ⏳
Archivo: app/core/database.py
Instrucciones para Copilot:
python# Configuración de SQLAlchemy para PostgreSQL
# Basado en requirements.md sección "Arquitectura de la Aplicación"
# 
# Debe incluir:
# - create_engine usando settings.DATABASE_URL
# - SessionLocal con autocommit=False, autoflush=False
# - Base = declarative_base()
# - Función get_db() como dependency para FastAPI (yield pattern)
#
# Configuraciones adicionales:
# - pool_pre_ping=True para manejar desconexiones
# - echo=settings.DEBUG para log de queries en desarrollo

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings
Validación:
python# Crear script de prueba test_db.py
from app.core.database import engine
engine.connect()  # Debe conectar sin errores

1.3 Archivo init.py ⏳
Archivos:

app/__init__.py
app/core/__init__.py
app/api/__init__.py
app/models/__init__.py
app/schemas/__init__.py

Copilot, genera archivos vacíos o con:
python# Paquete [nombre_del_modulo]

1.4 Configuración de Alembic ⏳
Comando:
bashalembic init alembic
Archivo: alembic/env.py
Instrucciones para Copilot:
python# Modificar alembic/env.py para usar nuestra configuración
# 
# Cambios necesarios:
# 1. Importar Base y settings:
#    from app.core.database import Base
#    from app.core.settings import settings
#
# 2. Cambiar sqlalchemy.url en alembic.ini a usar settings:
#    config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
#
# 3. Configurar target_metadata = Base.metadata

# Agregar estos imports al inicio de env.py
from app.core.database import Base
from app.core.settings import settings
Validación:
bashalembic revision --autogenerate -m "Initial migration"
# Debe crear archivo en alembic/versions/ sin errores

🗄️ FASE 2: MODELOS DE DATOS (45 min)
Objetivo: Crear modelos ORM y schemas de validación
📋 Checklist
2.1 Modelo Plan de Seguro ⏳
Archivo: app/models/plan_seguro.py
Instrucciones para Copilot:
python# Modelo SQLAlchemy para tabla planes_seguro
# Basado en requirements.md sección "Modelo de Datos"
#
# Campos:
# - id: Integer, PK, autoincrement
# - nombre: String(100), unique, not null (Gratuito, Independiente, NRUS, etc.)
# - descripcion: Text, nullable
# - created_at: DateTime, default=func.now()
#
# Relación: 
# - atenciones: relación one-to-many con modelo Atencion

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

2.2 Modelo IPRESS ⏳
Archivo: app/models/ipress.py
Instrucciones para Copilot:
python# Modelo SQLAlchemy para tabla ipress (establecimientos de salud)
# Basado en requirements.md sección "Modelo de Datos"
#
# Campos:
# - id: Integer, PK
# - codigo: String(50), unique, not null
# - nombre: String(200), not null
# - nivel: String(10), not null (I, II, III)
# - region: String(100), not null
# - provincia: String(100)
# - distrito: String(100)
# - created_at: DateTime
#
# Relación:
# - atenciones: one-to-many con Atencion

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

2.3 Modelo Servicio ⏳
Archivo: app/models/servicio.py
Instrucciones para Copilot:
python# Modelo SQLAlchemy para tabla servicios (tipos de atención médica)
# Basado en requirements.md sección "Modelo de Datos"
#
# Campos:
# - id: Integer, PK
# - nombre: String(200), unique, not null
# - categoria: String(100), nullable
# - created_at: DateTime
#
# Relación:
# - atenciones: one-to-many con Atencion

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

2.4 Modelo Atención (Principal) ⏳
Archivo: app/models/atencion.py
Instrucciones para Copilot:
python# Modelo SQLAlchemy para tabla atenciones (registro principal)
# Basado en requirements.md sección "Modelo de Datos"
#
# Campos:
# - id: Integer, PK, autoincrement
# - año: Integer, not null
# - mes: Integer, not null (1-12)
# - region: String(100), not null
# - provincia: String(100)
# - distrito: String(100)
# - sexo: String(20), not null (Masculino/Femenino)
# - grupo_edad: String(20), not null (00-04, 05-11, 12-17, 18-29, 30-59, 60+)
# - cantidad_atenciones: Integer, not null
# - plan_seguro_id: ForeignKey(planes_seguro.id)
# - ipress_id: ForeignKey(ipress.id)
# - servicio_id: ForeignKey(servicios.id)
# - created_at: DateTime, default=func.now()
#
# Relaciones (back_populates):
# - plan_seguro: many-to-one con PlanSeguro
# - ipress: many-to-one con IPRESS
# - servicio: many-to-one con Servicio
#
# Índices (para optimizar queries):
# - Index('idx_atencion_año_mes', 'año', 'mes')
# - Index('idx_atencion_region', 'region')
# - Index('idx_atencion_grupo_edad', 'grupo_edad')

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

2.5 Actualizar init de models ⏳
Archivo: app/models/__init__.py
Instrucciones para Copilot:
python# Importar todos los modelos para que Alembic los detecte
# Esto es necesario para autogenerar migraciones

from app.models.plan_seguro import PlanSeguro
from app.models.ipress import IPRESS
from app.models.servicio import Servicio
from app.models.atencion import Atencion

__all__ = ['PlanSeguro', 'IPRESS', 'Servicio', 'Atencion']

2.6 Crear Migración Inicial ⏳
Comando:
bash# Asegúrate de importar modelos en alembic/env.py antes:
# from app.models import *

alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head
Validación:

Verificar tablas en PostgreSQL: \dt en psql
Deben existir: planes_seguro, ipress, servicios, atenciones


2.7 Schemas Pydantic - Plan Seguro ⏳
Archivo: app/schemas/plan_seguro_schema.py
Instrucciones para Copilot:
python# Schemas Pydantic para PlanSeguro
# Basado en requirements.md sección "Funcionalidades Requeridas"
#
# Crear 3 clases:
# 1. PlanSeguroBase: campos compartidos (nombre, descripcion)
# 2. PlanSeguroCreate: hereda de Base, para POST requests
# 3. PlanSeguroResponse: hereda de Base, agrega id, created_at
#    - Config: from_attributes = True
#
# Validaciones:
# - nombre debe estar en: ["Gratuito", "Independiente", "NRUS", "Microempresa", "Para Todos"]
# - usar Field() para documentar cada campo

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

2.8 Schemas Pydantic - IPRESS ⏳
Archivo: app/schemas/ipress_schema.py
Instrucciones para Copilot:
python# Schemas Pydantic para IPRESS
# Seguir mismo patrón que plan_seguro_schema.py
#
# Clases:
# - IPRESSBase (codigo, nombre, nivel, region, provincia, distrito)
# - IPRESSCreate
# - IPRESSResponse (+ id, created_at)
#
# Validaciones:
# - nivel debe ser: "I", "II" o "III"
# - codigo debe ser alfanumérico
# - nombre min_length=3

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

2.9 Schemas Pydantic - Servicio ⏳
Archivo: app/schemas/servicio_schema.py
Instrucciones para Copilot:
python# Schemas Pydantic para Servicio
# Patrón: Base, Create, Response
#
# Campos en Base:
# - nombre: str
# - categoria: Optional[str]

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

2.10 Schemas Pydantic - Atención ⏳
Archivo: app/schemas/atencion_schema.py
Instrucciones para Copilot:
python# Schemas Pydantic para Atencion (modelo principal)
# Basado en requirements.md sección "Modelo de Datos"
#
# Clases:
# 1. AtencionBase:
#    - año: int (2020-2025)
#    - mes: int (1-12)
#    - region, provincia, distrito: str
#    - sexo: str ("Masculino" o "Femenino")
#    - grupo_edad: str (validar rangos del requirements.md)
#    - cantidad_atenciones: int (>= 0)
#    - plan_seguro_id, ipress_id, servicio_id: int
#
# 2. AtencionCreate: hereda de Base
#
# 3. AtencionResponse: hereda de Base, agrega:
#    - id: int
#    - created_at: datetime
#    - Relaciones anidadas (opcional): plan_seguro, ipress, servicio
#
# 4. AtencionFilter: para queries (todos los campos opcionales)
#
# 5. EstadisticasResponse:
#    - total_atenciones: int
#    - promedio_mensual: float
#    - distribucion_por_sexo: dict
#    - distribucion_por_edad: dict
#    - regiones_top_5: list
#
# Validadores:
# - @validator('año'): rango 2020-2025
# - @validator('mes'): rango 1-12
# - @validator('sexo'): ["Masculino", "Femenino"]
# - @validator('grupo_edad'): ["00-04", "05-11", "12-17", "18-29", "30-59", "60+"]

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, List

🔧 FASE 3: UTILIDADES Y ETL (60 min)
Objetivo: Crear herramientas para cargar y limpiar datos del CSV
📋 Checklist
3.1 Utilidad de Limpieza de Datos ⏳
Archivo: app/utils/data_cleaner.py
Instrucciones para Copilot:
python# Funciones para limpieza y transformación de datos del SIS
# Basado en requirements.md sección "Fase 3: Preparación de los Datos"
#
# Funciones a implementar:
#
# 1. limpiar_duplicados(df: pd.DataFrame) -> pd.DataFrame
#    - Elimina filas duplicadas
#    - Log de cantidad eliminada
#
# 2. imputar_valores_nulos(df: pd.DataFrame) -> pd.DataFrame
#    - Categóricas: imputar con moda
#    - Numéricas: imputar con mediana
#
# 3. estandarizar_texto(df: pd.DataFrame, columnas: list) -> pd.DataFrame
#    - Convertir a mayúsculas
#    - Eliminar espacios extras
#    - Remover acentos (unidecode)
#
# 4. validar_rangos(df: pd.DataFrame) -> pd.DataFrame
#    - Filtrar años fuera de 2020-2025
#    - Filtrar meses fuera de 1-12
#    - Filtrar atenciones negativas
#
# 5. normalizar_categorias(df: pd.DataFrame) -> pd.DataFrame
#    - Mapear variaciones de género a "Masculino"/"Femenino"
#    - Unificar nombres de regiones
#    - Estandarizar grupos etarios
#
# Usar logging para reportar cada paso

import pandas as pd
import logging
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

3.2 Cargador de CSV a BD ⏳
Archivo: app/utils/load_csv_to_db.py
Instrucciones para Copilot:
python# Script ETL para cargar dataset.csv a PostgreSQL
# Basado en requirements.md sección "Funcionalidades Requeridas"
#
# Flujo del proceso:
# 1. Leer app/static/dataset.csv con pandas
# 2. Aplicar funciones de data_cleaner
# 3. Cargar/crear registros de planes_seguro, ipress, servicios
# 4. Insertar atenciones con referencias (FKs)
# 5. Commit en batches de 1000 registros (performance)
# 6. Mostrar barra de progreso con tqdm
# 7. Log de estadísticas finales
#
# Función principal:
# def load_csv_to_database(csv_path: str, batch_size: int = 1000) -> None
#
# Manejo de errores:
# - Rollback si falla un batch
# - Log detallado de errores
# - Continuar con siguiente batch si es posible

import pandas as pd
from tqdm import tqdm
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import PlanSeguro, IPRESS, Servicio, Atencion
from app.utils.data_cleaner import (
    limpiar_duplicados,
    imputar_valores_nulos,
    estandarizar_texto,
    validar_rangos,
    normalizar_categorias
)
import logging

logger = logging.getLogger(__name__)
Validación:
bashpython -m app.utils.load_csv_to_db
# Debe cargar datos sin errores y mostrar progreso

3.3 Seeder de Datos Maestros ⏳
Archivo: app/utils/seed_data.py
Instrucciones para Copilot:
python# Script para poblar datos maestros (catálogos)
# Ejecutar antes de cargar atenciones
#
# Datos a insertar:
# 1. Planes de seguro (5 planes del requirements.md)
# 2. Niveles de IPRESS (al menos 10 ejemplos por región principal)
# 3. Servicios médicos comunes (20-30 servicios típicos)
#
# Función:
# def seed_master_data() -> None
#
# Usar get_or_create pattern para evitar duplicados

from app.core.database import SessionLocal
from app.models import PlanSeguro, IPRESS, Servicio
import logging

logger = logging.getLogger(__name__)

🌐 FASE 4: API ENDPOINTS (90 min)
Objetivo: Crear endpoints REST para análisis descriptivo
📋 Checklist
4.1 Router Principal ⏳
Archivo: app/api/routes.py
Instrucciones para Copilot:
python# Router principal que agrupa todos los sub-routers
# Basado en requirements.md sección "Funcionalidades Requeridas"

from fastapi import APIRouter
from app.api.endpoints import atencion, prediccion, health

api_router = APIRouter()

# Incluir routers con prefijos
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(atencion.router, prefix="/atenciones", tags=["atenciones"])
api_router.include_router(prediccion.router, prefix="/prediccion", tags=["prediccion"])

4.2 Endpoint Health Check ⏳
Archivo: app/api/endpoints/health.py
Instrucciones para Copilot:
python# Endpoint de healthcheck
# GET /api/v1/health
#
# Respuesta:
# {
#   "status": "ok",
#   "database": "connected",
#   "timestamp": "2025-01-15T10:30:00"
# }
#
# Verificar conexión a BD intentando una query simple

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from datetime import datetime

router = APIRouter()

4.3 Servicios de Negocio - Atenciones ⏳
Archivo: app/services/atencion_service.py
Instrucciones para Copilot:
python# Lógica de negocio para análisis de atenciones
# Separar queries complejas de los endpoints
#
# Funciones a implementar:
#
# 1. get_estadisticas(db, filters: AtencionFilter) -> EstadisticasResponse
#    - Total de atenciones
#    - Promedio mensual
#    - Distribución por sexo
#    - Distribución por edad
#    - Top 5 regiones
#
# 2. get_atenciones_por_region(db, año, mes) -> List[Dict]
#    - Agrupar por región
#    - Incluir totales y porcentajes
#
# 3. get_atenciones_por_servicio(db, filters) -> List[Dict]
#    - Agrupar por servicio
#    - Ordenar por cantidad descendente
#
# 4. get_segmentacion_demografica(db, filters) -> Dict
#    - Matriz grupo_edad x sexo
#    - Totales por cada combinación
#
# Optimizar queries con:
# - func.sum(), func.count()
# - group_by
# - Joins eficientes

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Optional
from app.models import Atencion, PlanSeguro, IPRESS, Servicio
from app.schemas.atencion_schema import AtencionFilter, EstadisticasResponse

4.4 Endpoints de Análisis Descriptivo ⏳
Archivo: app/api/endpoints/atencion.py
Instrucciones para Copilot:
python# Endpoints para análisis descriptivo de atenciones
# Basado en requirements.md sección "Funcionalidades Requeridas - Endpoints de Análisis Descriptivo"
#
# Endpoints:
#
# 1. GET /estadisticas
#    Query params: año?, mes?, region?, plan_seguro_id?
#    Retorna: EstadisticasResponse
#    Usa: atencion_service.get_estadisticas()
#
# 2. GET /por-region
#    Query params: año, mes?
#    Retorna: List[Dict] con region, total, porcentaje
#    Usa: atencion_service.get_atenciones_por_region()
#
# 3. GET /por-servicio
#    Query params: año?, mes?, region?
#    Retorna: List[Dict] con servicio, total, porcentaje
#    Usa: atencion_service.get_atenciones_por_servicio()
#
# 4. GET /por-edad-sexo
#    Query params: año?, region?
#    Retorna: Dict con matriz edad x sexo
#    Usa: atencion_service.get_segmentacion_demografica()
#
# 5. GET /{id}
#    Path param: id
#    Retorna: AtencionResponse
#
# 6. POST / (opcional, para testing)
#    Body: AtencionCreate
#    Retorna: AtencionResponse
#
# Manejo de errores:
# - HTTPException 404 si no hay datos
# - HTTPException 422 para validaciones fallidas
# - HTTPException 500 para errores de BD

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from app.core.database import get_db
from app.schemas.atencion_schema import (
    AtencionCreate,
    AtencionResponse,
    AtencionFilter,
    EstadisticasResponse
)
from app.services import atencion_service

router = APIRouter()
Validación:
bash# Iniciar servidor
uvicorn app.main:app --reload

# Probar endpoints
curl http://localhost:8000/api/v1/atenciones/estadisticas?año=2024

4.5 Main Application ⏳
Archivo: app/main.py
Instrucciones para Copilot:
python# Entry point de la aplicación FastAPI
# Basado en requirements.md sección "Arquitectura de la Aplicación"
#
# Configuración:
# - Título: "API de Análisis del SIS"
# - Descripción desde requirements.md
# - Versión desde settings.API_VERSION
# - CORS configurado con settings.CORS_ORIGINS
#
# Incluir:
# - api_router con prefijo /api/v1
# - Middleware CORS
# - Logging configurado
#
# Evento startup:
# - Log de inicio
# - Verificar conexión a BD
#
# Evento shutdown:
# - Log de cierre
# - Cerrar conexiones

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.core.settings import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Descripción para la documentación automática
description = """
API de Análisis Descriptivo y Predictivo del Seguro Integral de Salud (SIS) del Perú.

Permite:
* Análisis estadístico de atenciones médicas
* Segmentación demográfica y geográfica
* Predicción de demanda de servicios de salud
"""
Validación:
bashuvicorn app.main:app --reload
# Visitar: http://localhost:8000/docs
# Debe mostrar documentación Swagger con todos los endpoints