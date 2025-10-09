from models.datos_empresa import DatosEmpresa as DatosEmpresaModel
from schemas.datos_empresa import DatosEmpresa

class EmpresaService:

    def __init__(self, db) -> None:
        self.db = db

    #def __init__(self, db: Session):
    #    self.db = db

    def get_datos_empresa(self) -> DatosEmpresaModel | None:
        return self.db.query(DatosEmpresaModel).first()

    def update_datos_empresa(self, data: DatosEmpresa) -> DatosEmpresaModel:
        datos = self.get_datos_empresa()
        if datos:
            datos.cbu = data.cbu
            datos.cvu = data.cvu
            datos.formas_pago = data.formas_pago
        else:
            datos = DatosEmpresaModel(**data.dict())
            self.db.add(datos)

        self.db.commit()
        self.db.refresh(datos)
        return datos
    