from fastapi import APIRouter, status, Depends, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from database import get_database_session
from models.recordatorios import Recordatorios as RecordatoriosModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from services.recordatorios import RecordatoriosService
from sqlalchemy.orm import Session, joinedload
from schemas.recordatorios import RecordatorioOut, PagoManualIn
from models.clientes import Clientes as ClientesModel
from models.servicios import Servicios as ServiciosModel, ServiciosCliente as ServiciosClienteModel
from datetime import date
from models.usuarios import Usuarios as UsuariosModel


recordatorios_router = APIRouter()


@recordatorios_router.post('/recordatorios/generar-iniciales', tags=['Recordatorios'],response_model=dict, status_code=201)
def generar_iniciales(db: Session = Depends(get_database_session)) -> dict:
    result = RecordatoriosService(db).generar_recordatorios_dia_1()
    return JSONResponse(status_code=201, content={"message": f"Se generaron {len(result)} recordatorios"}
    )


@recordatorios_router.get('/recordatorios', tags=['Recordatorios'], response_model=List[RecordatorioOut])
def get_recordatorios(db: Session = Depends(get_database_session)):
    result = RecordatoriosService(db).get_recordatorios()
    return result


@recordatorios_router.put('/recordatorios/{id}/marcar-enviado', tags=['Recordatorios'], response_model=dict)
def marcar_como_enviado(id: int, db: Session = Depends(get_database_session)):
    actualizado = RecordatoriosService(db).marcar_como_enviado(id)
    if not actualizado:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    return {"message": "Recordatorio marcado como enviado"}


@recordatorios_router.delete('/recordatorios/{id}', tags=['Recordatorios'], response_model=dict)
def eliminar_recordatorio(id: int, db: Session = Depends(get_database_session)):
    eliminado = RecordatoriosService(db).delete_recordatorio(id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Recordatorio no encontrado")
    return {"message": "Recordatorio eliminado correctamente"}


@recordatorios_router.post('/recordatorios/generar-dia-10', tags=['Recordatorios'], response_model=dict)
def generar_recordatorios_dia_10(db: Session = Depends(get_database_session)) -> dict:
    result = RecordatoriosService(db).generar_recordatorios_dia_10()
    enviados = RecordatoriosService(db).enviar_recordatorios_no_enviados()
    return JSONResponse(status_code=201, content={"message": f"Se generaron {len(result)} recordatorios de deudores (día 10)", "enviados": enviados})


@recordatorios_router.post('/recordatorios/generar-mora', tags=['Recordatorios'], response_model=dict, status_code=201)
def generar_mora(db: Session = Depends(get_database_session)) -> dict:
    result = RecordatoriosService(db).generar_recordatorios_dia_20()
    enviados = RecordatoriosService(db).enviar_recordatorios_no_enviados()
    return JSONResponse(status_code=201, content={"message": f"Se generaron {len(result)} recordatorios de mora", "enviados": enviados})


@recordatorios_router.post('/recordatorios/generar-corte', tags=['Recordatorios'], response_model=dict, status_code=201)
def generar_corte(db: Session = Depends(get_database_session)) -> dict:
    result = RecordatoriosService(db).generar_recordatorios_dia_28()
    enviados = RecordatoriosService(db).enviar_recordatorios_no_enviados()
    return JSONResponse(status_code=201, content={"message": f"Se generaron {len(result)} recordatorios de corte", "enviados": enviados})


# @recordatorios_router.post('/recordatorios/registrar-pago', tags=['Recordatorios'], response_model=dict, status_code=200)
# def registrar_pago_manual(data: PagoManualIn, db: Session = Depends(get_database_session)):
#     cantidad = RecordatoriosService(db).registrar_pago_manual(
#         servicio_cliente_id=data.servicio_cliente_id,
#         tipo_pago=data.tipo_pago.value
#     )

#     if cantidad == 0:
#         raise HTTPException(status_code=404, detail="No se encontraron recordatorios para actualizar")

#     return {"message": f"Se actualizaron {cantidad} recordatorios con estado '{data.tipo_pago.value}'"}


@recordatorios_router.get('/recordatorios/listado-mensual', tags=["Recordatorios"])
def generar_listado_mensual(condicion_iva: Optional[str] = Query(default=None),responsable_id: Optional[int] = Query(default=None), db: Session = Depends(get_database_session)):

    query = (
        db.query(ServiciosClienteModel)
        .join(ClientesModel, ServiciosClienteModel.cliente_id == ClientesModel.id)
        .join(UsuariosModel, ClientesModel.responsable_id == UsuariosModel.id)
        .join(ServiciosModel, ServiciosClienteModel.servicio_id == ServiciosModel.id)
        .options(
            joinedload(ServiciosClienteModel.cliente).joinedload(ClientesModel.responsable),
            joinedload(ServiciosClienteModel.servicio)
        )
        .filter(ServiciosClienteModel.activo == True)
    )
    if condicion_iva:
        query = query.filter(ClientesModel.condicion_iva == condicion_iva)

    if responsable_id:
        query = query.filter(ClientesModel.responsable_id == responsable_id)

    servicios = query.order_by(UsuariosModel.nombre.asc(), ClientesModel.empresa.asc()).all()

    resultado = []
    for sc in servicios:
        cliente = sc.cliente
        vendedor = cliente.responsable

        resultado.append({
            "empresa": cliente.empresa,
            "cliente": f"{cliente.nombre} {cliente.apellido}",
            "vendedor": vendedor.nombre if vendedor else "Sin asignar",
            "servicio": sc.servicio.nombre,
            "monto": sc.precio_congelado,
            "metodo_aviso": cliente.metodo_aviso,
            "fecha_inicio": sc.fecha_inicio,
            "fecha_vencimiento": sc.fecha_vencimiento,
            "cuotas": sc.cuotas,
        })

    return resultado

