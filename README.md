# 🏥 API del Sistema de Análisis del SIS

API REST para el análisis de datos del Sistema Integral de Salud (SIS) del Perú. 

## 🎯 Características

✅ **Análisis Descriptivo** - Estadísticas, tendencias y visualización de datos históricos  
✅ **Predicción con ML** - Modelos de Machine Learning para predecir demanda futura

---

## 📚 Documentación Completa

### 📊 [Análisis Descriptivo](./README_DESCRIPTIVO.md)
Endpoints para análisis estadístico de atenciones:
- ✅ Estadísticas generales
- ✅ Análisis por región y servicios
- ✅ Análisis demográfico
- ✅ Tendencias temporales
- ✅ Búsqueda avanzada

### 🤖 [Predicción de Demanda](./README_PREDICTIVO.md)
Endpoints de Machine Learning:
- ✅ Predicción individual de demanda
- ✅ Predicción masiva (batch)
- ✅ Información de modelos
- ✅ Gestión de cache

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.10 o superior** ([Descargar](https://www.python.org/downloads/))
- **PostgreSQL 12 o superior** ([Descargar](https://www.postgresql.org/download/))
- **Git** ([Descargar](https://git-scm.com/downloads))
- **pip** (viene con Python)

### Verificar Instalaciones
```bash
python --version    # Debe mostrar Python 3.10+
psql --version      # Debe mostrar PostgreSQL
git --version       # Debe mostrar Git
```

---

## 🚀 Inicio Rápido

### Instalación desde Cero (Nueva Máquina)

#### 0. Prerequisitos del Sistema (REQUERIDO)

**IMPORTANTE:** Antes de instalar las dependencias de Python, necesitas instalar herramientas de compilación:

**Fedora/RHEL/CentOS:**
```bash
sudo dnf install python3-devel postgresql-devel gcc gcc-c++
```

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-dev libpq-dev gcc g++
```

**macOS:**
```bash
brew install postgresql gcc
```

Estos paquetes son necesarios para compilar numpy, pandas, scipy y psycopg2.

#### 1. Clonar el Repositorio
```bash
git clone https://github.com/devbryan02/modelo-descriptivo-predictivo-sis.git
cd modelo-prediccion-sis
```

#### 2. Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Linux/Mac)
source .venv/bin/activate

# Activar (Windows)
# .venv\Scripts\activate
```

#### 3. Instalar TODAS las Dependencias
```bash
# Esto instalará TODO lo necesario (FastAPI, scikit-learn, pandas, etc)
pip install -r requirements.txt
```

**Nota:** El archivo `requirements.txt` incluye TODAS las dependencias necesarias:
- FastAPI y Uvicorn (web framework)
- SQLAlchemy y Alembic (base de datos)
- scikit-learn, pandas, numpy, joblib (machine learning)
- Y todas las demás librerías

**Verificar instalación:**
```bash
# Ejecutar script de verificación
python verificar_dependencias.py
```

Si todo está correcto verás ✅ en todos los módulos. Si falta algo, el script te dirá qué instalar.

#### 4. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/sis_db
ENVIRONMENT=development
API_VERSION=v1
```

**Importante:** Reemplaza `user`, `password` y `sis_db` con tus credenciales de PostgreSQL.

#### 5. Ejecutar Migraciones (primera vez)
```bash
# Crear las tablas en la base de datos
alembic upgrade head
```

#### 6. Entrenar Modelos de ML (primera vez)
```bash
# Esto entrenará los 3 modelos de Machine Learning
python train_models.py
```

**Este proceso:**
- Conecta a PostgreSQL
- Extrae datos de las tablas
- Entrena 3 modelos (Linear, Random Forest, Gradient Boosting)
- Guarda modelos en `app/ml/models/`
- **Tiempo estimado:** 5-15 minutos dependiendo de la cantidad de datos

#### 7. Iniciar el Servidor
```bash
# Opción 1: Desarrollo (con reload automático)
uvicorn app.main:app --reload

# Opción 2: Usar el script
python run_api.py
```

#### 8. Verificar Funcionamiento
```bash
# Health check
curl http://localhost:8000/health

# Ver documentación interactiva
# Abrir en navegador: http://localhost:8000/docs
```

---

### Instalación Rápida (Si Ya Tienes el Entorno)

```bash
# Activar entorno virtual
source .venv/bin/activate

# Iniciar servidor
python run_api.py
```

---

## 📊 Ejemplos Rápidos

### Análisis Descriptivo

```bash
# Estadísticas generales
curl "http://localhost:8000/api/v1/atenciones/estadisticas"

# Top 5 regiones con más atenciones
curl "http://localhost:8000/api/v1/atenciones/por-region?limit=5"

# Tendencias mensuales
curl "http://localhost:8000/api/v1/atenciones/tendencias?agrupacion=mes"
```

### Predicción de Demanda

```bash
# Predicción individual
curl -X POST "http://localhost:8000/api/v1/prediccion/demanda" \
  -H "Content-Type: application/json" \
  -d '{
    "año": 2025,
    "mes": 6,
    "region": "LIMA",
    "grupo_edad": "18-29",
    "sexo": "FEMENINO",
    "nivel_ipress": "II",
    "servicio_categoria": "CONSULTA EXTERNA",
    "plan_seguro": "SIS GRATUITO"
  }'

# Ver modelos disponibles
curl "http://localhost:8000/api/v1/prediccion/modelos"
```

---

## 📖 Documentación Interactiva

Una vez que el servidor esté corriendo:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Endpoint raíz**: http://localhost:8000

---

## 🗄️ Estructura del Proyecto

```
modelo-prediccion-sis/
├── app/
│   ├── api/
│   │   ├── endpoints/          # Controladores REST
│   │   │   ├── atenciones.py   # Endpoints de análisis
│   │   │   ├── prediccion.py   # Endpoints de ML
│   │   │   └── health.py       # Health checks
│   │   ├── routes/             # Configuración de rutas
│   │   └── services/           # Lógica de negocio
│   │       ├── atencion_service.py
│   │       └── prediccion_service.py
│   ├── core/
│   │   ├── database.py         # Conexión PostgreSQL
│   │   └── settings.py         # Configuración
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── atencion.py
│   │   ├── ipress.py
│   │   ├── servicio.py
│   │   └── plan_seguro.py
│   ├── schemas/                # Schemas Pydantic
│   │   ├── atencion_schema.py
│   │   └── prediccion_schema.py
│   ├── ml/                     # Machine Learning
│   │   ├── predictor.py        # Clase principal
│   │   ├── models/             # Modelos .pkl
│   │   └── training/           # Scripts de entrenamiento
│   └── main.py                 # Entry point FastAPI
├── alembic/                    # Migraciones de BD
├── train_models.py             # Script de entrenamiento
├── run_api.py                  # Script para ejecutar API
├── requirements.txt            # Dependencias
├── README.md                   # Este archivo
├── README_DESCRIPTIVO.md       # Docs análisis descriptivo
└── README_PREDICTIVO.md        # Docs predicción ML
```

---

## 🔧 Stack Tecnológico

### Backend
- **FastAPI** - Framework web moderno
- **SQLAlchemy** - ORM para PostgreSQL
- **Pydantic** - Validación de datos
- **Alembic** - Migraciones de BD

### Machine Learning
- **scikit-learn** - Modelos de ML
- **pandas** - Procesamiento de datos
- **numpy** - Operaciones numéricas
- **joblib** - Serialización de modelos

### Base de Datos
- **PostgreSQL** - Base de datos relacional

---

## 🤖 Modelos de Machine Learning

### 1. Regresión Lineal
- Baseline simple
- Rápido y ligero

### 2. Random Forest ⭐ **Recomendado**
- Mejor rendimiento
- Robusto y preciso

### 3. Gradient Boosting
- Alta precisión
- Patrones complejos

**Métricas de evaluación:**
- R² (Coeficiente de determinación)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)

---

## 📝 Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión PostgreSQL | `postgresql://user:pass@localhost:5432/db` |
| `ENVIRONMENT` | Entorno de ejecución | `development`, `production` |
| `API_VERSION` | Versión de la API | `v1` |
| `SECRET_KEY` | Clave secreta (futuro) | `your-secret-key` |

---

## 🔍 Casos de Uso

### 1. Dashboard de Análisis
Obtener estadísticas para un dashboard regional:
```bash
curl "http://localhost:8000/api/v1/atenciones/por-region?limit=25"
```

### 2. Planificación de Recursos
Predecir demanda futura para asignación de recursos:
```bash
curl -X POST "http://localhost:8000/api/v1/prediccion/demanda" \
  -H "Content-Type: application/json" \
  -d '{"año": 2025, "mes": 7, "region": "CUSCO", ...}'
```

### 3. Reportes Demográficos
Generar reportes de atención por grupo etario:
```bash
curl "http://localhost:8000/api/v1/atenciones/demografico"
```

### 4. Análisis de Tendencias
Ver evolución temporal de atenciones:
```bash
curl "http://localhost:8000/api/v1/atenciones/tendencias?agrupacion=mes"
```

---

## 🛠️ Comandos Útiles

```bash
# Ejecutar API en desarrollo
uvicorn app.main:app --reload

# Ejecutar API en producción
python run_api.py

# Entrenar todos los modelos
python train_models.py

# Entrenar un modelo específico
python train_models.py --model random_forest

# Ejecutar migraciones
alembic upgrade head

# Crear nueva migración
alembic revision --autogenerate -m "descripción"

# Ver logs del servidor
tail -f logs/api.log
```

---

## 🐛 Solución de Problemas

### 1. Error: "ModuleNotFoundError: No module named 'xxx'"

**Causa:** Falta instalar dependencias.

**Solución:**
```bash
# Verificar qué falta
python verificar_dependencias.py

# Instalar todo
pip install -r requirements.txt
```

### 2. Error: "Modelo no encontrado"

**Causa:** Los modelos ML no han sido entrenados.

**Solución:**
```bash
python train_models.py
```

### 3. Error: "No se puede conectar a la base de datos"

**Causa:** PostgreSQL no está corriendo o las credenciales en `.env` son incorrectas.

**Solución:**
```bash
# Verificar que PostgreSQL esté corriendo
psql --version

# Probar conexión manualmente
psql -U usuario -d sis_db -c "SELECT 1;"

# Revisar archivo .env
cat .env
```

### 4. Error en otra máquina: "No encuentra módulos"

**Causa:** El entorno virtual no está activado o las dependencias no están instaladas.

**Solución:**
```bash
# 1. Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 2. Verificar que pip use el entorno virtual
which pip  # Debe apuntar a .venv/bin/pip

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar instalación
python verificar_dependencias.py
```

### 5. Re-entrenar modelos

Si los datos cambiaron o quieres actualizar los modelos:
```bash
python train_models.py --model all
```

### 6. Verificación Completa del Sistema

```bash
# 1. Verificar Python
python --version

# 2. Verificar entorno virtual activo
which python  # Debe apuntar a .venv

# 3. Verificar dependencias
python verificar_dependencias.py

# 4. Verificar base de datos
psql -U usuario -d sis_db -c "SELECT COUNT(*) FROM atenciones;"

# 5. Verificar modelos entrenados
ls -lh app/ml/models/*.pkl
```

---

## 🔄 Mejoras Recientes del Predictor (v2.0)

El predictor ha sido refactorizado con mejoras significativas para forecasting de demanda:

### ✨ Nuevas Características

1. **Features Temporales**
   - `lag_1`: Valor del mes anterior
   - `rolling_mean_3`: Promedio móvil de 3 meses
   - `rolling_mean_6`: Promedio móvil de 6 meses
   - Agrupados por: región, sexo, grupo_edad, servicio_categoria, plan_seguro

2. **Target Encoding**
   - Reemplaza LabelEncoder para variables de alta cardinalidad
   - Variables: `region`, `servicio_categoria`, `plan_seguro`
   - Mejor captura de relación con el target

3. **Modelo Poisson GLM** (NUEVO)
   - Ideal para datos de conteo como `cantidad_atenciones`
   - Garantiza predicciones no-negativas
   - Uso: `SISPredictor(model_type="poisson")`

4. **Scaling Selectivo**
   - Linear y Poisson: ✅ Con scaling
   - Random Forest y Gradient Boosting: ❌ Sin scaling (mejor performance)

5. **Output Mejorado**
   ```python
   {
     "expected_value": 12.5,
     "rounded_prediction": 12,
     "demand_level": "MEDIUM"  # LOW/MEDIUM/HIGH
   }
   ```

### 📝 Modelos Disponibles

- `linear` - Regresión lineal (baseline)
- `poisson` - GLM Poisson (recomendado para conteos)
- `random_forest` - Random Forest
- `gradient_boosting` - Gradient Boosting

### 🧪 Verificar Refactor

```bash
python test_refactor.py
```

---

## 📚 Documentación Adicional

- **[README_DESCRIPTIVO.md](./README_DESCRIPTIVO.md)** - Documentación completa de endpoints de análisis
- **[README_PREDICTIVO.md](./README_PREDICTIVO.md)** - Documentación completa de endpoints de predicción
- **[REQUERIMENTS.MD](./REQUERIMENTS.MD)** - Especificación técnica del proyecto
- **[IMPLEMENTACION_COMPLETADA.md](./IMPLEMENTACION_COMPLETADA.md)** - Resumen de implementación

---

## 🎓 Equipo de Desarrollo

- Cardenas Muñoz, Brayan Yonque
- Conde Nuñez, Percy Emerson
- Huamán Mallqui, Abdias Eri
- Lopez Quispe, Brady
- Mitma Arango, Pilar Dana
- Trejo Gavilan, Mavel Leonor

**Docente:** Jhonatan Jurado

---

## 📅 Información del Proyecto

**Institución:** Universidad  
**Curso:** Análisis de Datos  
**Año:** 2025  
**Versión API:** 1.0.0

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico para el análisis del Sistema Integral de Salud (SIS) del Perú.

---

**¿Necesitas ayuda?** Consulta la documentación interactiva en http://localhost:8000/docs
