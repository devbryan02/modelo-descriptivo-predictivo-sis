#!/usr/bin/env python3
"""
Script de verificación de dependencias del proyecto
Ejecuta este script para verificar que todas las dependencias estén correctamente instaladas
"""

import sys
import importlib
from typing import List, Tuple

def verificar_modulo(nombre: str, paquete: str = None) -> Tuple[bool, str]:
    """
    Verifica si un módulo está instalado
    
    Args:
        nombre: Nombre del módulo a importar
        paquete: Nombre del paquete en pip (si es diferente)
    
    Returns:
        Tupla (exitoso, mensaje)
    """
    paquete = paquete or nombre
    try:
        modulo = importlib.import_module(nombre)
        version = getattr(modulo, '__version__', 'versión desconocida')
        return True, f"[OK] {paquete:20s} {version}"
    except ImportError:
        return False, f"[X] {paquete:20s} NO INSTALADO"

def main():
    """Verifica todas las dependencias del proyecto"""
    
    print("=" * 70)
    print("VERIFICACIÓN DE DEPENDENCIAS - Sistema de Análisis del SIS")
    print("=" * 70)
    print()
    
    # Lista de módulos a verificar
    modulos = [
        # Framework Web
        ("fastapi", None),
        ("uvicorn", None),
        ("pydantic", None),
        
        # Base de Datos
        ("sqlalchemy", None),
        ("psycopg2", "psycopg2-binary"),
        ("alembic", None),
        
        # Data Science & ML
        ("pandas", None),
        ("numpy", None),
        ("sklearn", "scikit-learn"),
        ("joblib", None),
        
        # Utilidades
        ("dotenv", "python-dotenv"),
    ]
    
    # Verificar Python
    print("PYTHON")
    print("-" * 70)
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 10:
        print(f"[OK] Python {version_info.major}.{version_info.minor}.{version_info.micro}")
    else:
        print(f"[WARNING] Python {version_info.major}.{version_info.minor}.{version_info.micro} (Se recomienda 3.10+)")
    print()
    
    # Verificar módulos
    print("MÓDULOS PYTHON")
    print("-" * 70)
    
    fallos = []
    for nombre, paquete in modulos:
        exitoso, mensaje = verificar_modulo(nombre, paquete)
        print(mensaje)
        if not exitoso:
            fallos.append(paquete or nombre)
    
    print()
    print("=" * 70)
    
    if fallos:
        print("[WARNING] FALTAN DEPENDENCIAS")
        print("=" * 70)
        print()
        print("Ejecuta el siguiente comando para instalar todo:")
        print()
        print("    pip install -r requirements.txt")
        print()
        return 1
    else:
        print("[OK] TODAS LAS DEPENDENCIAS ESTÁN INSTALADAS")
        print("=" * 70)
        print()
        print("El proyecto está listo para ejecutarse.")
        print()
        print("Próximos pasos:")
        print("  1. Configurar archivo .env con credenciales de PostgreSQL")
        print("  2. Ejecutar migraciones: alembic upgrade head")
        print("  3. Entrenar modelos: python train_models.py")
        print("  4. Iniciar servidor: python run_api.py")
        print()
        return 0

if __name__ == "__main__":
    sys.exit(main())
