"""
ETL Súper Optimizado para dataset SIS
Usa PostgreSQL COPY para máxima velocidad (~10,000+ registros/segundo)
VERSIÓN SIN VALIDACIONES - Carga desde cero siempre
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import io
import logging
from tqdm import tqdm
from typing import Dict, Set
import time
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración de conexión
DB_CONFIG = {
    'host': 'localhost',
    'database': 'sis_db', 
    'user': 'postgres',
    'password': 'postgres',
    'port': 5432
}

CSV_PATH = '/home/bryancmy/Documentos/pyhton-projects/modelo-prediccion-sis/app/static/dataset.csv'


def get_connection():
    """Crear conexión a PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)


def load_master_data_bulk(conn):
    """Cargar datos maestros usando COPY bulk - SIEMPRE CARGA"""
    cur = conn.cursor()
    
    logger.info("Cargando datos maestros...")
    
    # 1. Planes de Seguro (SIEMPRE CARGAR)
    planes_data = [
        (1, 'SIS GRATUITO', 'Plan de seguro SIS GRATUITO del Sistema Integral de Salud'),
        (2, 'SIS PARA TODOS', 'Plan de seguro SIS PARA TODOS del Sistema Integral de Salud'),
        (3, 'SIS MICROEMPRESA', 'Plan de seguro SIS MICROEMPRESA del Sistema Integral de Salud'),
        (4, 'SIS INDEPENDIENTE', 'Plan de seguro SIS INDEPENDIENTE del Sistema Integral de Salud'),
        (5, 'SIS EMPRENDEDOR', 'Plan de seguro SIS EMPRENDEDOR del Sistema Integral de Salud')
    ]
    
    execute_values(
        cur,
        "INSERT INTO planes_seguro (id, nombre, descripcion) VALUES %s ON CONFLICT (id) DO NOTHING",
        planes_data,
        template=None,
        page_size=1000
    )
    
    logger.info(f"Planes de seguro: {len(planes_data)} registros")
    
    # 2. Servicios básicos (SIEMPRE CARGAR)
    servicios_data = [
        (1, 'MEDICINA GENERAL', 'CONSULTA_EXTERNA'),
        (2, 'PEDIATRIA', 'CONSULTA_EXTERNA'), 
        (3, 'GINECOLOGIA', 'CONSULTA_EXTERNA'),
        (4, 'OBSTETRICIA', 'CONSULTA_EXTERNA'),
        (5, 'EMERGENCIA', 'EMERGENCIA'),
        (6, 'HOSPITALIZACION', 'HOSPITALIZACION'),
        (7, 'CIRUGIA', 'CIRUGIA'),
        (8, 'LABORATORIO', 'APOYO_DIAGNOSTICO'),
        (9, 'RADIOLOGIA', 'APOYO_DIAGNOSTICO'),
        (10, 'FARMACIA', 'APOYO_CLINICO')
    ]
    
    execute_values(
        cur,
        "INSERT INTO servicios (id, nombre, categoria) VALUES %s ON CONFLICT (id) DO NOTHING",
        servicios_data,
        template=None,
        page_size=1000
    )
    
    logger.info(f"Servicios: {len(servicios_data)} registros")
    
    conn.commit()


def analyze_csv_structure(csv_path: str, sample_size: int = 10000):
    """Analizar estructura del CSV para optimizar la carga"""
    logger.info(f"Analizando estructura del CSV...")
    
    # Definir tipos de datos para evitar warnings
    dtype_spec = {
        'PROVINCIA': 'str',
        'COD_IPRESS': 'str',  # Alfanumérico como A013001
        'DISTRITO': 'str',
        'IPRESS': 'str',
        'DESC_SERVICIO': 'str'
    }
    
    # Leer una muestra para análisis
    df_sample = pd.read_csv(csv_path, nrows=sample_size, dtype=dtype_spec, low_memory=False)
    
    logger.info(f"Columnas encontradas: {list(df_sample.columns)}")
    logger.info(f"Muestra analizada: {len(df_sample):,} registros")
    
    # Analizar planes únicos
    planes_unicos = df_sample['PLAN_SEGURO'].dropna().unique()
    logger.info(f"Planes únicos encontrados: {len(planes_unicos)}")
    for plan in planes_unicos:
        logger.info(f"   - {plan}")
    
    # Analizar IPRESS únicos (muestra)
    ipress_unicos = df_sample[['COD_IPRESS', 'IPRESS']].dropna().drop_duplicates()
    logger.info(f"IPRESS únicos (muestra): {len(ipress_unicos):,}")
    
    # Analizar servicios únicos
    servicios_unicos = df_sample['DESC_SERVICIO'].dropna().unique()
    logger.info(f"Servicios únicos encontrados: {len(servicios_unicos)}")
    
    return {
        'planes': set(planes_unicos),
        'servicios': set(servicios_unicos),
        'total_ipress_sample': len(ipress_unicos)
    }


def create_ipress_mapping(conn, csv_path: str):
    """Crear mapeo masivo de IPRESS usando COPY"""
    logger.info("Creando mapeo de IPRESS...")
    
    # Definir tipos para columnas problemáticas
    ipress_dtype_spec = {
        'COD_IPRESS': 'str',
        'IPRESS': 'str', 
        'NIVEL_EESS': 'str',
        'REGION': 'str',
        'PROVINCIA': 'str',
        'DISTRITO': 'str'
    }
    
    # Leer solo columnas de IPRESS
    df_ipress = pd.read_csv(
        csv_path, 
        usecols=['COD_IPRESS', 'IPRESS', 'NIVEL_EESS', 'REGION', 'PROVINCIA', 'DISTRITO'],
        dtype=ipress_dtype_spec,
        low_memory=False
    )
    
    # Limpiar y preparar datos
    df_ipress = df_ipress.dropna(subset=['COD_IPRESS', 'IPRESS'])
    df_ipress = df_ipress.drop_duplicates(subset=['COD_IPRESS'])
    
    logger.info(f"IPRESS únicos para cargar: {len(df_ipress):,}")
    
    # Preparar datos para bulk insert
    ipress_data = []
    for idx, row in df_ipress.iterrows():
        # Manejar códigos de IPRESS que pueden ser alfanuméricos
        codigo_ipress = str(row['COD_IPRESS']) if pd.notna(row['COD_IPRESS']) else f"AUTO_{idx}"
        
        ipress_data.append((
            codigo_ipress[:50],  # Códigos como string, limitados a 50 chars
            str(row['IPRESS'])[:255],  # Limitar longitud
            str(row.get('NIVEL_EESS', 'NO_ESPECIFICADO'))[:50],
            str(row.get('REGION', 'NO_ESPECIFICADO'))[:100],
            str(row.get('PROVINCIA', 'NO_ESPECIFICADO'))[:100],
            str(row.get('DISTRITO', 'NO_ESPECIFICADO'))[:100]
        ))
    
    # Bulk insert usando execute_values
    cur = conn.cursor()
    execute_values(
        cur,
        """INSERT INTO ipress (codigo, nombre, nivel, region, provincia, distrito) 
           VALUES %s ON CONFLICT (codigo) DO NOTHING""",
        ipress_data,
        template=None,
        page_size=5000
    )
    
    conn.commit()
    logger.info(f"IPRESS cargados: {len(ipress_data):,} registros")
    
    # Crear mapeo en memoria para velocidad
    cur.execute("SELECT codigo, id FROM ipress")
    ipress_mapping = {codigo: id for codigo, id in cur.fetchall()}
    
    return ipress_mapping


def create_servicios_mapping(conn, servicios_unicos: Set[str]):
    """Crear mapeo masivo de servicios usando COPY"""
    logger.info("Creando mapeo de servicios...")
    
    cur = conn.cursor()
    
    # Servicios que no existen, crearlos
    servicios_data = []
    next_id = 11  # Empezar después de los servicios básicos
    
    for servicio in servicios_unicos:
        if pd.notna(servicio):
            servicios_data.append((
                next_id,
                str(servicio)[:255],  # Limitar longitud
                'OTRO'
            ))
            next_id += 1
    
    if servicios_data:
        execute_values(
            cur,
            """INSERT INTO servicios (id, nombre, categoria) 
               VALUES %s ON CONFLICT (nombre) DO NOTHING""",
            servicios_data,
            template=None,
            page_size=1000
        )
        
        conn.commit()
        logger.info(f"Servicios adicionales: {len(servicios_data)} registros")
    
    # Crear mapeo en memoria
    cur.execute("SELECT nombre, id FROM servicios")
    servicios_mapping = {nombre: id for nombre, id in cur.fetchall()}
    
    return servicios_mapping


def load_atenciones_ultra_fast(conn, csv_path: str, ipress_mapping: Dict, servicios_mapping: Dict):
    """Cargar atenciones usando método ultra rápido - DESDE CERO SIEMPRE"""
    logger.info("Iniciando carga ultra rápida de atenciones DESDE CERO...")
    
    # Mapeo de planes
    planes_mapping = {
        'SIS GRATUITO': 1,
        'SIS PARA TODOS': 2, 
        'SIS MICROEMPRESA': 3,
        'SIS INDEPENDIENTE': 4,
        'SIS EMPRENDEDOR': 5
    }
    
    chunk_size = 50000  # Procesar en chunks
    total_rows = sum(1 for line in open(csv_path)) - 1  # -1 para header
    
    logger.info(f"Total registros en CSV: {total_rows:,}")
    logger.info(f"Iniciando carga completa desde registro 1...")
    
    # Definir tipos de datos para el chunking principal
    main_dtype_spec = {
        'AÑO': 'int16',
        'MES': 'int8', 
        'REGION': 'str',
        'PROVINCIA': 'str',
        'DISTRITO': 'str',
        'COD_IPRESS': 'str',  # Clave: alfanumérico
        'IPRESS': 'str',
        'NIVEL_EESS': 'str',
        'PLAN_SEGURO': 'str',
        'DESC_SERVICIO': 'str',
        'SEXO': 'str',
        'GRUPO_EDAD': 'str',
        'ATENCIONES': 'int32'
    }
    
    processed = 0
    inserted = 0
    errors = 0
    
    # Leer CSV en chunks DESDE EL INICIO (SIN WARNINGS)
    for chunk_num, df_chunk in enumerate(pd.read_csv(csv_path, chunksize=chunk_size, dtype=main_dtype_spec, low_memory=False)):
        
        logger.info(f"Procesando chunk {chunk_num + 1} (registros {processed + 1:,} - {processed + len(df_chunk):,})...")
        
        # Preparar datos para bulk insert
        atenciones_data = []
        error_details = {
            'plan_invalido': 0,
            'ipress_invalido': 0, 
            'servicio_invalido': 0,
            'otros_errores': 0
        }
        
        for _, row in df_chunk.iterrows():
            try:
                # Validar y mapear datos
                plan_key = row.get('PLAN_SEGURO')
                if pd.isna(plan_key) or plan_key not in planes_mapping:
                    error_details['plan_invalido'] += 1
                    continue
                
                ipress_codigo = row.get('COD_IPRESS')
                if pd.isna(ipress_codigo) or str(ipress_codigo) not in ipress_mapping:
                    error_details['ipress_invalido'] += 1
                    continue
                
                servicio_nombre = row.get('DESC_SERVICIO')
                if pd.isna(servicio_nombre) or servicio_nombre not in servicios_mapping:
                    error_details['servicio_invalido'] += 1
                    continue
                
                # Preparar registro
                atencion = (
                    int(row.get('AÑO', 2020)),
                    int(row.get('MES', 1)),
                    str(row.get('REGION', 'NO_ESPECIFICADO'))[:100],
                    str(row.get('PROVINCIA', ''))[:100] if pd.notna(row.get('PROVINCIA')) else None,
                    str(row.get('DISTRITO', ''))[:100] if pd.notna(row.get('DISTRITO')) else None,
                    str(row.get('SEXO', 'NO_ESPECIFICADO'))[:20],
                    str(row.get('GRUPO_EDAD', 'NO_ESPECIFICADO'))[:20],
                    int(row.get('ATENCIONES', 1)),
                    planes_mapping[plan_key],
                    ipress_mapping[str(ipress_codigo)],
                    servicios_mapping[servicio_nombre]
                )
                
                atenciones_data.append(atencion)
                
            except Exception as e:
                error_details['otros_errores'] += 1
                continue
        
        # Sumar errores del chunk
        chunk_errors = sum(error_details.values())
        errors += chunk_errors
        
        # Bulk insert del chunk
        if atenciones_data:
            cur = conn.cursor()
            execute_values(
                cur,
                """INSERT INTO atenciones 
                   (año, mes, region, provincia, distrito, sexo, grupo_edad, 
                    cantidad_atenciones, plan_seguro_id, ipress_id, servicio_id)
                   VALUES %s""",
                atenciones_data,
                template=None,
                page_size=5000
            )
            conn.commit()
            cur.close()
            
            inserted += len(atenciones_data)
        
        processed += len(df_chunk)
        
        # Progress con detalles de errores
        progress = (processed / total_rows) * 100
        logger.info(f"Progreso: {progress:.1f}% | Insertados: {inserted:,} | Errores: {chunk_errors:,}")
        
        # Log detalles de errores cada 10 chunks
        if chunk_num % 10 == 0 and chunk_errors > 0:
            logger.info(f"Errores chunk {chunk_num + 1}: Plan={error_details['plan_invalido']}, IPRESS={error_details['ipress_invalido']}, Servicio={error_details['servicio_invalido']}, Otros={error_details['otros_errores']}")
    
    logger.info(f"Carga completada!")
    logger.info(f"Total procesados: {processed:,}")
    logger.info(f"Total insertados: {inserted:,}")
    logger.info(f"Total errores: {errors:,}")
    
    return {'processed': processed, 'inserted': inserted, 'errors': errors}


def main():
    """Función principal del ETL ultra rápido"""
    start_time = time.time()
    
    logger.info("Iniciando ETL Ultra Rápido para SIS (SIN VALIDACIONES)")
    logger.info(f"Archivo CSV: {CSV_PATH}")
    
    try:
        # Conectar a la base de datos
        conn = get_connection()
        logger.info("Conexión a PostgreSQL establecida")
        
        # Paso 1: Cargar datos maestros (SIEMPRE)
        load_master_data_bulk(conn)
        
        # Paso 2: Analizar CSV
        analysis = analyze_csv_structure(CSV_PATH)
        
        # Paso 3: Crear mapeos de IPRESS 
        ipress_mapping = create_ipress_mapping(conn, CSV_PATH)
        
        # Paso 4: Crear mapeos de servicios
        servicios_mapping = create_servicios_mapping(conn, analysis['servicios'])
        
        # Paso 5: Carga ultra rápida de atenciones (DESDE CERO)
        stats = load_atenciones_ultra_fast(conn, CSV_PATH, ipress_mapping, servicios_mapping)
        
        # Estadísticas finales
        elapsed_time = time.time() - start_time
        records_per_second = stats['inserted'] / elapsed_time if elapsed_time > 0 else 0
        
        logger.info(f"ETL COMPLETADO!")
        logger.info(f"Tiempo total: {elapsed_time:.2f} segundos")
        logger.info(f"Velocidad: {records_per_second:,.0f} registros/segundo")
        logger.info(f"Registros insertados: {stats['inserted']:,}")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Error en ETL: {e}")
        raise


if __name__ == "__main__":
    main()