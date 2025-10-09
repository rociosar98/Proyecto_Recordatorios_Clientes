from models.servicios import Servicios as ServiciosModel, ServiciosCliente as ServiciosClienteModel
from schemas.servicios import Servicios, ServiciosCliente, AsignarServicioCliente
from typing import Optional
from fastapi.exceptions import HTTPException
from datetime import date
from dateutil.relativedelta import relativedelta
from models.clientes import Clientes as ClientesModel
from datetime import date, timedelta

class ServiciosService():
    
    def __init__(self, db) -> None:
        self.db = db

    def get_servicios(self):
        result = self.db.query(ServiciosModel).filter(ServiciosModel.activo == True).all()
        return result

    #def get_servicios(self):
    #    result = self.db.query(ServiciosModel).all()
    #    return result.all()

    def get_servicio_id(self, id):
        result = self.db.query(ServiciosModel).filter(ServiciosModel.id == id).first()
        return result
    
    def create_servicio(self, Servicio: Servicios):
        new_servicio = ServiciosModel(**Servicio.model_dump(exclude={"id"}))
        self.db.add(new_servicio)
        self.db.commit()
        return
    
    def update_servicio(self, id: int, data: Servicios):
        servicio = self.db.query(ServiciosModel).filter(ServiciosModel.id == id).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")

        #detectar si cambio el precio
        precio_anterior = servicio.precio
        nuevo_precio = data.precio
        cambio_precio = nuevo_precio != precio_anterior

        #actualizar campos
        servicio.nombre = data.nombre
        servicio.tipo = data.tipo
        servicio.precio = nuevo_precio
        servicio.recurrencia = data.recurrencia
        servicio.cuotas_permitidas = data.cuotas_permitidas

        #si es recurrente y cambio el precio, actualizar también los precios congelados de los clientes
        if servicio.tipo == "recurrente" and cambio_precio:
            clientes_servicio = self.db.query(ServiciosClienteModel).filter(
            ServiciosClienteModel.servicio_id == id,
            ServiciosClienteModel.activo == True
            ).all()
            for cliente_servicio in clientes_servicio:
                cliente_servicio.precio_congelado = nuevo_precio

        # Si es pago único, el precio NO se actualiza para clientes actuales
        self.db.commit()
        return
    
    def delete_servicio(self, id: int):
       servicio = self.db.query(ServiciosModel).filter(ServiciosModel.id == id).first()
       servicio.activo = False
       self.db.commit()
       return
    
    def asignar_servicio_cliente(self, data: AsignarServicioCliente):
        servicio = self.db.query(ServiciosModel).filter(ServiciosModel.id == data.servicio_id).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        
        # Verificar que el cliente exista
        cliente = self.db.query(ClientesModel).filter(ClientesModel.id == data.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Verificar si ya tiene ese servicio activo
        existente = self.db.query(ServiciosClienteModel).filter(
            ServiciosClienteModel.cliente_id == data.cliente_id,
            ServiciosClienteModel.servicio_id == data.servicio_id,
            ServiciosClienteModel.activo == True
        ).first()
        if existente:
            raise HTTPException(status_code=400, detail="El cliente ya tiene este servicio activo")
        
        # Calcular fechas
        fecha_inicio = date.today()
        fecha_vencimiento = None

        if servicio.tipo == "pago_unico":
            if data.cuotas not in [1, 3, 6, 12]:
                raise HTTPException(status_code=400, detail="Cantidad de cuotas inválida")
            meses = data.cuotas
            fecha_vencimiento = fecha_inicio + relativedelta(months = meses)
        elif servicio.tipo == "recurrente":
            # No hay vencimiento, es indefinido (hasta que se dé de baja manual)
            data.cuotas = None

        nuevo = ServiciosClienteModel(
            servicio_id = data.servicio_id,
            cliente_id = data.cliente_id,
            precio_congelado = servicio.precio,
            cuotas = data.cuotas,
            fecha_inicio = fecha_inicio,
            fecha_vencimiento = fecha_vencimiento,
            activo = True
        )

        self.db.add(nuevo)
        self.db.commit()
        return
    
    #def get_servicios_clientes(self):
    #    result = self.db.query(ServiciosClienteModel).filter(ServiciosClienteModel.activo == True).all()
    #    return result
    
    def get_servicios_asignados(self):
        servicios = self.db.query(
            ServiciosClienteModel,
            ServiciosModel.nombre.label("servicio_nombre"),
            ClientesModel.nombre.label("cliente_nombre")
        ).join(
            ServiciosModel, ServiciosClienteModel.servicio_id == ServiciosModel.id
        ).join(
            ClientesModel, ServiciosClienteModel.cliente_id == ClientesModel.id
        ).all()

        resultado = []
        for sc, servicio_nombre, cliente_nombre in servicios:
            resultado.append({
                "id": sc.id,
                "cliente_id": sc.cliente_id,
                "cliente_nombre": cliente_nombre,
                "servicio_id": sc.servicio_id,
                "servicio_nombre": servicio_nombre,
                "precio_congelado": sc.precio_congelado,
                "cuotas": sc.cuotas,
                "fecha_inicio": sc.fecha_inicio,
                "fecha_vencimiento": sc.fecha_vencimiento,
                "activo": sc.activo
            })

        return resultado

    

    def get_servicios_por_cliente(self, cliente_id: int):
        hoy = date.today()

        servicios = self.db.query(
            ServiciosClienteModel,
            ServiciosModel.nombre.label("servicio_nombre"),
            ServiciosModel.tipo
        ).join(
            ServiciosModel,
            ServiciosClienteModel.servicio_id == ServiciosModel.id
        ).filter(
            ServiciosClienteModel.cliente_id == cliente_id
        ).all()

        resultado = []
        for sc, servicio_nombre, tipo in servicios:
        # Determinar estado
            if not sc.activo:
                estado = "baja"
            elif sc.fecha_vencimiento and sc.fecha_vencimiento < hoy:
                estado = "vencido"
            else:
                estado = "activo"

            resultado.append({
                "servicio_id": sc.servicio_id,
                "servicio_nombre": servicio_nombre,
                "tipo": tipo,
                "precio_congelado": sc.precio_congelado,
                "cuotas": sc.cuotas,
                "fecha_inicio": sc.fecha_inicio,
                "fecha_vencimiento": sc.fecha_vencimiento,
                "estado": estado
            })

        return resultado

    
    def servicios_por_vencer(self, dias: int = 30):
        hoy = date.today()
        limite = hoy + timedelta(days = dias)

        servicios = self.db.query(ServiciosClienteModel).filter(
            ServiciosClienteModel.fecha_vencimiento != None,
            ServiciosClienteModel.fecha_vencimiento <= limite,
            ServiciosClienteModel.activo == True
        ).all()

        return servicios

        #return self.db.query(ServiciosClienteModel).filter(
        #    ServiciosClienteModel.fecha_vencimiento != None,
        #    ServiciosClienteModel.fecha_vencimiento <= limite,
        #    ServiciosClienteModel.activo == True
        #).all()
    




   

    