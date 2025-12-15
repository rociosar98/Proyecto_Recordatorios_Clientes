from pydantic import BaseModel
from datetime import date
from typing import Optional
from core.enums import MetodoAviso, TipoRecordatorio, EstadoPago

class RecordatorioOut(BaseModel):
    id: int
    servicio_cliente_id: int
    fecha_recordatorio: date
    metodo_envio: MetodoAviso
    tipo_recordatorio: TipoRecordatorio
    numero_cuota: Optional[int] = None
    enviado: bool
    estado_pago: Optional[EstadoPago] = None

    class Config:
        from_attributes = True

