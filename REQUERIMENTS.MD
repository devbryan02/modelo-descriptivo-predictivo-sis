# Requirements Document - Sistema de Análisis del SIS

## 📋 Información General del Proyecto

**Nombre:** Modelo de Análisis Descriptivo y Predictivo para la Identificación de Patrones en las Atenciones del Seguro Integral de Salud (SIS)

**Objetivo Principal:** Desarrollar un sistema backend con FastAPI que procese, analice y prediga patrones en las atenciones médicas del SIS, exponiendo resultados mediante una API REST consumida por un frontend en Next.js.

**Stack Tecnológico:**
- Backend: Python 3.10+, FastAPI, SQLAlchemy, Alembic
- Base de Datos: PostgreSQL
- ML/Data Science: scikit-learn, pandas, numpy
- Testing: pytest
- Frontend (futuro): Next.js

---

## 🎯 Contexto del Negocio

### Entidad: Seguro Integral de Salud (SIS) - Perú
- Institución pública del Ministerio de Salud (MINSA)
- Garantiza acceso a servicios de salud para población vulnerable
- Gestiona múltiples planes: SIS Gratuito, Independiente, NRUS, Microempresas, Para Todos
- Trabaja con IPRESS (Instituciones Prestadoras de Servicios de Salud) en 3 niveles (I, II, III)

### Problema a Resolver
- Millones de atenciones médicas sin análisis sistemático
- Falta de herramientas para anticipar demanda de servicios
- Datos dispersos sin integración
- Procesos manuales de análisis
- Dificultad para detectar patrones o planificar recursos

---

## 📊 Modelo de Datos

### Variables Clave del Dataset

| Variable | Tipo | Descripción |
|----------|------|-------------|
| AÑO | Numérica | Año de la atención médica |
| MES | Numérica | Mes de la atención (1-12) |
| REGIÓN | Categórica | Región donde se brindó la atención |
| PROVINCIA | Categórica | Provincia de la atención |
| DISTRITO | Categórica | Distrito/ubicación del establecimiento |
| SEXO | Categórica | Masculino/Femenino |
| GRUPO_EDAD | Categórica | Rangos: 00-04, 05-11, 12-17, 18-29, 30-59, 60+ |
| PLAN_DE_SEGURO | Categórica | Gratuito, Independiente, NRUS, Microempresa, Para Todos |
| NIVEL_EESS | Categórica | Nivel del establecimiento (I, II, III) |
| DESC_SERVICIO | Categórica | Tipo de servicio médico brindado |
| ATENCIONES | Numérica | Número total de atenciones registradas |

### Esquema de Base de Datos (PostgreSQL)

**Tablas OLTP:**
- `pacientes`: datos demográficos (sexo, grupo_etario, tipo_seguro)
- `ipress`: establecimientos de salud (nombre, nivel, ubicación)
- `servicios`: catálogo de servicios médicos
- `planes_seguro`: tipos de planes SIS
- `regiones`: estructura geográfica (región, provincia, distrito, ubigeo)
- `atenciones`: registro principal (FK a todas las anteriores)

**Vistas Analíticas:**
- `vw_resumen_atenciones`: totales por año, mes, región
- `vw_atenciones_por_servicio`: distribución por tipo de servicio
- `vw_atenciones_por_plan`: agrupadas por plan de seguro
- `vw_atenciones_por_edad_y_sexo`: segmentación demográfica

---

## 🏗️ Arquitectura de la Aplicación

### Estructura de Carpetas

```
MODELO-PREDICCION-SIS/
├── app/
│   ├── api/
│   │   ├── endpoints/       # Controladores (atencion.py, prediccion.py)
│   │   └── routes/          # Rutas principales de la API
│   ├── core/
│   │   ├── config.py        # Variables de entorno
│   │   ├── database.py      # Conexión a PostgreSQL
│   │   └── settings.py      # Configuración global
│   ├── models/              # SQLAlchemy ORM models
│   │   └── atencion.py
│   ├── schemas/             # Pydantic schemas para validación
│   │   └── atencion_schema.py
│   ├── services/            # Lógica de negocio (crear si no existe)
│   ├── ml/                  # Modelos de ML (crear si no existe)
│   │   ├── predictor.py
│   │   ├── models/          # Modelos entrenados (.pkl)
│   │   └── training/        # Scripts de entrenamiento
│   ├── utils/
│   │   └── load_csv_to_db.py
│   ├── static/
│   │   └── dataset.csv      # Dataset del SIS
│   └── main.py              # Entry point FastAPI
├── scripts/
│   └── load_data.py         # Script ETL
├── alembic/                 # Migraciones de BD
├── tests/                   # Tests unitarios/integración
└── requirements.txt
```

---

## 🔧 Funcionalidades Requeridas

### 1. API REST con FastAPI

#### Endpoints de Análisis Descriptivo
- `GET /api/v1/atenciones/estadisticas`
  - Query params: año, mes, región, plan_seguro
  - Retorna: totales, promedios, distribuciones
  
- `GET /api/v1/atenciones/por-region`
  - Agrupa atenciones por región geográfica
  
- `GET /api/v1/atenciones/por-edad-sexo`
  - Segmentación demográfica
  
- `GET /api/v1/atenciones/por-servicio`
  - Distribución por tipo de servicio médico

#### Endpoints de Predicción
- `POST /api/v1/prediccion/demanda`
  - Body: `{año, mes, región, grupo_edad, sexo, plan_seguro}`
  - Retorna: predicción de número de atenciones
  
- `POST /api/v1/prediccion/batch`
  - Predicción masiva para múltiples escenarios

#### Endpoints de Gestión
- `POST /api/v1/data/load-csv` (admin)
  - Carga masiva desde CSV al OLTP
  
- `GET /api/v1/health`
  - Healthcheck de la API y conexión a BD

### 2. Procesamiento de Datos

**Limpieza y Transformación:**
- Eliminar duplicados
- Imputación de valores nulos (moda para categóricas, mediana para numéricas)
- Estandarización de formatos (fechas, texto)
- Validación de integridad referencial
- Filtrado de registros inconsistentes

**Feature Engineering:**
- Derivar: total_atenciones_por_paciente, promedio_mensual_por_region
- Agrupar categorías redundantes
- Crear variables temporales: año, mes, trimestre
- Clasificar grupos etarios: 0-11, 12-17, 18-59, 60+

**Codificación para ML:**
- One-Hot Encoding: sexo, tipo_seguro, región, servicio
- Label Encoding: nivel_ipress
- StandardScaler: variables numéricas

### 3. Modelos de Machine Learning

**Objetivo:** Predecir la demanda futura de atenciones médicas

**Modelos a implementar:**
- Regresión Lineal (baseline)
- Random Forest Regressor
- Gradient Boosting (XGBoost/LightGBM)
- Opcionalmente: LSTM para series temporales

**Métricas de evaluación:**
- R² (coeficiente de determinación)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)

**Pipeline ML:**
1. Preprocesamiento (escalado, codificación)
2. Entrenamiento con train/test split (80/20)
3. Validación cruzada
4. Serialización del modelo (joblib/pickle)
5. Carga del modelo en la API

---

## 📝 Reglas de Negocio

1. **Validación de Datos:**
   - Años válidos: 2020-2025
   - Meses: 1-12
   - Grupos de edad deben seguir los rangos establecidos
   - Sexo: solo "Masculino" o "Femenino"

2. **Filtros de Consulta:**
   - Permitir filtrado múltiple por región, año, mes, plan
   - Paginación en endpoints que retornen muchos registros

3. **Seguridad:**
   - Autenticación JWT (futuro)
   - Rate limiting para prevenir abuso
   - Logs de auditoría para operaciones críticas

4. **Performance:**
   - Cache de consultas frecuentes (Redis, futuro)
   - Índices en PostgreSQL para campos filtrados
   - Queries optimizadas con SQLAlchemy

---

## 🧪 Testing

**Tipos de tests requeridos:**
- Unitarios: modelos, schemas, utilidades
- Integración: endpoints de la API
- E2E: flujo completo de carga → análisis → predicción

**Cobertura mínima:** 70%

**Herramientas:**
- pytest
- pytest-cov
- httpx (para tests de FastAPI)

---

## 🚀 Deploy y Entorno

**Variables de Entorno (.env):**
```
DATABASE_URL=postgresql://user:password@localhost:5432/sis_db
SECRET_KEY=your-secret-key
DEBUG=True
API_VERSION=v1
```

**Comandos principales:**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
alembic upgrade head

# Cargar datos iniciales
python scripts/load_data.py

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload

# Ejecutar tests
pytest tests/ -v --cov=app
```

---

## 📚 Dependencias Principales

**Backend:**
- fastapi
- uvicorn[standard]
- sqlalchemy
- psycopg2-binary
- alembic
- pydantic
- python-dotenv

**Data Science:**
- pandas
- numpy
- scikit-learn
- joblib
- matplotlib
- seaborn

**Testing:**
- pytest
- pytest-cov
- httpx

---

## 🎨 Convenciones de Código

- **Estilo:** PEP 8
- **Nombrado:**
  - Archivos: snake_case
  - Clases: PascalCase
  - Funciones/variables: snake_case
  - Constantes: UPPER_CASE
- **Docstrings:** Google Style
- **Type hints:** obligatorios en funciones públicas

---

## 🔮 Roadmap Futuro

**Fase 1 (Actual):**
- ✅ Estructura del proyecto
- ✅ Modelos de BD
- ✅ Endpoints básicos
- ⏳ Pipeline de ML

**Fase 2:**
- Autenticación y autorización
- Dashboard en Next.js
- Cache con Redis
- Dockerización

**Fase 3:**
- Despliegue en producción
- Monitoreo con Prometheus/Grafana
- CI/CD con GitHub Actions
- Documentación con Swagger/ReDoc

---

## 👥 Equipo

- Cardenas Muñoz, Brayan Yonque
- Conde Nuñez, Percy Emerson
- Huamán Mallqui, Abdias Eri
- Lopez Quispe, Brady
- Mitma Arango, Pilar Dana
- Trejo Gavilan, Mavel Leonor

**Docente:** Jhonatan Jurado

---

## 📖 Referencias

- [Documentación FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Scikit-learn](https://scikit-learn.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

**Última actualización:** Octubre 2025