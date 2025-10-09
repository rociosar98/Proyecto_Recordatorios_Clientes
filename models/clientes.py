from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
from core.enums import MetodoAviso

class Clientes(Base):

    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(20))
    apellido = Column(String(20))
    empresa = Column(String(100))
    domicilio = Column(String(100))
    codigo_postal = Column(String(10))
    localidad = Column(String(50))
    provincia = Column(String(50))
    pais = Column(String(50))
    telefono = Column(String(20))
    whatsapp = Column(String(20))
    correo = Column(String(100), unique=True)
    metodo_aviso = Column(Enum(MetodoAviso ,name="metodo_aviso"), nullable=False)
    condicion_iva = Column(String(50))
    responsable_id = Column(Integer, ForeignKey("usuarios.id"))
    activo = Column(Boolean, nullable=False, default=True)

    # Relación con el usuario responsable
    responsable = relationship("Usuarios", back_populates="clientes")
    servicios = relationship("ServiciosCliente", back_populates="cliente")

