#!/usr/bin/env python3
"""
Script para entrenar modelos de predicción del SIS
Wrapper simple para facilitar el uso desde el directorio raíz

OPTIMIZADO para datasets grandes (5M+ registros)
"""

import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Agregar directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Importar y ejecutar el script de entrenamiento
from app.ml.training.train_model import train_all_models, train_single_model

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Entrenar modelos de predicción de demanda del SIS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python train_models.py                    # Entrenar TODOS los modelos (análisis comparativo)
  python train_models.py --model random_forest
  python train_models.py --model gradient_boosting
  python train_models.py --model linear

Los 3 modelos permiten comparar performance y elegir el mejor para tu dataset.
Los modelos se guardarán en: app/ml/models/
        """
    )
    
    parser.add_argument(
        '--model',
        type=str,
        choices=['linear', 'random_forest', 'gradient_boosting', 'poisson', 'all'],
        default='all',
        help="Tipo de modelo a entrenar (default: all - ideal para análisis comparativo)"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("ENTRENAMIENTO DE MODELOS DE PREDICCIÓN DEL SIS")
    print("=" * 80)
    print(f"Modelo(s) a entrenar: {args.model.upper()}")
    print("MODELOS DISPONIBLES:")
    print("   • LINEAR: Regresión lineal (rápido, baseline)")
    print("   • RANDOM_FOREST: 50 árboles (robusto, no lineal)")
    print("   • GRADIENT_BOOSTING: 100 estimators (mejor accuracy)")
    print("   • POISSON: GLM para conteos (RECOMENDADO para datos de conteo)")
    print()
    if args.model == 'all':
        print("ANÁLISIS COMPARATIVO: Entrenando los 4 modelos")
        print("   Perfecto para evaluar performance y elegir el mejor")
        print()
    print("OPTIMIZACIONES:")
    print("   • Sampling inteligente para datasets grandes (>2M registros)")
    print("   • Procesamiento en chunks para evitar Out of Memory")
    print("   • Parámetros optimizados para velocidad/accuracy")
    print("=" * 80)
    print()
    
    try:
        if args.model == 'all':
            train_all_models()
        else:
            train_single_model(args.model)
        
        print()
        print("=" * 80)
        print("[OK] ENTRENAMIENTO COMPLETADO")
        print("=" * 80)
        print()
        print("Los modelos están disponibles en: app/ml/models/")
        print()
        if args.model == 'all':
            print("ANÁLISIS COMPARATIVO:")
            print("   Compara las métricas R², RMSE y MAE de cada modelo")
            print("   El modelo con mejor R² en test es el más confiable")
            print("   TIP: Usa estas métricas en tu informe/presentación")
        else:
            print(f"[OK] Modelo {args.model.upper()} entrenado exitosamente")
        print()
        print("Puedes usarlos mediante la API:")
        print("  POST /api/v1/prediccion/demanda")
        print("  POST /api/v1/prediccion/batch")
        print("  GET  /api/v1/prediccion/modelos")
        print()
        
    except Exception as e:
        print()
        print("=" * 80)
        print("[ERROR] ERROR EN EL ENTRENAMIENTO")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        sys.exit(1)
