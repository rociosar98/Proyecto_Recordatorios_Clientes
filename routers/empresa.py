from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_database_session
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from models.datos_empresa import DatosEmpresa as DatosEmpresaModel
from schemas.datos_empresa import DatosEmpresa

from passlib.context import CryptContext
from utils.jwt_manager import create_token
from utils.dependencies import get_current_user, admin_required

from services.empresa import EmpresaService


empresa_router = APIRouter(prefix="/empresa", tags=["Empresa"])

@empresa_router.get("", response_model=DatosEmpresa, status_code=status.HTTP_200_OK)
def obtener_datos_empresa(db: Session = Depends(get_database_session)):
    service = EmpresaService(db)
    datos = service.get_datos_empresa()
    if not datos:
        raise HTTPException(status_code=404, detail="Datos de empresa no configurados")
    return datos

@empresa_router.post("", response_model=DatosEmpresa, status_code=status.HTTP_200_OK, dependencies=[Depends(admin_required)])
def crear_o_actualizar_datos_empresa(data: DatosEmpresa, db: Session = Depends(get_database_session)) -> dict:
    service = EmpresaService(db)
    datos = service.update_datos_empresa(data)
    return datos

