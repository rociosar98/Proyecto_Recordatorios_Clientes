from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from core.enums import MetodoAviso
from schemas.usuarios import UsuarioMini

class Clientes(BaseModel):
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
    metodo_aviso: MetodoAviso  # "email", "whatsapp", "ambos"
    condicion_iva: str
    responsable_id: Optional[UsuarioMini]
    activo: Optional[bool] = True 

    class Config:
        from_attributes = True


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
    metodo_aviso: MetodoAviso  # "email", "whatsapp", "ambos"
    condicion_iva: str
    responsable_id: int  # ID del usuario responsable (vendedor)
    activo: Optional[bool] = True 
    
    class Config:
        from_attributes = True