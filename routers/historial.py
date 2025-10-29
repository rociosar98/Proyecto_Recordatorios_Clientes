from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_database_session 
from utils.dependencies import get_current_user, admin_required
from services.historial import HistorialService
from sqlalchemy import or_

from schemas.pagos import PagoOut, HistorialPagoOut
from models.pagos import Pagos as PagosModel
from models.servicios import ServiciosCliente as ServiciosClienteModel
from models.clientes import Clientes as ClientesModel
from models.usuarios import Usuarios as UsuariosModel

historial_router = APIRouter()


@historial_router.get('/historial', tags=['Historial'], response_model=List[HistorialPagoOut], status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
def historial_pagos(cliente_id: Optional[int] = None, db: Session = Depends(get_database_session)):
    pagos = HistorialService(db).obtener_historial(cliente_id)
    if not pagos:
        raise HTTPException(status_code=404, detail="No se encontraron pagos")
    return pagos


#@historial_router.get('/historial/{cliente_id}', tags=['Historial'], response_model=List[PagoOut], status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
#def historial_pagos(cliente_id: int, db: Session = Depends(get_database_session)):
#    pagos = HistorialService(db).obtener_historial(cliente_id)
#    if not pagos:
#        raise HTTPException(status_code=404, detail="No se encontraron pagos")
#    return pagos
    #return HistorialService(db).obtener_historial(cliente_id)


@historial_router.get('/listado-mensual', tags=['Historial'], status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
def listado_mensual(
    #fecha: date,
    condicion_iva: Optional[str] = None,
    responsable_nombre: Optional[str] = None,
    db: Session = Depends(get_database_session)
):
    #query = db.query(ServiciosClienteModel).join(ClientesModel)

    #if condicion_iva:
    #    query = query.filter(ClientesModel.condicion_iva == condicion_iva)
    
    #if responsable_nombre:
    # Filtra por nombre o apellido del responsable
    #    query = query.join(ClientesModel.responsable).filter(
    #        or_(
    #            UsuariosModel.nombre.ilike(f"%{responsable_nombre}%"),
    #            UsuariosModel.apellido.ilike(f"%{responsable_nombre}%")
    #        )
    #    )

    return HistorialService(db).listar_por_filtros(condicion_iva, responsable_nombre)

@historial_router.get('/listado-entradas', tags=['Historial'], status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
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