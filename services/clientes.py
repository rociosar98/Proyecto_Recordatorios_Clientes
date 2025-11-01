from models.clientes import Clientes as ClientesModel
from schemas.clientes import ClientesCreate, ClientesUpdate
from typing import Optional
from sqlalchemy.orm import joinedload

class ClientesService():
    
    def __init__(self, db) -> None:
        self.db = db

    def get_clientes(self, activo: Optional[bool] = None):
        query = (
            self.db.query(ClientesModel)
            .options(joinedload(ClientesModel.responsable))
        )

        if activo is not None:
            query = query.filter(ClientesModel.activo == activo)

        return query.all()



        #return (
        #    self.db.query(ClientesModel)
        #    .options(joinedload(ClientesModel.responsable))  # carga los datos del responsable
        #    .filter(ClientesModel.activo == True)
        #    .all()
        #)
        #result = self.db.query(ClientesModel).filter(ClientesModel.activo == True).all()
        #return result
    
    def get_cliente_id(self, id):
        return (
            self.db.query(ClientesModel)
            .options(joinedload(ClientesModel.responsable))
            .filter(ClientesModel.id == id)
            .first()
        )

        #result = self.db.query(ClientesModel).filter(ClientesModel.id == id).first()
        #return result
    
    def create_cliente(self, Cliente: ClientesCreate):
        new_cliente = ClientesModel(**Cliente.model_dump(exclude={"id"}))
        self.db.add(new_cliente)
        self.db.commit()
        return
    
    def update_cliente(self, id: int, data: ClientesUpdate):
        cliente = self.db.query(ClientesModel).filter(ClientesModel.id == id).first()
        cliente.nombre = data.nombre
        cliente.apellido = data.apellido
        cliente.empresa = data.empresa
        cliente.domicilio = data.domicilio
        cliente.codigo_postal = data.codigo_postal
        cliente.localidad = data.localidad
        cliente.provincia = data.provincia
        cliente.pais = data.pais
        cliente.telefono = data.telefono
        cliente.whatsapp = data.whatsapp
        cliente.correo = data.correo
        cliente.metodo_aviso = data.metodo_aviso
        cliente.condicion_iva = data.condicion_iva
        cliente.responsable_id = data.responsable_id
        self.db.commit()
        return

    def delete_cliente(self, id: int):
        cliente = self.db.query(ClientesModel).filter(ClientesModel.id == id).first()
        cliente.activo = False
        #cliente.fecha_baja = datetime.utcnow()
        self.db.commit()
        return

    #def delete_cliente(self, id: int):
    #    self.db.query(ClientesModel).filter(ClientesModel.id == id).delete()
    #    self.db.commit()
    #    return