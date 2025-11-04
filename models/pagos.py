from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
from core.enums import EstadoPago
from models.servicios import ServiciosCliente

class Pagos(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    servicio_cliente_id = Column(Integer, ForeignKey("servicios_clientes.id"), nullable=False)
    monto = Column(Float, nullable=False)
    fecha_facturacion = Column(Date, nullable=False)
    fecha_pago = Column(Date, nullable=True)
    estado = Column(Enum(EstadoPago, name="estado_pago"), nullable=False)
    observaciones = Column(String(250), nullable=True)

    servicio_cliente = relationship("ServiciosCliente", back_populates="pagos")

    @property
    def cliente(self):
        return self.servicio_cliente.cliente if self.servicio_cliente else None

    @property
    def servicio(self):
        return self.servicio_cliente.servicio if self.servicio_cliente else None


# class PagoItem(Base):
#     __tablename__ = "pagos_items"

#     id = Column(Integer, primary_key=True, index=True)
#     servicio_cliente_id = Column(Integer, ForeignKey("servicios_clientes.id"), nullable=False)
#     descripcion = Column(String(200), nullable=False)
#     monto = Column(Float, nullable=False)
#     fecha_generacion = Column(Date, nullable=True)  # opcional, si querés saber de qué mes es

#     # Relación con el servicio-cliente
#     servicio_cliente = relationship("ServiciosCliente", back_populates="items")