from models.clientes import Clientes as ClientesModel
from schemas.pagos import EntradaPagoOut
from typing import Optional
from models.pagos import Pagos as PagosModel
from models.servicios import ServiciosCliente as ServiciosClienteModel
from datetime import date
from datetime import timedelta
from sqlalchemy import extract
from sqlalchemy.orm import joinedload
from models.usuarios import Usuarios as UsuariosModel


class HistorialService:

    def __init__(self, db) -> None:
        self.db = db


    def obtener_historial(self, cliente_id: Optional[int] = None):
        query = (
            self.db.query(PagosModel)
            .join(ServiciosClienteModel)
            .options(
                joinedload(PagosModel.servicio_cliente).joinedload(ServiciosClienteModel.cliente),
                joinedload(PagosModel.servicio_cliente).joinedload(ServiciosClienteModel.servicio)
            )
        )

        if cliente_id:
            query = query.filter(ServiciosClienteModel.cliente_id == cliente_id)

        pagos = query.all()

        resultado = []

        for pago in pagos:
            pagos_relacionados = (
                self.db.query(PagosModel)
                .filter_by(servicio_cliente_id=pago.servicio_cliente_id)
                .all()
            )
            total_pagado = sum(p.monto for p in pagos_relacionados)
            monto_total = pago.servicio_cliente.precio_congelado

            # Determinar estado del pago
            if total_pagado >= monto_total:
                estado = "pagado"
            elif total_pagado > 0:
                estado = "parcial"
            else:
                estado = "pendiente"

            cliente = pago.servicio_cliente.cliente
            servicio = pago.servicio_cliente.servicio

            resultado.append({
                "monto": pago.monto,
                "fecha_facturacion": pago.fecha_facturacion,
                "fecha_pago": pago.fecha_pago,
                "estado": estado,
                "cliente": {
                    "id": cliente.id,
                    "nombre": cliente.nombre,
                    "apellido": cliente.apellido,
                    "empresa": cliente.empresa,
                    "condicion_iva": cliente.condicion_iva,
                },
                #"servicio": {
                #    "id": servicio.id,
                #    "nombre": servicio.nombre,
                "servicio": pago.servicio_cliente.servicio.nombre
                #}
            })

        return resultado


    def listar_por_filtros(self, condicion_iva: Optional[str], responsable_nombre: Optional[str]):
        query = (
            self.db.query(PagosModel)
            .join(ServiciosClienteModel, PagosModel.servicio_cliente_id == ServiciosClienteModel.id)
            .join(ClientesModel, ServiciosClienteModel.cliente_id == ClientesModel.id)
            .join(UsuariosModel, ClientesModel.responsable_id == UsuariosModel.id, isouter=True)
            .options(
                joinedload(PagosModel.servicio_cliente)
                .joinedload(ServiciosClienteModel.cliente)
                .joinedload(ClientesModel.responsable)
            )
        )

        if condicion_iva:
            query = query.filter(ClientesModel.condicion_iva == condicion_iva)

        if responsable_nombre:
            nombre_completo = (UsuariosModel.nombre + " " + UsuariosModel.apellido)
            query = query.filter(nombre_completo.ilike(f"%{responsable_nombre}%"))
            #query = query.filter(ClientesModel.responsable_id == responsable_cuenta)

        pagos = query.all()

        resultados = []
        for pago in pagos:
            resultados.append({
                "id": pago.id,
                "servicio_cliente_id": pago.servicio_cliente_id,
                "monto": pago.monto,
                "fecha_facturacion": pago.fecha_facturacion,
                "fecha_pago": pago.fecha_pago,
                "estado": pago.estado.value,
                "observaciones": pago.observaciones,
                "cliente": {
                    "id": pago.servicio_cliente.cliente.id,
                    "nombre": pago.servicio_cliente.cliente.nombre,
                    "apellido": pago.servicio_cliente.cliente.apellido,
                    "empresa": pago.servicio_cliente.cliente.empresa,
                    "condicion_iva": pago.servicio_cliente.cliente.condicion_iva,
                    "responsable": {
                        "id": pago.servicio_cliente.cliente.responsable.id,
                        "nombre": pago.servicio_cliente.cliente.responsable.nombre,
                        "apellido": pago.servicio_cliente.cliente.responsable.apellido
                    } if pago.servicio_cliente.cliente.responsable else None
                },
                "servicio": {
                    "id": pago.servicio_cliente.servicio.id,
                    "nombre": pago.servicio_cliente.servicio.nombre
                }
            })

        return resultados
    

    def listar_entradas(self, periodo: Optional[str], anio: Optional[int], mes: Optional[int], fecha_inicio: Optional[date], fecha_fin: Optional[date]):
        query = self.db.query(PagosModel)

        if periodo == "mensual":
            inicio = date(anio, mes, 1)
            if mes == 12:
                fin = date(anio + 1, 1, 1)
            else:
                fin = date(anio, mes + 1, 1)
            query = query.filter(PagosModel.fecha_facturacion >= inicio, PagosModel.fecha_facturacion < fin)

        elif periodo == "anual":
            inicio = date(anio, 1, 1)
            fin = date(anio + 1, 1, 1)
            query = query.filter(PagosModel.fecha_facturacion >= inicio, PagosModel.fecha_facturacion < fin)

        else:
            # Rango personalizado
            query = query.filter(PagosModel.fecha_facturacion >= fecha_inicio, PagosModel.fecha_facturacion <= fecha_fin)

        return query.all()

    