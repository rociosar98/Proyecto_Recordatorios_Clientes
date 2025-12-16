from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_database_session
from schemas.pagos import PagoIn, PagoOut, ResumenPagoOut
from services.pagos import PagosService
from typing import List
from services.historial import HistorialService
from datetime import date


pagos_router = APIRouter()

@pagos_router.post('/pagos/registrar', tags=['Pagos'], response_model=dict, status_code=200)
def registrar_pago(data: PagoIn, background_tasks: BackgroundTasks, db: Session = Depends(get_database_session)):
    try:
        pago = PagosService(db).registrar_pago(
            servicio_cliente_id = data.servicio_cliente_id,
            monto = data.monto,
            fecha_facturacion = data.fecha_facturacion,
            fecha_pago = data.fecha_pago,
            observaciones = data.observaciones,
            background_tasks=background_tasks  # PASAMOS background_tasks
        )
        return {"message": f"Pago registrado exitosamente con ID {pago.id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@pagos_router.get('/pagos', tags=['Pagos'], response_model=List[PagoOut], status_code=200)
def listar_pagos(db: Session = Depends(get_database_session)):
    return PagosService(db).listar_pagos()


@pagos_router.get('/pagos/resumen',tags=['Pagos'], response_model=List[ResumenPagoOut], status_code=200)
def get_resumen_pagos(db: Session = Depends(get_database_session)):
    resumenes = PagosService(db).obtener_resumen_pagos()
    return resumenes


@pagos_router.get("/pagos/mensuales", tags=['Pagos'], status_code=200)
def pagos_mensuales(anio: int, mes: int, db: Session = Depends(get_database_session)):
    service = HistorialService(db)
    #listado = service.listado_mensual(anio, mes)

    listado = service.listado_mensual_actualizado(db, anio, mes)
    return [{"pagos": listado}]

    # Agrupamos por mes
    ##mes_nombre = date(anio, mes, 1).strftime("%B").capitalize()
    ##return [{"mes": mes_nombre, "pagos": listado}]

