from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from core.enums import PermisoUsuario

class User(BaseModel): # clase para login
    email: str
    password: str
class UsuarioBase(BaseModel): #clase con los campos comunes de usuario
    nombre: str
    apellido: str
    correo: EmailStr
    rol: str
    activo: bool

    class Config:
        from_attributes = True

class Usuarios(UsuarioBase):
    password: str

class UsuarioPublico(BaseModel): # este modelo se usa en respuestas de endpoints para mostrar información del usuario sin incluir la contraseña.
    id: int
    nombre: str
    apellido: str
    correo: EmailStr
    rol: str
    permiso: Optional[PermisoUsuario] = None
    activo: bool

    class Config:
        from_attributes = True


class UsuarioUpdate(BaseModel):
    nombre: Optional[str]
    apellido: Optional[str]
    correo: Optional[EmailStr]
    rol: Optional[str]
    password: Optional[str]


class UsuarioMini(BaseModel):
    nombre: str
    apellido: str

    class Config:
        from_attributes = True


class UsuarioPermiso(BaseModel):
    permiso: PermisoUsuario