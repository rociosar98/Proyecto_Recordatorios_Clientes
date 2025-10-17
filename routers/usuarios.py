from fastapi import APIRouter, Depends, Path, Query, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from database import get_database_session
from models.usuarios import Usuarios as UsuarioModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from services.usuarios import UsuariosService
from passlib.context import CryptContext
from utils.jwt_manager import create_token
from schemas.usuarios import User, UsuarioBase, Usuarios, UsuarioPublico, UsuarioUpdate,UsuarioPermiso
from sqlalchemy.orm import Session
from utils.dependencies import get_current_user, admin_required
from utils.security import get_password_hash, verify_password


usuarios_router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def authenticate_user(users:dict, email: str, password: str)->UsuarioPublico:
    user = get_user(users, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    user = UsuarioPublico.from_orm(user)
    return user

#def get_password_hash(password):
#    return pwd_context.hash(password)

def get_user(users:list, email: str):
    for item in users:
        if item.correo == email:
            return item
        
#def verify_password(plain_password, hashed_password):
#    return pwd_context.verify(plain_password, hashed_password) 

@usuarios_router.post('/login', tags=['Autenticacion'])
def login(user: User, db=Depends(get_database_session)):
    
    usuariosDb: list = UsuariosService(db).get_usuarios()
    #usuariosDb:UsuarioModel = UsuariosService(db).get_usuarios()

    usuario = authenticate_user(usuariosDb, user.email, user.password)
    if not usuario:
       return JSONResponse(status_code=401, content={'accesoOk': False,'token':''})  
    else:
        token: str = create_token(user.model_dump())
        token: str = create_token({
            "sub": usuario.correo,
            "rol": usuario.rol
        })
        return JSONResponse(status_code=200, content={'accesoOk': True,'token':token, 'usuario': jsonable_encoder(usuario) })   
    
@usuarios_router.get("/usuarios", tags=['Usuarios'], response_model=List[UsuarioPublico], status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
def get_usuarios(db: Session = Depends(get_database_session)):
    return UsuariosService(db).get_usuarios()

#@usuarios_router.get("/usuarios", tags=["Usuarios"], status_code=status.HTTP_200_OK,
#                    response_model=List[UsuarioPublico], dependencies=[Depends(JWTBearer())])
#def get_usuarios(db=Depends(get_database_session)):
#    result = UsuariosService(db).get_usuarios()
#    return result


@usuarios_router.get('/usuarios/{id}', tags=['Usuarios'], response_model=UsuarioPublico,
                     status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
def get_usuario_id(id: int = Path(ge=1, le=2000), db=Depends(get_database_session)):
    result = UsuariosService(db).get_usuario_id(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return result

@usuarios_router.post('/usuarios', tags=['Usuarios'], response_model=dict, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)])
def create_usuarios(usuario: Usuarios,db: Session = Depends(get_database_session)) -> dict:
     # validación de token y usuario actual
    usuario.password = get_password_hash(usuario.password)
    UsuariosService(db).create_usuarios(usuario)
    return JSONResponse(status_code=201, content={"message": "Se ha registrado el usuario"})


@usuarios_router.put('/usuarios/{id}', tags=['Usuarios'], response_model=dict, status_code=200, dependencies=[Depends(admin_required)])
def update_usuarios(id: int, usuarios: UsuarioUpdate, db = Depends(get_database_session)) -> dict:
    result = UsuariosService(db).get_usuario_id(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontro el usuario")
    usuarios.password = get_password_hash(usuarios.password)
    UsuariosService(db).update_usuarios(id, usuarios)
    return JSONResponse(status_code=200, content={"message": "Se ha modificado el usuario"})


@usuarios_router.put('/usuarios/{id}', tags=['Usuarios'], response_model=dict, status_code=200, dependencies=[Depends(admin_required)])
def update_usuarios(id: int, usuarios: UsuarioUpdate, db = Depends(get_database_session)) -> dict:
    result = UsuariosService(db).get_usuario_id(id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontro el usuario")
    UsuariosService(db).update_usuarios(id, usuarios)
    return JSONResponse(status_code=200, content={"message": "Se ha modificado el usuario"})



@usuarios_router.delete('/usuarios/{id}', tags=['Usuarios'], response_model=dict, status_code=200, dependencies=[Depends(admin_required)])
def delete_usuarios(id: int, db = Depends(get_database_session)) -> dict:
    result: UsuarioModel = db.query(UsuarioModel).filter(UsuarioModel.id == id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontro el usuario")
    UsuariosService(db).delete_usuarios(id)
    return JSONResponse(status_code=200, content={"message": "Se elimino el usuario"})


@usuarios_router.put('/usuarios/{id}/permiso', tags=['Usuarios'], response_model=dict, status_code=200, dependencies=[Depends(admin_required)])
def otorgar_permiso(id: int, usuarios: UsuarioPermiso, db = Depends(get_database_session)) -> dict:
    usuario = UsuariosService(db).get_usuario_id(id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontro el usuario")
    UsuariosService(db).otorgar_permiso_usuario(id, usuarios)
    return JSONResponse(status_code=200, content={"message": "Permiso actualizado correctamente"})


#@usuarios_router.put('/usuarios/{id}/permiso',tags=['Usuarios'],response_model=dict,
#status_code=200,dependencies=[Depends(JWTBearer())])
#def otorgar_permiso(id: int, permiso_data: UsuarioPermisoIn,db: Session = Depends(get_database_session),
#    usuario_actual: UsuariosModel = Depends(get_current_user)) -> dict:
#    if usuario_actual.rol != "admin":
#        raise HTTPException(status_code=403, detail="Solo los administradores pueden otorgar permisos")

#    usuario = UsuariosService(db).get_usuario_id(id)
#    if not usuario:
#        raise HTTPException(status_code=404, detail="Usuario no encontrado")

#    UsuariosService(db).otorgar_permiso_usuario(id, permiso_data.permiso)
#    return {"message": "Permiso actualizado correctamente"}
    

