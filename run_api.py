#!/usr/bin/env python3
# filepath: /home/bryancmy/Documentos/pyhton-projects/modelo-prediccion-sis/run_api.py
"""
Script para ejecutar la API FastAPI del Sistema SIS
Ejecuta: python run_api.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Ejecutar la API FastAPI con uvicorn"""
    
    # Verificar que estamos en el directorio correcto
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print("Iniciando API FastAPI del Sistema SIS...")
    print()
    print("URL: http://localhost:8000")
    print("Documentación: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("-" * 50)
    
    try:
        # Comando uvicorn
        cmd = [
            "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--log-level", "info"
        ]
        
        # Ejecutar comando
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\nAPI detenida por el usuario")
        
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar uvicorn: {e}")
        sys.exit(1)
        
    except FileNotFoundError:
        print("uvicorn no encontrado. Instálalo con:")
        print("   pip install uvicorn[standard]")
        sys.exit(1)

if __name__ == "__main__":
    main()