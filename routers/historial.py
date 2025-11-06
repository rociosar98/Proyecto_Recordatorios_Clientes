from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from database import get_database_session 
from utils.dependencies import get_current_user, admin_required
from services.historial import HistorialService
from schemas.pagos import PagoOut, HistorialPagoOut
from models.listado_mensual import ListadoMensual as ListadoMensualModel


historial_router = APIRouter()


@historial_router.get('/historial', tags=['Historial'], response_model=List[HistorialPagoOut], status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
def historial_pagos(cliente_id: Optional[int] = None, db: Session = Depends(get_database_session)):
    pagos = HistorialService(db).obtener_historial(cliente_id)
    if not pagos:
        raise HTTPException(status_code=404, detail="No se encontraron pagos")
    return pagos


# @historial_router.get("/listado-mensual")
# def listado_mensual(year: Optional[int] = None, month: Optional[int] = None, db: Session = Depends(get_database_session)):
#     listado = db.query(ListadoMensualModel).order_by(ListadoMensualModel.fecha.desc()).first()
#     if not listado:
#         return []

#     # Filtrar por mes y año si se proporcionan (opcional)
#     if year and month:
#         filtrado = [
#             item for item in listado.contenido
#             if datetime.fromisoformat(item["fecha_facturacion"]).year == year
#             and datetime.fromisoformat(item["fecha_facturacion"]).month == month
#         ]
#         return filtrado

#     return listado.contenido


@historial_router.get("/listado-mensual")
def listado_mensual(db: Session = Depends(get_database_session)):
    listado = db.query(ListadoMensualModel).order_by(ListadoMensualModel.fecha.desc()).first()
    #return listado.contenido if listado else []
    return listado.contenido if listado and listado.contenido else []



# @historial_router.get('/listado-mensual', tags=['Historial'], status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
# def listado_mensual(
#     #fecha: date,
#     condicion_iva: Optional[str] = None,
#     responsable_nombre: Optional[str] = None,
#     db: Session = Depends(get_database_session)
# ):
#     return HistorialService(db).listar_por_filtros(condicion_iva, responsable_nombre)


@historial_router.get('/listado-entradas', tags=['Historial'], status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
def listado_entradas(
    periodo: Optional[str] = None,  # 'mensual', 'anual'
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

