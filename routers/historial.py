from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_database_session 
from services.historial import HistorialService

from schemas.pagos import PagoOut  # Asegúrate de tener un esquema que refleje los datos que quieres retornar
from models.pagos import Pagos as PagosModel
from models.servicios import ServiciosCliente as ServiciosClienteModel

historial_router = APIRouter()

@historial_router.get('/historial/{cliente_id}', tags=['Historial'], response_model=List[PagoOut])
def historial_pagos(cliente_id: int, db: Session = Depends(get_database_session)):
    pagos = HistorialService(db).obtener_historial(cliente_id)
    if not pagos:
        raise HTTPException(status_code=404, detail="No se encontraron pagos")
    return pagos
    #return HistorialService(db).obtener_historial(cliente_id)


@historial_router.get('/listado-mensual', tags=['Historial'])
def listado_mensual(
    #fecha: date,
    condicion_iva: Optional[str] = None,
    responsable_cuenta: Optional[str] = None,
    db: Session = Depends(get_database_session)
):
    return HistorialService(db).listar_por_filtros(condicion_iva, responsable_cuenta)

@historial_router.get('/listado-entradas', tags=['Historial'])
def listado_entradas(
    periodo: Optional[str] = None,  # 'mensual', 'anual', None
    anio: Optional[int] = None,
    mes: Optional[int] = None,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None,
    db: Session = Depends(get_database_session)
):
    # Validaciones básicas
    if periodo == "mensual":
        if not anio or not mes:
            raise HTTPException(status_code=400, detail="Debe especificar año y mes para periodo mensual")
    elif periodo == "anual":
        if not anio:
            raise HTTPException(status_code=400, detail="Debe especificar año para periodo anual")
    elif periodo is None:
        if not (fecha_inicio and fecha_fin):
            raise HTTPException(status_code=400, detail="Debe especificar fecha_inicio y fecha_fin para periodo personalizado")
    return HistorialService(db).listar_entradas(periodo, anio, mes, fecha_inicio, fecha_fin)



#@pagos_router.get('/pagos/entradas', tags=["Pagos"], response_model=List[EntradaPagoOut])
#def listado_entradas(
#    mes: Optional[int] = Query(None, ge=1, le=12),
#    anio: Optional[int] = Query(None, ge=2000),
#    desde: Optional[date] = None,
#    hasta: Optional[date] = None,
#    db: Session = Depends(get_database_session)
#):
#    return PagosService(db).listar_entradas(mes, anio, desde, hasta)