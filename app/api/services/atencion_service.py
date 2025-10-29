from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract, case
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
    Implementa la lógica de análisis basada en requirements.md
    """

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
            fecha_inicio: Fecha inicio del filtro (opcional)
            fecha_fin: Fecha fin del filtro (opcional)
            
        Returns:
            EstadisticasResponse con métricas generales
        """
        # Query base
        query = db.query(Atencion)
        
        # Aplicar filtros de fecha si se proporcionan
        if fecha_inicio:
            query = query.filter(Atencion.fecha_atencion >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Atencion.fecha_atencion <= fecha_fin)
        
        # Calcular métricas
        total_atenciones = query.count()
        
        # Costo total
        total_costo = query.with_entities(
            func.sum(Atencion.monto_pagado)
        ).scalar() or 0.0
        
        # Promedio de costo
        promedio_costo = (total_costo / total_atenciones) if total_atenciones > 0 else 0.0
        
        # Atenciones por género
        stats_genero = query.with_entities(
            Atencion.sexo,
            func.count(Atencion.id).label('count')
        ).group_by(Atencion.sexo).all()
        
        por_genero = {genero: count for genero, count in stats_genero}
        
        # Rango de fechas actual
        fecha_range = query.with_entities(
            func.min(Atencion.fecha_atencion).label('min_fecha'),
            func.max(Atencion.fecha_atencion).label('max_fecha')
        ).first()
        
        return EstadisticasResponse(
            total_atenciones=total_atenciones,
            total_costo=float(total_costo),
            promedio_costo=float(promedio_costo),
            por_genero=por_genero,
            fecha_inicio=fecha_range.min_fecha if fecha_range.min_fecha else None,
            fecha_fin=fecha_range.max_fecha if fecha_range.max_fecha else None
        )

    @staticmethod
    def get_atenciones_por_region(
        db: Session,
        limit: int = 10,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict]:
        """
        Obtiene estadísticas de atenciones por región (departamento)
        
        Args:
            db: Sesión de base de datos
            limit: Número máximo de regiones a retornar
            fecha_inicio: Fecha inicio del filtro
            fecha_fin: Fecha fin del filtro
            
        Returns:
            Lista de diccionarios con estadísticas por región
        """
        query = db.query(
            IPRESS.departamento.label('region'),
            func.count(Atencion.id).label('total_atenciones'),
            func.sum(Atencion.monto_pagado).label('total_costo'),
            func.avg(Atencion.monto_pagado).label('promedio_costo'),
            func.count(func.distinct(IPRESS.id)).label('total_ipress')
        ).join(
            IPRESS, Atencion.ipress_id == IPRESS.id
        )
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            query = query.filter(Atencion.fecha_atencion >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Atencion.fecha_atencion <= fecha_fin)
        
        resultados = query.group_by(
            IPRESS.departamento
        ).order_by(
            func.count(Atencion.id).desc()
        ).limit(limit).all()
        
        return [
            {
                "region": resultado.region,
                "total_atenciones": resultado.total_atenciones,
                "total_costo": float(resultado.total_costo or 0),
                "promedio_costo": float(resultado.promedio_costo or 0),
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
            fecha_inicio: Fecha inicio del filtro
            fecha_fin: Fecha fin del filtro
            
        Returns:
            Lista de diccionarios con estadísticas por servicio
        """
        query = db.query(
            Servicio.nombre.label('servicio'),
            Servicio.codigo.label('codigo_servicio'),
            func.count(Atencion.id).label('total_atenciones'),
            func.sum(Atencion.monto_pagado).label('total_costo'),
            func.avg(Atencion.monto_pagado).label('promedio_costo')
        ).join(
            Servicio, Atencion.servicio_id == Servicio.id
        )
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            query = query.filter(Atencion.fecha_atencion >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Atencion.fecha_atencion <= fecha_fin)
        
        resultados = query.group_by(
            Servicio.id, Servicio.nombre, Servicio.codigo
        ).order_by(
            func.count(Atencion.id).desc()
        ).limit(limit).all()
        
        return [
            {
                "servicio": resultado.servicio,
                "codigo_servicio": resultado.codigo_servicio,
                "total_atenciones": resultado.total_atenciones,
                "total_costo": float(resultado.total_costo or 0),
                "promedio_costo": float(resultado.promedio_costo or 0)
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
            fecha_inicio: Fecha inicio del filtro
            fecha_fin: Fecha fin del filtro
            
        Returns:
            Diccionario con análisis demográfico
        """
        query = db.query(Atencion)
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            query = query.filter(Atencion.fecha_atencion >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Atencion.fecha_atencion <= fecha_fin)
        
        # Análisis por grupos de edad
        grupos_edad = query.with_entities(
            case(
                (Atencion.edad < 18, "Menores (0-17)"),
                (and_(Atencion.edad >= 18, Atencion.edad < 30), "Jóvenes (18-29)"),
                (and_(Atencion.edad >= 30, Atencion.edad < 50), "Adultos (30-49)"),
                (and_(Atencion.edad >= 50, Atencion.edad < 65), "Adultos mayores (50-64)"),
                (Atencion.edad >= 65, "Tercera edad (65+)"),
                else_="Sin clasificar"
            ).label('grupo_edad'),
            func.count(Atencion.id).label('total_atenciones'),
            func.sum(Atencion.monto_pagado).label('total_costo')
        ).group_by('grupo_edad').all()
        
        # Análisis por género
        por_genero = query.with_entities(
            Atencion.sexo,
            func.count(Atencion.id).label('total_atenciones'),
            func.sum(Atencion.monto_pagado).label('total_costo'),
            func.avg(Atencion.edad).label('edad_promedio')
        ).group_by(Atencion.sexo).all()
        
        # Estadísticas de edad
        stats_edad = query.with_entities(
            func.min(Atencion.edad).label('edad_minima'),
            func.max(Atencion.edad).label('edad_maxima'),
            func.avg(Atencion.edad).label('edad_promedio')
        ).first()
        
        return {
            "grupos_edad": [
                {
                    "grupo": grupo.grupo_edad,
                    "total_atenciones": grupo.total_atenciones,
                    "total_costo": float(grupo.total_costo or 0)
                }
                for grupo in grupos_edad
            ],
            "por_genero": [
                {
                    "genero": genero.sexo,
                    "total_atenciones": genero.total_atenciones,
                    "total_costo": float(genero.total_costo or 0),
                    "edad_promedio": float(genero.edad_promedio or 0)
                }
                for genero in por_genero
            ],
            "estadisticas_edad": {
                "edad_minima": stats_edad.edad_minima,
                "edad_maxima": stats_edad.edad_maxima,
                "edad_promedio": float(stats_edad.edad_promedio or 0)
            }
        }

    @staticmethod
    def get_tendencias_temporales(
        db: Session,
        agrupacion: str = "mes",  # mes, trimestre, año
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> List[Dict]:
        """
        Obtiene tendencias temporales de las atenciones
        
        Args:
            db: Sesión de base de datos
            agrupacion: Tipo de agrupación temporal (mes, trimestre, año)
            fecha_inicio: Fecha inicio del filtro
            fecha_fin: Fecha fin del filtro
            
        Returns:
            Lista de diccionarios con tendencias temporales
        """
        query = db.query(Atencion)
        
        # Aplicar filtros de fecha
        if fecha_inicio:
            query = query.filter(Atencion.fecha_atencion >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Atencion.fecha_atencion <= fecha_fin)
        
        # Configurar agrupación según el parámetro
        if agrupacion == "año":
            grupo_temporal = extract('year', Atencion.fecha_atencion)
            formato_periodo = "año"
        elif agrupacion == "trimestre":
            grupo_temporal = func.concat(
                extract('year', Atencion.fecha_atencion),
                '-Q',
                func.ceil(extract('month', Atencion.fecha_atencion) / 3)
            )
            formato_periodo = "trimestre"
        else:  # mes por defecto
            grupo_temporal = func.concat(
                extract('year', Atencion.fecha_atencion),
                '-',
                func.lpad(extract('month', Atencion.fecha_atencion), 2, '0')
            )
            formato_periodo = "mes"
        
        resultados = query.with_entities(
            grupo_temporal.label('periodo'),
            func.count(Atencion.id).label('total_atenciones'),
            func.sum(Atencion.monto_pagado).label('total_costo'),
            func.avg(Atencion.monto_pagado).label('promedio_costo')
        ).group_by(
            grupo_temporal
        ).order_by(
            grupo_temporal
        ).all()
        
        return [
            {
                "periodo": str(resultado.periodo),
                "tipo_periodo": formato_periodo,
                "total_atenciones": resultado.total_atenciones,
                "total_costo": float(resultado.total_costo or 0),
                "promedio_costo": float(resultado.promedio_costo or 0)
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
            departamento: Filtro por departamento
            servicio_codigo: Filtro por código de servicio
            plan_codigo: Filtro por código de plan
            sexo: Filtro por sexo
            edad_min: Edad mínima
            edad_max: Edad máxima
            fecha_inicio: Fecha inicio del filtro
            fecha_fin: Fecha fin del filtro
            
        Returns:
            Tupla con lista de atenciones y total de registros
        """
        query = db.query(Atencion).join(IPRESS).join(Servicio).join(PlanSeguro)
        
        # Aplicar filtros
        if departamento:
            query = query.filter(IPRESS.departamento.ilike(f"%{departamento}%"))
        if servicio_codigo:
            query = query.filter(Servicio.codigo == servicio_codigo)
        if plan_codigo:
            query = query.filter(PlanSeguro.codigo == plan_codigo)
        if sexo:
            query = query.filter(Atencion.sexo == sexo)
        if edad_min is not None:
            query = query.filter(Atencion.edad >= edad_min)
        if edad_max is not None:
            query = query.filter(Atencion.edad <= edad_max)
        if fecha_inicio:
            query = query.filter(Atencion.fecha_atencion >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Atencion.fecha_atencion <= fecha_fin)
        
        # Obtener total y registros paginados
        total = query.count()
        atenciones = query.offset(skip).limit(limit).all()
        
        return atenciones, total