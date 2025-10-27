from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ValidationError
from typing import Optional, List
from datetime import date
from core.enums import TipoServicio, Recurrencia

class Servicios(BaseModel):
    nombre: str
    tipo: TipoServicio
    precio: float
    recurrencia: Optional[Recurrencia] = None
    #cuotas: Optional[int] = None
    #cuotas: Optional[bool] = False
    activo: Optional[bool] = True


    @model_validator(mode="after")
    def validar_campos_por_tipo(self):
        if self.tipo == TipoServicio.recurrente:
            if not self.recurrencia:
                raise ValueError("Los servicios recurrentes deben tener una recurrencia definida")
            #if self.cuotas is not None:
            #    raise ValueError("Los servicios recurrentes no deben tener cuotas")
        elif self.tipo == TipoServicio.pago_unico:
            if self.recurrencia is not None:
                raise ValueError("Los servicios de pago único no deben tener recurrencia")
            #if self.cuotas not in (1, 3, 6, 12):
            #    raise ValueError("Las cuotas permitidas para pago único son 1, 3, 6 o 12")
        return self

    #@model_validator(mode="after")
    #def validar_campos_por_tipo(self):
    #    if self.tipo == TipoServicio.recurrente:
    #        if not self.recurrencia:
    #            raise ValueError("Los servicios recurrentes deben tener una recurrencia definida")
    #    elif self.tipo == TipoServicio.pago_unico:
    #        if self.recurrencia is not None:
    #            raise ValueError("Los servicios de pago único no deben tener recurrencia")
    #    return self

    class Config:
        from_attributes = True

class ServicioRespuesta(BaseModel):
    id: int
    nombre: str
    tipo: TipoServicio
    precio: float
    recurrencia: Optional[Recurrencia] = None
    cuotas: Optional[int] = None
    #cuotas: Optional[bool] = False
    activo: Optional[bool] = True
    
    class Config:
        from_attributes = True


class ServiciosCliente(BaseModel):
    servicio_id: int
    cliente_id: int
    precio_congelado: float
    cuotas: int
    fecha_inicio: date
    fecha_vencimiento: date
    activo: Optional[bool] = True 

    class Config:
        from_attributes = True


class AsignarServicioCliente(BaseModel):
    servicio_id: int
    cliente_id: int
    cuotas: Optional[int] = 1  # Solo para pago único

    class Config:
        from_attributes = True


class ServicioAsignado(BaseModel):
    id: int
    cliente_id: int
    cliente_nombre: str
    cliente_apellido: str
    servicio_id: int
    servicio_nombre: str
    precio_congelado: float
    cuotas: int | None = None
    fecha_inicio: date
    fecha_vencimiento: date | None = None
    activo: bool

    class Config:
        from_attributes = True


class ServicioAsignadoDetalle(BaseModel):
    servicio_id: int
    servicio_nombre: str
    tipo: str
    precio_congelado: float
    cuotas: Optional[int] = None
    fecha_inicio: date
    fecha_vencimiento: Optional[date] = None
    estado: str  # "activo", "vencido", etc.

    class Config:
        from_attributes = True
