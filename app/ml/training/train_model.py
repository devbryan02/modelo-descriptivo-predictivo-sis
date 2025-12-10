"""
Script de entrenamiento de modelos de predicción del SIS
Basado en REQUERIMENTS.MD - Pipeline ML

Conecta a PostgreSQL, extrae datos, entrena modelos y los guarda
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

import logging
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.ml.predictor import SISPredictor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def train_all_models():
    """
    Entrena todos los modelos: Linear Regression, Random Forest, Gradient Boosting, Poisson
    """
    logger.info("=" * 80)
    logger.info("INICIANDO ENTRENAMIENTO DE MODELOS DE PREDICCIÓN DEL SIS")
    logger.info("=" * 80)
    
    # Crear sesión de BD
    db: Session = SessionLocal()
    
    try:
        # Modelos a entrenar según REQUERIMENTS.MD
        models_config = [
            {
                'type': 'linear',
                'name': 'Regresión Lineal (Baseline)',
                'params': {},
                'recommended': False
            },
            {
                'type': 'random_forest',
                'name': 'Random Forest Regressor',
                'params': {
                    'n_estimators': 150,
                    'max_depth': 12,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2
                },
                'recommended': False
            },
            {
                'type': 'gradient_boosting',
                'name': 'Gradient Boosting Regressor',
                'params': {
                    'n_estimators': 150,
                    'max_depth': 6,
                    'learning_rate': 0.1,
                    'subsample': 0.8
                },
                'recommended': False
            },
            {
                'type': 'poisson',
                'name': 'Poisson GLM (RECOMENDADO)',
                'params': {},
                'recommended': True
            }
        ]
        
        results = []
        
        for config in models_config:
            logger.info("\n" + "-" * 80)
            logger.info(f"ENTRENANDO: {config['name']}")
            logger.info("-" * 80)
            
            # Crear predictor
            predictor = SISPredictor(model_type=config['type'])
            
            # Entrenar
            metrics = predictor.train(
                db=db,
                test_size=0.2,
                random_state=42,
                **config['params']
            )
            
            # Guardar modelo
            model_path = predictor.save_model()
            
            # Guardar resultados
            results.append({
                'name': config['name'],
                'type': config['type'],
                'metrics': metrics,
                'path': str(model_path)
            })
            
            # Mostrar métricas
            logger.info(f"\nMÉTRICAS DE {config['name']}:")
            logger.info(f"  Train R²: {metrics['train']['r2']:.4f}")
            logger.info(f"  Test R²:  {metrics['test']['r2']:.4f}")
            logger.info(f"  RMSE:     {metrics['test']['rmse']:.4f}")
            logger.info(f"  MAE:      {metrics['test']['mae']:.4f}")
            
            # Métricas específicas de Poisson
            if config['type'] == 'poisson' and 'aic' in metrics:
                logger.info(f"  AIC:      {metrics['aic']:.2f}")
                if 'pseudo_r2' in metrics:
                    logger.info(f"  Pseudo-R²: {metrics['pseudo_r2']:.4f}")
            
            # Validación cruzada solo si está disponible
            if metrics.get('cv_r2_mean') is not None:
                logger.info(f"  CV R² (mean ± std): {metrics['cv_r2_mean']:.4f} ± {metrics['cv_r2_std']:.4f}")
            elif config['type'] != 'poisson':
                logger.info(f"  CV R²: Omitida (dataset muy grande)")
            
            logger.info(f"  Modelo guardado en: {model_path}")
        
        # Resumen comparativo
        logger.info("\n" + "=" * 80)
        logger.info("RESUMEN COMPARATIVO DE MODELOS")
        logger.info("=" * 80)
        logger.info(f"{'Model':<45} {'R2_test':<12} {'RMSE_test':<12} {'MAE_test':<12}")
        logger.info("-" * 80)
        
        for result in results:
            model_label = result['name']
            logger.info(
                f"{model_label:<45} "
                f"{result['metrics']['test']['r2']:<12.4f} "
                f"{result['metrics']['test']['rmse']:<12.4f} "
                f"{result['metrics']['test']['mae']:<12.4f}"
            )
        
        # Determinar mejor modelo
        best_model = max(results, key=lambda x: x['metrics']['test']['r2'])
        logger.info("\n" + "=" * 80)
        logger.info(f"MEJOR MODELO (por R²): {best_model['name']}")
        logger.info(f"  R² Test: {best_model['metrics']['test']['r2']:.4f}")
        logger.info(f"  Archivo: {best_model['path']}")
        
        # Identificar modelo recomendado para count data
        poisson_result = next((r for r in results if r['type'] == 'poisson'), None)
        if poisson_result:
            logger.info("\nRECOMENDACIÓN PARA DATOS DE CONTEO:")
            logger.info(f"   El modelo Poisson es ideal para cantidad_atenciones (datos de conteo)")
            logger.info(f"   Poisson R² Test: {poisson_result['metrics']['test']['r2']:.4f}")
        
        logger.info("=" * 80)
        
        # Guardar métricas comparativas en JSON
        metrics_file = Path(__file__).parent.parent / 'models' / 'comparative_metrics.json'
        comparative_data = {
            'timestamp': datetime.now().isoformat(),
            'models': [
                {
                    'name': r['name'],
                    'type': r['type'],
                    'metrics': {
                        'r2_test': float(r['metrics']['test']['r2']),
                        'rmse_test': float(r['metrics']['test']['rmse']),
                        'mae_test': float(r['metrics']['test']['mae']),
                        'aic': float(r['metrics'].get('aic', 0)) if r['type'] == 'poisson' else None,
                        'pseudo_r2': float(r['metrics'].get('pseudo_r2', 0)) if r['type'] == 'poisson' else None
                    },
                    'path': str(r['path']),
                    'recommended_for_count_data': r['type'] == 'poisson'
                }
                for r in results
            ],
            'best_model_by_r2': {
                'name': best_model['name'],
                'type': best_model['type'],
                'r2_test': float(best_model['metrics']['test']['r2'])
            }
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(comparative_data, f, indent=2)
        
        logger.info(f"\nMétricas comparativas guardadas en: {metrics_file}")
        logger.info("\n[OK] Entrenamiento completado exitosamente")
        
    except Exception as e:
        logger.error(f"[ERROR] Error durante el entrenamiento: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


def train_single_model(model_type: str = "random_forest"):
    """
    Entrena un solo modelo específico
    
    Args:
        model_type: Tipo de modelo ('linear', 'random_forest', 'gradient_boosting')
    """
    logger.info(f"Entrenando modelo: {model_type}")
    
    db: Session = SessionLocal()
    
    try:
        predictor = SISPredictor(model_type=model_type)
        metrics = predictor.train(db=db)
        model_path = predictor.save_model()
        
        logger.info(f"\n[OK] Modelo entrenado y guardado en: {model_path}")
        logger.info(f"  R² Test: {metrics['test']['r2']:.4f}")
        logger.info(f"  RMSE: {metrics['test']['rmse']:.4f}")
        logger.info(f"  MAE: {metrics['test']['mae']:.4f}")
        
    except Exception as e:
        logger.error(f"[ERROR] Error: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Entrenar modelos de predicción del SIS")
    parser.add_argument(
        '--model',
        type=str,
        choices=['linear', 'random_forest', 'gradient_boosting', 'poisson', 'all'],
        default='all',
        help="Tipo de modelo a entrenar (default: all)"
    )
    
    args = parser.parse_args()
    
    if args.model == 'all':
        train_all_models()
    else:
        train_single_model(args.model)
