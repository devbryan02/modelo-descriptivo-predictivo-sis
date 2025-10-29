# 🏥 API del Sistema de Análisis del SIS

API REST para el análisis de datos del Sistema Integral de Salud (SIS) del Perú. Esta API proporciona endpoints para analizar atenciones médicas, generar estadísticas y obtener insights sobre los servicios de salud.

## 📋 Información General

**Base URL:** `http://localhost:8000`

**Documentación interactiva:** 
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Formato de respuesta:** JSON

**Versión:** 1.0.0

---

## 🚀 Inicio Rápido

### 1. Verificar estado del servicio

```bash
curl http://localhost:8000/health/
```

**Respuesta:**
```json
{
  "status": "ok",
  "service": "API de Análisis del SIS",
  "timestamp": "2025-10-29T10:30:00.123456",
  "version": "1.0.0"
}
```

### 2. Health check detallado

```bash
curl http://localhost:8000/health/detailed
```

**Respuesta:**
```json
{
  "status": "ok",
  "service": "API de Análisis del SIS",
  "timestamp": "2025-10-29T10:30:00.123456",
  "version": "1.0.0",
  "database": "connected",
  "environment": "development",
  "checks": {
    "database": "✅ Conexión exitosa",
    "query_test": "✅ Query de prueba exitosa",
    "config": "✅ Configuración cargada"
  }
}
```

---

## 📊 Endpoints de Análisis de Atenciones

### 1. Estadísticas Generales

```http
GET /api/v1/atenciones/estadisticas
```

Obtiene métricas generales de las atenciones del SIS.

**Parámetros opcionales:**
- `fecha_inicio` (date): Fecha de inicio para filtro (YYYY-MM-DD)
- `fecha_fin` (date): Fecha de fin para filtro (YYYY-MM-DD)

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
    "M": 58420,
    "F": 67010
  },
  "fecha_inicio": "2024-01-01",
  "fecha_fin": "2024-12-31",
  "rango_fechas": {
    "primera_atencion": "2024-01-01",
    "ultima_atencion": "2024-12-31"
  }
}
```

### 2. Análisis por Región

```http
GET /api/v1/atenciones/por-region
```

Estadísticas de atenciones agrupadas por región (departamento).

**Parámetros opcionales:**
- `limit` (int): Máximo de regiones a mostrar (1-50, default: 10)
- `fecha_inicio` (date): Fecha de inicio para filtro
- `fecha_fin` (date): Fecha de fin para filtro

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/por-region?limit=5&fecha_inicio=2024-01-01"
```

**Respuesta:**
```json
[
  {
    "departamento": "LIMA",
    "total_atenciones": 35420,
    "costo_total": 4467890.50,
    "costo_promedio": 126.15,
    "numero_ipress": 287,
    "porcentaje_total": 28.2
  },
  {
    "departamento": "LA LIBERTAD",
    "total_atenciones": 18750,
    "costo_total": 2385672.80,
    "costo_promedio": 127.23,
    "numero_ipress": 156,
    "porcentaje_total": 14.9
  }
]
```

### 3. Análisis por Servicio

```http
GET /api/v1/atenciones/por-servicio
```

Estadísticas de atenciones agrupadas por tipo de servicio médico.

**Parámetros opcionales:**
- `limit` (int): Máximo de servicios a mostrar (1-50, default: 10)
- `fecha_inicio` (date): Fecha de inicio para filtro
- `fecha_fin` (date): Fecha de fin para filtro

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/por-servicio?limit=5"
```

**Respuesta:**
```json
[
  {
    "servicio_codigo": "001",
    "servicio_nombre": "MEDICINA GENERAL",
    "total_atenciones": 45620,
    "costo_total": 5847293.50,
    "costo_promedio": 128.15,
    "porcentaje_total": 36.4
  },
  {
    "servicio_codigo": "002",
    "servicio_nombre": "PEDIATRÍA",
    "total_atenciones": 28340,
    "costo_total": 3421567.80,
    "costo_promedio": 120.78,
    "porcentaje_total": 22.6
  }
]
```

### 4. Análisis Demográfico

```http
GET /api/v1/atenciones/demografico
```

Análisis detallado por grupos de edad y género.

**Parámetros opcionales:**
- `fecha_inicio` (date): Fecha de inicio para filtro
- `fecha_fin` (date): Fecha de fin para filtro

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/demografico"
```

**Respuesta:**
```json
{
  "por_grupo_edad": {
    "0-17": {
      "total": 32450,
      "porcentaje": 25.9,
      "costo_promedio": 115.20
    },
    "18-29": {
      "total": 28670,
      "porcentaje": 22.8,
      "costo_promedio": 125.45
    },
    "30-59": {
      "total": 45320,
      "porcentaje": 36.1,
      "costo_promedio": 135.78
    },
    "60+": {
      "total": 18990,
      "porcentaje": 15.1,
      "costo_promedio": 156.92
    }
  },
  "por_genero": {
    "M": {
      "total": 58420,
      "promedio_edad": 32.5,
      "costo_promedio": 128.45
    },
    "F": {
      "total": 67010,
      "promedio_edad": 34.2,
      "costo_promedio": 124.78
    }
  },
  "estadisticas_edad": {
    "edad_promedio": 33.4,
    "edad_mediana": 31.0,
    "edad_minima": 0,
    "edad_maxima": 95
  }
}
```

### 5. Tendencias Temporales

```http
GET /api/v1/atenciones/tendencias
```

Series temporales de atenciones agrupadas por periodo.

**Parámetros:**
- `agrupacion` (string): Tipo de agrupación ("mes", "trimestre", "año")

**Parámetros opcionales:**
- `fecha_inicio` (date): Fecha de inicio para filtro
- `fecha_fin` (date): Fecha de fin para filtro

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/tendencias?agrupacion=mes&fecha_inicio=2024-01-01&fecha_fin=2024-12-31"
```

**Respuesta:**
```json
[
  {
    "periodo": "2024-01",
    "total_atenciones": 9850,
    "costo_total": 1247382.50,
    "costo_promedio": 126.64
  },
  {
    "periodo": "2024-02",
    "total_atenciones": 10240,
    "costo_total": 1295673.20,
    "costo_promedio": 126.53
  },
  {
    "periodo": "2024-03",
    "total_atenciones": 11150,
    "costo_total": 1412856.75,
    "costo_promedio": 126.74
  }
]
```

### 6. Búsqueda con Filtros Múltiples

```http
GET /api/v1/atenciones/buscar
```

Búsqueda avanzada de atenciones con múltiples filtros y paginación.

**Parámetros de paginación:**
- `skip` (int): Número de registros a omitir (default: 0)
- `limit` (int): Máximo de registros a retornar (1-1000, default: 100)

**Parámetros de filtro opcionales:**
- `departamento` (string): Filtro por departamento (búsqueda parcial)
- `servicio_codigo` (string): Código exacto del servicio
- `plan_codigo` (string): Código exacto del plan
- `sexo` (string): Género ("M" o "F")
- `edad_min` (int): Edad mínima (0-120)
- `edad_max` (int): Edad máxima (0-120)
- `fecha_inicio` (date): Fecha de inicio para filtro
- `fecha_fin` (date): Fecha de fin para filtro

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/atenciones/buscar?departamento=LIMA&sexo=F&edad_min=18&edad_max=65&limit=50"
```

**Respuesta:**
```json
{
  "atenciones": [
    {
      "id": 12345,
      "fecha_atencion": "2024-03-15",
      "sexo": "F",
      "edad": 29,
      "monto_pagado": 125.50,
      "departamento": "LIMA",
      "provincia": "LIMA",
      "distrito": "SAN BORJA",
      "ipress_nombre": "HOSPITAL NACIONAL DOS DE MAYO",
      "servicio_nombre": "MEDICINA GENERAL",
      "servicio_codigo": "001",
      "plan_nombre": "SIS GRATUITO",
      "plan_codigo": "GRT"
    }
  ],
  "paginacion": {
    "total": 2847,
    "skip": 0,
    "limit": 50,
    "tiene_siguiente": true,
    "tiene_anterior": false,
    "pagina_actual": 1,
    "total_paginas": 57
  },
  "filtros_aplicados": {
    "departamento": "LIMA",
    "sexo": "F",
    "edad_min": 18,
    "edad_max": 65,
    "servicio_codigo": null,
    "plan_codigo": null,
    "fecha_inicio": null,
    "fecha_fin": null
  }
}
```

---

## 🔧 Endpoints de Monitoreo

### 1. Ping Simple

```http
GET /health/ping
```

**Respuesta:**
```json
{
  "message": "pong",
  "timestamp": "2025-10-29T10:30:00.123456"
}
```

---

## 📝 Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | Solicitud exitosa |
| 400 | Error en los parámetros de la solicitud |
| 404 | Recurso no encontrado |
| 422 | Error de validación de datos |
| 500 | Error interno del servidor |
| 503 | Servicio no disponible |

---

## 🛠️ Ejemplos de Uso con Diferentes Lenguajes

### JavaScript (Fetch API)

```javascript
// Obtener estadísticas generales
async function obtenerEstadisticas(fechaInicio = null, fechaFin = null) {
  const params = new URLSearchParams();
  if (fechaInicio) params.append('fecha_inicio', fechaInicio);
  if (fechaFin) params.append('fecha_fin', fechaFin);
  
  const response = await fetch(`http://localhost:8000/api/v1/atenciones/estadisticas?${params}`);
  const data = await response.json();
  
  return data;
}

// Buscar atenciones con filtros
async function buscarAtenciones(filtros) {
  const params = new URLSearchParams();
  Object.entries(filtros).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      params.append(key, value);
    }
  });
  
  const response = await fetch(`http://localhost:8000/api/v1/atenciones/buscar?${params}`);
  const data = await response.json();
  
  return data;
}

// Ejemplo de uso
const estadisticas = await obtenerEstadisticas('2024-01-01', '2024-12-31');
console.log(`Total de atenciones: ${estadisticas.total_atenciones}`);

const atenciones = await buscarAtenciones({
  departamento: 'LIMA',
  sexo: 'F',
  edad_min: 18,
  limit: 100
});
console.log(`Encontradas ${atenciones.paginacion.total} atenciones`);
```

### Python (requests)

```python
import requests
from datetime import date

BASE_URL = "http://localhost:8000"

def obtener_estadisticas(fecha_inicio=None, fecha_fin=None):
    """Obtiene estadísticas generales de atenciones"""
    params = {}
    if fecha_inicio:
        params['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        params['fecha_fin'] = fecha_fin
    
    response = requests.get(
        f"{BASE_URL}/api/v1/atenciones/estadisticas",
        params=params
    )
    response.raise_for_status()
    return response.json()

def buscar_atenciones(**filtros):
    """Busca atenciones con filtros múltiples"""
    # Filtrar valores None
    params = {k: v for k, v in filtros.items() if v is not None}
    
    response = requests.get(
        f"{BASE_URL}/api/v1/atenciones/buscar",
        params=params
    )
    response.raise_for_status()
    return response.json()

def obtener_tendencias(agrupacion="mes", fecha_inicio=None, fecha_fin=None):
    """Obtiene tendencias temporales"""
    params = {"agrupacion": agrupacion}
    if fecha_inicio:
        params['fecha_inicio'] = fecha_inicio
    if fecha_fin:
        params['fecha_fin'] = fecha_fin
    
    response = requests.get(
        f"{BASE_URL}/api/v1/atenciones/tendencias",
        params=params
    )
    response.raise_for_status()
    return response.json()

# Ejemplos de uso
if __name__ == "__main__":
    # Estadísticas del 2024
    stats = obtener_estadisticas(
        fecha_inicio="2024-01-01",
        fecha_fin="2024-12-31"
    )
    print(f"Total de atenciones 2024: {stats['total_atenciones']}")
    
    # Buscar atenciones de mujeres en Lima
    atenciones = buscar_atenciones(
        departamento="LIMA",
        sexo="F",
        edad_min=18,
        edad_max=65,
        limit=50
    )
    print(f"Atenciones encontradas: {atenciones['paginacion']['total']}")
    
    # Tendencias mensuales
    tendencias = obtener_tendencias(
        agrupacion="mes",
        fecha_inicio="2024-01-01",
        fecha_fin="2024-12-31"
    )
    print(f"Meses analizados: {len(tendencias)}")
```

### PHP (cURL)

```php
<?php
class SISApiClient {
    private $baseUrl;
    
    public function __construct($baseUrl = "http://localhost:8000") {
        $this->baseUrl = $baseUrl;
    }
    
    private function makeRequest($endpoint, $params = []) {
        $url = $this->baseUrl . $endpoint;
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json',
            'Accept: application/json'
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new Exception("API Error: HTTP $httpCode");
        }
        
        return json_decode($response, true);
    }
    
    public function obtenerEstadisticas($fechaInicio = null, $fechaFin = null) {
        $params = [];
        if ($fechaInicio) $params['fecha_inicio'] = $fechaInicio;
        if ($fechaFin) $params['fecha_fin'] = $fechaFin;
        
        return $this->makeRequest('/api/v1/atenciones/estadisticas', $params);
    }
    
    public function buscarAtenciones($filtros = []) {
        return $this->makeRequest('/api/v1/atenciones/buscar', $filtros);
    }
    
    public function obtenerPorRegion($limit = 10, $fechaInicio = null, $fechaFin = null) {
        $params = ['limit' => $limit];
        if ($fechaInicio) $params['fecha_inicio'] = $fechaInicio;
        if ($fechaFin) $params['fecha_fin'] = $fechaFin;
        
        return $this->makeRequest('/api/v1/atenciones/por-region', $params);
    }
}

// Ejemplo de uso
try {
    $api = new SISApiClient();
    
    // Obtener estadísticas generales
    $stats = $api->obtenerEstadisticas('2024-01-01', '2024-12-31');
    echo "Total de atenciones: " . $stats['total_atenciones'] . "\n";
    
    // Top 5 regiones
    $regiones = $api->obtenerPorRegion(5);
    echo "Top 5 regiones por atenciones:\n";
    foreach ($regiones as $region) {
        echo "- {$region['departamento']}: {$region['total_atenciones']}\n";
    }
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
```

---

## 🚨 Manejo de Errores

### Errores de Validación (422)

```json
{
  "detail": [
    {
      "loc": ["query", "edad_min"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error.number.not_ge",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

### Error de Rango de Fechas (400)

```json
{
  "detail": "La fecha de inicio no puede ser posterior a la fecha de fin"
}
```

### Error de Servicio No Disponible (503)

```json
{
  "detail": {
    "message": "Servicio no disponible",
    "error": "Database connection failed",
    "health_status": {
      "status": "error",
      "database": "error",
      "checks": {
        "database": "❌ Sin conexión a BD"
      }
    }
  }
}
```

---

## 🔍 Consejos de Performance

1. **Uso de filtros de fecha**: Siempre que sea posible, utiliza filtros de fecha para limitar el conjunto de datos.

2. **Paginación**: Para búsquedas que pueden retornar muchos resultados, usa los parámetros `skip` y `limit`.

3. **Límites apropiados**: No solicites más datos de los necesarios usando el parámetro `limit`.

4. **Monitoreo**: Usa el endpoint `/health/detailed` para verificar el estado del sistema.

---

## 📊 Casos de Uso Comunes

### 1. Dashboard de Estadísticas Generales

```bash
# Obtener métricas generales del año actual
curl "http://localhost:8000/api/v1/atenciones/estadisticas?fecha_inicio=2024-01-01&fecha_fin=2024-12-31"

# Top 10 regiones por atenciones
curl "http://localhost:8000/api/v1/atenciones/por-region?limit=10"

# Análisis demográfico
curl "http://localhost:8000/api/v1/atenciones/demografico"
```

### 2. Análisis de Tendencias

```bash
# Tendencias mensuales del 2024
curl "http://localhost:8000/api/v1/atenciones/tendencias?agrupacion=mes&fecha_inicio=2024-01-01&fecha_fin=2024-12-31"

# Comparación trimestral
curl "http://localhost:8000/api/v1/atenciones/tendencias?agrupacion=trimestre&fecha_inicio=2024-01-01&fecha_fin=2024-12-31"
```

### 3. Reportes Específicos

```bash
# Atenciones de pediatría en Lima
curl "http://localhost:8000/api/v1/atenciones/buscar?departamento=LIMA&servicio_codigo=002&limit=100"

# Atenciones de adultos mayores (60+) en el primer trimestre
curl "http://localhost:8000/api/v1/atenciones/buscar?edad_min=60&fecha_inicio=2024-01-01&fecha_fin=2024-03-31"
```

---

## 🔗 Enlaces Útiles

- **Documentación Swagger:** http://localhost:8000/docs
- **Documentación ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health/
- **Repositorio del proyecto:** (URL del repositorio)

---

## 👥 Equipo de Desarrollo

- Cardenas Muñoz, Brayan Yonque
- Conde Nuñez, Percy Emerson  
- Huamán Mallqui, Abdias Eri
- Lopez Quispe, Brady
- Mitma Arango, Pilar Dana
- Trejo Gavilan, Mavel Leonor

**Docente:** Jhonatan Jurado

---

**Última actualización:** Octubre 2025
**Versión de la API:** 1.0.0