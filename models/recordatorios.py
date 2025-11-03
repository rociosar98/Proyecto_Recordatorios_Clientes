from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Date, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import date, datetime
from core.enums import MetodoAviso, TipoRecordatorio, EstadoPago

class Recordatorios(Base):

    __tablename__ = "recordatorios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    servicio_cliente_id = Column(Integer, ForeignKey("servicios_clientes.id"), nullable=False)
    fecha_recordatorio = Column(Date, nullable=False)
    metodo_envio = Column(Enum(MetodoAviso, name="metodo_aviso", create_type=False), nullable=False)
    tipo_recordatorio = Column(Enum(TipoRecordatorio, name="tipo_recordatorio"), nullable=False)
    enviado = Column(Boolean, default=False)
    estado_pago = Column(Enum(EstadoPago, name="estado_pago", create_type=False), nullable=False)
    numero_cuota = Column(Integer, nullable=True)

    servicio_cliente = relationship("ServiciosCliente", back_populates="recordatorios")
