from fastapi import APIRouter, status, Depends, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from database import get_database_session
from models.servicios import Servicios as ServiciosModel, ServiciosCliente as ServiciosClientesModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from services.servicios import ServiciosService
from schemas.servicios import Servicios, ServicioRespuesta, ServiciosCliente, AsignarServicioCliente, ServicioAsignado, ServicioAsignadoDetalle
from sqlalchemy.orm import Session


servicios_router = APIRouter()

@servicios_router.get('/servicios', tags=['Servicios'], response_model=List[ServicioRespuesta],
                     status_code=status.HTTP_200_OK)
def get_servicios(db: Session = Depends(get_database_session)) -> List[Servicios]:
    return ServiciosService(db).get_servicios()

@servicios_router.get('/servicios/{id}', tags=['Servicios'], response_model=Servicios,
                     status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
def get_servicio_id(id: int = Path(ge=1, le=2000), db=Depends(get_database_session)):
    result = ServiciosService(db).get_servicio_id(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Servicio no encontrado")
    return result

@servicios_router.post('/servicios', tags=['Servicios'], response_model=dict, status_code=201)
def create_servicios(servicio: Servicios, db = Depends(get_database_session)) -> dict:
    ServiciosService(db).create_servicio(servicio)
    return JSONResponse(status_code=201, content={"message": "Servicio registrado exitosamente"})

@servicios_router.put('/servicios/{id}', tags=['Servicios'], response_model=dict, status_code=200)
def update_servicio(id: int, servicio: Servicios, db = Depends(get_database_session))-> dict:
    result = ServiciosService(db).get_servicio_id(id)
    if not result:
        return JSONResponse(status_code=404, content={'message': "No se encontró el servicio"})
    ServiciosService(db).update_servicio(id, servicio)
    return JSONResponse(status_code=200, content={"message": "Se modifico el servicio"})

@servicios_router.delete('/servicios/{id}', tags=['Servicios'], response_model=dict, status_code=200)
def delete_servicio(id: int, db = Depends(get_database_session))-> dict:
    result: ServiciosModel = db.query(ServiciosModel).filter(ServiciosModel.id == id).first()
    if not result:
        return JSONResponse(status_code=404, content={"message": "No se encontró el servicio"})
    ServiciosService(db).delete_servicio(id)
    return JSONResponse(status_code=200, content={"message": "Servicio eliminado con exito"})


@servicios_router.post('/servicios_clientes', tags=['Servicios por Cliente'], response_model=dict, status_code=201,)
def asignar_servicio_cliente(data: AsignarServicioCliente, db: Session = Depends(get_database_session)):
    ServiciosService(db).asignar_servicio_cliente(data)
    return {"message": "Servicio asignado correctamente"}



#@servicios_router.get('/servicios_clientes', tags=['Servicios por Cliente'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
#def listar_servicio_cliente(db: Session = Depends(get_database_session)) -> List[Servicios]:
#    return ServiciosService(db).get_servicios_clientes()

@servicios_router.get('/servicios_clientes', tags=['Servicios por Cliente'], response_model=List[ServicioAsignado], status_code=200)
def listar_servicios_asignados(db: Session = Depends(get_database_session)):
    return ServiciosService(db).get_servicios_asignados()


#@servicios_router.get('/servicios', tags=['Servicios'], response_model=List[Servicios],
#status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
#def get_servicios(db: Session = Depends(get_database_session)) -> List[Servicios]:
#    return ServiciosService(db).get_servicios()

#@servicios_router.get('/servicios_clientes/vencimientos', tags=['Servicios por Cliente'], response_model=List[ServicioAsignado])
#def get_servicios_por_vencer(dias: int = 7, db: Session = Depends(get_database_session)):
#    return ServiciosService(db).servicios_por_vencer(dias)

@servicios_router.get('/servicios_clientes/vencimientos', tags=["Servicios por Cliente"], response_model=List[ServiciosCliente])
def get_servicios_por_vencer(dias: int = 7, db: Session = Depends(get_database_session)):
    return ServiciosService(db).servicios_por_vencer(dias)

@servicios_router.get("/clientes/{cliente_id}/servicios", response_model=List[ServicioAsignadoDetalle], tags=["Servicios por Cliente"])
def listar_servicios_cliente(cliente_id: int, db: Session = Depends(get_database_session)):
    return ServiciosService(db).get_servicios_por_cliente(cliente_id)




