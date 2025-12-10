# 📊 API de Análisis Descriptivo del SIS

Módulo de análisis descriptivo de las atenciones del Sistema Integral de Salud (SIS) del Perú.

## 🎯 Objetivo

Proporcionar estadísticas, análisis y visualización de datos históricos de atenciones médicas del SIS mediante endpoints REST.

---

## 🔗 Endpoints Disponibles

### Base URL
```
http://localhost:8000/api/v1
```

---

## 📋 Health Check

### `GET /health`
Verificación básica del estado del servicio.

**Respuesta:**
```json
{
  "status": "ok",
  "service": "API de Análisis del SIS",
  "timestamp": "2025-12-08T10:30:00",
  "version": "1.0.0"
}
```

### `GET /health/detailed`
Health check detallado con verificación de base de datos.

**Respuesta:**
```json
{
  "status": "ok",
  "service": "API de Análisis del SIS",
  "database": "connected",
  "environment": "development",
  "checks": {
    "database": "✅ Conexión exitosa",
    "query_test": "✅ Query de prueba exitosa"
  }
}
```

---

## 📊 Estadísticas Generales

### `GET /api/v1/atenciones/estadisticas`
Obtiene métricas generales de las atenciones del SIS.

**Parámetros Query (opcionales):**
- `fecha_inicio` (date): Fecha inicio filtro (YYYY-MM-DD)
- `fecha_fin` (date): Fecha fin filtro (YYYY-MM-DD)

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/estadisticas?fecha_inicio=2024-01-01&fecha_fin=2024-12-31"
```

**Respuesta:**
```json
{
  "total_atenciones": 125430,
  "costo_total": 15847293.50,
  "costo_promedio": 126.32,
  "distribucion_genero": {
    "MASCULINO": 58420,
    "FEMENINO": 67010
  },
  "fecha_inicio": "2024-01-01",
  "fecha_fin": "2024-12-31",
  "rango_fechas": {
    "primera_atencion": "2024-01-01",
    "ultima_atencion": "2024-12-31"
  }
}
```

---

## 🗺️ Análisis Geográfico

### `GET /api/v1/atenciones/por-region`
Estadísticas de atenciones agrupadas por región/departamento.

**Parámetros Query:**
- `limit` (int): Número máximo de regiones (1-50, default: 10)
- `fecha_inicio` (date): Fecha inicio filtro
- `fecha_fin` (date): Fecha fin filtro

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/por-region?limit=5"
```

**Respuesta:**
```json
[
  {
    "region": "LIMA",
    "total_atenciones": 45230,
    "total_costo": 5678912.50,
    "promedio_costo": 125.55,
    "total_ipress": 156
  },
  {
    "region": "CUSCO",
    "total_atenciones": 23456,
    "total_costo": 2891234.00,
    "promedio_costo": 123.22,
    "total_ipress": 89
  }
]
```

---

## 🏥 Análisis por Servicios

### `GET /api/v1/atenciones/por-servicio`
Estadísticas de atenciones agrupadas por tipo de servicio médico.

**Parámetros Query:**
- `limit` (int): Número máximo de servicios (1-50, default: 10)
- `fecha_inicio` (date): Fecha inicio filtro
- `fecha_fin` (date): Fecha fin filtro

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/por-servicio?limit=5"
```

**Respuesta:**
```json
[
  {
    "servicio": "CONSULTA EXTERNA",
    "codigo_servicio": "CE-001",
    "total_atenciones": 67890,
    "total_costo": 8901234.00,
    "promedio_costo": 131.15
  },
  {
    "servicio": "EMERGENCIA",
    "codigo_servicio": "EM-001",
    "total_atenciones": 23456,
    "total_costo": 4567890.00,
    "promedio_costo": 194.65
  }
]
```

---

## 👥 Análisis Demográfico

### `GET /api/v1/atenciones/demografico`
Análisis demográfico de las atenciones por edad y sexo.

**Parámetros Query:**
- `fecha_inicio` (date): Fecha inicio filtro
- `fecha_fin` (date): Fecha fin filtro

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/demografico"
```

**Respuesta:**
```json
{
  "grupos_edad": [
    {
      "grupo": "Menores (0-17)",
      "total_atenciones": 25678,
      "total_costo": 3456789.00
    },
    {
      "grupo": "Jóvenes (18-29)",
      "total_atenciones": 34567,
      "total_costo": 4567890.00
    },
    {
      "grupo": "Adultos (30-49)",
      "total_atenciones": 45678,
      "total_costo": 6789012.00
    }
  ],
  "por_genero": [
    {
      "genero": "MASCULINO",
      "total_atenciones": 58420,
      "total_costo": 7890123.00,
      "edad_promedio": 35.5
    },
    {
      "genero": "FEMENINO",
      "total_atenciones": 67010,
      "total_costo": 8901234.00,
      "edad_promedio": 33.2
    }
  ],
  "estadisticas_edad": {
    "edad_minima": 0,
    "edad_maxima": 95,
    "edad_promedio": 34.2
  }
}
```

---

## 📈 Tendencias Temporales

### `GET /api/v1/atenciones/tendencias`
Análisis de tendencias temporales de las atenciones.

**Parámetros Query:**
- `agrupacion` (string): Tipo de agrupación ("mes", "trimestre", "año")
- `fecha_inicio` (date): Fecha inicio filtro
- `fecha_fin` (date): Fecha fin filtro

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/tendencias?agrupacion=mes"
```

**Respuesta:**
```json
[
  {
    "periodo": "2024-01",
    "tipo_periodo": "mes",
    "total_atenciones": 12345,
    "total_costo": 1567890.00,
    "promedio_costo": 127.15
  },
  {
    "periodo": "2024-02",
    "tipo_periodo": "mes",
    "total_atenciones": 13456,
    "total_costo": 1678901.00,
    "promedio_costo": 124.78
  }
]
```

---

## 🔍 Búsqueda Avanzada

### `GET /api/v1/atenciones/buscar`
Búsqueda de atenciones con múltiples filtros.

**Parámetros Query:**
- `skip` (int): Registros a omitir (paginación)
- `limit` (int): Número máximo de registros (1-100)
- `departamento` (string): Filtro por departamento
- `servicio_codigo` (string): Filtro por código de servicio
- `plan_codigo` (string): Filtro por código de plan
- `sexo` (string): Filtro por sexo
- `edad_min` (int): Edad mínima
- `edad_max` (int): Edad máxima
- `fecha_inicio` (date): Fecha inicio
- `fecha_fin` (date): Fecha fin

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/buscar?departamento=LIMA&sexo=FEMENINO&edad_min=18&edad_max=30&limit=20"
```

**Respuesta:**
```json
{
  "total": 1543,
  "registros": [
    {
      "id": 1,
      "año": 2024,
      "mes": 6,
      "region": "LIMA",
      "sexo": "FEMENINO",
      "grupo_edad": "18-29",
      "cantidad_atenciones": 3,
      "plan_seguro": "SIS GRATUITO",
      "ipress": "Hospital Nacional",
      "servicio": "CONSULTA EXTERNA"
    }
  ]
}
```

---

## 🚀 Uso Rápido

### Con curl
```bash
# Estadísticas generales
curl http://localhost:8000/api/v1/atenciones/estadisticas

# Top 5 regiones
curl "http://localhost:8000/api/v1/atenciones/por-region?limit=5"

# Tendencias mensuales
curl "http://localhost:8000/api/v1/atenciones/tendencias?agrupacion=mes"
```

### Con Python
```python
import requests

# Estadísticas generales
response = requests.get(
    "http://localhost:8000/api/v1/atenciones/estadisticas",
    params={
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2024-12-31"
    }
)
data = response.json()
print(f"Total atenciones: {data['total_atenciones']}")
```

### Con JavaScript/Fetch
```javascript
// Análisis por región
fetch('http://localhost:8000/api/v1/atenciones/por-region?limit=10')
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## 📚 Documentación Interactiva

Visita los siguientes endpoints para explorar la API de forma interactiva:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🗄️ Modelos de Datos

### Atencion
- `año`, `mes`: Periodo temporal
- `region`, `provincia`, `distrito`: Ubicación geográfica
- `sexo`, `grupo_edad`: Datos demográficos
- `cantidad_atenciones`: Número de atenciones
- `plan_seguro_id`, `ipress_id`, `servicio_id`: Relaciones

### IPRESS
- `codigo`, `nombre`: Identificación
- `nivel`: I, II o III
- `region`, `provincia`, `distrito`: Ubicación

### Servicio
- `nombre`: Tipo de servicio médico
- `categoria`: Categoría del servicio

### PlanSeguro
- `nombre`: Tipo de plan (Gratuito, Independiente, NRUS, etc.)
- `descripcion`: Descripción del plan

---

## 🔧 Configuración

### Variables de Entorno
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/sis_db
ENVIRONMENT=development
API_VERSION=v1
```

### Iniciar Servidor
```bash
# Desarrollo
uvicorn app.main:app --reload

# Producción
python run_api.py
```

---

## 📊 Casos de Uso

### 1. Dashboard Regional
Obtener estadísticas de todas las regiones para un dashboard:
```bash
curl "http://localhost:8000/api/v1/atenciones/por-region?limit=25"
```

### 2. Análisis de Demanda
Ver tendencias mensuales para planificación:
```bash
curl "http://localhost:8000/api/v1/atenciones/tendencias?agrupacion=mes&fecha_inicio=2024-01-01"
```

### 3. Reportes Demográficos
Generar reportes de atención por grupo etario:
```bash
curl "http://localhost:8000/api/v1/atenciones/demografico"
```

### 4. Búsqueda Específica
Encontrar atenciones con criterios específicos:
```bash
curl "http://localhost:8000/api/v1/atenciones/buscar?departamento=CUSCO&servicio_codigo=CE-001&limit=50"
```

---

## 🎓 Equipo

- Cardenas Muñoz, Brayan Yonque
- Conde Nuñez, Percy Emerson
- Huamán Mallqui, Abdias Eri
- Lopez Quispe, Brady
- Mitma Arango, Pilar Dana
- Trejo Gavilan, Mavel Leonor

**Docente:** Jhonatan Jurado

---

**Fecha:** Diciembre 2025
