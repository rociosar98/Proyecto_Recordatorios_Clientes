from sqlalchemy import Column, Integer, Date, JSON
from database import Base
from datetime import date, datetime


class ListadoMensual(Base):
    __tablename__ = "listado_mensual"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, default=date.today)
    contenido = Column(JSON)  # guarda toda la info del listado

