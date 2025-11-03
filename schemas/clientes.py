from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from core.enums import MetodoAviso
from schemas.usuarios import UsuarioMini

class ClientesBase(BaseModel):
    nombre: str
    apellido: str
    empresa: str
    domicilio: str
    codigo_postal: str
    localidad: str
    provincia: str
    pais: str
    telefono: Optional[str] = None
    whatsapp: Optional[str] = None
    correo: EmailStr
    metodo_aviso: MetodoAviso
    condicion_iva: str
    activo: Optional[bool] = True


class ClientesCreate(ClientesBase):
    responsable_id: int


class ClientesUpdate(ClientesBase):
    responsable_id: Optional[int] = None  # por si se quiere cambiar o dejar igual


class ClientesOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    empresa: str
    domicilio: str
    codigo_postal: str
    localidad: str
    provincia: str
    pais: str
    telefono: Optional[str] = None
    whatsapp: Optional[str] = None
    correo: EmailStr
    metodo_aviso: MetodoAviso
    condicion_iva: str
    activo: Optional[bool] = True
    responsable: Optional[UsuarioMini]

    class Config:
        from_attributes = True


class ClientesMini(BaseModel):
    id: int
    nombre: str
    apellido: str
    empresa: str


#class Clientes(BaseModel):
#    responsable_id: int
#    Optional[UsuarioMini]

#    class Config:
#        from_attributes = True
