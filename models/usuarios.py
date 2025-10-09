from database import Base
from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from core.enums import PermisoUsuario

class Usuarios(Base):

    __tablename__ = "usuarios" 

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(20))
    apellido = Column(String(20))
    correo = Column(String(100), unique=True)
    password = Column(String(100))
    rol = Column(String(20))
    activo = Column(Boolean, nullable=False, default=True)
    permiso = Column(Enum(PermisoUsuario, name="permiso_usuario"), nullable=False)

    clientes = relationship("Clientes", back_populates="responsable")
