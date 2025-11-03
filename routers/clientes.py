from fastapi import APIRouter, status, Depends, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from database import get_database_session
from models.clientes import Clientes as ClientesModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from services.clientes import ClientesService
from schemas.clientes import ClientesOut, ClientesBase, ClientesCreate, ClientesUpdate
from sqlalchemy.orm import Session

clientes_router = APIRouter()

@clientes_router.get('/clientes', tags=['Clientes'], response_model=List[ClientesOut],
                     status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
def get_clientes(activo: Optional[bool] = None, db: Session = Depends(get_database_session)):
    return ClientesService(db).get_clientes(activo)


@clientes_router.get('/clientes/{id}', tags=['Clientes'], response_model=ClientesOut,
                     status_code=status.HTTP_200_OK, dependencies=[Depends(JWTBearer())])
def get_cliente_id(id: int = Path(ge=1, le=2000), db=Depends(get_database_session)):
    result = ClientesService(db).get_cliente_id(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return result


@clientes_router.post('/clientes', tags=['Clientes'], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_clientes(cliente: ClientesCreate, db = Depends(get_database_session)) -> dict:
    ClientesService(db).create_cliente(cliente)
    return JSONResponse(status_code=201, content={"message": "Cliente registrado exitosamente"})


@clientes_router.put('/clientes/{id}', tags=['Clientes'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def update_cliente(id: int, cliente: ClientesUpdate, db = Depends(get_database_session))-> dict:
    result = ClientesService(db).get_cliente_id(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el cliente")
    ClientesService(db).update_cliente(id, cliente)
    return JSONResponse(status_code=200, content={"message": "Se modifico el cliente"})


@clientes_router.delete('/clientes/{id}', tags=['Clientes'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def delete_cliente(id: int, db: Session = Depends(get_database_session)) -> dict:
    result = ClientesService(db).get_cliente_id(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontró el cliente")
    ClientesService(db).delete_cliente(id)
    return JSONResponse(status_code=200, content={"message": "Cliente dado de bajo"})
    
