from pydantic import BaseModel
from datetime import date
from typing import Optional
from schemas.clientes import ClientesMini
#from schemas.servicios import ServiciosMini

class PagoIn(BaseModel):
    servicio_cliente_id: int
    monto: float
    fecha_facturacion: date
    fecha_pago: Optional[date] = None
    observaciones: Optional[str] = None

class PagoOut(BaseModel):
    id: int
    servicio_cliente_id: int
    monto: float
    fecha_facturacion: date
    fecha_pago: Optional[date] = None
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True


class HistorialPagoOut(BaseModel):
    monto: float
    fecha_facturacion: date
    fecha_pago: Optional[date]
    estado: str
    cliente: ClientesMini
    #servicio: ServiciosMini
    #cliente: str
    servicio: str

    class Config:
        from_attributes = True


class ResumenPagoOut(BaseModel):
    servicio_cliente_id: int
    cliente_nombre: str
    empresa: str
    servicio: str
    monto_total: float
    total_pagado: float
    estado: str  # "pagado" | "parcial" | "impago"
    saldo: float
    saldo_a_favor: float

    class Config:
        from_attributes = True

class EntradaPagoOut(BaseModel):
    cliente_nombre: str
    empresa: str
    servicio: str
    monto: float
    fecha_facturacion: date
    fecha_pago: Optional[date]
    observaciones: Optional[str]

    class Config:
        from_attributes = True

# class PagoItem(BaseModel):
#     descripcion: str
#     monto: float

#     class Config:
#         from_attributes = True