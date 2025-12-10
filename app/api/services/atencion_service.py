from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract, case, String
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from app.models.atencion import Atencion
from app.models.plan_seguro import PlanSeguro  
from app.models.ipress import IPRESS
from app.models.servicio import Servicio
from app.schemas.atencion_schema import EstadisticasResponse


class AtencionService:
    """
    Servicio de negocio para operaciones con Atenciones del SIS
    Usa solo campos reales: año, mes, region, sexo, grupo_edad, cantidad_atenciones
    """
    
    # Constante para cálculos estimados de costo
    COSTO_PROMEDIO_POR_ATENCION = 150.0  # S/ 150 por atención (ajustable)

    @staticmethod
    def get_estadisticas_generales(
        db: Session,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> EstadisticasResponse:
        """
        Obtiene estadísticas generales de atenciones
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: No se usa (compatibilidad)
            fecha_fin: No se usa (compatibilidad)
            
        Returns:
            EstadisticasResponse con métricas generales
        """
        query = db.query(Atencion)
        
        # Total de registros
        total_registros = query.count()
        
        # Suma total de atenciones (campo cantidad_atenciones)
        total_atenciones_result = query.with_entities(
            func.sum(Atencion.cantidad_atenciones)
        ).scalar()
        total_atenciones = int(total_atenciones_result or 0)
        
        # Costo total estimado
        total_costo = total_atenciones * AtencionService.COSTO_PROMEDIO_POR_ATENCION
        
        # Distribución por género (suma de cantidad_atenciones por género)
        stats_genero = query.with_entities(
            Atencion.sexo,
            func.sum(Atencion.cantidad_atenciones).label('count')
        ).group_by(Atencion.sexo).all()
        
        distribucion_por_sexo = {genero: int(count or 0) for genero, count in stats_genero}
        
        # Distribución por edad (grupo_edad)
        stats_edad = query.with_entities(
            Atencion.grupo_edad,
            func.sum(Atencion.cantidad_atenciones).label('count')
        ).group_by(Atencion.grupo_edad).all()
        
        distribucion_por_edad = {grupo: int(count or 0) for grupo, count in stats_edad}
        
        # Top 5 regiones
        top_regiones = query.with_entities(
            Atencion.region,
            func.sum(Atencion.cantidad_atenciones).label('total')
        ).group_by(Atencion.region).order_by(
            func.sum(Atencion.cantidad_atenciones).desc()
        ).limit(5).all()
        
        regiones_top_5 = [
            {"region": region, "total_atenciones": int(total or 0)}
            for region, total in top_regiones
        ]
        
        # Calcular promedio mensual (total atenciones / número de meses únicos)
        meses_unicos = query.with_entities(
            func.count(func.distinct(func.concat(func.cast(Atencion.año, String), '-', func.cast(Atencion.mes, String))))
        ).scalar() or 1
        
        promedio_mensual = total_atenciones / meses_unicos if meses_unicos > 0 else 0
        
        return EstadisticasResponse(
            total_atenciones=total_atenciones,
            promedio_mensual=float(promedio_mensual),
            distribucion_por_sexo=distribucion_por_sexo,
            distribucion_por_edad=distribucion_por_edad,
            regiones_top_5=regiones_top_5
        )

    @staticmethod
    def get_atenciones_por_region(
        db: Session,
        limit: int = 10,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict]:
        """
        Obtiene estadísticas de atenciones por región
        
        Args:
            db: Sesión de base de datos
            limit: Número máximo de regiones a retornar
            fecha_inicio: No se usa (compatibilidad)
            fecha_fin: No se usa (compatibilidad)
            
        Returns:
            Lista de diccionarios con estadísticas por región
        """
        query = db.query(
            Atencion.region.label('region'),
            func.sum(Atencion.cantidad_atenciones).label('total_atenciones'),
            func.count(func.distinct(Atencion.ipress_id)).label('total_ipress')
        ).group_by(
            Atencion.region
        ).order_by(
            func.sum(Atencion.cantidad_atenciones).desc()
        ).limit(limit)
        
        resultados = query.all()
        
        return [
            {
                "region": resultado.region,
                "total_atenciones": int(resultado.total_atenciones or 0),
                "total_ipress": resultado.total_ipress
            }
            for resultado in resultados
        ]

    @staticmethod
    def get_atenciones_por_servicio(
        db: Session,
        limit: int = 10,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict]:
        """
        Obtiene estadísticas de atenciones por tipo de servicio
        
        Args:
            db: Sesión de base de datos
            limit: Número máximo de servicios a retornar
            fecha_inicio: No se usa (compatibilidad)
            fecha_fin: No se usa (compatibilidad)
            
        Returns:
            Lista de diccionarios con estadísticas por servicio
        """
        query = db.query(
            Servicio.nombre.label('servicio'),
            Servicio.categoria.label('categoria'),
            func.sum(Atencion.cantidad_atenciones).label('total_atenciones')
        ).join(
            Servicio, Atencion.servicio_id == Servicio.id
        ).group_by(
            Servicio.id, Servicio.nombre, Servicio.categoria
        ).order_by(
            func.sum(Atencion.cantidad_atenciones).desc()
        ).limit(limit)
        
        resultados = query.all()
        
        return [
            {
                "servicio": resultado.servicio,
                "codigo_servicio": resultado.categoria or "Sin categoría",
                "total_atenciones": int(resultado.total_atenciones or 0)
            }
            for resultado in resultados
        ]

    @staticmethod
    def get_analisis_demografico(
        db: Session,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Dict:
        """
        Obtiene análisis demográfico de las atenciones
        
        Args:
            db: Sesión de base de datos
            fecha_inicio: No se usa (compatibilidad)
            fecha_fin: No se usa (compatibilidad)
            
        Returns:
            Diccionario con análisis demográfico
        """
        query = db.query(Atencion)
        
        # Análisis por grupos de edad (usando grupo_edad del modelo)
        grupos_edad = query.with_entities(
            Atencion.grupo_edad,
            func.sum(Atencion.cantidad_atenciones).label('total_atenciones')
        ).group_by(Atencion.grupo_edad).all()
        
        # Análisis por género
        por_genero = query.with_entities(
            Atencion.sexo,
            func.sum(Atencion.cantidad_atenciones).label('total_atenciones')
        ).group_by(Atencion.sexo).all()
        
        return {
            "grupos_edad": [
                {
                    "grupo": grupo.grupo_edad,
                    "total_atenciones": int(grupo.total_atenciones or 0)
                }
                for grupo in grupos_edad
            ],
            "por_genero": [
                {
                    "genero": genero.sexo,
                    "total_atenciones": int(genero.total_atenciones or 0)
                }
                for genero in por_genero
            ]
        }

    @staticmethod
    def get_tendencias_temporales(
        db: Session,
        agrupacion: str = "mes",
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict]:
        """
        Obtiene tendencias temporales de las atenciones
        
        Args:
            db: Sesión de base de datos
            agrupacion: Tipo de agrupación temporal (mes, trimestre, año)
            fecha_inicio: No se usa (compatibilidad)
            fecha_fin: No se usa (compatibilidad)
            
        Returns:
            Lista de diccionarios con tendencias temporales
        """
        query = db.query(Atencion)
        
        # Configurar agrupación según el parámetro usando año y mes
        if agrupacion == "año":
            grupo_temporal = func.cast(Atencion.año, String)
            formato_periodo = "año"
        elif agrupacion == "trimestre":
            # Concatenar año-Q<trimestre>
            grupo_temporal = func.concat(
                func.cast(Atencion.año, String),
                '-Q',
                func.cast(func.ceil(Atencion.mes / 3), String)
            )
            formato_periodo = "trimestre"
        else:  # mes por defecto
            # Concatenar año-mes con formato YYYY-MM
            grupo_temporal = func.concat(
                func.cast(Atencion.año, String),
                '-',
                func.lpad(func.cast(Atencion.mes, String), 2, '0')
            )
            formato_periodo = "mes"
        
        resultados = query.with_entities(
            grupo_temporal.label('periodo'),
            func.sum(Atencion.cantidad_atenciones).label('total_atenciones')
        ).group_by(
            grupo_temporal
        ).order_by(
            grupo_temporal
        ).all()
        
        return [
            {
                "periodo": str(resultado.periodo),
                "tipo_periodo": formato_periodo,
                "total_atenciones": int(resultado.total_atenciones or 0)
            }
            for resultado in resultados
        ]

    @staticmethod
    def buscar_atenciones(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        departamento: Optional[str] = None,
        servicio_codigo: Optional[str] = None,
        plan_codigo: Optional[str] = None,
        sexo: Optional[str] = None,
        edad_min: Optional[int] = None,
        edad_max: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Tuple[List[Atencion], int]:
        """
        Busca atenciones con filtros múltiples
        
        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir
            limit: Número máximo de registros a retornar
            departamento: Filtro por región (usa campo region)
            servicio_codigo: Filtro por código de servicio
            plan_codigo: Filtro por código de plan
            sexo: Filtro por sexo
            edad_min: No se usa (no hay campo edad)
            edad_max: No se usa (no hay campo edad)
            fecha_inicio: No se usa (compatibilidad)
            fecha_fin: No se usa (compatibilidad)
            
        Returns:
            Tupla con lista de atenciones y total de registros
        """
        query = db.query(Atencion).join(IPRESS).join(Servicio).join(PlanSeguro)
        
        # Aplicar filtros disponibles
        if departamento:
            query = query.filter(Atencion.region.ilike(f"%{departamento}%"))
        if servicio_codigo:
            query = query.filter(Servicio.categoria.ilike(f"%{servicio_codigo}%"))
        if plan_codigo:
            query = query.filter(PlanSeguro.nombre.ilike(f"%{plan_codigo}%"))
        if sexo:
            query = query.filter(Atencion.sexo == sexo)
        
        # Obtener total y registros paginados
        total = query.count()
        atenciones = query.offset(skip).limit(limit).all()
        
        return atenciones, total
