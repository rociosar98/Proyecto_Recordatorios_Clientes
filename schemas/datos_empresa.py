from pydantic import BaseModel

class DatosEmpresa(BaseModel):
    cbu: str
    cvu: str
    formas_pago: str | None = None

    class Config:
        from_attributes = True
