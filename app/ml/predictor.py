"""
Predictor de demanda de atenciones del SIS usando Machine Learning
Basado en REQUERIMENTS.MD - Modelos de ML para predecir demanda futura

Extrae datos desde PostgreSQL (tablas normalizadas) y entrena modelos

MEJORAS:
- Temporal features: lags y rolling means por grupos clave
- Target encoding para variables categóricas principales
- Modelo Poisson para datos de conteo (cantidad_atenciones)
- Scaling selectivo (solo para regresión lineal)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import joblib
import logging
from pathlib import Path

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Poisson regression for count data
import statsmodels.api as sm
from statsmodels.genmod.families import Poisson

from app.models.atencion import Atencion
from app.models.ipress import IPRESS
from app.models.servicio import Servicio
from app.models.plan_seguro import PlanSeguro

logger = logging.getLogger(__name__)


class SISPredictor:
    """
    Predictor de demanda de atenciones médicas del SIS
    
    Implementa:
    - Extracción de datos desde BD PostgreSQL
    - Preparación de features desde tablas normalizadas con lags temporales
    - Entrenamiento de modelos: Linear Regression, Random Forest, Gradient Boosting, Poisson
    - Predicción de cantidad de atenciones futuras
    - Métricas: R², RMSE, MAE
    
    MODELOS SOPORTADOS:
    - 'linear': Regresión lineal (baseline, con scaling)
    - 'random_forest': Random Forest (sin scaling)
    - 'gradient_boosting': Gradient Boosting (sin scaling)
    - 'poisson': GLM Poisson (ideal para datos de conteo no-negativos)
    """
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Inicializa el predictor
        
        Args:
            model_type: Tipo de modelo ('linear', 'random_forest', 'gradient_boosting', 'poisson')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.encoders = {}  # Para variables categóricas no target-encoded
        self.target_encodings = {}  # Para target encoding
        self.feature_columns = []
        self.is_trained = False
        self.metrics = {}
        
        # Directorio para guardar modelos
        self.models_dir = Path(__file__).parent / "models"
        self.models_dir.mkdir(exist_ok=True)
    
    def extract_data_from_db(
        self, 
        db: Session,
        limit: Optional[int] = None,
        sample_size: Optional[int] = None,
        random_state: int = 42
    ) -> pd.DataFrame:
        """
        Extrae datos de la BD PostgreSQL con joins a tablas relacionadas
        OPTIMIZADO para datasets grandes (5M+ registros)
        
        Args:
            db: Sesión de SQLAlchemy
            limit: Límite de registros (None para todos)
            sample_size: Muestra aleatoria estratificada (recomendado: 500K-1M para 5M registros)
            random_state: Semilla para reproducibilidad del sampling
            
        Returns:
            DataFrame con datos listos para ML
        """
        logger.info("Extrayendo datos desde PostgreSQL...")
        
        # Obtener total de registros
        total_count = db.query(func.count(Atencion.id)).scalar()
        logger.info(f"Total de registros en BD: {total_count:,}")
        
        # Query con joins a tablas relacionadas
        query = db.query(
            Atencion.año,
            Atencion.mes,
            Atencion.region,
            Atencion.provincia,
            Atencion.distrito,
            Atencion.sexo,
            Atencion.grupo_edad,
            Atencion.cantidad_atenciones,
            IPRESS.nivel.label('nivel_ipress'),
            IPRESS.region.label('region_ipress'),
            Servicio.nombre.label('servicio_nombre'),
            Servicio.categoria.label('servicio_categoria'),
            PlanSeguro.nombre.label('plan_seguro')
        ).join(
            IPRESS, Atencion.ipress_id == IPRESS.id
        ).join(
            Servicio, Atencion.servicio_id == Servicio.id
        ).join(
            PlanSeguro, Atencion.plan_seguro_id == PlanSeguro.id
        )
        
        # Sampling estratificado para datasets grandes
        if sample_size and total_count > sample_size:
            logger.info(f"Aplicando sampling: {sample_size:,} de {total_count:,} registros ({sample_size/total_count*100:.1f}%)")
            # PostgreSQL random sampling optimizado
            query = query.order_by(func.random()).limit(sample_size)
        elif limit:
            query = query.limit(limit)
        
        # Convertir a DataFrame en chunks para evitar OOM
        logger.info("Cargando datos en memoria...")
        chunk_size = 100000
        results = query.yield_per(chunk_size)
        
        data_chunks = []
        total_loaded = 0
        
        for row in results:
            data_chunks.append({
                'año': row.año,
                'mes': row.mes,
                'region': row.region,
                'provincia': row.provincia,
                'distrito': row.distrito,
                'sexo': row.sexo,
                'grupo_edad': row.grupo_edad,
                'nivel_ipress': row.nivel_ipress,
                'servicio_categoria': row.servicio_categoria or 'GENERAL',
                'plan_seguro': row.plan_seguro,
                'cantidad_atenciones': row.cantidad_atenciones
            })
            
            total_loaded += 1
            if total_loaded % 50000 == 0:
                logger.info(f"  Cargados: {total_loaded:,} registros...")
        
        df = pd.DataFrame(data_chunks)
        logger.info(f"[OK] Datos extraídos: {len(df):,} registros")
        
        return df
    
    def _add_temporal_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Añade features temporales: lags y rolling means
        
        IMPORTANT: Los lags se calculan por grupos clave para capturar patrones específicos
        de demanda según región, demografía y tipo de servicio.
        
        Args:
            df: DataFrame con datos ordenados por fecha
            fit: Si es True, calcula lags (training). Si False, usa últimos valores conocidos.
            
        Returns:
            DataFrame con features temporales agregadas
        """
        logger.info("Añadiendo features temporales (lags y rolling means)...")
        
        df = df.copy()
        
        # Asegurar orden temporal
        df = df.sort_values(['año', 'mes'])
        
        # Crear fecha para ordenamiento
        df['fecha'] = pd.to_datetime(df['año'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2) + '-01')
        
        # Grupos clave para calcular lags
        group_cols = ['region', 'sexo', 'grupo_edad', 'servicio_categoria', 'plan_seguro']
        
        if fit:
            # Calcular lags por grupos
            df['lag_1'] = df.groupby(group_cols)['cantidad_atenciones'].shift(1)
            df['rolling_mean_3'] = df.groupby(group_cols)['cantidad_atenciones'].transform(
                lambda x: x.rolling(window=3, min_periods=1).mean().shift(1)
            )
            df['rolling_mean_6'] = df.groupby(group_cols)['cantidad_atenciones'].transform(
                lambda x: x.rolling(window=6, min_periods=1).mean().shift(1)
            )
            
            # Manejar NaNs: rellenar con 0 (interpretación: sin histórico previo)
            df['lag_1'] = df['lag_1'].fillna(0)
            df['rolling_mean_3'] = df['rolling_mean_3'].fillna(0)
            df['rolling_mean_6'] = df['rolling_mean_6'].fillna(0)
            
            logger.info(f"  Lags creados. NaNs iniciales rellenados con 0.")
        else:
            # En predicción, usar valores por defecto (últimos conocidos o 0)
            # Esto se manejará en el método predict()
            df['lag_1'] = 0
            df['rolling_mean_3'] = 0
            df['rolling_mean_6'] = 0
        
        return df
    
    def _apply_target_encoding(self, df: pd.DataFrame, target_col: str, fit: bool = True) -> pd.DataFrame:
        """
        Aplica Target Encoding a variables categóricas principales
        
        Target Encoding: Reemplaza cada categoría con la media del target para esa categoría.
        Es útil para variables de alta cardinalidad y captura relación directa con el target.
        
        Args:
            df: DataFrame con variables categóricas
            target_col: Nombre de la columna target
            fit: Si es True, calcula encodings. Si False, usa los existentes.
            
        Returns:
            DataFrame con variables target-encoded
        """
        logger.info(f"Aplicando Target Encoding (fit={fit})...")
        
        df = df.copy()
        
        # Variables a target-encode (alta cardinalidad, relación directa con demanda)
        target_encode_cols = ['region', 'servicio_categoria', 'plan_seguro']
        
        for col in target_encode_cols:
            if col not in df.columns:
                continue
                
            if fit:
                # Calcular media del target por categoría
                encoding_map = df.groupby(col)[target_col].mean().to_dict()
                self.target_encodings[col] = encoding_map
                
                # Aplicar encoding
                df[f'{col}_encoded'] = df[col].map(encoding_map)
                
                # Manejar valores faltantes con la media global
                global_mean = df[target_col].mean()
                df[f'{col}_encoded'] = df[f'{col}_encoded'].fillna(global_mean)
                
                logger.info(f"  Target encoding para '{col}': {len(encoding_map)} categorías")
            else:
                # Usar encoding existente
                encoding_map = self.target_encodings.get(col, {})
                global_mean = df[target_col].mean() if target_col in df.columns else 0
                
                df[f'{col}_encoded'] = df[col].map(encoding_map).fillna(global_mean)
        
        return df
    
    def prepare_features(
        self, 
        df: pd.DataFrame,
        fit: bool = True
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara features desde los datos extraídos de la BD
        
        MEJORAS:
        - Temporal features: lag_1, rolling_mean_3, rolling_mean_6
        - Target encoding para region, servicio_categoria, plan_seguro
        - Scaling solo para regresión lineal
        
        Args:
            df: DataFrame con datos crudos
            fit: Si es True, ajusta encoders y scaler
            
        Returns:
            Tupla (X, y) - features y target
        """
        logger.info(f"Preparando features (fit={fit})...")
        df_prep = df.copy()
        
        # 1. Features temporales básicas
        df_prep['trimestre'] = df_prep['mes'].apply(lambda x: (x - 1) // 3 + 1)
        df_prep['semestre'] = df_prep['mes'].apply(lambda x: 1 if x <= 6 else 2)
        
        # Temporada alta (meses con típicamente mayor demanda)
        meses_alta = [1, 2, 6, 7, 8, 12]
        df_prep['temporada_alta'] = df_prep['mes'].isin(meses_alta).astype(int)
        
        # 2. Temporal features: lags y rolling means
        df_prep = self._add_temporal_features(df_prep, fit=fit)
        
        # 3. Clasificación de edad
        edad_mapping = {
            '00-04': 'INFANCIA',
            '05-11': 'INFANCIA',
            '12-17': 'ADOLESCENCIA',
            '18-29': 'ADULTOS',
            '30-59': 'ADULTOS',
            '60+': 'ADULTOS_MAYORES',
            '60-69': 'ADULTOS_MAYORES',
            '70+': 'ADULTOS_MAYORES'
        }
        df_prep['categoria_edad'] = df_prep['grupo_edad'].map(edad_mapping).fillna('ADULTOS')
        
        # 4. Target Encoding para variables principales
        df_prep = self._apply_target_encoding(df_prep, 'cantidad_atenciones', fit=fit)
        
        # 5. LabelEncoding para otras variables categóricas
        other_categorical_cols = ['sexo', 'nivel_ipress', 'categoria_edad']
        
        for col in other_categorical_cols:
            if col in df_prep.columns:
                if fit:
                    # Crear y ajustar encoder
                    le = LabelEncoder()
                    df_prep[f'{col}_encoded'] = le.fit_transform(df_prep[col].astype(str))
                    self.encoders[col] = le
                else:
                    # Usar encoder existente
                    le = self.encoders[col]
                    # Manejar categorías nuevas
                    df_prep[f'{col}_encoded'] = df_prep[col].astype(str).apply(
                        lambda x: le.transform([x])[0] if x in le.classes_ else -1
                    )
        
        # 6. Features numéricas
        numeric_features = [
            'año', 'mes', 'trimestre', 'semestre', 'temporada_alta',
            'lag_1', 'rolling_mean_3', 'rolling_mean_6'
        ]
        
        # Features codificadas (target-encoded + label-encoded)
        encoded_features = []
        for col in ['region', 'servicio_categoria', 'plan_seguro', 'sexo', 'nivel_ipress', 'categoria_edad']:
            if f'{col}_encoded' in df_prep.columns:
                encoded_features.append(f'{col}_encoded')
        
        # Combinar todas las features
        all_features = numeric_features + encoded_features
        X = df_prep[all_features].values
        
        # 7. Escalar features SOLO para regresión lineal (NO para Poisson)
        if fit:
            self.feature_columns = all_features
            if self.model_type == 'linear':
                logger.info(f"  Aplicando StandardScaler para {self.model_type}")
                X = self.scaler.fit_transform(X)
            else:
                logger.info(f"  Sin scaling para {self.model_type}")
        else:
            if self.model_type == 'linear':
                X = self.scaler.transform(X)
        
        # 8. Target
        y = df_prep['cantidad_atenciones'].values
        
        logger.info(f"Features preparadas: {X.shape}, Target: {y.shape}")
        logger.info(f"  Features: {len(numeric_features)} numéricas + {len(encoded_features)} codificadas")
        return X, y
    
    def train(
        self, 
        db: Session,
        test_size: float = 0.2,
        random_state: int = 42,
        sample_size: Optional[int] = None,
        **model_params
    ) -> Dict:
        """
        Entrena el modelo con datos de la BD
        OPTIMIZADO para datasets grandes (5M+ registros)
        
        Args:
            db: Sesión de SQLAlchemy
            test_size: Proporción del conjunto de test
            random_state: Semilla para reproducibilidad
            sample_size: Muestra de datos (None=automático basado en total, recomendado: 500K-1M)
            **model_params: Parámetros adicionales para el modelo
            
        Returns:
            Diccionario con métricas de evaluación
        """
        logger.info(f"Iniciando entrenamiento del modelo {self.model_type.upper()}...")
        
        # 1. Determinar sample_size óptimo si no se especifica
        if sample_size is None:
            total_records = db.query(func.count(Atencion.id)).scalar()
            if total_records > 2_000_000:
                sample_size = 800_000  # 800K para datasets grandes
                logger.info(f"Dataset grande detectado ({total_records:,} registros)")
                logger.info(f"   Usando sampling optimizado: {sample_size:,} registros")
            elif total_records > 1_000_000:
                sample_size = 500_000
                logger.info(f"Usando {sample_size:,} registros de {total_records:,}")
        
        # 2. Extraer datos con sampling
        df = self.extract_data_from_db(db, sample_size=sample_size, random_state=random_state)
        
        if len(df) == 0:
            raise ValueError("No hay datos en la base de datos para entrenar")
        
        logger.info(f"Memoria usada por DataFrame: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # 3. Preparar features
        logger.info("Preparando features...")
        X, y = self.prepare_features(df, fit=True)
        
        # Liberar memoria del DataFrame original
        del df
        import gc
        gc.collect()
        
        # 4. Split train/test
        logger.info(f"Dividiendo datos (train: {(1-test_size)*100:.0f}%, test: {test_size*100:.0f}%)...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        logger.info(f"   Train: {X_train.shape[0]:,} registros")
        logger.info(f"   Test:  {X_test.shape[0]:,} registros")
        
        # 5. Crear modelo según tipo con parámetros optimizados para datasets grandes
        if self.model_type == "linear":
            logger.info("Modelo: Linear Regression (rápido, baseline)")
            self.model = LinearRegression(**model_params)
        elif self.model_type == "poisson":
            # Modelo Poisson GLM para datos de conteo
            # IMPORTANTE: cantidad_atenciones es un conteo (no-negativo, entero, sesgado)
            # Poisson es apropiado porque:
            # - Modela eventos de conteo (número de atenciones)
            # - Garantiza predicciones no-negativas
            # - Captura la varianza proporcional a la media (común en conteos)
            logger.info("Modelo: Poisson GLM (ideal para datos de conteo no-negativos)")
            logger.info("   Razón: cantidad_atenciones es un conteo con sesgo y varianza proporcional")
            # El modelo se creará durante fit() con statsmodels
            self.model = "poisson"  # Placeholder, se creará en fit
        elif self.model_type == "random_forest":
            # Parámetros optimizados para datasets grandes
            default_params = {
                'n_estimators': 50,        # Reducido de 100 a 50 para velocidad
                'max_depth': 12,           # Más profundidad para captar patrones
                'min_samples_split': 20,   # Evitar overfitting
                'min_samples_leaf': 10,
                'max_features': 'sqrt',    # Reducir features por árbol
                'random_state': random_state,
                'n_jobs': -1,              # Usar todos los cores
                'verbose': 1               # Mostrar progreso
            }
            default_params.update(model_params)
            logger.info(f"Modelo: Random Forest ({default_params['n_estimators']} árboles, depth={default_params['max_depth']})")
            self.model = RandomForestRegressor(**default_params)
        elif self.model_type == "gradient_boosting":
            # Parámetros optimizados
            default_params = {
                'n_estimators': 100,       # Mantener para accuracy
                'max_depth': 6,            # Profundidad moderada
                'learning_rate': 0.1,
                'subsample': 0.8,          # Sampling para reducir overfitting
                'min_samples_split': 20,
                'min_samples_leaf': 10,
                'random_state': random_state,
                'verbose': 1
            }
            default_params.update(model_params)
            logger.info(f"Modelo: Gradient Boosting ({default_params['n_estimators']} estimators, lr={default_params['learning_rate']})")
            self.model = GradientBoostingRegressor(**default_params)
        else:
            raise ValueError(f"Tipo de modelo no soportado: {self.model_type}")
        
        # 6. Entrenar
        logger.info(f"\nEntrenando modelo {self.model_type.upper()}...")
        import time
        start_time = time.time()
        
        if self.model_type == "poisson":
            # Entrenar modelo Poisson GLM con statsmodels
            # Añadir constante para intercept
            X_train_const = sm.add_constant(X_train, has_constant='add')
            
            # Ajustar GLM con familia Poisson
            self.model = sm.GLM(y_train, X_train_const, family=Poisson())
            self.model = self.model.fit()
            
            logger.info(f"   Convergencia: {self.model.converged}")
            logger.info(f"   Iteraciones: {self.model.fit_history['iteration']}")
        else:
            # Entrenar modelos sklearn
            self.model.fit(X_train, y_train)
        
        training_time = time.time() - start_time
        logger.info(f"[OK] Entrenamiento completado en {training_time:.2f} segundos ({training_time/60:.2f} minutos)")
        
        # 7. Evaluar
        logger.info("Evaluando modelo...")
        if self.model_type == "poisson":
            # Predicción con Poisson
            X_train_const = sm.add_constant(X_train, has_constant='add')
            X_test_const = sm.add_constant(X_test, has_constant='add')
            y_pred_train = self.model.predict(X_train_const)
            y_pred_test = self.model.predict(X_test_const)
        else:
            y_pred_train = self.model.predict(X_train)
            y_pred_test = self.model.predict(X_test)
        
        # Métricas según REQUERIMENTS.MD
        train_r2 = r2_score(y_train, y_pred_train)
        train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
        train_mae = mean_absolute_error(y_train, y_pred_train)
        
        test_r2 = r2_score(y_test, y_pred_test)
        test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        test_mae = mean_absolute_error(y_test, y_pred_test)
        
        self.metrics = {
            'train': {
                'r2': train_r2,
                'rmse': train_rmse,
                'mae': train_mae
            },
            'test': {
                'r2': test_r2,
                'rmse': test_rmse,
                'mae': test_mae
            },
            'training_time_seconds': training_time,
            'n_samples': len(X_train) + len(X_test)
        }
        
        # Add Poisson-specific metrics
        if self.model_type == "poisson":
            self.metrics['aic'] = self.model.aic
            # Pseudo R² (McFadden's)
            # R² = 1 - (log-likelihood of fitted model / log-likelihood of null model)
            if hasattr(self.model, 'llf') and hasattr(self.model, 'llnull'):
                self.metrics['pseudo_r2'] = 1 - (self.model.llf / self.model.llnull)
            logger.info(f"   AIC: {self.metrics['aic']:.2f}")
            if 'pseudo_r2' in self.metrics:
                logger.info(f"   Pseudo-R² (McFadden): {self.metrics['pseudo_r2']:.4f}")
        
        # 8. Validación cruzada (solo para modelos sklearn pequeños/medianos)
        if self.model_type != "poisson" and len(X_train) < 500_000:
            logger.info("Ejecutando validación cruzada (5-fold)...")
            cv_scores = cross_val_score(
                self.model, X_train, y_train, 
                cv=5, scoring='r2', n_jobs=-1
            )
            self.metrics['cv_r2_mean'] = cv_scores.mean()
            self.metrics['cv_r2_std'] = cv_scores.std()
            logger.info(f"   CV R² = {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        else:
            if self.model_type == "poisson":
                logger.info("Validación cruzada omitida para Poisson GLM")
            else:
                logger.info("Validación cruzada omitida (dataset muy grande)")
            self.metrics['cv_r2_mean'] = None
            self.metrics['cv_r2_std'] = None
        
        self.is_trained = True
        
        # Mostrar resumen de métricas
        logger.info("\n" + "="*60)
        logger.info(f"RESULTADOS DEL MODELO {self.model_type.upper()}")
        logger.info("="*60)
        logger.info(f"  TRAIN:  R²={train_r2:.4f}  RMSE={train_rmse:.2f}  MAE={train_mae:.2f}")
        logger.info(f"  TEST:   R²={test_r2:.4f}  RMSE={test_rmse:.2f}  MAE={test_mae:.2f}")
        logger.info(f"  Tiempo: {training_time:.2f}s ({training_time/60:.2f} min)")
        logger.info(f"  Muestras: {len(X_train) + len(X_test):,}")
        logger.info("="*60 + "\n")
        
        return self.metrics
    
    def predict(
        self,
        año: int,
        mes: int,
        region: str,
        sexo: str,
        grupo_edad: str,
        nivel_ipress: str,
        servicio_categoria: str,
        plan_seguro: str,
        lag_1: float = 0.0,
        rolling_mean_3: float = 0.0,
        rolling_mean_6: float = 0.0
    ) -> Dict:
        """
        Realiza predicción de cantidad de atenciones
        
        RETORNA:
        - expected_value: Predicción cruda del modelo
        - rounded_prediction: Predicción redondeada al entero más cercano
        - demand_level: Nivel de demanda (LOW < 5, MEDIUM 5-15, HIGH > 15)
        
        Args:
            año, mes, region, sexo, grupo_edad, nivel_ipress, servicio_categoria, plan_seguro:
                Parámetros demográficos y contextuales
            lag_1, rolling_mean_3, rolling_mean_6:
                Features temporales (opcional, usar valores históricos si están disponibles)
            
        Returns:
            Dict con expected_value, rounded_prediction, demand_level
        """
        if not self.is_trained:
            raise ValueError("El modelo no ha sido entrenado. Ejecute train() primero.")
        
        # Crear DataFrame con los datos de entrada
        input_df = pd.DataFrame([{
            'año': año,
            'mes': mes,
            'region': region,
            'provincia': '',
            'distrito': '',
            'sexo': sexo,
            'grupo_edad': grupo_edad,
            'nivel_ipress': nivel_ipress,
            'servicio_categoria': servicio_categoria,
            'plan_seguro': plan_seguro,
            'cantidad_atenciones': 0  # No se usa, solo para compatibilidad
        }])
        
        # Preparar features
        X, _ = self.prepare_features(input_df, fit=False)
        
        # Predecir según tipo de modelo
        if self.model_type == "poisson":
            # Predicción con Poisson GLM
            X_const = sm.add_constant(X, has_constant='add')
            prediction = self.model.predict(X_const)[0]
        else:
            # Predicción con sklearn
            prediction = self.model.predict(X)[0]
        
        # Asegurar predicción no negativa
        expected_value = max(0, prediction)
        rounded_prediction = int(round(expected_value))
        
        # Clasificar nivel de demanda
        if rounded_prediction < 5:
            demand_level = "LOW"
        elif rounded_prediction <= 15:
            demand_level = "MEDIUM"
        else:
            demand_level = "HIGH"
        
        return {
            "expected_value": float(expected_value),
            "rounded_prediction": rounded_prediction,
            "demand_level": demand_level
        }
    
    def save_model(self, filename: Optional[str] = None) -> Path:
        """
        Guarda el modelo entrenado con backward compatibility
        
        Args:
            filename: Nombre del archivo (opcional)
            
        Returns:
            Path del archivo guardado
        """
        if not self.is_trained:
            raise ValueError("El modelo no ha sido entrenado")
        
        if filename is None:
            filename = f"sis_predictor_{self.model_type}.pkl"
        
        filepath = self.models_dir / filename
        
        # Guardar modelo completo con metadatos (incluyendo target_encodings)
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'encoders': self.encoders,
            'target_encodings': self.target_encodings,  # NUEVO: target encoding maps
            'feature_columns': self.feature_columns,
            'model_type': self.model_type,
            'metrics': self.metrics,
            'version': '2.0'  # Versión con temporal features y target encoding
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Modelo guardado en: {filepath}")
        logger.info(f"  Versión: {model_data['version']} (con temporal features y target encoding)")
        
        return filepath
    
    def load_model(self, filename: Optional[str] = None) -> Dict:
        """
        Carga un modelo previamente entrenado con backward compatibility
        
        Args:
            filename: Nombre del archivo (opcional)
            
        Returns:
            Métricas del modelo cargado
        """
        if filename is None:
            filename = f"sis_predictor_{self.model_type}.pkl"
        
        filepath = self.models_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Modelo no encontrado: {filepath}")
        
        # Cargar modelo y metadatos
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.encoders = model_data['encoders']
        self.feature_columns = model_data['feature_columns']
        self.model_type = model_data['model_type']
        self.metrics = model_data.get('metrics', {})
        
        # Backward compatibility: modelos antiguos sin target_encodings
        self.target_encodings = model_data.get('target_encodings', {})
        
        version = model_data.get('version', '1.0')
        logger.info(f"Modelo cargado desde: {filepath}")
        logger.info(f"  Versión: {version}")
        
        if version == '1.0':
            logger.warning("[WARNING] Modelo antiguo (v1.0) sin temporal features. Considere re-entrenar.")
        
        self.is_trained = True
        
        return self.metrics
