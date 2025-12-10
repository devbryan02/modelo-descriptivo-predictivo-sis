"""
Procesador de datos para Machine Learning del SIS
Basado en REQUERIMENTS.MD - Sección "Procesamiento de Datos"

NOTA: Este módulo ya no se usa directamente.
La funcionalidad de procesamiento de datos está integrada en predictor.py
que extrae datos directamente desde PostgreSQL usando SQLAlchemy.

Este archivo se mantiene como referencia de las técnicas de procesamiento.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Procesador de datos para preparar dataset del SIS para Machine Learning
    """
    
    def __init__(self):
        """Inicializa encoders y scalers"""
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.one_hot_encoders = {}
        self.feature_names = []
        self.is_fitted = False
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpieza y transformación de datos
        
        Implementa:
        - Eliminación de duplicados
        - Imputación de valores nulos
        - Estandarización de formatos
        - Validación de integridad
        - Filtrado de inconsistencias
        
        Args:
            df: DataFrame con datos crudos
            
        Returns:
            DataFrame limpio
        """
        logger.info("Iniciando limpieza de datos...")
        df_clean = df.copy()
        
        # 1. Eliminar duplicados
        before_count = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        logger.info(f"Duplicados eliminados: {before_count - len(df_clean)}")
        
        # 2. Validar rangos de años (2020-2025)
        df_clean = df_clean[
            (df_clean['año'] >= 2020) & 
            (df_clean['año'] <= 2025)
        ]
        
        # 3. Validar meses (1-12)
        df_clean = df_clean[
            (df_clean['mes'] >= 1) & 
            (df_clean['mes'] <= 12)
        ]
        
        # 4. Estandarizar valores de sexo
        df_clean['sexo'] = df_clean['sexo'].str.upper().str.strip()
        df_clean = df_clean[df_clean['sexo'].isin(['MASCULINO', 'FEMENINO', 'M', 'F'])]
        
        # Mapear M/F a MASCULINO/FEMENINO
        df_clean['sexo'] = df_clean['sexo'].map({
            'M': 'MASCULINO',
            'F': 'FEMENINO',
            'MASCULINO': 'MASCULINO',
            'FEMENINO': 'FEMENINO'
        })
        
        # 5. Normalizar texto (región, provincia, distrito)
        text_columns = ['region', 'provincia', 'distrito']
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].str.upper().str.strip()
        
        # 6. Imputación de valores nulos
        # Categóricas: usar la moda
        categorical_cols = ['sexo', 'grupo_edad', 'region', 'provincia', 'distrito']
        for col in categorical_cols:
            if col in df_clean.columns and df_clean[col].isnull().any():
                mode_value = df_clean[col].mode()[0] if not df_clean[col].mode().empty else 'DESCONOCIDO'
                df_clean[col].fillna(mode_value, inplace=True)
                logger.info(f"Valores nulos en '{col}' imputados con: {mode_value}")
        
        # Numéricas: usar la mediana
        numeric_cols = ['cantidad_atenciones']
        for col in numeric_cols:
            if col in df_clean.columns and df_clean[col].isnull().any():
                median_value = df_clean[col].median()
                df_clean[col].fillna(median_value, inplace=True)
                logger.info(f"Valores nulos en '{col}' imputados con mediana: {median_value}")
        
        # 7. Validar cantidad_atenciones > 0
        df_clean = df_clean[df_clean['cantidad_atenciones'] > 0]
        
        logger.info(f"Limpieza completada. Registros finales: {len(df_clean)}")
        return df_clean
    
    def feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Creación de features adicionales
        
        Implementa:
        - Variables temporales (trimestre, semestre)
        - Agregaciones (total por paciente, promedio mensual)
        - Clasificación de grupos etarios
        
        Args:
            df: DataFrame limpio
            
        Returns:
            DataFrame con features adicionales
        """
        logger.info("Aplicando feature engineering...")
        df_fe = df.copy()
        
        # 1. Variables temporales
        df_fe['trimestre'] = df_fe['mes'].apply(lambda x: (x - 1) // 3 + 1)
        df_fe['semestre'] = df_fe['mes'].apply(lambda x: 1 if x <= 6 else 2)
        
        # 2. Clasificar grupos etarios según REQUERIMENTS.MD
        # 0-11: Infancia, 12-17: Adolescencia, 18-59: Adultos, 60+: Adultos Mayores
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
        
        if 'grupo_edad' in df_fe.columns:
            df_fe['categoria_edad'] = df_fe['grupo_edad'].map(edad_mapping)
            df_fe['categoria_edad'].fillna('ADULTOS', inplace=True)
        
        # 3. Indicador de temporada (alta/baja demanda típica)
        # Asumimos que meses de verano e invierno tienen mayor demanda
        meses_alta_demanda = [1, 2, 6, 7, 8, 12]
        df_fe['temporada_alta'] = df_fe['mes'].isin(meses_alta_demanda).astype(int)
        
        logger.info(f"Feature engineering completado. Features creados: trimestre, semestre, categoria_edad, temporada_alta")
        return df_fe
    
    def encode_features(
        self, 
        df: pd.DataFrame, 
        fit: bool = True
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Codificación de features para ML
        
        Implementa:
        - One-Hot Encoding: sexo, region, categoria_edad
        - Label Encoding: nivel_ipress (si existe)
        - StandardScaler: variables numéricas
        
        Args:
            df: DataFrame con features
            fit: Si es True, ajusta los encoders. Si es False, solo transforma
            
        Returns:
            Tupla (matriz de features codificadas, nombres de features)
        """
        logger.info(f"Codificando features (fit={fit})...")
        df_encoded = df.copy()
        
        # Columnas a codificar con One-Hot
        one_hot_cols = ['sexo', 'region']
        if 'categoria_edad' in df_encoded.columns:
            one_hot_cols.append('categoria_edad')
        
        # Columnas numéricas para escalar
        numeric_cols = ['año', 'mes', 'cantidad_atenciones', 'trimestre', 'semestre', 'temporada_alta']
        numeric_cols = [col for col in numeric_cols if col in df_encoded.columns]
        
        # One-Hot Encoding
        encoded_dfs = []
        for col in one_hot_cols:
            if col in df_encoded.columns:
                if fit:
                    # Crear dummies y guardar categorías
                    dummies = pd.get_dummies(df_encoded[col], prefix=col, drop_first=False)
                    self.one_hot_encoders[col] = list(dummies.columns)
                    encoded_dfs.append(dummies)
                else:
                    # Usar categorías guardadas
                    dummies = pd.get_dummies(df_encoded[col], prefix=col, drop_first=False)
                    # Asegurar que tengamos todas las columnas esperadas
                    for expected_col in self.one_hot_encoders[col]:
                        if expected_col not in dummies.columns:
                            dummies[expected_col] = 0
                    dummies = dummies[self.one_hot_encoders[col]]
                    encoded_dfs.append(dummies)
        
        # Variables numéricas
        numeric_df = df_encoded[numeric_cols].copy()
        
        if fit:
            numeric_scaled = self.scaler.fit_transform(numeric_df)
        else:
            numeric_scaled = self.scaler.transform(numeric_df)
        
        numeric_scaled_df = pd.DataFrame(
            numeric_scaled, 
            columns=numeric_cols,
            index=df_encoded.index
        )
        encoded_dfs.append(numeric_scaled_df)
        
        # Combinar todas las features
        X = pd.concat(encoded_dfs, axis=1)
        
        if fit:
            self.feature_names = list(X.columns)
            self.is_fitted = True
        
        logger.info(f"Codificación completada. Total features: {len(self.feature_names)}")
        return X.values, self.feature_names
    
    def prepare_for_training(
        self, 
        df: pd.DataFrame,
        target_col: str = 'cantidad_atenciones',
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, List[str]]:
        """
        Pipeline completo de preparación de datos para entrenamiento
        
        Args:
            df: DataFrame crudo
            target_col: Columna objetivo a predecir
            test_size: Proporción del conjunto de test
            random_state: Semilla para reproducibilidad
            
        Returns:
            Tupla (X_train, X_test, y_train, y_test, feature_names)
        """
        logger.info("Iniciando pipeline de preparación de datos...")
        
        # 1. Limpieza
        df_clean = self.clean_data(df)
        
        # 2. Feature Engineering
        df_fe = self.feature_engineering(df_clean)
        
        # 3. Separar target
        y = df_fe[target_col].values
        df_features = df_fe.drop(columns=[target_col])
        
        # 4. Train-test split
        X_train_df, X_test_df, y_train, y_test = train_test_split(
            df_features, y, test_size=test_size, random_state=random_state
        )
        
        # 5. Codificación (fit solo en train)
        X_train, feature_names = self.encode_features(X_train_df, fit=True)
        X_test, _ = self.encode_features(X_test_df, fit=False)
        
        logger.info(f"Preparación completada. Train: {X_train.shape}, Test: {X_test.shape}")
        return X_train, X_test, y_train, y_test, feature_names
    
    def transform_new_data(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transforma nuevos datos usando encoders ya ajustados
        
        Args:
            df: DataFrame con nuevos datos
            
        Returns:
            Matriz de features codificadas
        """
        if not self.is_fitted:
            raise ValueError("El DataProcessor no ha sido ajustado. Ejecute prepare_for_training primero.")
        
        logger.info("Transformando nuevos datos...")
        
        # Limpieza y feature engineering
        df_clean = self.clean_data(df)
        df_fe = self.feature_engineering(df_clean)
        
        # Codificación (sin fit)
        X, _ = self.encode_features(df_fe, fit=False)
        
        return X
