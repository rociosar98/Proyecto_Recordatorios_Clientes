from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime, Date, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import date, datetime
from core.enums import TipoServicio, Recurrencia

class Servicios(Base):

    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(20))
    tipo = Column(Enum(TipoServicio, name="tipo_servicio"), nullable=False)
    precio = Column(Float, nullable=False)
    recurrencia = Column(Enum(Recurrencia, name="recurrencia_servicio"), nullable=True)
    cuotas = Column(Boolean, default=False)  # Solo aplica para pago único
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    clientes = relationship("ServiciosCliente", back_populates="servicio")


class ServiciosCliente(Base):

    __tablename__ = "servicios_clientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    precio_congelado = Column(Float, nullable=False)
    cuotas = Column(Integer, nullable=True)
    fecha_inicio = Column(Date, default=date.today)
    fecha_vencimiento = Column(Date, nullable=True)

    servicio = relationship("Servicios", back_populates="clientes")
    cliente = relationship("Clientes", back_populates="servicios")

    #servicio = relationship(Servicios)
    #cliente = relationship(Clientes)

    activo = Column(Boolean, default=True)

    recordatorios = relationship("Recordatorios", back_populates="servicio_cliente", cascade="all, delete-orphan")
    pagos = relationship("Pagos", back_populates="servicio_cliente")

