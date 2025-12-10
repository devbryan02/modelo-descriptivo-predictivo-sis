# 🤖 API de Predicción de Demanda del SIS

Módulo de Machine Learning para predecir la demanda futura de atenciones del Sistema Integral de Salud (SIS) del Perú.

## 🎯 Objetivo

Utilizar modelos de Machine Learning para predecir la cantidad de atenciones médicas esperadas según parámetros demográficos, temporales y geográficos.

---

## 🔗 Endpoints de Predicción

### Base URL
```
http://localhost:8000/api/v1/prediccion
```

---

## 🔮 Predicción Individual

### `POST /api/v1/prediccion/demanda`
Predice la demanda de atenciones para un escenario específico.

**Request Body:**
```json
{
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
```

**Parámetros:**
- `año` (int, requerido): Año de predicción (2020-2030)
- `mes` (int, requerido): Mes de predicción (1-12)
- `region` (string, requerido): Región/Departamento del Perú
- `grupo_edad` (string, requerido): Rango etario (ej: "00-04", "18-29", "60+")
- `sexo` (string, requerido): "MASCULINO" o "FEMENINO"
- `nivel_ipress` (string, opcional): Nivel del establecimiento ("I", "II", "III")
- `servicio_categoria` (string, opcional): Categoría del servicio
- `plan_seguro` (string, requerido): Tipo de plan del SIS
- `modelo` (string, opcional): Tipo de modelo ("linear", "random_forest", "gradient_boosting")

**Ejemplo con curl:**
```bash
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
    "plan_seguro": "SIS GRATUITO",
    "modelo": "random_forest"
  }'
```

**Respuesta:**
```json
{
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
```

---

## 📊 Predicción Masiva (Batch)

### `POST /api/v1/prediccion/batch`
Realiza predicciones para múltiples escenarios en una sola llamada.

**Request Body:**
```json
{
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
```

**Límites:**
- Mínimo: 1 predicción
- Máximo: 100 predicciones por llamada

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/api/v1/prediccion/batch" \
  -H "Content-Type: application/json" \
  -d @predicciones.json
```

**Respuesta:**
```json
{
  "total_predicciones": 2,
  "modelo_usado": "random_forest",
  "resultados": [
    {
      "prediccion": 245.67,
      "prediccion_redondeada": 246,
      "parametros": {
        "año": 2025,
        "mes": 6,
        "region": "LIMA"
      }
    },
    {
      "prediccion": 156.32,
      "prediccion_redondeada": 156,
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
    "desviacion_estandar": 63.18,
    "total_exitosas": 2,
    "total_fallidas": 0
  }
}
```

---

## 📋 Información de Modelos

### `GET /api/v1/prediccion/modelos`
Obtiene información sobre los modelos disponibles y sus métricas.

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/prediccion/modelos"
```

**Respuesta:**
```json
{
  "modelos_disponibles": [
    {
      "tipo": "random_forest",
      "nombre": "Random Forest Regressor",
      "metricas": {
        "r2": 0.87,
        "rmse": 12.45,
        "mae": 8.32
      },
      "estado": "disponible",
      "archivo": "sis_predictor_random_forest.pkl"
    },
    {
      "tipo": "gradient_boosting",
      "nombre": "Gradient Boosting Regressor",
      "metricas": {
        "r2": 0.85,
        "rmse": 13.12,
        "mae": 9.01
      },
      "estado": "disponible",
      "archivo": "sis_predictor_gradient_boosting.pkl"
    },
    {
      "tipo": "linear",
      "nombre": "Regresión Lineal",
      "metricas": {
        "r2": 0.72,
        "rmse": 18.45,
        "mae": 14.23
      },
      "estado": "disponible",
      "archivo": "sis_predictor_linear.pkl"
    }
  ],
  "modelo_recomendado": "random_forest"
}
```

---

## 🔧 Gestión de Modelos

### `POST /api/v1/prediccion/modelos/limpiar-cache`
Limpia el cache de modelos cargados en memoria.

**Uso:**
```bash
curl -X POST "http://localhost:8000/api/v1/prediccion/modelos/limpiar-cache"
```

**Respuesta:**
```json
{
  "mensaje": "Cache de modelos limpiado exitosamente",
  "accion": "Los modelos se recargarán en la próxima predicción"
}
```

**Cuándo usar:**
- Después de re-entrenar modelos
- Para liberar memoria
- Si se detectan problemas con modelos en cache

---

## 🤖 Modelos Disponibles

### 1. Regresión Lineal (`linear`)
- **Tipo**: Baseline
- **Características**: Simple, rápido
- **Uso**: Comparación de referencia
- **Rendimiento**: Moderado

### 2. Random Forest (`random_forest`) ⭐ **RECOMENDADO**
- **Tipo**: Ensemble
- **Características**: Robusto, maneja no-linealidades
- **Uso**: Producción
- **Rendimiento**: Excelente

### 3. Gradient Boosting (`gradient_boosting`)
- **Tipo**: Boosting
- **Características**: Alta precisión, patrones complejos
- **Uso**: Análisis detallado
- **Rendimiento**: Muy bueno

---

## 📊 Métricas de Evaluación

### R² (Coeficiente de Determinación)
- **Rango**: 0 - 1
- **Interpretación**: Proporción de varianza explicada
- **Mejor**: Más cercano a 1

### RMSE (Root Mean Squared Error)
- **Unidad**: Misma que la variable objetivo
- **Interpretación**: Error promedio en predicciones
- **Mejor**: Menor valor

### MAE (Mean Absolute Error)
- **Unidad**: Misma que la variable objetivo
- **Interpretación**: Error absoluto promedio
- **Mejor**: Menor valor

---

## 🚀 Guía de Uso

### Paso 1: Entrenar Modelos

**Primera vez solamente:**
```bash
# Entrenar todos los modelos
python train_models.py

# O entrenar uno específico
python train_models.py --model random_forest
```

Este proceso:
1. Conecta a PostgreSQL
2. Extrae datos con joins
3. Prepara features
4. Entrena modelos
5. Guarda archivos .pkl
6. Muestra métricas

**Tiempo estimado**: 5-15 minutos dependiendo del tamaño de datos

### Paso 2: Iniciar API

```bash
# Desarrollo
uvicorn app.main:app --reload

# Producción
python run_api.py
```

### Paso 3: Hacer Predicciones

Ver ejemplos de uso arriba ⬆️

---

## 💡 Casos de Uso

### 1. Planificación de Recursos
Predecir demanda para el próximo mes por región:
```python
import requests

# Predecir para Lima en Junio 2025
response = requests.post(
    "http://localhost:8000/api/v1/prediccion/demanda",
    json={
        "año": 2025,
        "mes": 6,
        "region": "LIMA",
        "grupo_edad": "18-29",
        "sexo": "FEMENINO",
        "nivel_ipress": "II",
        "servicio_categoria": "CONSULTA EXTERNA",
        "plan_seguro": "SIS GRATUITO"
    }
)
resultado = response.json()
print(f"Atenciones esperadas: {resultado['prediccion_redondeada']}")
```

### 2. Análisis Comparativo
Comparar demanda entre múltiples regiones:
```python
import requests

predicciones = {
    "predicciones": [
        {"año": 2025, "mes": 6, "region": "LIMA", ...},
        {"año": 2025, "mes": 6, "region": "CUSCO", ...},
        {"año": 2025, "mes": 6, "region": "AREQUIPA", ...}
    ],
    "modelo": "random_forest"
}

response = requests.post(
    "http://localhost:8000/api/v1/prediccion/batch",
    json=predicciones
)
```

### 3. Proyección Anual
Predecir demanda para todos los meses del año:
```python
import requests

meses = list(range(1, 13))
predicciones = {
    "predicciones": [
        {
            "año": 2025,
            "mes": mes,
            "region": "LIMA",
            "grupo_edad": "18-29",
            "sexo": "FEMENINO",
            "nivel_ipress": "II",
            "servicio_categoria": "CONSULTA EXTERNA",
            "plan_seguro": "SIS GRATUITO"
        }
        for mes in meses
    ],
    "modelo": "random_forest"
}

response = requests.post(
    "http://localhost:8000/api/v1/prediccion/batch",
    json=predicciones
)
```

---

## 🔍 Features Utilizadas

### Temporales
- año, mes, trimestre, semestre
- temporada_alta (indicador binario)

### Demográficas
- sexo (MASCULINO/FEMENINO)
- categoria_edad (INFANCIA, ADOLESCENCIA, ADULTOS, ADULTOS_MAYORES)

### Geográficas
- region (departamento)

### Contextuales
- nivel_ipress (I, II, III)
- servicio_categoria
- plan_seguro

**Procesamiento:**
- Label Encoding para variables categóricas
- StandardScaler para variables numéricas

---

## 🐛 Solución de Problemas

### Error: "Modelo no encontrado"
```bash
# Entrenar los modelos
python train_models.py
```

### Error: "No hay datos en la base de datos"
Verifica conexión y datos:
```python
from app.core.database import SessionLocal
from app.models.atencion import Atencion

db = SessionLocal()
count = db.query(Atencion).count()
print(f"Total atenciones: {count}")
```

### Predicciones inconsistentes
```bash
# Limpiar cache y volver a cargar
curl -X POST "http://localhost:8000/api/v1/prediccion/modelos/limpiar-cache"
```

### Re-entrenar modelos
Si los datos han cambiado significativamente:
```bash
python train_models.py --model all
```

---

## 📁 Estructura de Archivos

```
app/ml/
├── __init__.py
├── predictor.py              # Clase principal SISPredictor
├── data_processor.py         # (Referencia, no se usa)
├── models/                   # Modelos entrenados (.pkl)
│   ├── .gitignore
│   ├── .gitkeep
│   ├── sis_predictor_linear.pkl
│   ├── sis_predictor_random_forest.pkl
│   └── sis_predictor_gradient_boosting.pkl
└── training/
    ├── __init__.py
    └── train_model.py        # Script de entrenamiento
```

---

## 📚 Documentación Adicional

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **ML README**: `app/ml/README.md`

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
