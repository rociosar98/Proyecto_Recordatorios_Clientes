from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_database_session
from schemas.pagos import PagoIn, PagoOut, ResumenPagoOut
from services.pagos import PagosService
from typing import List


pagos_router = APIRouter()

@pagos_router.post('/pagos/registrar', tags=['Pagos'], response_model=dict, status_code=200)
def registrar_pago(data: PagoIn, db: Session = Depends(get_database_session)):
    try:
        pago = PagosService(db).registrar_pago(
            servicio_cliente_id = data.servicio_cliente_id,
            monto = data.monto,
            fecha_facturacion = data.fecha_facturacion,
            fecha_pago = data.fecha_pago,
            observaciones = data.observaciones
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

