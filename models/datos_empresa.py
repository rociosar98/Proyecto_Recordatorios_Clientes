from sqlalchemy import Column, Integer, String
from database import Base

class DatosEmpresa(Base):
    __tablename__ = "datos_empresa"

    id = Column(Integer, primary_key=True, index=True)
    cbu = Column(String(50), nullable=False)
    cvu = Column(String(50), nullable=False)
    formas_pago = Column(String(200), nullable=True)
